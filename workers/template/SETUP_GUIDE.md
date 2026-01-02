# 🚀 Guida Setup Worker per Nuovo Paese

Questa guida ti aiuta a creare un nuovo worker per un paese diverso da UK.

## 📋 Prerequisiti

1. **Bot Telegram**: Crea un nuovo bot con @BotFather
2. **Canali Telegram**: 
   - Canale sorgente (da cui fare scraping)
   - Canale destinazione (dove pubblicare deals)
3. **Affiliate Tag**: Ottieni il tuo tag affiliato Amazon per il paese

## 🔧 Step-by-Step

### 1. Crea Struttura Directory

```bash
# Copia template per il tuo paese (es. IT per Italia)
cp -r workers/template workers/it

# Rinomina file
cd workers/it
mv config.py config.py
```

### 2. Configura `config.py`

Apri `workers/it/config.py` e personalizza:

```python
# Bot Telegram
BOT_TOKEN = 'YOUR_NEW_BOT_TOKEN'
BOT_USERNAME = '@your_new_bot'
BOT_ID = 123456789

# Canali
PUBLISH_CHANNEL_ID = -1001234567890
PUBLISH_CHANNEL_NAME = '@your_publish_channel'
SOURCE_CHANNEL_ID = -1001234567890
SOURCE_CHANNEL_NAME = '@your_source_channel'

# Configurazione
WORKER_COUNTRY = 'IT'  # Codice paese
WORKER_NAME = 'DealScout IT Worker'
AFFILIATE_TAG = 'your-it-tag-21'

# Pattern Amazon per il paese
AMAZON_PATTERNS = {
    'domain': [r'amazon\.it', r'amzn\.eu'],
    'asin': [r'amazon\.it/.*?/dp/([A-Z0-9]{10})', ...]
}

# Pattern Prezzi (€ per Italia)
PRICE_PATTERNS = [
    r'€(\d+),(\d{2})',
    r'(\d+),(\d{2})\s*€',
    ...
]
```

### 3. Copia Worker Script

```bash
# Copia il worker UK come base
cp ../uk/worker_uk.py worker_it.py

# Modifica import in worker_it.py
# Cambia: from config import ...
# In: from config import ...
```

### 4. Crea `.env`

```bash
# Copia template
cp ../uk/.env .env

# Modifica con i tuoi dati
WORKER_BOT_TOKEN=your_new_token
WORKER_PORT=8002  # Porta diversa per ogni worker
```

### 5. Crea `Dockerfile`

```bash
# Copia Dockerfile UK
cp ../uk/Dockerfile .

# Modifica ultima riga:
# Da: CMD ["python", "worker_uk.py"]
# A:  CMD ["python", "worker_it.py"]
```

### 6. Crea `README.md`

```bash
# Copia README UK
cp ../uk/README.md .

# Personalizza con i tuoi dati
```

## 🧪 Test Locale

```bash
# Installa dipendenze
pip install -r ../../requirements.txt

# Configura ambiente
export $(cat .env | grep -v '^#' | xargs)

# Avvia worker
python worker_it.py
```

## 🐳 Test Docker

```bash
# Build
docker build -f Dockerfile -t dealscout-it:latest ../..

# Run
docker run -d \
  --name worker-it \
  -p 8002:8002 \
  --env-file .env \
  dealscout-it:latest

# Test
curl http://localhost:8002/health
```

## 🔌 Integrazione Coordinatore

Aggiungi il nuovo worker al coordinatore in `coordinator/main.py`:

```python
self.workers = {
    'UK': {...},
    'IT': {
        'url': os.getenv('WORKER_IT_URL', 'http://localhost:8002'),
        'channel': os.getenv('IT_CHANNEL', '@your_channel'),
        'affiliate_tag': 'your-it-tag-21'
    }
}
```

Aggiungi variabili in `.env`:

```bash
WORKER_IT_URL=http://your-it-worker-ip:8002
IT_CHANNEL=@your_publish_channel
```

## 📝 Checklist

- [ ] Bot Telegram creato
- [ ] Canali Telegram creati
- [ ] `config.py` personalizzato
- [ ] `worker_xx.py` creato
- [ ] `.env` configurato
- [ ] `Dockerfile` personalizzato
- [ ] Test locale OK
- [ ] Test Docker OK
- [ ] Coordinatore aggiornato
- [ ] Deploy completato

## 🌍 Paesi Supportati

Crea worker per questi paesi seguendo questa guida:

- 🇬🇧 UK (amazon.co.uk) - ✅ Già fatto
- 🇮🇹 IT (amazon.it) - Template pronto
- 🇫🇷 FR (amazon.fr) - Template pronto
- 🇩🇪 DE (amazon.de) - Template pronto
- 🇪🇸 ES (amazon.es) - Template pronto
- 🇸🇪 SE (amazon.se) - Template pronto

## 💡 Tips

1. **Porte**: Usa porte diverse per ogni worker (8001, 8002, 8003, etc.)
2. **Affiliate Tags**: Ogni paese ha tag diversi
3. **Pattern Prezzi**: Adatta ai separatori decimali del paese (. vs ,)
4. **Canali**: Assicurati che il bot sia membro dei canali
5. **Rate Limiting**: Modifica se necessario per il tuo paese

## 🆘 Troubleshooting

### Worker non trova deals

1. Verifica che il bot sia membro del canale sorgente
2. Controlla i pattern Amazon per il dominio corretto
3. Verifica i pattern prezzi con la valuta giusta
4. Aumenta `SCRAPE_LOOKBACK_HOURS`

### Errore connessione Telegram

1. Verifica token bot
2. Verifica permessi canali
3. Controlla firewall/proxy
4. Verifica rate limiting

### Porta già in uso

```bash
# Cambia porta in .env
WORKER_PORT=8003

# O libera porta
lsof -i :8002
kill -9 <PID>
```

## 📚 Risorse

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Amazon ASIN Format](https://docs.aws.amazon.com/AWSECommerceService/latest/DeveloperGuide/ASIN.html)
- [python-telegram-bot Docs](https://python-telegram-bot.readthedocs.io/)

## 🤝 Supporto

Se hai problemi, controlla:
1. I logs del worker: `docker logs worker-xx -f`
2. Health check: `curl http://localhost:PORT/health`
3. Scrape test: `curl http://localhost:PORT/scrape`