# ⚡ Northflk Quick Start

Deploy in 10 minuti.

## 🚀 Comandi Essenziali

### 1. Connettiti a Northflk
```bash
ssh user@northflk-server
cd dealbot
```

### 2. Configura .env
```bash
cp .env.example .env
nano .env

# Inserisci:
BOT_TOKEN=your_coordinator_token
WORKER_BOT_TOKEN=7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w
SOURCE_CHANNEL_ID=-1001303541715
PUBLISH_CHANNEL_ID=-1001232723285
UK_CHANNEL=@DealScoutUKBot
UK_CHANNEL_ID=-1001232723285
```

### 3. Build & Run
```bash
docker-compose build
docker-compose up -d
```

### 4. Verifica
```bash
docker-compose ps
docker-compose logs -f
curl http://localhost:8001/health | jq
```

## 📊 Monitoraggio

```bash
# Logs in tempo reale
docker-compose logs -f

# Health check
curl http://localhost:8001/health | jq

# Scrape test
curl http://localhost:8001/scrape | jq

# Stats
curl http://localhost:8001/stats | jq
```

## 🛑 Gestione

```bash
# Stop
docker-compose stop

# Restart
docker-compose restart

# Logs coordinatore
docker-compose logs coordinator -f

# Logs worker UK
docker-compose logs worker-uk -f
```

## 🆘 Problemi

### Container non parte
```bash
docker-compose logs
```

### Errore build
```bash
docker-compose build --no-cache
```

### Restart completo
```bash
docker-compose down
docker-compose up -d
```

## ✅ Checklist

- [ ] SSH a Northflk
- [ ] `.env` configurato
- [ ] `docker-compose build`
- [ ] `docker-compose up -d`
- [ ] `docker-compose ps` → 2 container running
- [ ] `curl http://localhost:8001/health` → 200 OK
- [ ] Logs OK: `docker-compose logs -f`

---

**Fatto!** Sistema in esecuzione su Northflk.