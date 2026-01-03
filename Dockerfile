FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice
COPY coordinator/ ./coordinator/
COPY workers/ ./workers/

# Copia la sessione Telethon
COPY workers/uk/session_uk.session /tmp/session_uk.session

# Esponi porte
EXPOSE 8000 8001

# Comando di avvio - avvia entrambi
CMD ["bash", "-c", "python -u workers/uk/worker_uk_v2.py & sleep 5 && python -u coordinator/main.py"]
