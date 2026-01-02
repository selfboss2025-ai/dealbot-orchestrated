# 🚀 DEPLOY ORA SU NORTHFLK

Tutto è configurato. Procedi con questi comandi su Northflk.

## 📋 Configurazione Verificata

```
BOT COORDINATORE: 7935915288:AAHWLybhV0LDZoOZNEu9XZp57YJ7dft8ito
BOT WORKER UK: 7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w

Canale Sorgente: @NicePriceDeals (ID: -1001303541715)
Canale Destinazione: @DealScoutUKBot (ID: -1001232723285)

Affiliate Tag: ukbestdeal02-21
```

## 🚀 Comandi per Northflk

### 1. Connettiti a Northflk
```bash
ssh user@northflk-server
cd dealbot-orchestrated
```

### 2. Build Immagini Docker
```bash
docker-compose build
```

Dovresti vedere:
```
Building coordinator
Building worker-uk
Successfully tagged dealbot-orchestrated_coordinator:latest
Successfully tagged dealbot-orchestrated_worker-uk:latest
```

### 3. Avvia Servizi
```bash
docker-compose up -d
```

Dovresti vedere:
```
Creating network "dealbot-orchestrated_dealbot-network" with driver "bridge"
Creating worker-uk ... done
Creating coordinator ... done
```

### 4. Verifica Container
```bash
docker-compose ps
```

Dovresti vedere:
```
NAME          IMAGE                                    STATUS
coordinator   dealbot-orchestrated_coordinator:latest  Up 2 seconds
worker-uk     dealbot-orchestrated_worker-uk:latest    Up 2 seconds
```

## 🧪 Test

### Health Check Worker UK
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

## 📊 Monitoraggio

### Logs in Tempo Reale
```bash
docker-compose logs -f
```

### Scrape Test
```bash
curl http://localhost:8001/scrape | jq
```

### Stats
```bash
curl http://localhost:8001/stats | jq
```

## 🛑 Gestione

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

### Logs Specifici
```bash
docker-compose logs coordinator -f
docker-compose logs worker-uk -f
```

## ✅ Checklist

- [ ] SSH a Northflk
- [ ] `docker-compose build` completato
- [ ] `docker-compose up -d` completato
- [ ] `docker-compose ps` mostra 2 container running
- [ ] `curl http://localhost:8001/health` → 200 OK
- [ ] Logs coordinatore OK
- [ ] Logs worker UK OK
- [ ] Bot posta su @DealScoutUKBot

## 🎯 Cosa Succede Ora

1. **Coordinatore** è in esecuzione su Northflk
2. **Worker UK** è in esecuzione su Northflk (porta 8001)
3. Ogni 6 ore il coordinatore:
   - Chiama `/scrape` del worker UK
   - Riceve lista di deals
   - Genera link affiliati
   - Posta su @DealScoutUKBot

## 📈 Prossimi Passi

1. Monitora logs per 24 ore
2. Verifica che deals vengono postati su @DealScoutUKBot
3. Quando pronto, aggiungi worker IT, FR, DE

## 💡 Comandi Utili

```bash
# Logs
docker-compose logs -f

# Health
curl http://localhost:8001/health | jq

# Scrape
curl http://localhost:8001/scrape | jq

# Restart
docker-compose restart

# Stop
docker-compose stop

# Status
docker-compose ps
```

## 🆘 Se Hai Problemi

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

### Errore Telegram
1. Verifica token bot
2. Verifica bot sia membro di @NicePriceDeals
3. Verifica bot sia admin di @DealScoutUKBot

---

**PRONTO! Procedi con i comandi sopra su Northflk.** 🚀