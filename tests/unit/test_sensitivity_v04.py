from src.services.sensitivity_service import analyze

def test_sensitivity_scenarios():
    records=[{'student_id':1,'r':0.8,'f':0.6,'p':0.4},{'student_id':2,'r':0.2,'f':0.1,'p':0.9}]
    out=analyze(records)
    assert set(out)=={'50/30/20','40/35/25','30/30/40'}
    assert len(out['40/35/25']['records'])==2
