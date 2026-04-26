-- =============================================================================
-- Migration: Module data normalisation
-- Date:      April 2026
-- Branch:    claude/relaxed-williamson-20a883
-- Author:    surfaced during TAB1 redesign (commit 38c2e86)
-- =============================================================================
--
-- Purpose: Bring modules_module rows into agreement with the Django model's
--          choices tuples and the canonical UNESCO mapping documented in
--          MODULE_CONTENT_GUIDE.md / Doctoral_System_Design_Summary.md /
--          CONTENT_VALIDATION_MATRIX.md.
--
-- Targets four pre-existing data quality issues (data only, no schema change):
--
--   1. unesco_aspect column held a mix of snake_case and Title Case values,
--      with several rows holding values not in the model's choices tuple
--      (causing get_unesco_aspect_display() to fall through to raw values).
--
--   2. proficiency_level for M2, M7, M12 was lowercase ('acquire' / 'deepen'
--      / 'create') instead of the model's Title Case choices.
--
--   3. M1 unesco_aspect was 'ai_foundations' (Aspect 3). Per the canonical
--      mapping, M1 belongs to Aspect 1 — Human-Centred Mindset. The TAB1
--      MODULE_TO_ASPECT hardcoded mapping was already correct; this brings
--      the database into agreement.
--
--   4. M8 module_overview was stored as a JSON blob {"overview": "..."}
--      instead of plain text. After this migration, the unwrap_overview
--      template filter is no longer needed and will be removed in a
--      follow-up commit.
--
-- Style note: targeted UPDATEs (only rows that need changing) are used here
--             instead of generic IN-clauses. This makes the change set fully
--             transparent in the Postgres "UPDATE n" output, and keeps the
--             migration idempotent — re-running it is a no-op for rows that
--             are already canonical.
--
-- Run instructions: open in pgAdmin, execute the BEGIN block + verification
--                   SELECTs, inspect output, then manually uncomment either
--                   COMMIT or ROLLBACK at the bottom.
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Issue 1 + 3: unesco_aspect normalisation (6 rows)
-- -----------------------------------------------------------------------------

-- M1: 'ai_foundations' -> 'human_centered'
-- Issue 3: M1 belongs to Aspect 1 (Human-Centred Mindset), not Aspect 3.
-- The DB had M1 mis-classified; the canonical mapping per the dissertation
-- documentation places M1 in Aspect 1.
UPDATE modules_module SET unesco_aspect = 'human_centered' WHERE code = 'M1';

-- M4: 'AI Pedagogy' -> 'ai_pedagogy'
-- Title Case value not present in the model's choices; normalising to
-- the canonical snake_case value 'ai_pedagogy'.
UPDATE modules_module SET unesco_aspect = 'ai_pedagogy' WHERE code = 'M4';

-- M6: 'human_centred_mindset' -> 'human_centered'
-- British spelling with '_mindset' suffix is not in the model's choices.
-- Model uses American spelling 'human_centered' without suffix.
UPDATE modules_module SET unesco_aspect = 'human_centered' WHERE code = 'M6';

-- M9: 'AI Pedagogy' -> 'ai_pedagogy'
-- Same Title Case issue as M4.
UPDATE modules_module SET unesco_aspect = 'ai_pedagogy' WHERE code = 'M9';

-- M11: 'human_centred_mindset' -> 'human_centered'
-- Same British-spelling issue as M6.
UPDATE modules_module SET unesco_aspect = 'human_centered' WHERE code = 'M11';

-- M15: 'Professional Development' -> 'professional_development'
-- Same Title Case issue as M4 / M9, for the Aspect 5 column.
UPDATE modules_module SET unesco_aspect = 'professional_development' WHERE code = 'M15';

-- -----------------------------------------------------------------------------
-- Issue 2: proficiency_level normalisation (3 rows)
-- -----------------------------------------------------------------------------

