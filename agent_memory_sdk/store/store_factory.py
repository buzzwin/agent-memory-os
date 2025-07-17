"""
Store factory for Agent Memory OS

Creates appropriate storage backends based on configuration.
"""

import os
from typing import Optional

from .base_store import BaseStore
from .sqlite_store import SQLiteStore
from .pinecone_store import PineconeStore
from .postgresql_store import PostgreSQLStore


class StoreFactory:
    """Factory for creating storage backends"""

    @staticmethod
    def create_store(store_type: str = None, **kwargs) -> BaseStore:
        """
        Create a storage backend based on configuration

        Args:
            store_type: Type of store ('sqlite', 'pinecone', 'postgresql' or None for auto-detect)
            **kwargs: Additional arguments for the store

        Returns:
            Configured storage backend

        Raises:
            ValueError: If an unknown store type is specified.
            ImportError: If a required library for an auto-detected store is not installed.
        """
        # Auto-detect store type if not specified
        if not store_type:
            if os.getenv("POSTGRESQL_HOST") or os.getenv("POSTGRESQL_CONNECTION_STRING"):
                store_type = "postgresql"
            elif os.getenv("PINECONE_API_KEY"):
                # Try Pinecone, but fall back to SQLite if there are issues
                try:
                    # Attempt to import Pinecone. This line was indented incorrectly.
                    from pinecone import Pinecone # Keep this import here for the check
                    store_type = "pinecone"
                except ImportError: # Catch specific ImportError if Pinecone is not installed
                    print("⚠️ Pinecone not installed, falling back to SQLite.")
                    store_type = "sqlite"
            else:
                # Default to SQLite if no specific env vars are set
                store_type = "sqlite"
        
        # Ensure store_type is lowercase for consistent comparison
        store_type = store_type.lower()
        
        if store_type == "sqlite":
            db_path = kwargs.get("db_path", "agent_memory.db")
            return SQLiteStore(db_path=db_path)
        
        elif store_type == "pinecone":
            # Ensure Pinecone is actually available if it's the chosen type
            try:
                from pinecone import Pinecone # Re-import to confirm availability
            except ImportError:
                raise ImportError("Pinecone is selected but 'pinecone' package is not installed. Install with: pip install pinecone>=7.0.0")

            api_key = kwargs.get("api_key", os.getenv("PINECONE_API_KEY")) # Get from kwargs or env
            environment = kwargs.get("environment", os.getenv("PINECONE_ENVIRONMENT")) # Get from kwargs or env
            index_name = kwargs.get("index_name", "agent-memory-os")
            
            return PineconeStore(
                api_key=api_key,
                environment=environment,
                index_name=index_name,
                **kwargs # Pass remaining kwargs to PineconeStore constructor for flexibility
            )
        
        elif store_type == "postgresql":
            # Ensure psycopg2 is actually available if it's the chosen type
            try:
                import psycopg2 # Re-import to confirm availability
            except ImportError:
                raise ImportError("PostgreSQL is selected but 'psycopg2' package is not installed. Install with: pip install psycopg2-binary")

            connection_string = kwargs.get("connection_string", os.getenv("POSTGRESQL_CONNECTION_STRING"))
            if not connection_string:
                # If connection_string is not provided, try to build it from individual env vars
                host = kwargs.get("host", os.getenv("POSTGRESQL_HOST"))
                port = kwargs.get("port", os.getenv("POSTGRESQL_PORT", "5432"))
                user = kwargs.get("user", os.getenv("POSTGRESQL_USER"))
                password = kwargs.get("password", os.getenv("POSTGRESQL_PASSWORD"))
                database = kwargs.get("database", os.getenv("POSTGRESQL_DATABASE"))

                if host and user and database:
                    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
                else:
                    raise ValueError("PostgreSQL connection string or individual connection parameters (host, user, database) are required.")

            return PostgreSQLStore(connection_string=connection_string, **kwargs)
        
        else:
            raise ValueError(f"Unknown store type: {store_type}. Supported types: sqlite, pinecone, postgresql")

    #------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_available_stores() -> list:
        """Get list of available store types based on installed libraries and environment variables."""
        stores = ["sqlite"] # SQLite is always considered available as it's built-in

        # Check if PostgreSQL is available
        try:
            import psycopg2 # Attempt to import psycopg2 (or psycopg2-binary)
            # Only add if relevant environment variables are also set, indicating a potential configuration
            if os.getenv("POSTGRESQL_HOST") or os.getenv("POSTGRESQL_CONNECTION_STRING"):
                stores.append("postgresql")
        except ImportError:
            pass # psycopg2 not installed

        # Check if Pinecone is available
        try:
            from pinecone import Pinecone # Attempt to import Pinecone
            # Only add if an API key is available, indicating a potential configuration
            if os.getenv("PINECONE_API_KEY"):
                stores.append("pinecone")
        except ImportError:
            pass # Pinecone not installed
        except Exception as e:
            # Catch other potential issues with Pinecone client initialization/availability
            print(f"Warning: Could not verify Pinecone availability: {e}")
            pass
        
        return stores