from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
"""Importador controlado do legado ITA 2025.
Não converte score ITA em IAL, CRPS ou decisão. Ajuste o mapeamento ao arquivo legado real.
"""
import pandas as pd
def read_legacy(path):return pd.read_excel(path)
if __name__=='__main__':print(__doc__)