-- M2: 'acquire' -> 'Acquire'
-- Lowercase value not in the model's Title Case choices tuple, causing
-- get_proficiency_level_display() to fall through to the raw lowercase string.
UPDATE modules_module SET proficiency_level = 'Acquire' WHERE code = 'M2';

-- M7: 'deepen' -> 'Deepen'
-- Same lowercase issue as M2.
UPDATE modules_module SET proficiency_level = 'Deepen' WHERE code = 'M7';

-- M12: 'create' -> 'Create'
-- Same lowercase issue as M2.
UPDATE modules_module SET proficiency_level = 'Create' WHERE code = 'M12';

-- -----------------------------------------------------------------------------
-- Issue 4: Unwrap M8 module_overview from JSON blob to plain text (1 row)
-- -----------------------------------------------------------------------------

-- M8: '{"overview": "..."}' -> '...'
-- Column type is text (not jsonb); the ::jsonb cast parses the text as JSON
-- at execution time, then ->> 'overview' extracts the inner string. The
-- WHERE-clause LIKE guard makes this safely idempotent: re-running after
-- the unwrap leaves the row alone.
UPDATE modules_module
SET    module_overview = (module_overview::jsonb ->> 'overview')
WHERE  code = 'M8'
  AND  module_overview LIKE '{"overview"%';

-- =============================================================================
-- Verification 1: per-row canonicality check
-- =============================================================================
-- All 15 rows should print is_canonical = 'OK'. Any 'WRONG' means an UPDATE
-- above did not land as expected and the migration must be ROLLBACKed.

SELECT code,
       unesco_aspect,
       proficiency_level,
       CASE
         WHEN (code = 'M1'  AND unesco_aspect = 'human_centered'           AND proficiency_level = 'Acquire')
           OR (code = 'M2'  AND unesco_aspect = 'ethics'                   AND proficiency_level = 'Acquire')
           OR (code = 'M3'  AND unesco_aspect = 'ai_foundations'           AND proficiency_level = 'Acquire')
           OR (code = 'M4'  AND unesco_aspect = 'ai_pedagogy'              AND proficiency_level = 'Acquire')
           OR (code = 'M5'  AND unesco_aspect = 'professional_development' AND proficiency_level = 'Acquire')
           OR (code = 'M6'  AND unesco_aspect = 'human_centered'           AND proficiency_level = 'Deepen')
           OR (code = 'M7'  AND unesco_aspect = 'ethics'                   AND proficiency_level = 'Deepen')
           OR (code = 'M8'  AND unesco_aspect = 'ai_foundations'           AND proficiency_level = 'Deepen')
           OR (code = 'M9'  AND unesco_aspect = 'ai_pedagogy'              AND proficiency_level = 'Deepen')
           OR (code = 'M10' AND unesco_aspect = 'professional_development' AND proficiency_level = 'Deepen')
           OR (code = 'M11' AND unesco_aspect = 'human_centered'           AND proficiency_level = 'Create')
           OR (code = 'M12' AND unesco_aspect = 'ethics'                   AND proficiency_level = 'Create')
           OR (code = 'M13' AND unesco_aspect = 'ai_foundations'           AND proficiency_level = 'Create')
           OR (code = 'M14' AND unesco_aspect = 'ai_pedagogy'              AND proficiency_level = 'Create')
           OR (code = 'M15' AND unesco_aspect = 'professional_development' AND proficiency_level = 'Create')
         THEN 'OK'
         ELSE 'WRONG'
       END AS is_canonical
FROM   modules_module
ORDER  BY order_index;

-- =============================================================================
-- Verification 2: M8 overview unwrap
-- =============================================================================
-- The preview should start with plain text (e.g. "This module moves from ...")
-- and must NOT begin with '{"overview"'.

SELECT id,
       code,
       LEFT(module_overview, 100) AS overview_preview
FROM   modules_module
WHERE  code = 'M8';

-- =============================================================================
-- After verification — uncomment ONE of the lines below in pgAdmin:
-- =============================================================================
-- COMMIT;
-- ROLLBACK;
