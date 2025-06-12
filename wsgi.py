import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path de Python
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

# Importar la aplicación
from src.main import main

# Ejecutar la aplicación
if __name__ == "__main__":
    main() 