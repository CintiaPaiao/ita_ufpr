from src.security.passwords import hash_password, verify_password

def test_pbkdf2_hash_and_verify():
    encoded=hash_password('senha-forte-123')
    assert encoded.startswith('pbkdf2_sha256$')
    assert 'senha-forte-123' not in encoded
    assert verify_password('senha-forte-123',encoded)
    assert not verify_password('errada',encoded)
