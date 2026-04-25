-- ============================================================================
-- RAG SYSTEM TABLES - Phase 2A Implementation
-- ============================================================================
-- Version: 1.0
-- Date: February 1, 2026
-- Author: John Dourvas
-- Purpose: Database schema for RAG-powered reflection feedback system
-- Reference: M1_RAG_SYSTEM_FINAL_SPECIFICATION.md
-- ============================================================================

-- Prerequisites: Ensure pgvector extension is installed
-- Run: CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- TABLE 1: documents - Document metadata for RAG corpus
-- ============================================================================

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    module_id INTEGER,  -- NULL for universal documents (UNESCO, research papers)
    file_path TEXT,     -- PDF path or 'database' for module content
    total_chunks INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',  -- {author, date, language, page_count, etc.}
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_document_type CHECK (document_type IN (
        'unesco_framework', 
        'research_paper', 
        'module_content', 
        'supplementary'
    )),
    
    -- Foreign key will be added when modules table exists
    -- CONSTRAINT fk_documents_module FOREIGN KEY (module_id) 
    --     REFERENCES modules_module(id) ON DELETE SET NULL
    
    -- Ensure unique document entries
    CONSTRAINT unique_document UNIQUE(title, document_type)
);

-- Indexes for performance
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_module ON documents(module_id) WHERE module_id IS NOT NULL;
CREATE INDEX idx_documents_created ON documents(created_at);

-- Comments for documentation
COMMENT ON TABLE documents IS 'Metadata for documents in RAG system corpus (PDFs, module content)';
COMMENT ON COLUMN documents.title IS 'Document title (e.g., "UNESCO AI Competency Framework for Teachers")';
COMMENT ON COLUMN documents.document_type IS 'Document classification: unesco_framework, research_paper, module_content, supplementary';
COMMENT ON COLUMN documents.module_id IS 'NULL for universal documents, module ID for module-specific content';
COMMENT ON COLUMN documents.file_path IS 'Full path to PDF or "database" for content from database';
COMMENT ON COLUMN documents.total_chunks IS 'Total number of text chunks created from this document';
COMMENT ON COLUMN documents.metadata IS 'JSON object with author, date, language, page_count, etc.';

-- ============================================================================
-- TABLE 2: document_chunks - Text chunks with vector embeddings
-- ============================================================================

CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,      -- 500-1000 tokens of text
    chunk_index INTEGER NOT NULL,  -- Sequential order within document
    embedding vector(768),          -- Gemini embedding dimension
    metadata JSONB DEFAULT '{}',    -- {section, page, keywords, competency_level, unesco_aspect}
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_chunk UNIQUE(document_id, chunk_index),
    CONSTRAINT chunk_index_positive CHECK (chunk_index >= 0),
    CONSTRAINT chunk_text_not_empty CHECK (LENGTH(chunk_text) > 0)
);

-- Critical: Vector similarity index for fast RAG retrieval
-- Using ivfflat for approximate nearest neighbor search
CREATE INDEX idx_chunks_embedding ON document_chunks 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);  -- 100 clusters for ~10,000 chunks

-- Additional indexes for filtering and joining
CREATE INDEX idx_chunks_document ON document_chunks(document_id);
CREATE INDEX idx_chunks_metadata ON document_chunks USING gin(metadata);
CREATE INDEX idx_chunks_created ON document_chunks(created_at);

-- Comments for documentation
COMMENT ON TABLE document_chunks IS 'Text chunks with vector embeddings for RAG retrieval';
COMMENT ON COLUMN document_chunks.chunk_text IS 'Text content (500-1000 tokens, ~300-600 words)';
COMMENT ON COLUMN document_chunks.chunk_index IS 'Sequential position within parent document (0-based)';
COMMENT ON COLUMN document_chunks.embedding IS 'Gemini 768-dimensional embedding vector for similarity search';
COMMENT ON COLUMN document_chunks.metadata IS 'JSON with section, page, keywords, competency_level, unesco_aspect, etc.';

-- ============================================================================
-- TABLE 3: rag_queries - RAG query logs and user feedback
-- ============================================================================

