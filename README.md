# 🤖 Deal Bot Orchestrato - Architettura Distribuita

Sistema robusto e scalabile per monitoraggio e pubblicazione automatica di offerte Amazon UK/IT attraverso Telegram, con architettura coordinatore-worker per massima resilienza.

## 🏗️ Architettura

### Componenti Principali

1. **Coordinatore Centrale** (`coordinator/`)
   - Bot principale che orchestra tutto il sistema
   - Schedulazione automatica ogni 6 ore
   - Gestione affiliate links e pubblicazione
   - Deploy consigliato: Northflk (server affidabile 24/7)

2. **Worker Bot** (`worker/`)
   - Bot specializzati per scraping canali specifici
   - Espongono endpoint HTTP `/scrape`
   - Isolati e indipendenti
   - Deploy flessibile: VPS, Raspberry Pi, locale

### Vantaggi Architettura

✅ **Crash Isolation**: Se un worker va offline, il coordinatore continua con gli altri  
✅ **Scalabilità**: Aggiungi nuovi worker senza modificare il coordinatore  
✅ **Risorse Ottimizzate**: Worker leggeri, coordinatore su server stabile  
✅ **Manutenzione Semplice**: Ogni componente ha responsabilità specifiche  
✅ **Compliance**: Solo parsing di canali interni, nessun scraping Amazon diretto  

## 🚀 Setup Rapido

### 1. Clona e Configura

```bash
git clone <repository>
cd dealbot-orchestrated
cp .env.example .env
# Modifica .env con i tuoi token e configurazioni
```

### 2. Installa Dipendenze

```bash
pip install -r requirements.txt
```

### 3. Avvia Worker (Locale/VPS)

```bash
# Worker UK
export WORKER_BOT_TOKEN=your_uk_bot_token
export SOURCE_CHANNEL=@your_uk_source_channel
export WORKER_COUNTRY=UK
export WORKER_PORT=8001

python worker/worker.py
```

### 4. Avvia Coordinatore (Northflk)

```bash
# Coordinatore
export BOT_TOKEN=your_coordinator_bot_token
export WORKER_UK_URL=http://your-worker-ip:8001
export UK_CHANNEL=@DealScoutUKBot

python coordinator/main.py
```

## 🐳 Deploy con Docker

### Deploy Completo (Sviluppo)

```bash
docker-compose up -d
```

### Deploy Solo Coordinatore (Produzione Northflk)

```bash
# Build immagine coordinatore
docker build -f coordinator/Dockerfile -t dealbot-coordinator .

# Run coordinatore
docker run -d \
  --name coordinator \
  --env-file .env \
  --restart unless-stopped \
  dealbot-coordinator
```

### Deploy Solo Worker (VPS/Raspberry Pi)

```bash
# Build immagine worker
docker build -f worker/Dockerfile -t dealbot-worker .

# Run worker UK
docker run -d \
  --name worker-uk \
  -p 8001:8001 \
  -e WORKER_BOT_TOKEN=your_token \
  -e SOURCE_CHANNEL=@your_channel \
  -e WORKER_COUNTRY=UK \
  -e WORKER_PORT=8001 \
  --restart unless-stopped \
  dealbot-worker
```

## ⚙️ Configurazione

### Variabili Ambiente Coordinatore

```bash
BOT_TOKEN=your_coordinator_bot_token
UK_CHANNEL=@DealScoutUKBot
IT_CHANNEL=@AmazonITDealScout
WORKER_UK_URL=http://worker-uk-server:8001
WORKER_IT_URL=http://worker-it-server:8002
```

### Variabili Ambiente Worker

```bash
WORKER_BOT_TOKEN=your_worker_bot_token
SOURCE_CHANNEL=@source_deals_channel
WORKER_COUNTRY=UK  # o IT
WORKER_PORT=8001   # porta HTTP endpoint
```

## 🔄 Flusso Operativo

1. **Scheduling**: Coordinatore si attiva ogni 6 ore
2. **Worker Call**: Chiama endpoint `/scrape` di ogni worker (timeout 30s)
3. **Data Processing**: Worker restituisce deals in formato JSON
4. **Affiliate Links**: Coordinatore genera link affiliati per paese
5. **Publishing**: Posta deals sui canali Telegram appropriati
6. **Error Handling**: Continua anche se alcuni worker sono offline

## 📊 Monitoraggio

### Health Check Worker

```bash
curl http://worker-ip:8001/health
```

### Logs Coordinatore

```bash
docker logs coordinator -f
```

### Logs Worker

```bash
docker logs worker-uk -f
```

## 🛠️ Personalizzazione

### Aggiungere Nuovo Paese (es. Francia)

1. **Coordinatore**: Aggiungi configurazione in `main.py`
```python
'FR': {
    'url': os.getenv('WORKER_FR_URL'),
    'channel': '@DealScoutFRBot',
    'affiliate_tag': 'yourfrtag-21'
}
```

2. **Worker**: Deploy nuovo worker con `WORKER_COUNTRY=FR`

3. **Patterns**: Aggiorna pattern Amazon Francia in `worker.py`

### Modificare Frequenza Scheduling

Modifica in `coordinator/main.py`:
```python
trigger=IntervalTrigger(hours=4)  # Ogni 4 ore invece di 6
```

### Personalizzare Formato Messaggi

Modifica `format_deal_message()` in `coordinator/main.py`

## 🔧 Troubleshooting

### Worker Non Risponde

```bash
# Verifica connettività
curl http://worker-ip:8001/health

# Controlla logs
docker logs worker-uk

# Restart worker
docker restart worker-uk
```

### Coordinatore Non Posta

1. Verifica token bot Telegram
2. Controlla permessi canali
3. Verifica URL worker raggiungibili
4. Controlla logs per errori specifici

### Rate Limiting Telegram

Il coordinatore include pause di 2 secondi tra post. Modifica in `main.py` se necessario:
```python
await asyncio.sleep(5)  # Pausa più lunga
```

## 📝 Note Tecniche

- **Timeout Worker**: 30 secondi per chiamate HTTP
- **Rate Limiting**: 2 secondi tra post Telegram
- **Retry Logic**: Coordinatore continua anche con worker offline
- **Data Format**: JSON standardizzato per comunicazione worker-coordinatore
- **Security**: Container non-root, variabili ambiente per credenziali

## 🤝 Contributi

Per miglioramenti o nuove funzionalità, apri una issue o pull request.

## 📄 Licenza

MIT License - Vedi file LICENSE per dettagli.