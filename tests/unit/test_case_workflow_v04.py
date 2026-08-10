# Teste de contrato mínimo da máquina de estados/ações.
from src.services.workflow import can_transition

def test_workflow_core_transitions():
    assert can_transition('DADOS_VALIDADOS','MCN_IAL_CALCULADOS')
    assert not can_transition('DADOS_VALIDADOS','CRPS-3')
