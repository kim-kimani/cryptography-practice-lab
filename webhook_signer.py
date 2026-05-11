import hmac
import hashlib
import time
import json
from typing import Dict, Any

class WebhookSigner:
    """HMAC-SHA256 webhook signature handler"""
    
    def __init__(self, secret: str):
        self.secret = secret.encode('utf-8')
    
    def sign_payload(self, payload: Dict[str, Any]) -> str:
        """Generate HMAC-SHA256 signature for payload"""
        # Convert payload to JSON string
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        payload_bytes = payload_str.encode('utf-8')
        
        # Generate HMAC signature
        signature = hmac.new(
            self.secret, 
            payload_bytes, 
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, payload: Dict[str, Any], received_signature: str) -> bool:
        """Timing-safe signature verification"""
        expected_signature = self.sign_payload(payload)
        
        return hmac.compare_digest(expected_signature, received_signature)
    
    def sign_with_timestamp(self, payload: Dict[str, Any]) -> tuple:
        """Add timestamp to prevent replay attacks"""
        timestamp = str(int(time.time()))
        payload_with_ts = {**payload, "timestamp": timestamp}
        signature = self.sign_payload(payload_with_ts)
        return signature, timestamp

class StripeLikeWebhook(WebhookSigner):
    """Simulate Stripe/GitHub webhook signature format"""
    
    def sign_stripe_format(self, payload: Dict[str, Any]) -> str:
        """Stripe uses t=timestamp,v1=signature format"""
        signature, timestamp = self.sign_with_timestamp(payload)
        return f"t={timestamp},v1={signature}"
    
    def verify_stripe_format(self, payload: Dict[str, Any], stripe_header: str) -> bool:
        """Verify Stripe-style signature header"""
        try:
            parts = stripe_header.split(',')
            timestamp_part = parts[0].split('=')
            signature_part = parts[1].split('=')
            
            timestamp = timestamp_part[1]
            received_signature = signature_part[1]
            
            if abs(int(time.time()) - int(timestamp)) > 300:
                return False
            
            # Verify signature with timestamp
            payload_with_ts = {**payload, "timestamp": timestamp}
            expected = self.sign_payload(payload_with_ts)
            
            return hmac.compare_digest(expected, received_signature)
        except Exception:
            return False

if __name__ == "__main__":
    webhook_secret = "whsec_test_secret_key_12345"
    signer = WebhookSigner(webhook_secret)
    
    # Sample payload (e.g., GitHub webhook)
    payload = {
        "event": "push",
        "repository": "user/repo",
        "commits": ["abc123", "def456"],
        "ref": "refs/heads/main"
    }
    
    signature = signer.sign_payload(payload)
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"Signature: {signature}")
    
    is_valid = signer.verify_signature(payload, signature)
    print(f"Verification: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    
    tampered_payload = payload.copy()
    tampered_payload["commits"] = ["hacked123"]
    is_valid = signer.verify_signature(tampered_payload, signature)
    print(f"Tampered verification: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    
    # Stripe-style webhook
    stripe_handler = StripeLikeWebhook(webhook_secret)
    stripe_header = stripe_handler.sign_stripe_format(payload)
    print(f"\nStripe Header: {stripe_header}")
    is_valid = stripe_handler.verify_stripe_format(payload, stripe_header)
    print(f"Stripe verification: {'✓ PASSED' if is_valid else '✗ FAILED'}")