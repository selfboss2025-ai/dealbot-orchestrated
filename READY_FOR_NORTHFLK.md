# ✅ PRONTO PER NORTHFLK

Tutto è configurato e pronto per il deploy su Northflk con Docker Compose.

## 📦 Cosa è Incluso

```
dealbot-orchestrated/
├── coordinator/              ← Bot coordinatore
├── workers/uk/              ← Worker UK
├── docker-compose.yml       ← Compose per Northflk
├── .env.example             ← Template configurazione
├── requirements.txt         ← Dipendenze Python
├── NORTHFLK_DEPLOY.md       ← Guida completa
├── NORTHFLK_QUICK.md        ← Quick start
└── [Documentazione]
```

## 🎯 3 Step per Northflk

### Step 1: Configura
```bash
cp .env.example .env
# Modifica BOT_TOKEN (coordinatore)
# Resto già configurato
```

### Step 2: Build
```bash
docker-compose build
```

### Step 3: Run
```bash
docker-compose up -d
```

## ✅ Verifica

```bash
# Vedi container
docker-compose ps

# Vedi logs
docker-compose logs -f

# Test health
curl http://localhost:8001/health | jq
```

## 📋 Dati Già Configurati

```
Bot UK: @dealscoutuk_bot
Sorgente: @NicePriceDeals
Destinazione: @DealScoutUKBot
Affiliate: ukbestdeal02-21
```

## 🚀 Cosa Succede

1. **Coordinatore** avvia su Northflk
2. **Worker UK** avvia su Northflk (porta 8001)
3. Ogni 6 ore: coordinatore chiama worker
4. Worker scrapa @NicePriceDeals
5. Coordinatore posta deals su @DealScoutUKBot

## 📚 Documentazione

- `NORTHFLK_DEPLOY.md` - Guida completa
- `NORTHFLK_QUICK.md` - Quick start
- `docker-compose.yml` - Configurazione Docker

## 🎯 Prossimi Passi

1. Upload su Northflk
2. Configura `.env` con BOT_TOKEN coordinatore
3. `docker-compose build`
4. `docker-compose up -d`
5. Monitora logs

## 💡 Comandi Utili

```bash
# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose stop

# Health
curl http://localhost:8001/health | jq

# Scrape
curl http://localhost:8001/scrape | jq
```

## ✨ Caratteristiche

✅ Coordinatore + Worker UK su Northflk
✅ Docker Compose per facile gestione
✅ Logging strutturato
✅ Health check integrato
✅ Auto-restart su crash
✅ Pronto per espansione (IT, FR, DE)

## 🎉 Pronto!

Tutto è configurato. Procedi con il deploy su Northflk seguendo `NORTHFLK_QUICK.md`.