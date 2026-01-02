# 🚀 Deploy su Northflk - Docker Compose

Guida completa per il deploy su Northflk con Docker Compose.

## 📋 Prerequisiti

- Accesso SSH a Northflk
- Docker installato su Northflk
- Docker Compose installato su Northflk

## 🔧 Step 1: Prepara Northflk

### Connettiti a Northflk
```bash
ssh user@northflk-server
```

### Verifica Docker
```bash
docker --version
docker-compose --version
```

Se non installati, installa:
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 📁 Step 2: Clona Repository

```bash
# Clona il progetto
git clone <your-repo-url> dealbot
cd dealbot

# Oppure upload via SFTP
# scp -r dealbot-northflk/ user@northflk-server:/home/user/
```

## ⚙️ Step 3: Configura .env

```bash
# Copia template
cp .env.example .env

# Modifica con i tuoi dati
nano .env
```

Inserisci:
```bash
# Bot Coordinatore (crea con @BotFather se non hai)
BOT_TOKEN=your_coordinator_bot_token

# Worker UK (già configurato)
WORKER_BOT_TOKEN=7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w
SOURCE_CHANNEL_ID=-1001303541715
PUBLISH_CHANNEL_ID=-1001232723285

# Canale destinazione
UK_CHANNEL=@DealScoutUKBot
UK_CHANNEL_ID=-1001232723285

# Configurazione
MIN_DISCOUNT_PERCENT=10
LOG_LEVEL=INFO
```

## 🐳 Step 4: Build Immagini

```bash
# Build coordinatore e worker UK
docker-compose build

# Verifica immagini
docker images | grep dealbot
```

## 🚀 Step 5: Avvia Servizi

```bash
# Avvia in background
docker-compose up -d

# Verifica container in esecuzione
docker-compose ps
```

Dovresti vedere:
```
NAME          STATUS
coordinator   Up 2 seconds
worker-uk     Up 2 seconds
```

## 🧪 Step 6: Verifica

### Logs Coordinatore
```bash
docker-compose logs coordinator -f
```

Dovresti vedere:
```
🤖 Avvio Deal Coordinator
Bot connesso: @your_coordinator_bot
📅 Scheduler avviato - processing ogni 6 ore
```

### Logs Worker UK
```bash
docker-compose logs worker-uk -f
```

Dovresti vedere:
```
🤖 Worker UK inizializzato
📺 Canale sorgente: -1001303541715
📤 Canale pubblicazione: -1001232723285
✅ Bot connesso: @dealscoutuk_bot
🌐 Server HTTP su 0.0.0.0:8001
```

### Test Health Check
```bash
curl http://localhost:8001/health | jq
```

Risposta attesa:
```json
{
  "status": "healthy",
  "worker": "DealScout UK",
  "country": "UK",
  "source_channel": -1001303541715,
  "publish_channel": -1001232723285,
  "timestamp": "2024-01-01T12:00:00"
}
```

### Test Scrape
```bash
curl http://localhost:8001/scrape | jq
```

## 📊 Monitoraggio

### Logs in Tempo Reale
```bash
# Coordinatore
docker-compose logs coordinator -f

# Worker UK
docker-compose logs worker-uk -f

# Tutti
docker-compose logs -f
```

### Status Servizi
```bash
docker-compose ps
```

### Statistiche Container
```bash
docker stats
```

## 🛑 Gestione Servizi

### Stop
```bash
docker-compose stop
```

### Restart
```bash
docker-compose restart
```

### Restart Singolo Servizio
```bash
docker-compose restart coordinator
docker-compose restart worker-uk
```

### Stop e Rimuovi
```bash
docker-compose down
```

### Stop e Rimuovi Volumi
```bash
docker-compose down -v
```

## 🔄 Update Codice

Se aggiorni il codice:

```bash
# Pull ultimi cambiamenti
git pull

# Rebuild immagini
docker-compose build

# Restart servizi
docker-compose up -d
```

## 📈 Prossimi Passi

### Aggiungere Worker IT
1. Crea `workers/it/` copiando `workers/uk/`
2. Personalizza `workers/it/config.py`
3. Aggiungi a `docker-compose.yml`:
```yaml
worker-it:
  build:
    context: .
    dockerfile: workers/it/Dockerfile
  environment:
    - WORKER_BOT_TOKEN=${WORKER_BOT_TOKEN_IT}
    - SOURCE_CHANNEL_ID=${SOURCE_CHANNEL_ID_IT}
    - PUBLISH_CHANNEL_ID=${PUBLISH_CHANNEL_ID_IT}
  ports:
    - "8002:8002"
```
4. Aggiungi a `.env`:
```bash
WORKER_BOT_TOKEN_IT=your_it_token
SOURCE_CHANNEL_ID_IT=your_it_source
PUBLISH_CHANNEL_ID_IT=your_it_publish
```
5. Restart: `docker-compose up -d`

## 🆘 Troubleshooting

### Container non parte
```bash
docker-compose logs coordinator
docker-compose logs worker-uk
```

### Errore build
```bash
docker-compose build --no-cache
```

### Porta occupata
```bash
lsof -i :8001
kill -9 <PID>
```

### Errore Telegram
1. Verifica token bot
2. Verifica bot sia membro di @NicePriceDeals
3. Verifica bot sia admin di @DealScoutUKBot

### Nessun deal trovato
1. Verifica canale sorgente ha messaggi
2. Aumenta `MIN_DISCOUNT_PERCENT` in `.env`
3. Controlla logs: `docker-compose logs worker-uk -f`

## 📝 Comandi Utili

```bash
# Logs
docker-compose logs -f

# Health check
curl http://localhost:8001/health | jq

# Scrape test
curl http://localhost:8001/scrape | jq

# Stats
curl http://localhost:8001/stats | jq

# Restart
docker-compose restart

# Stop
docker-compose stop

# Start
docker-compose start

# Rebuild
docker-compose build --no-cache

# Prune (pulisci)
docker system prune -a
```

## 🎯 Checklist Deploy

- [ ] SSH accesso a Northflk
- [ ] Docker installato
- [ ] Docker Compose installato
- [ ] Repository clonato
- [ ] `.env` configurato
- [ ] Immagini buildato
- [ ] Container avviati
- [ ] Health check OK
- [ ] Logs controllati
- [ ] Scrape test OK
- [ ] Bot posta su Telegram

## ✅ Completamento

Una volta che tutto funziona:

1. Monitora logs regolarmente
2. Verifica health check periodicamente
3. Aggiungi worker per altri paesi quando pronto
4. Configura backup e monitoring

## 📞 Supporto

Per problemi:
1. Controlla logs: `docker-compose logs -f`
2. Verifica health: `curl http://localhost:8001/health`
3. Test scrape: `curl http://localhost:8001/scrape`

---

**Deploy completato!** Il sistema è ora in esecuzione su Northflk.