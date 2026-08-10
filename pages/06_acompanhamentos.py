from src.ui.common import page_setup,model_table
from src.models.models import Accompaniment
page_setup('Acompanhamentos Institucionais', allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA'));model_table(Accompaniment)
