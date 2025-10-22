from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# OWASP-friendly starting params (tune later after perf testing)
ph = PasswordHasher(
    time_cost=3,         # iterations
    memory_cost=131072,  # KiB (128 MiB)
    parallelism=2,
    hash_len=32,
    salt_len=16,
)

def hash_password(password: str) -> str:
    # returns a full hash string: $argon2id$v=19$m=...,t=...,p=...$<salt>$<hash>
    return ph.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        ph.verify(hashed, plain)
        return True
    except VerifyMismatchError:
        return False

def needs_rehash(hashed: str) -> bool:
    # if you later bump time_cost/memory_cost, this will tell you to re-hash
    return ph.check_needs_rehash(hashed)
