# 🏗️ Architettura Deal Bot Orchestrato

Documentazione completa dell'architettura distribuita.

## 📐 Diagramma Architettura

```
┌─────────────────────────────────────────────────────────────────┐
│                    COORDINATORE CENTRALE                         │
│                   (Northflk - 24/7 Stabile)                      │
│                                                                   │
│  - Orchestrazione worker                                         │
│  - Scheduling ogni 6 ore                                         │
│  - Gestione affiliate links                                      │
│  - Pubblicazione deals                                           │
│  - Error handling e retry logic                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │  WORKER UK   │ │  WORKER IT   │ │  WORKER FR   │
        │  (Port 8001) │ │  (Port 8002) │ │  (Port 8003) │
        │              │ │              │ │              │
        │ - Scraping   │ │ - Scraping   │ │ - Scraping   │
        │ - Parsing    │ │ - Parsing    │ │ - Parsing    │
        │ - HTTP API   │ │ - HTTP API   │ │ - HTTP API   │
        └──────────────┘ └──────────────┘ └──────────────┘
                │             │             │
        ┌───────▼─────┐ ┌─────▼───────┐ ┌──▼────────────┐
        │@NicePriceD. │ │@ItalianDeals│ │@FrenchDeals  │
        │(Scraping)   │ │(Scraping)   │ │(Scraping)    │
        └─────────────┘ └─────────────┘ └──────────────┘
                │             │             │
        ┌───────▼─────┐ ┌─────▼───────┐ ┌──▼────────────┐
        │@DealScoutUK │ │@DealScoutIT │ │@DealScoutFR  │
        │(Publishing) │ │(Publishing) │ │(Publishing)  │
        └─────────────┘ └─────────────┘ └──────────────┘
```

## 🔄 Flusso Operativo

### 1. Scheduling (Coordinatore)

```
Ogni 6 ore:
  ├─ Verifica worker disponibili
  ├─ Chiama /scrape di ogni worker
  └─ Processa risultati
```

### 2. Scraping (Worker)

```
Worker riceve richiesta /scrape:
  ├─ Legge ultimi messaggi da canale sorgente
  ├─ Estrae ASIN, prezzi, sconti
  ├─ Valida deals
  ├─ Ritorna JSON al coordinatore
  └─ Mantiene cache ASIN
```

### 3. Pubblicazione (Coordinatore)

```
Per ogni deal ricevuto:
  ├─ Genera link affiliato
  ├─ Formatta messaggio Markdown
  ├─ Invia foto (se disponibile)
  ├─ Posta su canale destinazione
  └─ Pausa 2 secondi (rate limiting)
```

## 📁 Struttura Directory

```
dealbot-orchestrated/
├── coordinator/
│   ├── main.py              # Bot coordinatore principale
│   ├── Dockerfile           # Container coordinatore
│   └── README.md            # Docs coordinatore
│
├── workers/
│   ├── uk/                  # Worker UK (IMPLEMENTATO)
│   │   ├── config.py        # Configurazione UK
│   │   ├── worker_uk.py     # Worker UK
│   │   ├── .env             # Variabili ambiente
│   │   ├── Dockerfile       # Container UK
│   │   └── README.md        # Docs UK
│   │
│   ├── template/            # Template per nuovi worker
│   │   ├── config.py        # Config template
│   │   ├── SETUP_GUIDE.md   # Guida setup
│   │   └── .env.example     # Env template
│   │
│   └── it/                  # Worker IT (DA CREARE)
│       └── (stessa struttura di uk/)
│
├── scripts/
│   ├── deploy-coordinator.sh    # Deploy coordinatore
│   ├── deploy-worker-uk.sh      # Deploy worker UK
│   ├── test-worker-uk.sh        # Test worker UK
│   ├── test-system.sh           # Test sistema completo
│   └── deploy-worker.sh         # Template deploy worker
│
├── docker-compose.yml       # Compose per dev completo
├── requirements.txt         # Dipendenze Python
├── .env.example            # Env template coordinatore
├── README.md               # Docs principale
├── SETUP_UK_WORKER.md      # Setup worker UK
├── ARCHITECTURE.md         # Questo file
└── .gitignore
```

