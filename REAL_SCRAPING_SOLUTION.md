# ✅ Real Scraping Solution - Legge i Messaggi REALI

## I Veri Problemi Identificati

### 1. ❌ Posta Sempre gli Stessi 2 Prodotti
**Causa**: Usa i messaggi di test, non legge il canale reale

### 2. ❌ Uno ha Link Corretto, l'Altro No
**Causa**: B0ABCDEF12 è un ASIN fake nei test messages

### 3. ❌ Non Legge le Nuove Offerte
**Causa**: Non sta leggendo da @NicePriceDeals

### 4. ✅ Per le Immagini
**Soluzione**: Includi il link Amazon nel messaggio - Telegram mostra l'immagine automaticamente!

## La Soluzione Implementata

### 1. ✅ Telethon per Scraping Reale
```python
async def scrape_channel_telethon(self) -> List[Dict]:
    """Legge i messaggi REALI da @NicePriceDeals"""
    client = TelegramClient('session_uk', api_id, api_hash)
    
    async for message in client.iter_messages(source_channel_id, limit=50):
        if message.text:
            deal = self.parse_message(message.text)
            if deal:
                deals.append(deal)
```

### 2. ✅ Database Locale per Tracciare i Deals
```python
self.db_file = '/tmp/worker_uk_deals.json'

# Salva i deals già processati
{
    'processed_asins': ['B0DS63GM2Z', 'B0ABCDEF12', ...],
    'last_message_id': 12345,
    'last_updated': '2026-01-02T14:28:31'
}
```

### 3. ✅ Link Amazon nel Messaggio per Immagini
```python
message = f"""🔥 **DEAL ALERT** 🔥

📦 {deal['title']}

💰 **Prezzo**: £{current_price_pounds:.2f}
~~£{list_price_pounds:.2f}~~

🎯 **Sconto**: -{discount}%
💾 **ASIN**: `{deal['asin']}`

{amazon_url}  # ← Telegram mostra l'immagine automaticamente!
```

## Flusso Nuovo

```
1. Worker avvia
   ↓
2. Carica i deals già processati dal database
   ↓
3. Legge i messaggi REALI da @NicePriceDeals con Telethon
   ↓
4. Per ogni messaggio:
   - Estrai testo
   - Parsa prezzo, sconto, ASIN, descrizione
   - Valida il deal
   ↓
5. Se nuovo (non in database):
   - Salva nel database
   - Posta su @DealScoutUKBot
   ↓
6. Messaggio include:
   - Descrizione completa
   - Prezzo e sconto
   - Link Amazon (mostra immagine)
   - 5 bottoni di sharing
```

## Configurazione Telethon

Per usare Telethon, aggiungi a `.env`:

```bash
# Telethon Configuration
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
```

### Come Ottenere le Credenziali

1. Vai a https://my.telegram.org/apps
2. Accedi con il tuo account Telegram
3. Crea una nuova app
4. Copia API ID e API Hash
5. Usa il tuo numero di telefono Telegram

## Comportamento Atteso

✅ **Legge i messaggi REALI** da @NicePriceDeals
✅ **Posta NUOVE offerte** continuamente
✅ **Non ripete** i deals già postati (database locale)
✅ **ASIN sempre validi** (solo da messaggi reali)
✅ **Immagini automatiche** (link Amazon nel messaggio)
✅ **5 bottoni di sharing** funzionanti

## Vantaggi

✅ **Real-time** - Legge i messaggi non appena arrivano
✅ **Nessun duplicato** - Database traccia i deals
✅ **Immagini automatiche** - Telegram le mostra dal link
✅ **Scalabile** - Può leggere più canali
✅ **Affidabile** - Telethon è stabile

## Files Modified

✅ `requirements.txt` - Aggiunto telethon
✅ `workers/uk/worker_uk_v2.py` - Implementato Telethon scraping

## Deploy

```bash
git add requirements.txt workers/uk/worker_uk_v2.py
git commit -m "feat: Implement real Telegram scraping with Telethon"
git push
```

Rebuild su Northflk e configura le credenziali Telethon in `.env`.

## Se Telethon Non è Configurato

Se non configuri Telethon:
- Il worker non troverà deals
- Non posterà nulla
- Aspetta la configurazione

## Prossimi Passi

1. Ottieni le credenziali Telethon da https://my.telegram.org/apps
2. Aggiungi a `.env` su Northflk:
   ```
   TELEGRAM_API_ID=your_id
   TELEGRAM_API_HASH=your_hash
   TELEGRAM_PHONE=+1234567890
   ```
3. Rebuild su Northflk
4. Il worker inizierà a leggere i messaggi reali

---

**Questo è il vero fix. Leggerà i messaggi reali da @NicePriceDeals.**
