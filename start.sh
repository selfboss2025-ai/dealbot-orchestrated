#!/bin/bash

# Avvia worker UK in background
python workers/uk/worker_uk.py &

# Avvia coordinatore in foreground
python coordinator/main.py
