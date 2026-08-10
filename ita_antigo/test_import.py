import ita_calc
import sys

print("Import successful")
try:
    # Just check if function exists
    assert callable(ita_calc.calculate_ita)
    print("Function calculate_ita exists")
except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
