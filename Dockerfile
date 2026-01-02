FROM python:3.11-slim

WORKDIR /app

# Copia i file
COPY . .

# Installa dipendenze Python
RUN pip install -r requirements.txt

# Esponi porte
EXPOSE 8001

# Comando di avvio
CMD ["python", "coordinator/main.py"]
