"""
LLM client wrapper — abstracts NEW (google.genai) vs OLD (google.generativeai)
Gemini SDK detection into a single interface used by every agent.

Replaces the dual-import block that was duplicated inline at 5 call sites in
rag_query_system.py (embed_query, generate_feedback, synthesize_peer_insight,
extract_tensions, extract_development_themes / generate_development_narrative).

Cost-estimation formula matches the monolith (rag_query_system.py:553-554):
    tokens_estimate   = len(text.split()) * 1.3
    cost_eur_estimate = (tokens_estimate / 1_000_000) * 0.30 * 0.93

The 0.30 USD/Mtok rate is the Gemini 2.5 Flash output price; 0.93 is the
USD->EUR conversion used elsewhere in the monolith. Both centralised here as
module constants so a price/rate change is a single-line edit.
"""

import os
from dataclasses import dataclass
from typing import Any, Optional


DEFAULT_MODEL = 'gemini-2.5-flash'
DEFAULT_EMBEDDING_MODEL_NEW = 'models/gemini-embedding-001'
DEFAULT_EMBEDDING_MODEL_OLD = 'models/text-embedding-004'
DEFAULT_EMBEDDING_DIM = 768

# Cost model — kept consistent with rag_query_system.process_reflection().
USD_PER_MILLION_OUTPUT_TOKENS = 0.30
USD_TO_EUR = 0.93
WORDS_TO_TOKENS = 1.3


@dataclass
class GenerationResult:
    """Composite return value from LLMClient.generate.

    Carries the generated text plus the cost-accounting fields every agent's
    cost-tracker needs. Agents should treat `text` as the primary payload and
    pass the whole object to `_track_cost`.
    """
    text: str
    model: str
    tokens_estimate: int
    cost_eur_estimate: float


class LLMClient:
    """Single Gemini facade for all agents.

    Detects which Google SDK is installed on import and dispatches accordingly.
    Tests mock this class via `get_llm_client()` patching.
    """

    def __init__(self):
        self._new_api = False
        self._client = None
        self._genai_old = None
        api_key = os.getenv('GEMINI_API_KEY')

        try:
            from google import genai as genai_client
            self._new_api = True
            self._client = genai_client.Client(api_key=api_key)
            return
        except ImportError:
            pass

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self._genai_old = genai
        except ImportError as exc:
            raise RuntimeError(
                "Neither google.genai nor google.generativeai is installed. "
                "Install one with: pip install google-genai"
            ) from exc

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------
    def embed(self, text: str, output_dim: int = DEFAULT_EMBEDDING_DIM):
        """Return embedding vector for `text`, or None on failure.

        Matches the behaviour of rag_query_system.embed_query: dimension
        reduction to 768 under the NEW API to stay compatible with the
        existing pgvector schema; OLD API uses text-embedding-004 which is
        already 768-d.
        """
        try:
            if self._new_api:
                result = self._client.models.embed_content(
                    model=DEFAULT_EMBEDDING_MODEL_NEW,
                    contents=text,
                    config={"output_dimensionality": output_dim},
                )
                if hasattr(result, 'embeddings') and result.embeddings:
                    return result.embeddings[0].values
                # Fallback shape — older client builds returned a dict.
                return result if isinstance(result, list) else result.get(
                    'embedding', result,
                )
            else:
                result = self._genai_old.embed_content(
                    model=DEFAULT_EMBEDDING_MODEL_OLD,
                    content=text,
                    task_type="retrieval_query",
                )
                return result['embedding']
        except Exception as exc:
            # Mirror the monolith: print to stderr, return None, do not raise.
            # Callers branch on None to surface graceful UI fallbacks.
            import traceback
            print(f"LLMClient.embed error: {exc}")
            traceback.print_exc()
            return None

    # ------------------------------------------------------------------
    # Text generation
    # ------------------------------------------------------------------
    def generate(
        self,
        prompt: str,
        *,
        model: str = DEFAULT_MODEL,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
    ) -> Optional[GenerationResult]:
        """Generate text with Gemini. Return GenerationResult or None.

        None signals API failure — the monolith returns None on errors and
        callers check for that; we preserve the contract verbatim so the
        strangler-step prompt-and-behaviour parity tests stay green.

        thinking_budget: pass 0 to disable Gemini 2.5 model thinking, so the
        whole `max_output_tokens` budget is available for the visible
        response. Agents that use an explicit in-response reasoning scaffold
        (e.g. XAIAgent's <reasoning> block) should disable thinking — the
        model's hidden thinking would otherwise duplicate that scaffold and
        consume the token budget, truncating the visible answer. Only the
        NEW google.genai SDK supports this; ignored on the OLD SDK.
        """
        try:
            if self._new_api:
                from google.genai import types as genai_types
                config_kwargs: dict[str, Any] = {}
                if max_output_tokens is not None:
                    config_kwargs['max_output_tokens'] = max_output_tokens
                if temperature is not None:
                    config_kwargs['temperature'] = temperature
                if thinking_budget is not None:
                    config_kwargs['thinking_config'] = genai_types.ThinkingConfig(
                        thinking_budget=thinking_budget,
                    )
                config = (
                    genai_types.GenerateContentConfig(**config_kwargs)
                    if config_kwargs
                    else None
                )
                response = self._client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                if not response or not response.candidates:
                    return None
                text = response.text
                if not text or not text.strip():
                    return None
            else:
                gen_config = None
                if temperature is not None or max_output_tokens is not None:
                    gen_config = self._genai_old.types.GenerationConfig(
                        **{
                            k: v for k, v in {
                                'temperature': temperature,
                                'max_output_tokens': max_output_tokens,
                            }.items() if v is not None
                        }
                    )
                old_model = self._genai_old.GenerativeModel(model)
                response = (
                    old_model.generate_content(prompt, generation_config=gen_config)
                    if gen_config is not None
                    else old_model.generate_content(prompt)
                )
                text = response.text

            tokens = int(len(text.split()) * WORDS_TO_TOKENS)
            cost_eur = (tokens / 1_000_000) * USD_PER_MILLION_OUTPUT_TOKENS * USD_TO_EUR
            return GenerationResult(
                text=text,
                model=model,
                tokens_estimate=tokens,
                cost_eur_estimate=cost_eur,
            )
        except Exception as exc:
            import traceback
            print(f"LLMClient.generate error: {exc}")
            traceback.print_exc()
            return None


_singleton: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Return the process-wide LLMClient.

    Lazy instantiation lets tests patch the symbol before the first call
    without needing to load credentials at import time.
    """
    global _singleton
    if _singleton is None:
        _singleton = LLMClient()
    return _singleton


def reset_llm_client_for_tests() -> None:
    """Test-only hook — re-initialises the singleton on next access."""
    global _singleton
    _singleton = None
