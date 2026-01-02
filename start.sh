#!/bin/bash

# Avvia worker UK in background
python workers/uk/worker_uk.py &
WORKER_PID=$!

# Aspetta che il worker sia pronto
sleep 5

# Avvia coordinatore in foreground
python coordinator/main.py
