from src.domain.prioritization.engine import *
def test_layers():
    assert classify_layer(PriorityInput('GRR20260001',1,ial_score=70,ial_band='Prioridade acadêmica intensiva')).layer=='A';assert classify_layer(PriorityInput('GRR20260002',reassessment=True,longitudinal_worsening=True)).layer=='B';assert classify_layer(PriorityInput('GRR20260003',protective_priority=True)).layer=='D'
def test_n():assert len(prioritize([PriorityInput(f'GRR2026{i:04d}',ial_score=50,ial_band='Prioridade acadêmica elevada') for i in range(10)],3))==3
