FROM docker:latest

WORKDIR /app

# Installa docker-compose
RUN apk add --no-cache docker-compose python3 py3-pip

# Copia i file
COPY . .

# Installa dipendenze Python
RUN pip install -r requirements.txt

# Esponi porte
EXPOSE 8001

# Comando di avvio
CMD ["docker-compose", "up"]
