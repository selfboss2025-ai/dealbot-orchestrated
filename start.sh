#!/bin/bash

# Avvia worker UK v2 in background
python workers/uk/worker_uk_v2.py &
WORKER_PID=$!

# Aspetta che il worker sia pronto
sleep 5

# Avvia coordinatore in foreground
python coordinator/main.py
