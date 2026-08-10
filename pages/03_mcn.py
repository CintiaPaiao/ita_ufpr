from src.ui.common import page_setup,model_table
from src.models.models import MCNResult
page_setup('MCN – Matriz de Critérios Normativos', allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA', 'AUDITOR'));model_table(MCNResult)
