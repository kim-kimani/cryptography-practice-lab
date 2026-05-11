# Cryptography for Developers - Practice Exercises

A comprehensive set of hands-on exercises covering essential cryptography concepts for developers, including **TLS certificate validation**, **HMAC signatures**, **RSA digital signatures**, and **JWT refresh token rotation**.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Exercises Overview](#exercises-overview)
- [Exercise 1: TLS Certificate Inspection](#exercise-1-tls-certificate-inspection)
- [Exercise 2: HMAC-SHA256 Webhook Signatures](#exercise-2-hmac-sha256-webhook-signatures)
- [Exercise 3: RSA Digital Signatures](#exercise-3-rsa-digital-signatures)
- [Exercise 4: Refresh Token Rotation System](#exercise-4-refresh-token-rotation-system)
- [Best Practices Summary](#best-practices-summary)
- [Common Issues & Solutions](#common-issues--solutions)
- [Project Structure](#project-structure)
- [Additional Resources](#additional-resources)
- [License](#license)
- [Contributing](#contributing)
- [Support](#support)

---

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu/Debian recommended)
- **Python**: 3.8 or higher
- **Tools**: OpenSSL command-line tools
- **Internet**: Required for TLS exercises

### Required Python Packages

```bash
# Core cryptography libraries
pip3 install cryptography pyopenssl requests

# JWT libraries
pip3 install pyjwt python-jose[cryptography]

# Password hashing (bonus)
pip3 install passlib[bcrypt]

# Utilities
pip3 install certifi
```

---

## Installation

### 1. Clone or Create Project Directory

```bash
mkdir crypto-exercises
cd crypto-exercises
```

### 2. Install System Dependencies (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3 python3-pip openssl curl
```

### 3. Install Python Dependencies

```bash
pip3 install cryptography pyopenssl requests pyjwt certifi
```

### 4. Verify Installation

```bash
python3 -c "import cryptography; print('✓ Cryptography OK')"
python3 -c "import jwt; print('✓ PyJWT OK')"
openssl version
```

---

## Exercises Overview


| Exercise | File                                           | Topic                      | Difficulty |
| -------- | ---------------------------------------------- | -------------------------- | ---------- |
| 1        | `[exercise1_tls.py](exercise1_tls.py)`         | TLS Certificate Validation | ⭐⭐         |
| 2        | `[exercise2_webhook.py](exercise2_webhook.py)` | HMAC-SHA256 Signatures     | ⭐⭐         |
| 3        | `[exercise3_rsa.py](exercise3_rsa.py)`         | RSA Digital Signatures     | ⭐⭐⭐        |
| 4        | `[exercise4_tokens.py](exercise4_tokens.py)`   | JWT Refresh Token Rotation | ⭐⭐⭐⭐       |


---

## Exercise 1: TLS Certificate Inspection

**File**: `[exercise1_tls.py](exercise1_tls.py)`

### Features

- Fetch TLS certificates from any HTTPS server.
- Parse certificate details (subject, issuer, validity).
- Extract **Subject Alternative Names (SANs)**.
- Validate certificate chains using OpenSSL.
- Check certificate expiration.

### Usage

```bash
# Run the Python script
python3 exercise1_tls.py

# Or use OpenSSL commands directly
echo | openssl s_client -connect github.com:443 -showcerts
echo | openssl s_client -connect google.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Sample Output

```
============================================================
Certificate Inspection: github.com
============================================================

Subject: github.com
Issuer: DigiCert SHA2 High Assurance Server CA

Valid From: 2024-01-01 00:00:00
Valid To: 2025-01-01 23:59:59
Currently Valid: True

Subject Alternative Names (SANs):
  - github.com
  - www.github.com

Serial Number: 0x123456789abcdef
Signature Algorithm: sha256WithRSAEncryption
```

### Key Learning Points

- Understanding **X.509 certificates**.
- Certificate chain of trust.
- **SAN** and wildcard certificates.
- Certificate expiration monitoring.

---

## Exercise 2: HMAC-SHA256 Webhook Signatures

**File**: `[exercise2_webhook.py](exercise2_webhook.py)`

> **⚠️ IMPORTANT**: **Do NOT name this file `hmac.py**` (conflicts with Python's standard library).  
> Use `webhook_signer.py` or `exercise2_webhook.py` instead.

### Features

- HMAC-SHA256 signature generation.
- Timing-safe signature comparison (prevents timing attacks).
- Timestamp-based replay attack prevention.
- Stripe-style signature format support.
- GitHub webhook simulation.

### Usage

```bash
python3 webhook_signer.py
# OR
python3 exercise2_webhook.py
```

### Sample Code

```python
from webhook_signer import WebhookSigner

signer = WebhookSigner("your-webhook-secret")
payload = {"event": "push", "repository": "user/repo"}
signature = signer.sign_payload(payload)
is_valid = signer.verify_signature(payload, signature)
```

### Sample Output

```
Payload: {
  "event": "push",
  "repository": "user/repo",
  "commits": ["abc123", "def456"],
  "ref": "refs/heads/main"
}
Signature: a7b3c9e2f1d4...
Verification: ✓ PASSED
Tampered verification: ✗ FAILED

Stripe Header: t=1705315200,v1=abc123...
Stripe verification: ✓ PASSED
```

### Key Learning Points

- **HMAC vs. regular hashing**.
- Timing attack vulnerabilities and prevention.
- Replay attack mitigation.
- Webhook security best practices.

---

## Exercise 3: RSA Digital Signatures

**File**: `[exercise3_rsa.py](exercise3_rsa.py)`

### Features

- RSA-2048 key pair generation.
- PEM format key export.
- **RSASSA-PSS** signature scheme.
- JSON payload signing.
- Signature verification with tamper detection.
- OpenSSL command-line alternatives.

### Usage

```bash
python3 exercise3_rsa.py
```

### Sample Output

```
============================================================
RSA KEYS (PEM format)
============================================================
Private Key (keep secret!):
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKg...
-----END PRIVATE KEY-----

Public Key:
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
-----END PUBLIC KEY-----

Payload: {
  "user_id": "12345",
  "action": "transfer",
  "amount": 1000
}
Signature (base64): abc123def456...

Verification: ✓ PASSED
Tampered verification: ✗ FAILED
```

### OpenSSL Alternative Commands

```bash
# Generate key pair
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

# Sign a file
echo '{"message":"hello"}' > payload.json
openssl dgst -sha256 -sign private.pem -out signature.bin payload.json

# Verify signature
openssl dgst -sha256 -verify public.pem -signature signature.bin payload.json
```

### Key Learning Points

- Asymmetric cryptography basics.
- Digital signatures for **non-repudiation**.
- PEM encoding format.
- **PSS padding scheme**.

---

## Exercise 4: Refresh Token Rotation System

**File**: `[exercise4_tokens.py](exercise4_tokens.py)`

### Features

- Short-lived access tokens (1-15 minutes).
- Long-lived refresh tokens with rotation.
- Token reuse attack detection.
- Token family tracking.
- Automatic revocation on reuse.
- Timing-safe operations.

### Usage

```bash
python3 exercise4_tokens.py
```

### Sample Output

```
============================================================
REFRESH TOKEN ROTATION SYSTEM DEMO
============================================================

1. USER LOGIN
Access Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Refresh Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Expires in: 60 seconds

2. ACCESS RESOURCE
Access token valid: True
User: user_12345, Role: user

3. REFRESH TOKEN
✓ Token rotation successful. Old token invalidated.
New access token issued: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

4. REUSE ATTEMPT (Security test)
REUSE DETECTED! Token already used or invalid
⚠️ SECURITY ALERT: Refresh token reuse detected!
Reuse attempt result: BLOCKED

5. VERIFY NEW TOKENS
New access token valid: True
```

### Key Learning Points

- JWT structure and claims.
- Token rotation strategy.
- Replay attack detection.
- Stateless vs. stateful token validation.

---

## Best Practices Summary

### Password Hashing

```python
from passlib.hash import bcrypt, argon2

# BCrypt (good for most use cases)
hash = bcrypt.hash("password123")
bcrypt.verify("password123", hash)

# Argon2 (best - memory-hard, use for high-security)
hash = argon2.using(rounds=4, memory_cost=65536).hash("password123")
```

### JWT Best Practices

- **Always use ES256** over HS256/RS256 (smaller, faster, more secure).
- Keep secrets in **environment variables**, never in code.
- Set short expiration (15 min max for access tokens).
- Don’t store sensitive data in JWT payload.
- Validate algorithm to prevent `alg: none` attacks.
- Implement **refresh token rotation**.

### TLS Best Practices

- Use **TLS 1.3** or 1.2 minimum.
- Disable weak ciphers (RC4, 3DES, MD5).
- Enable **HSTS** (`Strict-Transport-Security`).
- Pin certificates for critical services.
- Monitor certificate expiry.

### Timing Attack Prevention

```python
import hmac

# ✓ ALWAYS use timing-safe comparison for secrets
hmac.compare_digest(secret1, secret2)

# ✗ NEVER do this - vulnerable to timing attacks
secret1 == secret2
```

---

## Common Issues & Solutions


| Issue                                                  | Solution                                                                                  |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'jose'`          | `pip3 install python-jose[cryptography]` or `pip3 install pyjwt`                          |
| `AttributeError: module 'hmac' has no attribute 'new'` | Rename your file: `mv hmac.py webhook_signer.py`                                          |
| SSL Certificate Verification Failed                    | Update CA certificates: `sudo apt install ca-certificates && sudo update-ca-certificates` |
| JWT Expired Signature Error                            | Refresh token: `tokens = system.refresh_access_token(refresh_token)`                      |
| Permission Denied on Port 443                          | Use a higher port or `sudo` (not recommended for production)                              |


---

## Project Structure

```
crypto-exercises/
├── README.md                    # This file
├── exercise1_tls.py            # TLS certificate inspection
├── exercise2_webhook.py        # HMAC webhook signatures
├── exercise3_rsa.py            # RSA digital signatures
├── exercise4_tokens.py         # JWT refresh token rotation
├── requirements.txt            # Python dependencies
├── private.pem                 # Generated RSA private key (git-ignore!)
├── public.pem                  # Generated RSA public key
└── payload.json                # Test payloads
```

---

## requirements.txt

```txt
cryptography>=41.0.0
pyopenssl>=23.0.0
requests>=2.31.0
pyjwt>=2.8.0
certifi>=2023.0.0
passlib>=1.7.4
```

Install all dependencies at once:

```bash
pip3 install -r requirements.txt
```

---

## Testing & Validation

### Run All Exercises

```bash
for exercise in exercise*.py; do
    echo "Running $exercise..."
    python3 "$exercise"
    echo "---"
done
```

### Manual Testing Commands

```bash
# Test TLS
openssl s_client -connect example.com:443 -tlsextdebug

# Test HMAC
echo -n "test" | openssl dgst -sha256 -hmac "secret"

# Test RSA
openssl genrsa -out test.key 2048
openssl rsa -in test.key -pubout -out test.pub

# Test JWT (using jq for pretty output)
echo "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.signature" | jwt decode -
```

---

## Additional Resources

### Official Documentation

- [Cryptography.io](https://cryptography.io/) - Python cryptography library
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [OpenSSL Documentation](https://www.openssl.org/docs/)
- [JWT.io](https://jwt.io/) - JWT debugger and information

### Security Standards

- [NIST Cryptographic Standards](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)

### Recommended Reading

- *Serious Cryptography* by Jean-Philippe Aumasson
- *Understanding Cryptography* by Christof Paar
- *The TLS Protocol* by IETF RFC 8446

### Online Tools

> **⚠️ Use for learning only. Never for real secrets!**

- [SSL Labs SSL Test](https://www.ssllabs.com/ssltest/)
- [JWT Debugger](https://jwt.io/#debugger-io)
- [Cryptii](https://cryptii.com/) - Online crypto playground

---

## License

These exercises are for **educational purposes**. Feel free to use and modify for learning cryptography concepts.

---

## Contributing

Found a bug or have an improvement? Ensure:

1. All exercises work on Linux.
2. Code follows **security best practices**.
3. No hardcoded secrets.
4. Documentation is updated.

---

## Support

If you encounter issues:

1. Check the [Common Issues & Solutions](#common-issues--solutions) section.
2. Verify all prerequisites are installed.
3. Ensure file names don’t conflict with Python modules.
4. Check Python version (`python3 --version`).

---

**Happy Cryptography Learning!** 🔐

> *Remember: Never use custom cryptography in production. Always rely on well-audited libraries and standards.*