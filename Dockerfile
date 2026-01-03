FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice
COPY coordinator/ ./coordinator/
COPY workers/ ./workers/
COPY start.sh ./

# Copia la sessione Telethon
COPY workers/uk/session_uk.session /tmp/session_uk.session

# Rendi eseguibile lo script
RUN chmod +x start.sh

# Esponi porte
EXPOSE 8000 8001

# Comando di avvio
CMD ["./start.sh"]
