# 🔄 Strategy Change - Real-Time Message Monitoring

## Problem with Previous Approach

❌ `get_chat_history()` non funziona per canali pubblici
- Il bot non ha permessi di admin su @NicePriceDeals
- Non può leggere la cronologia dei messaggi
- Errore: "Forbidden: bot was blocked by the user"

## New Approach: Real-Time Message Handler

✅ **Message Handler Pattern**
- Il bot si iscrive ai messaggi in tempo reale dal canale
- Non ha bisogno di permessi di admin
- Funziona con canali pubblici
- Processa i messaggi non appena vengono pubblicati

## How It Works

### 1. Bot Initialization
```python
# Il bot si connette a Telegram
bot = Bot(token=WORKER_BOT_TOKEN)

# Crea un Application updater
app = Application.builder().token(bot_token).build()

# Registra handler per i messaggi
app.add_handler(MessageHandler(filters.TEXT, handle_channel_message))

# Avvia il polling
await app.updater.start_polling()
```

### 2. Message Flow
```
@NicePriceDeals pubblica un messaggio
    ↓
Bot riceve l'update via polling
    ↓
handle_channel_message() viene chiamato
    ↓
Estrae testo e foto
    ↓
parse_message() processa il deal
    ↓
Deal viene aggiunto al buffer
    ↓
Coordinatore chiama /scrape
    ↓
Ritorna i deals dal buffer
    ↓
Coordinatore posta i deals
```

### 3. Buffer System
```python
self.deals_buffer = []  # Buffer per i deals

# Quando arriva un messaggio:
deal = parse_message(text, photo)
self.deals_buffer.append(deal)

# Quando il coordinatore chiama /scrape:
deals = self.deals_buffer.copy()
self.deals_buffer.clear()
return deals
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Worker UK v2                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Telegram Bot (Polling)                      │  │
│  │  - Monitora @NicePriceDeals in tempo reale   │  │
│  │  - Riceve messaggi non appena pubblicati     │  │
│  └──────────────────────────────────────────────┘  │
│           ↓                                         │
│  ┌──────────────────────────────────────────────┐  │
│  │  Message Handler                             │  │
│  │  - Estrae testo e foto                       │  │
│  │  - Parsa il deal                             │  │
│  │  - Aggiunge al buffer                        │  │
│  └──────────────────────────────────────────────┘  │
│           ↓                                         │
│  ┌──────────────────────────────────────────────┐  │
│  │  Deals Buffer                                │  │
│  │  - Accumula i deals estratti                 │  │
│  │  - Svuotato quando il coordinatore chiama    │  │
│  └──────────────────────────────────────────────┘  │
│           ↓                                         │
│  ┌──────────────────────────────────────────────┐  │
│  │  Flask HTTP Server (port 8001)               │  │
│  │  - GET /scrape → ritorna deals dal buffer    │  │
│  │  - GET /health → status                      │  │
│  │  - GET /stats → statistiche                  │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Key Changes

### 1. Message Handler
```python
async def handle_channel_message(self, update: Update, context) -> None:
    message = update.channel_post
    
    # Estrai foto
    if message.photo:
        photo = message.photo[-1]
        file = await self.bot.get_file(photo.file_id)
        photo_url = file.file_path
    
    # Parsa deal
    deal = self.parse_message(message.text, photo_url)
    
    # Aggiungi al buffer
    if deal:
        self.deals_buffer.append(deal)
```

### 2. Scrape Endpoint
```python
async def scrape_channel(self) -> List[Dict]:
    # Ritorna i deals dal buffer
    deals = self.deals_buffer.copy()
    self.deals_buffer.clear()
    return deals
```

### 3. Bot Updater Thread
```python
# Avvia il bot in un thread separato
bot_thread = threading.Thread(
    target=lambda: asyncio.run(run_bot()),
    daemon=True
)
bot_thread.start()

# Flask server continua a girare nel main thread
app.run(host='0.0.0.0', port=8001)
```

## Advantages

✅ **Funziona con canali pubblici** - Non ha bisogno di permessi di admin
✅ **Real-time** - Processa i messaggi non appena arrivano
✅ **Scalabile** - Può monitorare più canali
✅ **Robusto** - Polling automatico gestisce disconnessioni
✅ **Efficiente** - Buffer evita duplicati e perdite di dati

## Disadvantages

⚠️ **Polling** - Consuma più risorse rispetto a webhook
⚠️ **Latenza** - Dipende dall'intervallo di polling (default 1 secondo)
⚠️ **Storico** - Non legge i messaggi precedenti, solo i nuovi

## Testing

### 1. Verifica che il bot sia connesso
```bash
curl http://localhost:8001/health | jq
```

Dovrebbe mostrare:
```json
{
  "status": "healthy",
  "buffer_size": 0,
  "worker": "DealScout UK v2"
}
```

### 2. Pubblica un messaggio su @NicePriceDeals
Formato:
```
About £X.XX 💥 YY% Price drop
https://www.amazon.co.uk/dp/ASIN/...
Descrizione prodotto
#ad Price and promotions...
```

### 3. Chiama /scrape
```bash
curl http://localhost:8001/scrape | jq
```

Dovrebbe ritornare il deal con:
- ASIN estratto
- Titolo completo
- Prezzo e sconto
- Foto (se disponibile)

### 4. Verifica i logs
```bash
docker-compose logs worker-uk -f
```

Dovrebbe mostrare:
```
✅ Deal estratto: B0DS63GM2Z - £2.49 (50% off) - Ravensburger Disney Stitch Mini Memory Game
```

## Files Modified

✅ `workers/uk/worker_uk_v2.py` - Implementato message handler e buffer system

## Next Steps

1. Push su GitHub:
   ```bash
   git add workers/uk/worker_uk_v2.py
   git commit -m "feat: Implement real-time message handler with buffer system"
   git push
   ```

2. Rebuild su Northflk

3. Pubblica un messaggio su @NicePriceDeals per testare

4. Verifica che il deal appaia su @DealScoutUKBot con:
   - Immagine
   - Descrizione completa
   - ASIN valido
   - 5 bottoni di sharing

---

**Status**: Ready for deployment ✅
