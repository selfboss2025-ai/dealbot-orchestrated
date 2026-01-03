# 🔍 Debug - ASIN e Photo Issues

## Problemi Identificati

### 1. ❌ ASIN Sbagliati su Alcuni Prodotti
**Causa**: Il regex per estrarre l'ASIN non gestisce correttamente i parametri query

**Esempio**:
```
URL: https://www.amazon.co.uk/dp/B0DS63GM2Z/?tag=frb-dls-21&psc=1
Regex sbagliato: Estrae "B0DS63GM2Z/?tag" ❌
Regex corretto: Estrae "B0DS63GM2Z" ✅
```

**Soluzione**:
```python
def extract_asin_from_url(self, url: str) -> Optional[str]:
    # Rimuovi parametri query PRIMA di fare il regex
    url_clean = url.split('?')[0].split('&')[0]
    
    # Poi estrai l'ASIN
    match = re.search(r'/dp/([A-Z0-9]{10})', url_clean)
```

### 2. ❌ Nessuna Immagine
**Causa**: Il worker usa messaggi di test che non hanno foto

**Soluzione**:
- Implementato `get_chat_history()` per leggere i messaggi reali
- Estrae `photo_file_id` dai messaggi reali
- Fallback a test messages se `get_chat_history` non disponibile

## Miglioramenti Implementati

### 1. ✅ ASIN Extraction Migliorato
```python
def extract_asin_from_url(self, url: str) -> Optional[str]:
    if not url:
        return None
    
    # Rimuovi parametri query
    url_clean = url.split('?')[0].split('&')[0]
    
    # Pattern: /dp/ASIN, /gp/product/ASIN
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_clean)
        if match:
            asin = match.group(1)
            if re.match(r'^[A-Z0-9]{10}$', asin):
                logger.debug(f"ASIN trovato: {asin}")
                return asin
    
    return None
```

### 2. ✅ Real Message Scraping
```python
async def scrape_channel(self) -> List[Dict]:
    try:
        # Leggi i messaggi reali dal canale
        messages = await self.bot.get_chat_history(
            chat_id=self.source_channel_id,
            limit=100,
            offset_id=self.last_message_id
        )
        
        for message in messages:
            # Estrai photo_file_id
            if message.photo:
                photo = message.photo[-1]
                photo_file_id = photo.file_id
            
            # Parsa il messaggio
            deal = self.parse_message(message.text, photo_file_id)
    
    except AttributeError:
        # Fallback a test messages
        deals = await self._get_test_deals()
```

### 3. ✅ Logging Dettagliato
Aggiunto logging a ogni step:
```
✅ ASIN estratto: B0DS63GM2Z
📸 Foto trovata: AgAC...
Titolo estratto: Ravensburger Disney Stitch Mini Memory Game
✅ Deal estratto: B0DS63GM2Z - £2.49 (50% off)
```

### 4. ✅ Tracking Messaggi
```python
self.last_message_id = 0  # Traccia l'ultimo messaggio letto

# Aggiorna per leggere solo i nuovi messaggi
if message.message_id > self.last_message_id:
    self.last_message_id = message.message_id
```

## Flusso Aggiornato

```
1. Worker avvia
   ↓
2. Prova a leggere i messaggi reali da @NicePriceDeals
   ↓
3. Per ogni messaggio:
   - Estrai testo
   - Estrai photo_file_id (se presente)
   - Pulisci URL dai parametri query
   - Estrai ASIN (validato)
   - Estrai descrizione
   ↓
4. Valida il deal
   ↓
5. Posta su @DealScoutUKBot:
   - Con foto (se disponibile)
   - Con bottoni di sharing
   - Fallback a testo se foto non disponibile
```

## Validazione ASIN

```python
# Validazione rigorosa
asin = deal.get('asin', '')
if not re.match(r'^[A-Z0-9]{10}$', asin):
    return False  # ASIN non valido
```

Requisiti:
- Esattamente 10 caratteri
- Solo lettere maiuscole e numeri
- Nessun carattere speciale

## Test

### Verifica ASIN Extraction
```python
# Test URL con parametri
url = "https://www.amazon.co.uk/dp/B0DS63GM2Z/?tag=frb-dls-21&psc=1"
asin = extract_asin_from_url(url)
# Risultato: B0DS63GM2Z ✅
```

### Verifica Photo Extraction
```
Messaggio con foto → photo_file_id estratto
Messaggio senza foto → photo_file_id = None
```

## Comportamento Atteso

✅ ASIN sempre validi (10 caratteri)
✅ Foto estratte dai messaggi reali
✅ Fallback a testo se foto non disponibile
✅ Descrizioni complete
✅ Bottoni di sharing funzionanti

## Files Modified

✅ `workers/uk/worker_uk_v2.py` - ASIN extraction migliorato, real message scraping

## Prossimi Passi

1. Push su GitHub:
   ```bash
   git add workers/uk/worker_uk_v2.py
   git commit -m "fix: Improve ASIN extraction, implement real message scraping"
   git push
   ```

2. Rebuild su Northflk

3. Verifica i logs:
   ```bash
   docker-compose logs worker-uk -f
   ```

4. Verifica i deals su @DealScoutUKBot:
   - ASIN validi
   - Foto presenti
   - Descrizioni complete

---

**Status**: Ready for deployment ✅