CREATE TABLE rag_queries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,      -- Will reference auth_user(id) in Django
    module_id INTEGER NOT NULL,    -- Will reference modules_module(id) in Django
    
    -- Query Context
    reflection_text TEXT NOT NULL,      -- Teacher's original reflection
    teacher_context JSONB NOT NULL,     -- {subject, grade, experience, goals, etc.}
    
    -- RAG Process
    query_embedding vector(768),        -- Embedded query for retrieval
    retrieved_chunks JSONB DEFAULT '[]', -- [{chunk_id, distance, text_preview}]
    num_chunks_retrieved INTEGER DEFAULT 0,
    
    -- Generated Response
    generated_response TEXT NOT NULL,
    generation_tokens INTEGER,          -- For cost tracking
    
    -- User Feedback (Research Data)
    feedback_rating INTEGER,            -- 1-5 stars
    feedback_comments TEXT,
    feedback_timestamp TIMESTAMP,
    
    -- Performance & Cost Tracking
    processing_time_ms INTEGER,         -- Total processing time
    api_cost_eur NUMERIC(10, 6),        -- Actual cost in euros
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT feedback_rating_range CHECK (
        feedback_rating IS NULL OR 
        (feedback_rating BETWEEN 1 AND 5)
    ),
    CONSTRAINT tokens_positive CHECK (
        generation_tokens IS NULL OR 
        generation_tokens > 0
    ),
    CONSTRAINT cost_non_negative CHECK (
        api_cost_eur IS NULL OR 
        api_cost_eur >= 0
    ),
    CONSTRAINT processing_time_positive CHECK (
        processing_time_ms IS NULL OR 
        processing_time_ms > 0
    ),
    
    -- One reflection per user per module
    CONSTRAINT user_module_unique UNIQUE(user_id, module_id)
);

-- Indexes for research analysis and performance
CREATE INDEX idx_rag_queries_user ON rag_queries(user_id);
CREATE INDEX idx_rag_queries_module ON rag_queries(module_id);
CREATE INDEX idx_rag_queries_rating ON rag_queries(feedback_rating) 
    WHERE feedback_rating IS NOT NULL;
CREATE INDEX idx_rag_queries_created ON rag_queries(created_at);
CREATE INDEX idx_rag_queries_feedback_timestamp ON rag_queries(feedback_timestamp)
    WHERE feedback_timestamp IS NOT NULL;

-- Comments for documentation
COMMENT ON TABLE rag_queries IS 'RAG query logs with user feedback for research analysis';
COMMENT ON COLUMN rag_queries.reflection_text IS 'Original reflection text submitted by teacher';
COMMENT ON COLUMN rag_queries.teacher_context IS 'JSON with subject, grade_level, experience, goals, etc.';
COMMENT ON COLUMN rag_queries.query_embedding IS 'Embedded query vector for retrieval (768-dim)';
COMMENT ON COLUMN rag_queries.retrieved_chunks IS 'Array of retrieved chunk objects with IDs, distances, and previews';
COMMENT ON COLUMN rag_queries.generated_response IS 'Final AI-generated feedback displayed to teacher';
COMMENT ON COLUMN rag_queries.generation_tokens IS 'Number of tokens generated (for cost calculation)';
COMMENT ON COLUMN rag_queries.feedback_rating IS '1-5 star rating from teacher (NULL if not yet rated)';
COMMENT ON COLUMN rag_queries.api_cost_eur IS 'Actual API cost in euros (embedding + generation)';
COMMENT ON COLUMN rag_queries.processing_time_ms IS 'Total processing time in milliseconds';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update updated_at for documents
CREATE TRIGGER trigger_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Auto-update updated_at for rag_queries
CREATE TRIGGER trigger_rag_queries_updated_at
    BEFORE UPDATE ON rag_queries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- GRANT PERMISSIONS (adjust as needed for your setup)
-- ============================================================================

-- Grant permissions to Django application user (adjust username as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON documents TO django_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON document_chunks TO django_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON rag_queries TO django_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE documents_id_seq TO django_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE document_chunks_id_seq TO django_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE rag_queries_id_seq TO django_app_user;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables were created
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
FROM information_schema.tables
WHERE table_schema = 'public' 
    AND table_name IN ('documents', 'document_chunks', 'rag_queries')
ORDER BY table_name;

-- Verify indexes were created
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('documents', 'document_chunks', 'rag_queries')
ORDER BY tablename, indexname;

-- Verify pgvector extension is available
SELECT * FROM pg_extension WHERE extname = 'vector';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
