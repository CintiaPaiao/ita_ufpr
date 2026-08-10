import sys
from src.security.passwords import hash_password

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python scripts/hash_password.py "SUA_SENHA"')
    print(hash_password(sys.argv[1]))
