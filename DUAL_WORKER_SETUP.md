# 🌍 DUAL WORKER SETUP - UK + IT

**Data**: 3 Gennaio 2026  
**Status**: ✅ CONFIGURATO - PRONTO PER DEPLOYMENT

---

## 📋 ARCHITETTURA DUAL-WORKER

```
┌─────────────────────────────────────────────────────┐
│  Container Unificato: dealscoutorch                 │
│                                                      │
│  ┌────────────────────┐    ┌────────────────────┐  │
│  │  Worker UK         │    │  Worker IT         │  │
│  │  Port: 8001        │    │  Port: 8002        │  │
│  │  @NicePriceDeals   │    │  @salvatore_       │  │
│  │  → @DealScoutUKBot │    │    aranzulla_      │  │
│  │                    │    │    offerte         │  │
│  │  Tag: ukbestdeal   │    │  → @AmazonIT       │  │
│  │       02-21        │    │    DealScout       │  │
│  │                    │    │                    │  │
│  │  Session: UK       │    │  Tag: srzone00-21  │  │
│  └────────────────────┘    │                    │  │
│            ↓                │  Session: IT       │  │
│            ↓                └────────────────────┘  │
│            ↓                         ↓              │
│            └─────────────┬───────────┘              │
│                          ↓                          │
│              ┌───────────────────────┐              │
│              │  Coordinator          │              │
│              │  Port: 8000           │              │
│              │  Scheduler: 15 min    │              │
│              │  Max: 5 deals/worker  │              │
│              └───────────────────────┘              │
└─────────────────────────────────────────────────────┘
```

---

## 🇬🇧 WORKER UK

### Configurazione
- **Bot**: @dealscoutuk_bot
- **Token**: 7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w
- **Porta**: 8001
- **Sessione**: `/tmp/session_uk.session`

### Canali
- **Sorgente**: @NicePriceDeals (ID: -1001303541715)
- **Pubblicazione**: @DealScoutUKBot (ID: -1001232723285)

### Amazon
- **Dominio**: amazon.co.uk
- **Tag Affiliato**: ukbestdeal02-21

---

## 🇮🇹 WORKER IT

### Configurazione
- **Bot**: @dealscoutit_bot
- **Token**: 7948123806:AAF3nwK3n_kpyzcq1YWL71M5jPccvZYJF2w
- **Porta**: 8002
- **Sessione**: `/tmp/session_it.session`

### Canali
- **Sorgente**: @salvatore_aranzulla_offerte (ID: -1001294879762)
- **Pubblicazione**: @AmazonITDealScout (ID: -1001080585126)

### Amazon
- **Dominio**: amazon.it
- **Tag Affiliato**: srzone00-21

---

## 🔧 CONFIGURAZIONE TELETHON

### Credenziali Condivise
- **API ID**: 24358896
- **API Hash**: 3963ba2988481928ad78d15d4b4388a8
- **Phone**: +447775827823

### Sessioni
- **UK**: `workers/uk/session_uk.session` → `/tmp/session_uk.session`
- **IT**: `workers/it/session_it.session` → `/tmp/session_it.session`

**Nota**: Entrambe le sessioni usano lo stesso account Telegram (stesso numero)

---

## 🚀 STARTUP SEQUENCE

### Script: `start.sh`

1. **Avvia Worker UK** (background, porta 8001)
2. **Avvia Worker IT** (background, porta 8002)
3. **Health Check UK** (max 30 tentativi)
4. **Health Check IT** (max 30 tentativi)
5. **Avvia Coordinator** (foreground, porta 8000)

### Tempi di Avvio
- Worker UK: ~5-10 secondi
- Worker IT: ~5-10 secondi
- Coordinator: ~2-3 secondi
- **Totale**: ~15-25 secondi

---

## 📊 OPERATIVITÀ

### Scheduler
- **Frequenza**: 15 minuti
- **Esecuzione**: Simultanea per entrambi i worker
- **Max Deals**: 5 per worker per ciclo
- **Totale**: Fino a 10 deals ogni 15 minuti (5 UK + 5 IT)

### Flusso per Ciclo
1. Coordinator chiama `/scrape` su Worker UK (8001)
2. Coordinator chiama `/scrape` su Worker IT (8002)
3. Worker UK legge 50 messaggi da @NicePriceDeals
4. Worker IT legge 50 messaggi da @salvatore_aranzulla_offerte
5. Parsing e sostituzione tag affiliato
6. Return max 5 deals per worker
7. Coordinator posta su canali rispettivi con immagini e bottoni

---

## 🔍 ENDPOINTS

