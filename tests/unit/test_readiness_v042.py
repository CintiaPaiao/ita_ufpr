from src.services.readiness_service import readiness_score


def test_critical_failure_blocks_readiness():
    checks = [
        {"ok": True, "level": "CRITICO"},
        {"ok": False, "level": "CRITICO"},
        {"ok": True, "level": "MEDIO"},
    ]
    score, ready = readiness_score(checks)
    assert score == 67
    assert ready is False


def test_noncritical_failure_does_not_block():
    checks = [
        {"ok": True, "level": "CRITICO"},
        {"ok": False, "level": "MEDIO"},
    ]
    score, ready = readiness_score(checks)
    assert score == 50
    assert ready is True
