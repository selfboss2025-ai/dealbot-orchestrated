# ⚡ Quick Start - Worker UK

Avvia il worker UK in 5 minuti.

## 🚀 Opzione 1: Locale (Sviluppo)

```bash
# 1. Installa dipendenze
pip install -r requirements.txt

# 2. Avvia worker
cd workers/uk
python worker_uk.py

# 3. Test (in altro terminale)
curl http://localhost:8001/health
```

## 🐳 Opzione 2: Docker (Consigliato)

```bash
# 1. Build
docker build -f workers/uk/Dockerfile -t dealscout-uk:latest .

# 2. Run
docker run -d \
  --name worker-uk \
  -p 8001:8001 \
  --env-file workers/uk/.env \
  dealscout-uk:latest

# 3. Test
curl http://localhost:8001/health
docker logs worker-uk -f
```

## 🚀 Opzione 3: Script Deploy

```bash
# Rendi eseguibile
chmod +x scripts/deploy-worker-uk.sh

# Deploy
./scripts/deploy-worker-uk.sh

# Monitora
docker logs worker-uk -f
```

## 🧪 Test Rapido

```bash
# Health check
curl http://localhost:8001/health | jq

# Scrape
curl http://localhost:8001/scrape | jq

# Stats
curl http://localhost:8001/stats | jq
```

## 📊 Endpoint Disponibili

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/scrape` | GET | Scrape deals |
| `/stats` | GET | Statistiche |

## 🔧 Configurazione

File: `workers/uk/.env`

```bash
WORKER_BOT_TOKEN=7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w
WORKER_PORT=8001
SOURCE_CHANNEL_ID=-1001303541715
PUBLISH_CHANNEL_ID=-1001232723285
MIN_DISCOUNT_PERCENT=10
```

## 📋 Dati Configurati

```
Bot: @dealscoutuk_bot
Sorgente: @NicePriceDeals
Destinazione: @DealScoutUKBot
Affiliate: ukbestdeal02-21
```

## 🛑 Stop/Restart

```bash
# Stop
docker stop worker-uk

# Restart
docker restart worker-uk

# Logs
docker logs worker-uk -f

# Remove
docker rm worker-uk
```

## 🆘 Troubleshooting

### Worker non risponde
```bash
docker logs worker-uk
curl http://localhost:8001/health
docker restart worker-uk
```

### Porta già in uso
```bash
lsof -i :8001
kill -9 <PID>
```

### Nessun deal trovato
1. Verifica che bot sia membro di @NicePriceDeals
2. Controlla logs: `docker logs worker-uk -f`
3. Aumenta `SCRAPE_LOOKBACK_HOURS` in `.env`

## 📚 Documentazione Completa

- `SETUP_UK_WORKER.md` - Setup dettagliato
- `ARCHITECTURE.md` - Architettura sistema
- `workers/uk/README.md` - Docs worker UK
- `README.md` - Overview generale

## 🎯 Prossimi Passi

1. ✅ Worker UK avviato
2. ⏳ Creare worker per altri paesi
3. ⏳ Deploy coordinatore
4. ⏳ Configurare monitoring

## 💡 Comandi Utili

```bash
# Logs in tempo reale
docker logs worker-uk -f

# Health check
curl http://localhost:8001/health | jq

# Scrape test
curl http://localhost:8001/scrape | jq '.[0:2]'

# Stats
curl http://localhost:8001/stats | jq

# Verifica bot Telegram
curl https://api.telegram.org/bot7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w/getMe | jq

# Restart
docker restart worker-uk

# Stop
docker stop worker-uk

# Remove
docker rm worker-uk
```

## 🚀 Deploy su VPS

```bash
# SSH nel server
ssh user@your-vps-ip

# Clona repo
git clone <your-repo>
cd dealbot-orchestrated

# Deploy
chmod +x scripts/deploy-worker-uk.sh
./scripts/deploy-worker-uk.sh

# Monitora
docker logs worker-uk -f
```

## 📞 Supporto Rapido

| Problema | Soluzione |
|----------|-----------|
| Worker non parte | `docker logs worker-uk` |
| Porta occupata | `lsof -i :8001` |
| Nessun deal | Verifica canale sorgente |
| Errore Telegram | Verifica token bot |
| Performance lenta | Aumenta risorse container |

---

**Fatto!** Il worker UK è pronto. Procedi con gli altri paesi o il coordinatore.