### Worker UK (8001)
- `GET /health` - Health check
- `GET /scrape` - Trigger scraping manuale
- `GET /stats` - Statistiche (ASIN processati, ultimo scrape)

### Worker IT (8002)
- `GET /health` - Health check
- `GET /scrape` - Trigger scraping manuale
- `GET /stats` - Statistiche (ASIN processati, ultimo scrape)

### Coordinator (8000)
- Nessun endpoint esposto (solo scheduler interno)

---

## 📁 STRUTTURA FILE

```
.
├── coordinator/
│   ├── main.py                    # Coordinator con supporto UK + IT
│   └── Dockerfile
├── workers/
│   ├── uk/
│   │   ├── worker_uk_v2.py       # Worker UK (NON MODIFICARE)
│   │   └── session_uk.session    # Sessione Telethon UK
│   └── it/
│       ├── worker_it.py          # Worker IT (nuovo)
│       └── session_it.session    # Sessione Telethon IT
├── Dockerfile                     # Container unificato
├── start.sh                       # Startup script dual-worker
├── .env                          # Credenziali UK + IT
└── requirements.txt              # Dipendenze condivise
```

---

## 🔒 PROTEZIONE WORKER UK

### File Protetti (NON MODIFICARE)
- ✅ `workers/uk/worker_uk_v2.py` - Stabile e funzionante
- ✅ `workers/uk/session_uk.session` - Sessione autenticata
- ✅ Configurazione UK in `.env`

### Worker IT Indipendente
- ✅ File separati in `workers/it/`
- ✅ Porta separata (8002)
- ✅ Sessione separata
- ✅ Configurazione separata in `.env`

**Modifiche a Worker IT non influenzano Worker UK**

---

## 🧪 TESTING

### Test Worker UK
```bash
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/scrape
curl http://127.0.0.1:8001/stats
```

### Test Worker IT
```bash
curl http://127.0.0.1:8002/health
curl http://127.0.0.1:8002/scrape
curl http://127.0.0.1:8002/stats
```

### Verifica Logs
```bash
# Worker UK logs
grep "Worker UK" /var/log/container.log

# Worker IT logs
grep "Worker IT" /var/log/container.log

# Coordinator logs
grep "Coordinator" /var/log/container.log
```

---

## 📈 METRICHE ATTESE

### Per Ciclo (15 minuti)
- Worker UK: 0-5 deals da @NicePriceDeals
- Worker IT: 0-5 deals da @salvatore_aranzulla_offerte
- Totale: 0-10 deals pubblicati

### Per Ora
- UK: 0-20 deals
- IT: 0-20 deals
- Totale: 0-40 deals

### Per Giorno
- UK: 0-480 deals
- IT: 0-480 deals
- Totale: 0-960 deals

---

## ⚠️ NOTE IMPORTANTI

### Sessioni Telethon
- Entrambe le sessioni usano lo stesso account Telegram
- Se una sessione scade, rigenerare con `create_session_uk.py` o `create_session_it.py`
- Copiare il file `.session` nella cartella corretta

### Rate Limiting
- Telegram: 30 messaggi/secondo (non raggiunto)
- Con 10 deals/15min siamo molto sotto i limiti

### Failover
- Se Worker UK fallisce, Worker IT continua a funzionare
- Se Worker IT fallisce, Worker UK continua a funzionare
- Coordinator gestisce errori di connessione gracefully

---

## 🚀 DEPLOYMENT

### Push su GitHub
```bash
git add .
git commit -m "feat: Dual worker setup UK + IT"
git push origin main
```

### Northflk Auto-Deploy
1. Northflk rileva il push
2. Rebuild del container
3. Avvio automatico con `start.sh`
4. Entrambi i worker si avviano
5. Coordinator inizia lo scheduling

### Verifica Deployment
1. Controllare logs Northflk
2. Verificare "✅ Worker UK pronto!"
3. Verificare "✅ Worker IT pronto!"
4. Verificare "📅 Scheduler avviato - processing ogni 15 minuti"
5. Attendere primo ciclo (max 15 minuti)

---

## 🎯 PROSSIMI PASSI

1. ✅ Push su GitHub
2. ✅ Verifica deployment Northflk
3. ✅ Monitorare primo ciclo Worker IT
4. ✅ Verificare deals pubblicati su @AmazonITDealScout
5. ✅ Confermare che Worker UK continua a funzionare

---

**Status**: ✅ PRONTO PER DEPLOYMENT  
**Backward Compatibility**: ✅ Worker UK non modificato  
**Rischio**: 🟢 BASSO (worker isolati)