## 🔌 API Endpoints

### Worker Endpoints

#### GET `/scrape`
Restituisce lista di deals trovati.

**Risposta**:
```json
[
  {
    "asin": "B09DFPV5HL",
    "title": "Echo Dot 5th Gen",
    "current_price_pence": 2999,
    "list_price_pence": 5999,
    "discount_pct": 50,
    "image_url": "https://...",
    "country": "UK",
    "channel_id": -1001303541715,
    "message_id": 12345,
    "scraped_at": "2024-01-01T12:00:00"
  }
]
```

#### GET `/health`
Health check worker.

**Risposta**:
```json
{
  "status": "healthy",
  "worker": "DealScout UK",
  "country": "UK",
  "source_channel": -1001303541715,
  "publish_channel": -1001232723285,
  "last_scrape": "2024-01-01T12:00:00",
  "timestamp": "2024-01-01T12:05:00"
}
```

#### GET `/stats`
Statistiche worker.

**Risposta**:
```json
{
  "processed_asins": 42,
  "last_scrape_time": "2024-01-01T12:00:00",
  "uptime": "running"
}
```

## 🔐 Sicurezza

### Token Management
- ✅ Token in variabili ambiente (non in codice)
- ✅ File .env in .gitignore
- ✅ Container non-root (utente botuser)

### Network
- ✅ Worker isolati su porte diverse
- ✅ Timeout su richieste HTTP (30s)
- ✅ Rate limiting su Telegram (2s tra post)

### Data Validation
- ✅ Validazione ASIN (10 caratteri alphanumerici)
- ✅ Validazione prezzi (range ragionevole)
- ✅ Validazione sconti (0-100%)
- ✅ Deduplicazione ASIN

## 📊 Configurazione Paesi

### UK (Implementato)
```
Bot: @dealscoutuk_bot
Canale Sorgente: @NicePriceDeals
Canale Destinazione: @DealScoutUKBot
Dominio: amazon.co.uk
Valuta: £ (pence)
Affiliate Tag: ukbestdeal02-21
Porta: 8001
```

### IT (Template Pronto)
```
Bot: @dealscoutit_bot (da creare)
Canale Sorgente: @your_source (da configurare)
Canale Destinazione: @DealScoutITBot (da creare)
Dominio: amazon.it
Valuta: € (centesimi)
Affiliate Tag: your-it-tag-21
Porta: 8002
```

### FR (Template Pronto)
```
Bot: @dealscoutfr_bot (da creare)
Canale Sorgente: @your_source (da configurare)
Canale Destinazione: @DealScoutFRBot (da creare)
Dominio: amazon.fr
Valuta: € (centesimi)
Affiliate Tag: your-fr-tag-21
Porta: 8003
```

## 🚀 Deployment Scenarios

### Scenario 1: Sviluppo Locale
```
Coordinatore: localhost:8000
Worker UK: localhost:8001
Worker IT: localhost:8002
```

### Scenario 2: Produzione Distribuita
```
Coordinatore: Northflk (server stabile)
Worker UK: VPS1 (8001)
Worker IT: VPS2 (8002)
Worker FR: Raspberry Pi (8003)
```

### Scenario 3: Docker Compose
```
Tutti i servizi in container
Network interno: dealbot-network
Coordinatore: coordinator:8000
Worker UK: worker-uk:8001
Worker IT: worker-it:8002
```

## 📈 Scalabilità

### Aggiungere Nuovo Paese

1. **Copia template**:
   ```bash
   cp -r workers/template workers/xx
   ```

2. **Personalizza config.py**:
   - Bot token
   - Canali Telegram
   - Pattern Amazon
   - Pattern prezzi

