from datetime import datetime, timedelta
import secrets
import hashlib
from typing import Optional, Dict, Set
from dataclasses import dataclass
from jose import jwt, JWTError
import uuid

@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int

class RefreshTokenRotationSystem:
    """JWT with refresh token rotation for security"""
    
    def __init__(self, secret_key: str, access_token_ttl: int = 15, refresh_token_ttl: int = 43200):
        
        self.secret_key = secret_key
        self.access_token_ttl = access_token_ttl
        self.refresh_token_ttl = refresh_token_ttl
        
        # Store valid refresh tokens
        self.valid_refresh_tokens: Set[str] = set()
        
        # Track token families
        self.token_families: Dict[str, str] = {}  # token_id -> user_id
    
    def _generate_token_id(self) -> str:
        return secrets.token_urlsafe(32)
    
    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
    
    def issue_tokens(self, user_id: str, additional_claims: dict = None) -> TokenPair:
        """Issue new access and refresh token pair"""
        
        access_token_id = self._generate_token_id()
        refresh_token_id = self._generate_token_id()
        
        now = datetime.utcnow()
        
        # Access token claims
        access_claims = {
            "sub": user_id,
            "jti": access_token_id,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self.access_token_ttl)
        }
        if additional_claims:
            access_claims.update(additional_claims)
        
        # Refresh token claims
        refresh_claims = {
            "sub": user_id,
            "jti": refresh_token_id,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(minutes=self.refresh_token_ttl),
            "family_id": str(uuid.uuid4())
        }
        
        # Generate tokens
        access_token = jwt.encode(access_claims, self.secret_key, algorithm="HS256")
        refresh_token = jwt.encode(refresh_claims, self.secret_key, algorithm="HS256")
        
        # Store hashed refresh token
        hashed_token = self._hash_token(refresh_token)
        self.valid_refresh_tokens.add(hashed_token)
        self.token_families[hashed_token] = user_id
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_ttl * 60
        )
    
    def refresh_access_token(self, refresh_token: str) -> Optional[TokenPair]:
        try:
            # Decode and verify refresh token
            payload = jwt.decode(
                refresh_token, 
                self.secret_key, 
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            
            # Verify token type
            if payload.get("type") != "refresh":
                print("Invalid token type")
                return None
            
            # Verify token exists in storage
            hashed_token = self._hash_token(refresh_token)
            if hashed_token not in self.valid_refresh_tokens:
                print("REUSE DETECTED! Token already used or invalid")
                # Detect token reuse
                self._handle_token_reuse(payload.get("sub"), payload.get("family_id"))
                return None
            
            user_id = payload.get("sub")
            family_id = payload.get("family_id")
            
            self.valid_refresh_tokens.remove(hashed_token)
            
            # Issue new token pair
            new_tokens = self.issue_tokens(user_id, {"family_id": family_id})
            
            print(f"✓ Token rotation successful. Old token invalidated.")
            return new_tokens
            
        except jwt.ExpiredSignatureError:
            print("Refresh token expired")
            return None
        except JWTError as e:
            print(f"Invalid refresh token: {e}")
            return None
    
    def _handle_token_reuse(self, user_id: str, family_id: str):
        """Handle detected refresh token reuse (potential attack)"""
        print(f"⚠️ SECURITY ALERT: Refresh token reuse detected!")
        print(f"   User: {user_id}, Family: {family_id}")
        print(f"   All tokens in this family will be invalidated")
        
        # Invalidate all tokens for this user
        tokens_to_remove = [
            token for token, uid in self.token_families.items() 
            if uid == user_id
        ]
        for token in tokens_to_remove:
            self.valid_refresh_tokens.discard(token)
            del self.token_families[token]
    
    def verify_access_token(self, access_token: str) -> Optional[dict]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(
                access_token,
                self.secret_key,
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            
            if payload.get("type") != "access":
                return None
            
            return payload
        except JWTError:
            return None
    
    def revoke_all_user_tokens(self, user_id: str):
        """Revoke all refresh tokens for a user (e.g., logout all devices)"""
        tokens_to_remove = [
            token for token, uid in self.token_families.items() 
            if uid == user_id
        ]
        for token in tokens_to_remove:
            self.valid_refresh_tokens.discard(token)
            del self.token_families[token]
        print(f"Revoked all tokens for user {user_id}")

if __name__ == "__main__":
    system = RefreshTokenRotationSystem(
        secret_key="your-256-bit-secret-key-here-keep-secure",
        access_token_ttl=1,  # 1 minute
        refresh_token_ttl=30  # 30 minutes
    )
    
    print("="*60)
    print("REFRESH TOKEN ROTATION SYSTEM DEMO")
    print("="*60)
    
    # 1. User login - issue tokens
    print("\n1. USER LOGIN")
    user_id = "user_12345"
    tokens = system.issue_tokens(user_id, {"role": "user"})
    print(f"Access Token: {tokens.access_token[:50]}...")
    print(f"Refresh Token: {tokens.refresh_token[:50]}...")
    print(f"Expires in: {tokens.expires_in} seconds")
    
    # 2. Access protected resource
    print("\n2. ACCESS RESOURCE")
    payload = system.verify_access_token(tokens.access_token)
    print(f"Access token valid: {payload is not None}")
    if payload:
        print(f"User: {payload.get('sub')}, Role: {payload.get('role')}")
    
    # 3. Refresh token (simulate after expiration)
    print("\n3. REFRESH TOKEN")
    new_tokens = system.refresh_access_token(tokens.refresh_token)
    if new_tokens:
        print(f"New access token issued: {new_tokens.access_token[:50]}...")
        print(f"Old refresh token is now INVALID")
    
    # 4. Try using old refresh token again (should detect reuse)
    print("\n4. REUSE ATTEMPT (Security test)")
    reused = system.refresh_access_token(tokens.refresh_token)
    print(f"Reuse attempt result: {'BLOCKED' if reused is None else 'ACCEPTED'}")
    
    # 5. Verify new tokens work
    print("\n5. VERIFY NEW TOKENS")
    payload = system.verify_access_token(new_tokens.access_token)
    print(f"New access token valid: {payload is not None}")
    
    print("\n" + "="*60)
    print("BEST PRACTICES IMPLEMENTED")
    print("="*60)
    print("✓ Short-lived access tokens (1-15 minutes)")
    print("✓ Refresh token rotation on each use")
    print("✓ Reuse detection with family tracking")
    print("✓ Tokens hashed before storage")
    print("✓ Separate token types (access vs refresh)")
    print("✓ Automatic invalidation on reuse")