# 🇬🇧 Worker UK - Deal Scout

Worker specializzato per il monitoraggio e scraping di offerte Amazon UK dal canale @NicePriceDeals.

## 📋 Configurazione

### Dati Bot
- **Bot ID**: 7768046661
- **Bot Username**: @dealscoutuk_bot
- **Bot Token**: `7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w`

### Canali Telegram
- **Canale Sorgente**: @NicePriceDeals (ID: -1001303541715)
- **Canale Pubblicazione**: @DealScoutUKBot (ID: -1001232723285)

### Affiliate
- **Tag Affiliato**: `ukbestdeal02-21`
- **Dominio**: amazon.co.uk

## 🚀 Avvio Rapido

### Locale (Sviluppo)

```bash
# Installa dipendenze
pip install -r ../../requirements.txt

# Configura variabili ambiente
export WORKER_BOT_TOKEN="7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w"
export WORKER_PORT=8001

# Avvia worker
python worker_uk.py
```

### Docker

```bash
# Build immagine
docker build -f Dockerfile -t dealscout-uk:latest ../..

# Run container
docker run -d \
  --name worker-uk \
  -p 8001:8001 \
  --env-file .env \
  --restart unless-stopped \
  dealscout-uk:latest
```

## 🔌 Endpoint HTTP

### `/scrape` (GET)
Restituisce lista di deals trovati nel canale sorgente.

```bash
curl http://localhost:8001/scrape
```

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

### `/health` (GET)
Health check del worker.

```bash
curl http://localhost:8001/health
```

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

### `/stats` (GET)
Statistiche del worker.

```bash
curl http://localhost:8001/stats
```

## 🔍 Funzionalità

### Parsing Messaggi
- ✅ Estrazione ASIN da link Amazon UK
- ✅ Parsing prezzi in £ (pence)
- ✅ Calcolo automatico sconti
- ✅ Estrazione immagini
- ✅ Validazione deals

### Filtri
- ✅ Sconto minimo: 10%
- ✅ Prezzo massimo: £100,000
- ✅ Deduplicazione ASIN
- ✅ Validazione formato ASIN

### Formattazione
- ✅ Link affiliati Amazon UK
- ✅ Messaggi Markdown formattati
- ✅ Emoji e formattazione visuale
- ✅ Hashtag per categorizzazione

## 🔧 Configurazione Avanzata

### Modificare Sconto Minimo

```bash
export MIN_DISCOUNT_PERCENT=15
python worker_uk.py
```

### Modificare Porta

```bash
export WORKER_PORT=9001
python worker_uk.py
```

### Modificare Lookback Scraping

```bash
export SCRAPE_LOOKBACK_HOURS=12
python worker_uk.py
```

## 📊 Monitoraggio

### Logs in Tempo Reale

```bash
docker logs worker-uk -f
```

### Statistiche Worker

```bash
curl http://localhost:8001/stats | jq
```

## 🐛 Troubleshooting

### Worker Non Risponde

```bash
# Verifica health
curl http://localhost:8001/health

# Controlla logs
docker logs worker-uk

# Restart
docker restart worker-uk
```

### Nessun Deal Trovato

1. Verifica che il bot sia membro di @NicePriceDeals
2. Controlla che il canale abbia messaggi con link Amazon
3. Verifica i pattern di parsing nei logs
4. Aumenta `SCRAPE_LOOKBACK_HOURS`

### Errore Telegram API

1. Verifica token bot
2. Verifica permessi canali
3. Controlla rate limiting
4. Verifica connessione internet

## 🔄 Integrazione Coordinatore

Il coordinatore chiama questo worker ogni 6 ore:

```python
response = requests.get('http://worker-uk-ip:8001/scrape', timeout=30)
deals = response.json()
```

Se il worker è offline, il coordinatore continua con altri worker.

## 📝 Note Tecniche

- **Linguaggio**: Python 3.11
- **Framework Web**: Flask
- **Bot API**: python-telegram-bot 20.7
- **Timeout**: 30 secondi per richieste HTTP
- **Rate Limiting**: 1 secondo tra richieste
- **Cache**: Deduplicazione ASIN in memoria

## 🚀 Prossimi Passi

1. Deploy su VPS/Northflk
2. Configurare coordinatore centrale
3. Aggiungere worker per altri paesi (IT, FR, DE)
4. Monitoraggio e alerting
5. Database per storico deals