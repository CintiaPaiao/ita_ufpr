from src.security.auth import hash_password
def test_hash():assert hash_password('abc')!='abc'
