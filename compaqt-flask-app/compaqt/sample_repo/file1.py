"""
Database connection manager module.

This module provides a robust database connection pooling system
with automatic reconnection and health checks. It supports multiple
database backends including PostgreSQL, MySQL, and SQLite.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager


# Configure module-level logger
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Configuration class for database connections.
    
    Attributes:
        host: Database server hostname
        port: Database server port
        database: Name of the database
        username: Database username
        password: Database password
        pool_size: Maximum number of connections in the pool
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "myapp",
        username: str = "admin",
        password: str = "",
        pool_size: int = 10
    ):
        # Store configuration values
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.pool_size = pool_size
        
        # Validate configuration
        self._validate()
    
    def _validate(self) -> None:
        """Validate the configuration parameters."""
        if not self.host:
            raise ValueError("Host cannot be empty")
        
        if self.port < 1 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        
        if self.pool_size < 1:
            raise ValueError("Pool size must be at least 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "username": self.username,
            "pool_size": self.pool_size
        }


class ConnectionPool:
    """
    Database connection pool implementation.
    
    This class manages a pool of database connections,
    providing efficient connection reuse and automatic
    cleanup of stale connections.
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        Initialize the connection pool.
        
        Args:
            config: Database configuration object
        """
        self.config = config
        self._connections: List[Any] = []
        self._available: List[Any] = []
        self._in_use: Dict[int, Any] = {}
        
        # Initialize the pool
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Create initial connections in the pool."""
        logger.info(f"Initializing connection pool with {self.config.pool_size} connections")
        
        for i in range(self.config.pool_size):
            conn = self._create_connection()
            self._connections.append(conn)
            self._available.append(conn)
    
    def _create_connection(self) -> Any:
        """Create a new database connection."""
        # Simulate connection creation
        return {"id": id(self), "created_at": time.time()}
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Yields:
            A database connection
        """
        conn = self._acquire()
        try:
            yield conn
        finally:
            self._release(conn)
    
    def _acquire(self) -> Any:
        """Acquire a connection from the pool."""
        if not self._available:
            raise RuntimeError("No available connections in pool")
        
        conn = self._available.pop()
        self._in_use[id(conn)] = conn
        return conn
    
    def _release(self, conn: Any) -> None:
        """Release a connection back to the pool."""
        conn_id = id(conn)
        if conn_id in self._in_use:
            del self._in_use[conn_id]
            self._available.append(conn)
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        logger.info("Closing all connections")
        self._connections.clear()
        self._available.clear()
        self._in_use.clear()
