#!/bin/bash
# This script sets up env_sc_acapulco for Python 3.11
if [ -d "env_sc_acapulco" ]; then
    echo "Removing existing env_sc_acapulco..."
    rm -rf env_sc_acapulco
fi

python3.11 -m venv env_sc_acapulco
source env_sc_acapulco/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python -m ipykernel install --user --name env_sc_acapulco --display-name "Python (sc_acapulco)"

