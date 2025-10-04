from joker_task.service.security import get_hash_password, verify_password


def test_get_and_verify_password():
    assert verify_password('oi', get_hash_password('oi'))
