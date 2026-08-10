from src.ui.common import page_setup,model_table
from src.models.models import ProtectionFactor
page_setup('Proteção e Prioridades PNAES', allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA'));model_table(ProtectionFactor)
