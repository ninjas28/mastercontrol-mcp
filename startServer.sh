#!/bin/bash

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Pass all arguments to the python script
python server.py "$@"
