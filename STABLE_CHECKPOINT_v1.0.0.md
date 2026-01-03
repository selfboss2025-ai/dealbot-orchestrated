# 🎯 STABLE CHECKPOINT v1.0.0 - PRODUCTION READY

**Data**: 3 Gennaio 2026  
**Status**: ✅ COMPLETAMENTE FUNZIONANTE IN PRODUZIONE  
**Deployment**: Northflk (Container unificato)

---

## 📋 CONFIGURAZIONE FINALE

### Bot Telegram
- **Coordinator Bot**: @dealscoutcoord_bot (Token: 7935915288:AAHWLybhV0LDZoOZNEu9XZp57YJ7dft8ito)
- **Worker Bot**: @dealscoutuk_bot (Token: 7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w)

### Canali
- **Sorgente**: @NicePriceDeals (ID: -1001303541715)
- **Pubblicazione**: @DealScoutUKBot (ID: -1001232723285)

### Telethon (Scraping Reale)
- **API ID**: 24358896
- **API Hash**: 3963ba2988481928ad78d15d4b4388a8
- **Phone**: +447775827823
- **Sessione**: `workers/uk/session_uk.session` (pre-autenticata)

### Parametri Operativi
- **Frequenza**: 15 minuti tra ogni ciclo
- **Max Deals**: 5 per ciclo
- **Duplicati**: Automaticamente evitati (tracking ASIN)
- **Tag Affiliato**: ukbestdeal02-21

---

## 🏗️ ARCHITETTURA

### Container Unificato (Northflk)
```
┌─────────────────────────────────────┐
│  Container: dealscoutorch           │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Worker UK (Port 8001)       │  │
│  │  - Telethon scraping         │  │
│  │  - Message parsing           │  │
│  │  - Affiliate tag replacement │  │
│  └──────────────────────────────┘  │
│              ↓ HTTP                 │
│  ┌──────────────────────────────┐  │
│  │  Coordinator (Port 8000)     │  │
│  │  - Scheduler (15 min)        │  │
│  │  - Deal posting with images  │  │
│  │  - 5 sharing buttons         │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Flusso Operativo
1. **Scheduler** (ogni 15 min) → chiama Worker UK
2. **Worker UK** → Telethon legge 50 messaggi da @NicePriceDeals
3. **Parsing** → Estrae ASIN, sostituisce tag affiliato
4. **Return** → Max 5 deals (no duplicati) al Coordinator
5. **Coordinator** → Posta su @DealScoutUKBot come foto + bottoni

---

## 📁 FILE CRITICI (NON MODIFICARE)

### Codice Principale
- `coordinator/main.py` - Scheduler e posting logic
- `workers/uk/worker_uk_v2.py` - Telethon scraping e parsing
- `Dockerfile` - Container unificato
- `start.sh` - Startup script (worker → coordinator)

### Configurazione
- `.env` - Credenziali e tokens
- `requirements.txt` - Dipendenze Python
- `workers/uk/session_uk.session` - Sessione Telethon autenticata

### Deployment
- `docker-compose.yml` - Configurazione container
- Repository: `https://github.com/selfboss2025-ai/dealbot-orchestrated.git`

---

## ✅ FUNZIONALITÀ IMPLEMENTATE

### Scraping
- ✅ Telethon connesso e autenticato
- ✅ Lettura messaggi reali da @NicePriceDeals
- ✅ Parsing automatico URL Amazon
- ✅ Estrazione ASIN da URL
- ✅ Sostituzione tag affiliato (frb-dls-21 → ukbestdeal02-21)

### Posting
- ✅ Invio come foto (immagine prodotto Amazon)
- ✅ URL nascosto dal testo (solo nei bottoni)
- ✅ 5 bottoni di sharing:
  - 🛒 VIEW ON AMAZON
  - 💬 WhatsApp
  - 👍 Facebook
  - 𝕏 Twitter
  - ✈️ Telegram

### Gestione
- ✅ Scheduler automatico (15 minuti)
- ✅ Prevenzione duplicati (ASIN tracking)
- ✅ Limite 5 deals per ciclo
- ✅ Health check endpoint
- ✅ Logging dettagliato

---

## 🚀 DEPLOYMENT

### Northflk
1. Push su GitHub: `git push origin main`
2. Northflk auto-rebuild dal repository
3. Container avviato automaticamente
4. Health check: `http://127.0.0.1:8001/health`

### Comandi Utili
```bash
# Verifica status
curl http://127.0.0.1:8001/health

# Verifica stats
curl http://127.0.0.1:8001/stats

# Trigger manuale scraping
curl http://127.0.0.1:8001/scrape
```

---

## 📊 METRICHE OPERATIVE

### Performance
- Tempo medio scraping: ~2-3 secondi
- Tempo medio posting: ~1 secondo per deal
- Ciclo completo: ~10-15 secondi

### Limiti Telegram
- Rate limit: 30 messaggi/secondo (non raggiunto)
- Max 5 deals/15min = 20 deals/ora (sicuro)

---

## 🔒 BACKUP E RECOVERY

### File da Backuppare
1. `workers/uk/session_uk.session` - CRITICO (sessione Telethon)
2. `.env` - Credenziali
3. Tutto il repository Git

### Recovery Procedure
1. Clone repository: `git clone https://github.com/selfboss2025-ai/dealbot-orchestrated.git`
2. Checkout stable: `git checkout v1.0.0-stable`
3. Verifica sessione Telethon presente
4. Push su Northflk
5. Verifica deployment

---

## 📝 NOTE IMPORTANTI

### ⚠️ NON MODIFICARE
- Sessione Telethon (`session_uk.session`)
- Credenziali in `.env`
- Logica di parsing in `worker_uk_v2.py`
- Scheduler timing in `coordinator/main.py`

### ✅ SICURO MODIFICARE
- Frequenza scheduler (se necessario)
- Max deals per ciclo (se necessario)
- Testo bottoni sharing
- Logging level

### 🔄 Se Serve Rigenerare Sessione
```bash
python create_session.py
# Inserire codice Telegram ricevuto via SMS
# Copiare session_uk.session in workers/uk/
```

---

## 🎉 RISULTATO FINALE

Sistema completamente automatizzato che:
1. Monitora @NicePriceDeals ogni 15 minuti
2. Estrae fino a 5 deals Amazon UK
3. Sostituisce tag affiliato
4. Pubblica su @DealScoutUKBot con immagini e bottoni
5. Evita duplicati automaticamente
6. Funziona 24/7 su Northflk

**Status**: ✅ PRODUCTION READY - NON MODIFICARE

---

**Git Tag**: `v1.0.0-stable`  
**Commit Hash**: Verificare con `git rev-parse HEAD`  
**Ultimo Test**: 3 Gennaio 2026 - 13:13 UTC  
**Test Result**: ✅ PASSED - Deal postato con successo
