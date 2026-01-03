#!/bin/bash

# Avvia worker in background
python -u workers/uk/worker_uk_v2.py &

# Aspetta che il worker sia pronto
echo "Aspettando che il worker sia pronto..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
        echo "✅ Worker pronto!"
        break
    fi
    echo "Tentativo $i/30..."
    sleep 1
done

# Avvia coordinator in foreground
python -u coordinator/main.py
