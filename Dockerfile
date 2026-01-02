FROM python:3.11-slim

WORKDIR /app

# Copia i file
COPY . .

# Installa dipendenze Python
RUN pip install -r requirements.txt

# Rendi eseguibile lo script di avvio
RUN chmod +x start.sh

# Esponi porte
EXPOSE 8001

# Comando di avvio
CMD ["./start.sh"]

