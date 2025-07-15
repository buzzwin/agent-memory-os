#!/usr/bin/env python3
"""
CLI script to run the Agent Memory OS REST API server
"""

import argparse
import uvicorn
import os
from pathlib import Path

from agent_memory_sdk.api import create_app


def main():
    parser = argparse.ArgumentParser(
        description="Run the Agent Memory OS REST API server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python run_api.py

  # Run on specific host and port
  python run_api.py --host 0.0.0.0 --port 8080

  # Run with custom database path
  python run_api.py --db-path /path/to/memory.db

  # Run in development mode with auto-reload
  python run_api.py --reload
        """
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    
    parser.add_argument(
        "--db-path",
        default="agent_memory.db",
        help="Path to the SQLite database file (default: agent_memory.db)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Validate database path
    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"Warning: Database file '{db_path}' does not exist. It will be created automatically.")
    
    print(f"🚀 Starting Agent Memory OS API server...")
    print(f"📍 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"💾 Database: {args.db_path}")
    print(f"📊 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 Interactive API: http://{args.host}:{args.port}/redoc")
    print(f"❤️  Health Check: http://{args.host}:{args.port}/health")
    print()
    
    # Create the app with the specified database path
    from agent_memory_sdk.api.server import create_app
    app = create_app(str(db_path))
    
    # Run the server
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        workers=args.workers if not args.reload else 1,
        access_log=True,
    )


if __name__ == "__main__":
    main() 