from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import json
import base64

class RSASigner:
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    def generate_key_pair(self, key_size: int = 2048):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        print(f"✓ Generated RSA-{key_size} key pair")
        return self
    
    def export_keys_as_pem(self) -> tuple:
        """Export keys in PEM format"""
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # Production: Use BestAvailableEncryption()
        )
        
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode('utf-8'), public_pem.decode('utf-8')
    
    def sign_payload(self, payload: dict) -> str:
        """Sign JSON payload with private key (RSASSA-PSS)"""
        payload_str = json.dumps(payload, sort_keys=True)
        payload_bytes = payload_str.encode('utf-8')
        
        signature = self.private_key.sign(
            payload_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, payload: dict, signature_b64: str) -> bool:
        try:
            payload_str = json.dumps(payload, sort_keys=True)
            payload_bytes = payload_str.encode('utf-8')
            signature = base64.b64decode(signature_b64)
            
            self.public_key.verify(
                signature,
                payload_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Verification failed: {e}")
            return False
    
    def load_public_key_from_pem(self, public_pem: str):
        """Load public key from PEM string"""
        self.public_key = serialization.load_pem_public_key(
            public_pem.encode('utf-8'),
            backend=default_backend()
        )

if __name__ == "__main__":
    # Generate keys
    signer = RSASigner()
    signer.generate_key_pair(2048)
    
    private_pem, public_pem = signer.export_keys_as_pem()
    print("\n" + "="*60)
    print("RSA KEYS (PEM format)")
    print("="*60)
    print(f"Private Key (keep secret!):\n{private_pem[:200]}...\n")
    print(f"Public Key:\n{public_pem[:200]}...\n")
    
    payload = {
        "user_id": "12345",
        "action": "transfer",
        "amount": 1000,
        "currency": "USD",
        "timestamp": "2026-05-09T10:30:00Z"
    }
    
    signature = signer.sign_payload(payload)
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"Signature (base64): {signature}")
    
    is_valid = signer.verify_signature(payload, signature)
    print(f"\nVerification: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    
    tampered_payload = payload.copy()
    tampered_payload["amount"] = 99999
    
    is_valid = signer.verify_signature(tampered_payload, signature)
    print(f"Tampered verification: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    
    # OpenSSL command-line alternative
    print("\n" + "="*60)
    print("OpenSSL Command Alternative")
    print("="*60)
    print("""
    # Generate key pair
    openssl genrsa -out private.pem 2048
    openssl rsa -in private.pem -pubout -out public.pem
    
    # Sign a file
    echo '{"message":"hello"}' > payload.json
    openssl dgst -sha256 -sign private.pem -out signature.bin payload.json
    
    # Verify signature
    openssl dgst -sha256 -verify public.pem -signature signature.bin payload.json
    """)