# 🚀 Setup Worker UK - Deal Scout

Guida completa per il setup e deploy del primo worker UK.

## 📋 Dati Configurati

```
Bot ID: 7768046661
Bot Username: @dealscoutuk_bot
Bot Token: 7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w

Canale Sorgente: @NicePriceDeals (ID: -1001303541715)
Canale Pubblicazione: @DealScoutUKBot (ID: -1001232723285)

Affiliate Tag: ukbestdeal02-21
Dominio: amazon.co.uk
```

## 🔧 Configurazione Veloce

### 1. Verifica Prerequisiti

```bash
# Verifica Python
python3 --version  # Deve essere 3.9+

# Verifica Docker (opzionale ma consigliato)
docker --version

# Verifica pip
pip3 --version
```

### 2. Installa Dipendenze

```bash
# Installa dipendenze Python
pip install -r requirements.txt

# Verifica installazione
python -c "import telegram; print('✅ python-telegram-bot OK')"
```

### 3. Avvia Worker UK (Locale)

```bash
# Naviga nella directory worker UK
cd workers/uk

# Avvia il worker
python worker_uk.py
```

Dovresti vedere:
```
🤖 Worker UK inizializzato
📺 Canale sorgente: -1001303541715
📤 Canale pubblicazione: -1001232723285
✅ Bot connesso: @dealscoutuk_bot
🌐 Server HTTP su 0.0.0.0:8001
```

### 4. Test Worker (in un altro terminale)

```bash
# Health check
curl http://localhost:8001/health

# Scrape test
curl http://localhost:8001/scrape

# Stats
curl http://localhost:8001/stats
```

## 🐳 Deploy con Docker

### Build Immagine

```bash
# Dalla root del progetto
docker build -f workers/uk/Dockerfile -t dealscout-uk:latest .
```

### Run Container

```bash
docker run -d \
  --name worker-uk \
  -p 8001:8001 \
  --env-file workers/uk/.env \
  --restart unless-stopped \
  dealscout-uk:latest
```

### Verifica Container

```bash
# Logs
docker logs worker-uk -f

# Health check
curl http://localhost:8001/health

# Stop
docker stop worker-uk

# Restart
docker restart worker-uk
```

## 🚀 Deploy su VPS/Northflk

### 1. Prepara Server

```bash
# SSH nel server
ssh user@your-vps-ip

# Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Aggiungi utente a docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clona Repository

```bash
# Clona il progetto
git clone <your-repo-url>
cd dealbot-orchestrated

# Configura .env
cp workers/uk/.env workers/uk/.env.local
nano workers/uk/.env.local  # Modifica se necessario
```

### 3. Deploy Worker

```bash
# Usa script di deploy
chmod +x scripts/deploy-worker-uk.sh
./scripts/deploy-worker-uk.sh
```

Oppure manualmente:

```bash
# Build
docker build -f workers/uk/Dockerfile -t dealscout-uk:latest .

# Run
docker run -d \
  --name worker-uk \
  -p 8001:8001 \
  --env-file workers/uk/.env \
  --restart unless-stopped \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  dealscout-uk:latest
```

### 4. Verifica Deploy

```bash
# Logs
docker logs worker-uk -f

# Health check
curl http://localhost:8001/health

# Test scrape
curl http://localhost:8001/scrape | jq
```

## 🔌 Integrazione Coordinatore

### 1. Configura Coordinatore

Modifica `.env` del coordinatore:

```bash
# URL del worker UK
WORKER_UK_URL=http://your-vps-ip:8001

# Canale destinazione
UK_CHANNEL=@DealScoutUKBot
UK_CHANNEL_ID=-1001232723285
```

### 2. Avvia Coordinatore

```bash
# Locale (test)
python coordinator/main.py

# Docker
docker build -f coordinator/Dockerfile -t dealbot-coordinator:latest .
docker run -d \
  --name coordinator \
  --env-file .env \
  --restart unless-stopped \
  dealbot-coordinator:latest
```

## 📊 Monitoraggio

### Logs in Tempo Reale

```bash
# Worker UK
docker logs worker-uk -f

# Coordinatore
docker logs coordinator -f
```

### Health Check

```bash
# Worker UK
curl http://localhost:8001/health | jq

# Coordinatore (se espone endpoint)
curl http://localhost:8000/health | jq
```

### Statistiche

```bash
# Worker UK
curl http://localhost:8001/stats | jq
```

## 🧪 Test Completo

### Script di Test

```bash
# Rendi eseguibile
chmod +x scripts/test-worker-uk.sh

# Esegui test
./scripts/test-worker-uk.sh

# Test con URL remoto
./scripts/test-worker-uk.sh http://your-vps-ip:8001
```

### Test Manuale

```bash
# 1. Health check
curl http://localhost:8001/health

# 2. Scrape
curl http://localhost:8001/scrape | jq

# 3. Stats
curl http://localhost:8001/stats | jq

# 4. Verifica bot Telegram
curl https://api.telegram.org/bot7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w/getMe | jq
```

## 🔧 Troubleshooting

### Worker Non Risponde

```bash
# Verifica se container è in esecuzione
docker ps | grep worker-uk

# Controlla logs
docker logs worker-uk

# Restart
docker restart worker-uk

# Verifica porta
lsof -i :8001
```

### Errore Connessione Telegram

```bash
# Verifica token
curl https://api.telegram.org/bot7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w/getMe

# Verifica permessi canali
# - Bot deve essere membro di @NicePriceDeals
# - Bot deve essere admin di @DealScoutUKBot
```

### Nessun Deal Trovato

1. Verifica che @NicePriceDeals abbia messaggi con link Amazon
2. Controlla i pattern di parsing nei logs
3. Aumenta `SCRAPE_LOOKBACK_HOURS` in `.env`
4. Verifica che il bot sia membro del canale

### Porta Già in Uso

```bash
# Cambia porta in workers/uk/.env
WORKER_PORT=8002

# O libera porta
lsof -i :8001
kill -9 <PID>
```

## 📈 Prossimi Passi

1. ✅ Worker UK configurato e testato
2. ⏳ Creare worker per altri paesi (IT, FR, DE)
3. ⏳ Deploy coordinatore su Northflk
4. ⏳ Configurare monitoring e alerting
5. ⏳ Aggiungere database per storico deals

## 📚 Risorse

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot Docs](https://python-telegram-bot.readthedocs.io/)
- [Amazon ASIN Format](https://docs.aws.amazon.com/AWSECommerceService/latest/DeveloperGuide/ASIN.html)
- [Docker Docs](https://docs.docker.com/)

## 💡 Tips

1. **Backup Token**: Salva il token bot in un posto sicuro
2. **Monitoring**: Usa `docker logs -f` per monitorare in tempo reale
3. **Scaling**: Quando aggiungi worker, usa porte diverse (8001, 8002, 8003)
4. **Rate Limiting**: Modifica `POST_DELAY_SECONDS` se necessario
5. **Logging**: Aumenta `LOG_LEVEL=DEBUG` per troubleshooting

## 🆘 Supporto

Se hai problemi:

1. Controlla i logs: `docker logs worker-uk -f`
2. Verifica health: `curl http://localhost:8001/health`
3. Test scrape: `curl http://localhost:8001/scrape`
4. Verifica bot: `curl https://api.telegram.org/bot<TOKEN>/getMe`