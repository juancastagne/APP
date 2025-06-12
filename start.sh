#!/bin/bash

echo "=== Start Script ==="
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

echo "Searching for main.py..."
find . -name "main.py"

echo "Python path:"
python -c "import sys; print('\n'.join(sys.path))"

echo "Running main.py..."
if [ -f "src/main.py" ]; then
    echo "Found main.py in src directory"
    python src/main.py
elif [ -f "APP/src/main.py" ]; then
    echo "Found main.py in APP/src directory"
    python APP/src/main.py
else
    echo "main.py not found in expected locations"
    exit 1
fi 