3. **Crea worker_xx.py**:
   - Copia da worker_uk.py
   - Aggiorna import config

4. **Aggiorna coordinatore**:
   - Aggiungi worker in main.py
   - Aggiungi variabili .env

5. **Deploy**:
   ```bash
   ./scripts/deploy-worker-xx.sh
   ```

## 🔄 Resilienza

### Fault Tolerance
- ✅ Worker offline: coordinatore continua con altri
- ✅ Timeout worker: skip e continua
- ✅ Errore Telegram: log e continua
- ✅ Errore parsing: skip deal e continua

### Retry Logic
- ✅ Timeout 30s per worker
- ✅ Continua anche con errori parziali
- ✅ Log dettagliati per debugging

### Monitoring
- ✅ Health check endpoint
- ✅ Stats endpoint
- ✅ Logging strutturato
- ✅ Docker logs

## 📊 Performance

### Coordinatore
- Scheduling: ogni 6 ore
- Timeout worker: 30 secondi
- Rate limiting: 2 secondi tra post
- Max deals: 50 per ciclo

### Worker
- Response time: < 1 secondo (target)
- Cache ASIN: in memoria
- Validazione: 100% deals

## 🔧 Configurazione Avanzata

### Modificare Frequenza Scheduling
```python
# coordinator/main.py
trigger=IntervalTrigger(hours=4)  # Ogni 4 ore
```

### Modificare Rate Limiting
```python
# coordinator/main.py
await asyncio.sleep(5)  # 5 secondi tra post
```

### Modificare Sconto Minimo
```bash
# workers/uk/.env
MIN_DISCOUNT_PERCENT=15
```

### Modificare Lookback Scraping
```bash
# workers/uk/.env
SCRAPE_LOOKBACK_HOURS=12
```

## 📝 Logging

### Livelli Log
- DEBUG: Informazioni dettagliate
- INFO: Operazioni normali
- WARNING: Situazioni anomale
- ERROR: Errori

### Configurazione
```bash
# .env
LOG_LEVEL=INFO
```

### Visualizzazione
```bash
# Logs in tempo reale
docker logs worker-uk -f

# Ultimi 100 log
docker logs worker-uk --tail 100

# Con timestamp
docker logs worker-uk -t
```

## 🎯 Roadmap

### Fase 1: MVP (Completato)
- ✅ Coordinatore centrale
- ✅ Worker UK
- ✅ Template worker generico
- ✅ Docker support

### Fase 2: Espansione
- ⏳ Worker IT
- ⏳ Worker FR
- ⏳ Worker DE
- ⏳ Database storico

### Fase 3: Ottimizzazione
- ⏳ Caching distribuito
- ⏳ Monitoring avanzato
- ⏳ Alerting
- ⏳ Analytics

### Fase 4: Produzione
- ⏳ Load balancing
- ⏳ Auto-scaling
- ⏳ Disaster recovery
- ⏳ Multi-region

## 📚 Documentazione

- `README.md` - Overview generale
- `SETUP_UK_WORKER.md` - Setup worker UK
- `ARCHITECTURE.md` - Questo file
- `workers/uk/README.md` - Docs worker UK
- `workers/template/SETUP_GUIDE.md` - Guida nuovi worker
- `coordinator/README.md` - Docs coordinatore

## 🤝 Contributi

Per aggiungere nuovi paesi o miglioramenti:

1. Copia template worker
2. Personalizza per il paese
3. Test locale
4. Test Docker
5. Integra coordinatore
6. Deploy

## 📞 Supporto

Per problemi o domande:

1. Controlla logs: `docker logs <container> -f`
2. Verifica health: `curl http://localhost:PORT/health`
3. Test scrape: `curl http://localhost:PORT/scrape`
4. Verifica bot: `curl https://api.telegram.org/bot<TOKEN>/getMe`