from passlib.hash import bcrypt, argon2

# BCrypt (good)
hash = bcrypt.hash("password123")
bcrypt.verify("password123", hash)

# Argon2 (better - memory-hard)
hash = argon2.using(rounds=4, memory_cost=65536).hash("password123")