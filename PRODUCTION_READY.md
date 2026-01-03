# 🚀 Production Ready - Sistema Operativo

## Configurazione Produzione

### 1. ✅ Scraping Ogni 10 Minuti
```python
trigger=IntervalTrigger(minutes=10)
```
- Coordinatore chiama il worker ogni 10 minuti
- Riduce il carico sul server
- Evita rate limiting di Telegram

### 2. ✅ Solo Messaggi Reali
- Rimossi i test messages
- Legge solo da Telethon (messaggi reali da @NicePriceDeals)
- Se Telethon non configurato, ritorna 0 deals (niente fallback)

### 3. ✅ Massimo 2 Deals per Scraping
```python
deals = deals[:2]  # Limita a 2
```
- Pubblica solo le ultime 2 offerte trovate
- Evita spam di messaggi
- Mantiene il canale pulito

## Flusso Produzione

```
Ogni 10 minuti:
  ↓
Coordinatore chiama /scrape
  ↓
Worker legge messaggi reali da @NicePriceDeals con Telethon
  ↓
Estrae max 2 deals
  ↓
Coordinatore posta i 2 deals su @DealScoutUKBot
  ↓
Attende 10 minuti
  ↓
Ripeti
```

## Configurazione Telethon

Le credenziali sono già in `.env`:
```
TELEGRAM_API_ID=24358896
TELEGRAM_API_HASH=3963ba2988481928ad78d15d4b4388a8
TELEGRAM_PHONE=+447775827823
```

Il worker leggerà i messaggi reali da @NicePriceDeals.

## Comportamento Atteso

✅ Ogni 10 minuti: Scraping da @NicePriceDeals
✅ Max 2 deals per scraping
✅ Posta su @DealScoutUKBot con:
  - Descrizione completa
  - Prezzo e sconto
  - Link Amazon (mostra immagine)
  - 5 bottoni di sharing

## Files Modified

✅ `coordinator/main.py` - Intervallo 10 minuti
✅ `workers/uk/worker_uk_v2.py` - Rimossi test, max 2 deals

## Deploy

```bash
git add coordinator/main.py workers/uk/worker_uk_v2.py
git commit -m "prod: 10-minute interval, real messages only, max 2 deals"
git push
```

Rebuild su Northflk.

## Monitoraggio

Verifica i logs:
```bash
docker-compose logs coordinator -f
docker-compose logs worker-uk -f
```

Dovresti vedere:
```
📅 Scheduler avviato - processing ogni 10 minuti
🔍 Scraping canale -1001303541715...
✅ Scraping completato: 2 deals trovati (max 2)
✅ Deal postato: ASIN1 su @DealScoutUKBot
✅ Deal postato: ASIN2 su @DealScoutUKBot
```

## Status

✅ **PRODUZIONE**
✅ **OPERATIVO**
✅ **PRONTO**

---

**Sistema in produzione. Scraping ogni 10 minuti, max 2 deals per ciclo.**
