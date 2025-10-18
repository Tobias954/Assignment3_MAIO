import os
import sys

# Lägg till projektroten i sys.path så "import src" fungerar i pytest lokalt och i CI
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
