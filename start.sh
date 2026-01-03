#!/bin/bash

# Avvia worker UK in background
echo "🇬🇧 Avvio Worker UK..."
python -u workers/uk/worker_uk_v2.py &
WORKER_UK_PID=$!

# Avvia worker IT in background
echo "🇮🇹 Avvio Worker IT..."
python -u workers/it/worker_it.py &
WORKER_IT_PID=$!

# Aspetta che entrambi i worker siano pronti
echo "Aspettando che i worker siano pronti..."

# Aspetta Worker UK
for i in {1..30}; do
    if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
        echo "✅ Worker UK pronto!"
        break
    fi
    echo "Worker UK - Tentativo $i/30..."
    sleep 1
done

# Aspetta Worker IT
for i in {1..30}; do
    if curl -s http://127.0.0.1:8002/health > /dev/null 2>&1; then
        echo "✅ Worker IT pronto!"
        break
    fi
    echo "Worker IT - Tentativo $i/30..."
    sleep 1
done

# Avvia coordinator in foreground
echo "🚀 Avvio Coordinator..."
python -u coordinator/main.py
