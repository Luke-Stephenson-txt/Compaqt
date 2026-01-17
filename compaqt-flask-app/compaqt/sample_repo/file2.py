"""
Authentication and authorization module.

Provides user authentication, session management,
and role-based access control functionality.
"""

import hashlib
import secrets
import time
from typing import Optional, Dict, List, Set
from dataclasses import dataclass, field
from enum import Enum


# Default session timeout in seconds (30 minutes)
DEFAULT_SESSION_TIMEOUT = 1800


class Role(Enum):
    """
    User roles for access control.
    
    These roles define the permission levels
    available in the system.
    """
    GUEST = "guest"
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


@dataclass
class User:
    """
    Represents a user in the system.
    
    Attributes:
        id: Unique user identifier
        username: User's login name
        email: User's email address
        password_hash: Hashed password
        roles: Set of roles assigned to user
        is_active: Whether the user account is active
        created_at: Timestamp of account creation
    """
    id: int
    username: str
    email: str
    password_hash: str
    roles: Set[Role] = field(default_factory=lambda: {Role.USER})
    is_active: bool = True
    created_at: float = field(default_factory=time.time)
    
    def has_role(self, role: Role) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
    
    def has_any_role(self, roles: List[Role]) -> bool:
        """Check if user has any of the specified roles."""
        return bool(self.roles.intersection(roles))


@dataclass
class Session:
    """
    Represents an authenticated user session.
    """
    token: str
    user_id: int
    created_at: float
    expires_at: float
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class PasswordHasher:
    """
    Secure password hashing utility.
    
    Uses SHA-256 with salt for password hashing.
    In production, use bcrypt or argon2 instead.
    """
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """
        Hash a password with salt.
        
        Args:
            password: Plain text password
            salt: Optional salt, generated if not provided
            
        Returns:
            Hashed password with salt prefix
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine salt and password
        salted = f"{salt}{password}"
        
        # Hash using SHA-256
        hash_obj = hashlib.sha256(salted.encode())
        password_hash = hash_obj.hexdigest()
        
        # Return salt:hash format
        return f"{salt}:{password_hash}"
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """
        Verify a password against stored hash.
        
        Args:
            password: Plain text password to verify
            stored_hash: Previously hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            salt, _ = stored_hash.split(":")
            new_hash = PasswordHasher.hash_password(password, salt)
            return secrets.compare_digest(new_hash, stored_hash)
        except ValueError:
            return False


class AuthenticationService:
    """
    Main authentication service.
    
    Handles user login, logout, and session management.
    """
    
    def __init__(self, session_timeout: int = DEFAULT_SESSION_TIMEOUT):
        """
        Initialize the authentication service.
        
        Args:
            session_timeout: Session timeout in seconds
        """
        self._users: Dict[int, User] = {}
        self._sessions: Dict[str, Session] = {}
        self._session_timeout = session_timeout
        self._hasher = PasswordHasher()
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str
    ) -> User:
        """
        Register a new user.
        
        Args:
            username: Desired username
            email: User's email
            password: Plain text password
            
        Returns:
            Created User object
        """
        # Generate unique ID
        user_id = len(self._users) + 1
        
        # Hash password
        password_hash = self._hasher.hash_password(password)
        
        # Create user
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        self._users[user_id] = user
        return user
    
    def authenticate(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Optional[Session]:
        """
        Authenticate a user and create a session.
        
        Args:
            username: User's username
            password: User's password
            ip_address: Client IP address
            
        Returns:
            Session object if successful, None otherwise
        """
        # Find user by username
        user = None
        for u in self._users.values():
            if u.username == username:
                user = u
                break
        
        if user is None or not user.is_active:
            return None
        
        # Verify password
        if not self._hasher.verify_password(password, user.password_hash):
            return None
        
        # Create session
        session = Session(
            token=secrets.token_urlsafe(32),
            user_id=user.id,
            created_at=time.time(),
            expires_at=time.time() + self._session_timeout,
            ip_address=ip_address
        )
        
        self._sessions[session.token] = session
        return session
    
    def validate_session(self, token: str) -> Optional[User]:
        """
        Validate a session token and return the user.
        
        Args:
            token: Session token to validate
            
        Returns:
            User if session is valid, None otherwise
        """
        session = self._sessions.get(token)
        
        if session is None:
            return None
        
        # Check expiration
        if time.time() > session.expires_at:
            del self._sessions[token]
            return None
        
        return self._users.get(session.user_id)
    
    def logout(self, token: str) -> bool:
        """
        Invalidate a session.
        
        Args:
            token: Session token to invalidate
            
        Returns:
            True if session was found and removed
        """
        if token in self._sessions:
            del self._sessions[token]
            return True
        return False
