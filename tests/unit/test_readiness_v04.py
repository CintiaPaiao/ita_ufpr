from src.services.readiness_service import readiness_score

def test_readiness_score_blocks_critical():
    checks=[{'ok':True,'level':'CRITICO'},{'ok':False,'level':'ALTO'}]
    score,ready=readiness_score(checks)
    assert ready is True
    checks.append({'ok':False,'level':'CRITICO'})
    _,ready=readiness_score(checks)
    assert ready is False
