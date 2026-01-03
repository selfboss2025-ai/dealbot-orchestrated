FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia codice coordinatore
COPY coordinator/ ./

# Esponi porta (opzionale per monitoring)
EXPOSE 8000

# Comando di avvio
CMD ["python", "-u", "main.py"]