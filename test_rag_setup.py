#!/usr/bin/env python3
"""
RAG System Database Setup Testing Script
=========================================
Version: 1.0
Date: February 1, 2026
Author: John Dourvas
Purpose: Automated testing for RAG database setup verification

Tests:
1. PostgreSQL connection
2. pgvector extension
3. RAG tables existence
4. Indexes creation
5. CRUD operations
6. Vector operations
7. Performance benchmarks

Usage:
    python test_rag_setup.py --db-name unesco_platform --db-user django_app
"""

import sys
import time
import json
import argparse
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")


class RAGSetupTester:
    """Test suite for RAG database setup"""
    
    def __init__(self, db_name: str, db_user: str, db_password: str = None, 
                 db_host: str = 'localhost', db_port: int = 5432):
        """Initialize tester with database connection parameters"""
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.conn = None
        self.cursor = None
        self.test_results = []
        
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            # Register vector type
            try:
                from pgvector.psycopg2 import register_vector
                register_vector(self.conn)
            except ImportError:
                print_warning("pgvector Python package not installed. Vector operations will be limited.")
            
            return True
        except Exception as e:
            print_error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def add_result(self, test_name: str, passed: bool, message: str = "", duration_ms: float = 0):
        """Record test result"""
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message,
            'duration_ms': duration_ms
        })
    
    def test_postgresql_version(self) -> bool:
        """Test 1: Check PostgreSQL version"""
        print_header("TEST 1: PostgreSQL Version")
        
        try:
            start = time.time()
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()['version']
            duration_ms = (time.time() - start) * 1000
            
            print_info(f"PostgreSQL version: {version}")
            
            # Extract major version
            major_version = int(version.split()[1].split('.')[0])
            
            if major_version >= 12:
                print_success(f"PostgreSQL {major_version} is supported (>= 12 required)")
                self.add_result("PostgreSQL Version", True, f"Version {major_version}", duration_ms)
                return True
            else:
                print_error(f"PostgreSQL {major_version} is too old (>= 12 required)")
                self.add_result("PostgreSQL Version", False, f"Version {major_version} too old", duration_ms)
                return False
        except Exception as e:
            print_error(f"Failed to check PostgreSQL version: {e}")
            self.add_result("PostgreSQL Version", False, str(e))
            return False
    
    def test_pgvector_extension(self) -> bool:
        """Test 2: Check pgvector extension"""
        print_header("TEST 2: pgvector Extension")
        
        try:
            start = time.time()
            self.cursor.execute("""
                SELECT extversion 
                FROM pg_extension 
                WHERE extname = 'vector';
            """)
            result = self.cursor.fetchone()
            duration_ms = (time.time() - start) * 1000
            
            if result:
                version = result['extversion']
                print_success(f"pgvector extension installed (version {version})")
                self.add_result("pgvector Extension", True, f"Version {version}", duration_ms)
                return True
            else:
                print_error("pgvector extension not found")
                print_info("Run: CREATE EXTENSION IF NOT EXISTS vector;")
                self.add_result("pgvector Extension", False, "Extension not found", duration_ms)
                return False
        except Exception as e:
            print_error(f"Failed to check pgvector extension: {e}")
            self.add_result("pgvector Extension", False, str(e))
            return False
    
    def test_tables_exist(self) -> bool:
        """Test 3: Check RAG tables exist"""
        print_header("TEST 3: RAG Tables Existence")
        
        required_tables = ['documents', 'document_chunks', 'rag_queries']
        all_exist = True
        
        try:
            start = time.time()
            for table in required_tables:
                self.cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table,))
                
                exists = self.cursor.fetchone()['exists']
                
                if exists:
                    # Get row count and size
                    self.cursor.execute(f"""
                        SELECT 
                            COUNT(*) as row_count,
                            pg_size_pretty(pg_total_relation_size('{table}')) as size
                        FROM {table};
                    """)
                    stats = self.cursor.fetchone()
                    
                    print_success(f"Table '{table}' exists ({stats['row_count']} rows, {stats['size']})")
                else:
                    print_error(f"Table '{table}' not found")
                    all_exist = False
            
            duration_ms = (time.time() - start) * 1000
            
            if all_exist:
                self.add_result("RAG Tables", True, "All tables exist", duration_ms)
            else:
                self.add_result("RAG Tables", False, "Some tables missing", duration_ms)
            
            return all_exist
        except Exception as e:
            print_error(f"Failed to check tables: {e}")
            self.add_result("RAG Tables", False, str(e))
            return False
    
    def test_indexes_exist(self) -> bool:
        """Test 4: Check required indexes exist"""
        print_header("TEST 4: Indexes Existence")
        
        required_indexes = {
            'documents': ['idx_documents_type', 'idx_documents_module', 'idx_documents_created'],
            'document_chunks': ['idx_chunks_embedding', 'idx_chunks_document', 'idx_chunks_metadata'],
            'rag_queries': ['idx_rag_queries_user', 'idx_rag_queries_module', 'idx_rag_queries_rating']
        }
        
        all_exist = True
        
        try:
            start = time.time()
            for table, indexes in required_indexes.items():
                for index in indexes:
                    self.cursor.execute("""
                        SELECT indexname, indexdef
                        FROM pg_indexes
                        WHERE tablename = %s AND indexname = %s;
                    """, (table, index))
                    
                    result = self.cursor.fetchone()
                    
                    if result:
                        print_success(f"Index '{index}' exists on '{table}'")
                    else:
                        print_error(f"Index '{index}' not found on '{table}'")
                        all_exist = False
            
            # Check vector index specifically
            self.cursor.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'document_chunks' 
                AND indexname = 'idx_chunks_embedding'
                AND indexdef LIKE '%ivfflat%';
            """)
            
            vector_index = self.cursor.fetchone()
            if vector_index:
                print_success("Vector similarity index (ivfflat) exists")
            else:
                print_error("Vector similarity index (ivfflat) not found or incorrect type")
                all_exist = False
            
            duration_ms = (time.time() - start) * 1000
            
            if all_exist:
                self.add_result("Indexes", True, "All indexes exist", duration_ms)
            else:
                self.add_result("Indexes", False, "Some indexes missing", duration_ms)
            
            return all_exist
        except Exception as e:
            print_error(f"Failed to check indexes: {e}")
            self.add_result("Indexes", False, str(e))
            return False
    
    def test_crud_operations(self) -> bool:
        """Test 5: CRUD operations on RAG tables"""
        print_header("TEST 5: CRUD Operations")
        
        try:
            start = time.time()
            
            # CREATE: Insert test document
            self.cursor.execute("""
                INSERT INTO documents (title, document_type, file_path, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (
                "Test Document",
                "supplementary",
                "/tmp/test.pdf",
                json.dumps({"author": "Test Author", "date": "2026-02-01"})
            ))
            doc_id = self.cursor.fetchone()['id']
            self.conn.commit()
            print_success(f"Created test document (ID: {doc_id})")
            
            # CREATE: Insert test chunk
            test_embedding = np.random.rand(768).tolist()
            self.cursor.execute("""
                INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                doc_id,
                "This is a test chunk with some content for testing purposes.",
                0,
                test_embedding,
                json.dumps({"section": "Introduction", "page": 1})
            ))
            chunk_id = self.cursor.fetchone()['id']
            self.conn.commit()
            print_success(f"Created test chunk (ID: {chunk_id})")
            
            # READ: Query document
            self.cursor.execute("SELECT * FROM documents WHERE id = %s;", (doc_id,))
            doc = self.cursor.fetchone()
            if doc:
                print_success(f"Read document: {doc['title']}")
            else:
                print_error("Failed to read document")
                return False
            
            # UPDATE: Modify document
            self.cursor.execute("""
                UPDATE documents 
                SET total_chunks = 1 
                WHERE id = %s;
            """, (doc_id,))
            self.conn.commit()
            print_success("Updated document")
            
            # DELETE: Remove test data
            self.cursor.execute("DELETE FROM document_chunks WHERE id = %s;", (chunk_id,))
            self.cursor.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
            self.conn.commit()
            print_success("Deleted test data")
            
            duration_ms = (time.time() - start) * 1000
            self.add_result("CRUD Operations", True, "All operations successful", duration_ms)
            return True
            
        except Exception as e:
            self.conn.rollback()
            print_error(f"CRUD operations failed: {e}")
            self.add_result("CRUD Operations", False, str(e))
            return False
    
    def test_vector_operations(self) -> bool:
        """Test 6: Vector similarity operations"""
        print_header("TEST 6: Vector Operations")
        
        try:
            start = time.time()
            
            # Create test document
            self.cursor.execute("""
                INSERT INTO documents (title, document_type)
                VALUES ('Vector Test Document', 'supplementary')
                RETURNING id;
            """)
            doc_id = self.cursor.fetchone()['id']
            
            # Create test chunks with embeddings
            chunk_ids = []
            for i in range(5):
                embedding = np.random.rand(768).tolist()
                self.cursor.execute("""
                    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """, (doc_id, f"Test chunk {i}", i, embedding))
                chunk_ids.append(self.cursor.fetchone()['id'])
            
            self.conn.commit()
            print_success(f"Created {len(chunk_ids)} test chunks with embeddings")
            
            # Test similarity search
            query_embedding = np.random.rand(768).tolist()
            self.cursor.execute("""
                SELECT 
                    id,
                    chunk_text,
                    embedding <=> %s::vector AS distance
                FROM document_chunks
                WHERE embedding IS NOT NULL
                ORDER BY distance
                LIMIT 3;
            """, (query_embedding,))
            
            results = self.cursor.fetchall()
            print_success(f"Similarity search returned {len(results)} results")
            
            for idx, result in enumerate(results, 1):
                print_info(f"  {idx}. Distance: {result['distance']:.4f} - {result['chunk_text'][:50]}...")
            
            # Cleanup
            self.cursor.execute("DELETE FROM document_chunks WHERE document_id = %s;", (doc_id,))
            self.cursor.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
            self.conn.commit()
            
            duration_ms = (time.time() - start) * 1000
            self.add_result("Vector Operations", True, f"{len(results)} results found", duration_ms)
            return True
            
        except Exception as e:
            self.conn.rollback()
            print_error(f"Vector operations failed: {e}")
            self.add_result("Vector Operations", False, str(e))
            return False
    
    def test_constraints(self) -> bool:
        """Test 7: Database constraints"""
        print_header("TEST 7: Constraints Validation")
        
        all_passed = True
        
        try:
            # Test 1: Unique constraint on documents
            try:
                self.cursor.execute("""
                    INSERT INTO documents (title, document_type) VALUES ('Duplicate Test', 'supplementary');
                    INSERT INTO documents (title, document_type) VALUES ('Duplicate Test', 'supplementary');
                """)
                self.conn.commit()
                print_error("Unique constraint on documents NOT working")
                all_passed = False
            except psycopg2.IntegrityError:
                self.conn.rollback()
                print_success("Unique constraint on documents works")
            
            # Test 2: Check constraint on document_type
            try:
                self.cursor.execute("""
                    INSERT INTO documents (title, document_type) 
                    VALUES ('Invalid Type Test', 'invalid_type');
                """)
                self.conn.commit()
                print_error("Check constraint on document_type NOT working")
                all_passed = False
            except psycopg2.IntegrityError:
                self.conn.rollback()
                print_success("Check constraint on document_type works")
            
            # Test 3: Cascade delete
            self.cursor.execute("""
                INSERT INTO documents (title, document_type) VALUES ('Cascade Test', 'supplementary')
                RETURNING id;
            """)
            doc_id = self.cursor.fetchone()['id']
            
            self.cursor.execute("""
                INSERT INTO document_chunks (document_id, chunk_text, chunk_index)
                VALUES (%s, 'Test chunk', 0);
            """, (doc_id,))
            self.conn.commit()
            
            self.cursor.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
            self.conn.commit()
            
            self.cursor.execute("""
                SELECT COUNT(*) as count 
                FROM document_chunks 
                WHERE document_id = %s;
            """, (doc_id,))
            
            count = self.cursor.fetchone()['count']
            if count == 0:
                print_success("CASCADE DELETE works correctly")
            else:
                print_error("CASCADE DELETE not working")
                all_passed = False
            
            if all_passed:
                self.add_result("Constraints", True, "All constraints valid")
            else:
                self.add_result("Constraints", False, "Some constraints failed")
            
            return all_passed
            
        except Exception as e:
            self.conn.rollback()
            print_error(f"Constraint tests failed: {e}")
            self.add_result("Constraints", False, str(e))
            return False
    
    def test_performance_benchmark(self) -> bool:
        """Test 8: Performance benchmark"""
        print_header("TEST 8: Performance Benchmark")
        
        try:
            # Create test dataset
            print_info("Creating test dataset (100 chunks)...")
            
            self.cursor.execute("""
                INSERT INTO documents (title, document_type)
                VALUES ('Performance Test', 'supplementary')
                RETURNING id;
            """)
            doc_id = self.cursor.fetchone()['id']
            
            # Bulk insert chunks
            start = time.time()
            for i in range(100):
                embedding = np.random.rand(768).tolist()
                self.cursor.execute("""
                    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding)
                    VALUES (%s, %s, %s, %s);
                """, (doc_id, f"Performance test chunk {i}", i, embedding))
            self.conn.commit()
            insert_time = (time.time() - start) * 1000
            
            print_success(f"Inserted 100 chunks in {insert_time:.2f}ms ({insert_time/100:.2f}ms per chunk)")
            
            # Test query performance
            query_embedding = np.random.rand(768).tolist()
            
            start = time.time()
            self.cursor.execute("""
                SELECT id, chunk_text, embedding <=> %s::vector AS distance
                FROM document_chunks
                WHERE document_id = %s
                ORDER BY distance
                LIMIT 10;
            """, (query_embedding, doc_id))
            results = self.cursor.fetchall()
            query_time = (time.time() - start) * 1000
            
            print_success(f"Similarity search (100 vectors) took {query_time:.2f}ms")
            
            # Cleanup
            self.cursor.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
            self.conn.commit()
            
            # Performance thresholds
            insert_threshold = 10  # ms per chunk
            query_threshold = 100  # ms for search
            
            passed = (insert_time/100 < insert_threshold) and (query_time < query_threshold)
            
            if passed:
                self.add_result("Performance", True, 
                    f"Insert: {insert_time/100:.2f}ms/chunk, Query: {query_time:.2f}ms", 
                    query_time)
            else:
                self.add_result("Performance", False, 
                    f"Performance below threshold", 
                    query_time)
            
            return passed
            
        except Exception as e:
            self.conn.rollback()
            print_error(f"Performance benchmark failed: {e}")
            self.add_result("Performance", False, str(e))
            return False
    
    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        print(f"Total tests: {total}")
        print(f"{Colors.OKGREEN}Passed: {passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed: {failed}{Colors.ENDC}")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = f"{Colors.OKGREEN}✅ PASS{Colors.ENDC}" if result['passed'] else f"{Colors.FAIL}❌ FAIL{Colors.ENDC}"
            duration = f" ({result['duration_ms']:.2f}ms)" if result['duration_ms'] > 0 else ""
            message = f" - {result['message']}" if result['message'] else ""
            
            print(f"{status} - {result['test']}{duration}{message}")
        
        print()
        
        if failed == 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed! RAG system ready for implementation.{Colors.ENDC}")
            return 0
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}❌ Some tests failed. Please review errors above.{Colors.ENDC}")
            return 1
    
    def run_all_tests(self) -> int:
        """Run all tests"""
        print_header("RAG SYSTEM DATABASE SETUP TESTING")
        print(f"Database: {self.db_name}")
        print(f"User: {self.db_user}")
        print(f"Host: {self.db_host}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.connect():
            print_error("Failed to connect to database. Aborting tests.")
            return 1
        
        try:
            # Run all tests
            self.test_postgresql_version()
            self.test_pgvector_extension()
            self.test_tables_exist()
            self.test_indexes_exist()
            self.test_crud_operations()
            self.test_vector_operations()
            self.test_constraints()
            self.test_performance_benchmark()
            
            # Print summary
            return self.print_summary()
            
        finally:
            self.disconnect()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Test RAG database setup',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--db-name', required=True, help='Database name')
    parser.add_argument('--db-user', required=True, help='Database user')
    parser.add_argument('--db-password', help='Database password (optional, will prompt if not provided)')
    parser.add_argument('--db-host', default='localhost', help='Database host (default: localhost)')
    parser.add_argument('--db-port', type=int, default=5432, help='Database port (default: 5432)')
    
    args = parser.parse_args()
    
    # Prompt for password if not provided
    db_password = args.db_password
    if not db_password:
        import getpass
        db_password = getpass.getpass(f"Password for {args.db_user}: ")
    
    # Run tests
    tester = RAGSetupTester(
        db_name=args.db_name,
        db_user=args.db_user,
        db_password=db_password,
        db_host=args.db_host,
        db_port=args.db_port
    )
    
    return tester.run_all_tests()


if __name__ == '__main__':
    sys.exit(main())
