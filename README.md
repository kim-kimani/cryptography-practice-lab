# Cryptography Practice Lab

A hands-on repository for practicing essential cryptography concepts, including **password hashing**, **RSA key generation**, **webhook signature verification**, and **refresh token rotation**.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Exercises Overview](#exercises-overview)
  - [Password Hashing](#password-hashing)
  - [RSA Key Generation](#rsa-key-generation)
  - [Webhook Signer](#webhook-signer)
  - [Refresh Token Rotation](#refresh-token-rotation)
- [Best Practices](#best-practices)
- [Common Issues & Solutions](#common-issues--solutions)
- [Additional Resources](#additional-resources)
- [License](#license)

---

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu/Debian recommended)
- **Python**: 3.8 or higher
- **Tools**: OpenSSL command-line tools
- **Internet**: Required for some exercises

### Required Python Packages

Install the dependencies listed in `[requirements.txt](requirements.txt)`:

```bash
pip3 install -r requirements.txt
```

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd cryptography-practice-lab
```

### 2. Install System Dependencies (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3 python3-pip openssl curl
```

### 3. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Verify Installation

```bash
python3 -c "import cryptography; print('✓ Cryptography OK')"
python3 -c "import jwt; print('✓ PyJWT OK')"
openssl version
```

---

## Project Structure

```
cryptography-practice-lab/
├── README.md                    # Project documentation
├── .gitignore                  # Git ignore rules
├── passhashing.py              # Password hashing exercise
├── rsakeygen.py                # RSA key generation exercise
├── webhook_signer.py           # HMAC webhook signature exercise
├── refreshtokenrotation.py     # JWT refresh token rotation exercise
└── requirements.txt            # Python dependencies
```

---

## Exercises Overview


| File                                                 | Topic                       | Description                                                         |
| ---------------------------------------------------- | --------------------------- | ------------------------------------------------------------------- |
| `[passhashing.py](passhashing.py)`                   | **Password Hashing**        | Securely hash and verify passwords using **bcrypt** and **Argon2**. |
| `[rsakeygen.py](rsakeygen.py)`                       | **RSA Key Generation**      | Generate RSA key pairs and sign/verify data.                        |
| `[webhook_signer.py](webhook_signer.py)`             | **HMAC Webhook Signatures** | Implement HMAC-SHA256 for webhook signature verification.           |
| `[refreshtokenrotation.py](refreshtokenrotation.py)` | **Refresh Token Rotation**  | Secure JWT-based authentication with token rotation.                |


---

## Password Hashing

**File**: `[passhashing.py](passhashing.py)`

### Features

- Hash passwords using **bcrypt** and **Argon2**.
- Verify hashed passwords securely.
- Timing-safe comparison.

### Usage

```bash
python3 passhashing.py
```

### Sample Code

```python
from passlib.hash import bcrypt, argon2

# BCrypt
hash = bcrypt.hash("password123")
bcrypt.verify("password123", hash)  # Returns True/False

# Argon2
hash = argon2.using(rounds=4, memory_cost=65536).hash("password123")
argon2.verify("password123", hash)  # Returns True/False
```

### Key Learning Points

- **Never store plaintext passwords**.
- Use **memory-hard** algorithms like Argon2 for high-security applications.
- Always use **timing-safe comparison** to prevent attacks.

---

## RSA Key Generation

**File**: `[rsakeygen.py](rsakeygen.py)`

### Features

- Generate **RSA-2048** key pairs.
- Export keys in **PEM format**.
- Sign and verify data using **RSASSA-PSS**.

### Usage

```bash
python3 rsakeygen.py
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

Payload: {"message": "Hello, RSA!"}
Signature (base64): abc123def456...
Verification: ✓ PASSED
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

- **Asymmetric cryptography** basics.
- **Digital signatures** for non-repudiation.
- **PEM encoding** format.

---

## Webhook Signer

**File**: `[webhook_signer.py](webhook_signer.py)`

### Features

- Generate and verify **HMAC-SHA256** signatures.
- Timing-safe comparison to prevent **timing attacks**.
- Support for **Stripe-style** and **GitHub-style** webhook signatures.

### Usage

```bash
python3 webhook_signer.py
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
Payload: {"event": "push", "repository": "user/repo"}
Signature: a7b3c9e2f1d4...
Verification: ✓ PASSED
Tampered verification: ✗ FAILED
```

### Key Learning Points

- **HMAC vs. regular hashing**.
- **Timing attack** prevention.
- **Replay attack** mitigation.

---

## Refresh Token Rotation

**File**: `[refreshtokenrotation.py](refreshtokenrotation.py)`

### Features

- **Short-lived access tokens** (1-15 minutes).
- **Long-lived refresh tokens** with rotation.
- **Token reuse attack** detection.
- **Token family tracking** for security.

### Usage

```bash
python3 refreshtokenrotation.py
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
⚠️ SECURITY ALERT: Refresh token reuse detected!
Reuse attempt result: BLOCKED
```

### Key Learning Points

- **JWT structure** and claims.
- **Token rotation** strategy.
- **Replay attack** detection.

---

## Best Practices

### Password Hashing

- Use **Argon2** for high-security applications.
- Use **bcrypt** for general-purpose hashing.
- **Never** use plaintext passwords or weak algorithms like MD5/SHA1.

### JWT Best Practices

- Use **ES256** over HS256/RS256.
- Store secrets in **environment variables**.
- Set **short expiration** (15 min max for access tokens).
- Validate the **algorithm** to prevent `alg: none` attacks.

### TLS Best Practices

- Use **TLS 1.3** or 1.2 minimum.
- Disable weak ciphers (RC4, 3DES, MD5).
- Enable **HSTS** (`Strict-Transport-Security`).
- Monitor **certificate expiry**.

### Timing Attack Prevention

```python
import hmac

# ✓ Use timing-safe comparison
hmac.compare_digest(secret1, secret2)

# ✗ Avoid direct comparison
secret1 == secret2  # Vulnerable to timing attacks
```

---

## Common Issues & Solutions


| Issue                                                  | Solution                                                                                  |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'jose'`          | Run `pip3 install python-jose[cryptography]` or `pip3 install pyjwt`                      |
| `AttributeError: module 'hmac' has no attribute 'new'` | Rename your file to avoid conflicts with Python's `hmac` module.                          |
| SSL Certificate Verification Failed                    | Update CA certificates: `sudo apt install ca-certificates && sudo update-ca-certificates` |
| JWT Expired Signature Error                            | Refresh the token using `system.refresh_access_token(refresh_token)`                      |
| Permission Denied on Port 443                          | Use a higher port or `sudo` (not recommended for production).                             |


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

### Online Tools

> **⚠️ Use for learning only. Never for real secrets!**

- [SSL Labs SSL Test](https://www.ssllabs.com/ssltest/)
- [JWT Debugger](https://jwt.io/#debugger-io)
- [Cryptii](https://cryptii.com/)

---

## License

This project is for **educational purposes**. Feel free to use and modify the code for learning cryptography concepts.

---

**Happy Cryptography Learning!** 🔐

> *Remember: Never use custom cryptography in production. Always rely on well-audited libraries and standards.*