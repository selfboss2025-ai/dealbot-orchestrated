# 🔍 Telethon Debug - Diagnostica Dettagliata

## Problema

Il worker sta ancora usando i messaggi di test, non sta leggendo da Telethon.

## Soluzione

Ho aggiunto **logging dettagliato** per capire cosa sta succedendo:

```python
logger.info(f"API_ID: {self.api_id}")
logger.info(f"API_HASH: {self.api_hash[:10]}...")
logger.info(f"PHONE: {self.phone}")
logger.info("🔗 Connessione a Telegram...")
logger.info(f"📖 Lettura messaggi da canale {self.source_channel_id}...")
logger.info(f"✅ Letti {message_count} messaggi, {len(deals)} deals trovati")
```

## Prossimi Passi

1. **Push su GitHub**:
   ```bash
   git add workers/uk/worker_uk_v2.py
   git commit -m "debug: Add detailed Telethon logging"
   git push
   ```

2. **Rebuild su Northflk**

3. **Verifica i logs**:
   ```bash
   docker-compose logs worker-uk -f
   ```

Dovresti vedere uno di questi scenari:

### Scenario 1: ✅ Funziona
```
API_ID: 24358896
API_HASH: 3963ba29...
PHONE: +447775827823
🔗 Connessione a Telegram...
✅ Connesso a Telegram
📖 Lettura messaggi da canale -1001303541715...
✅ Letti 50 messaggi, X deals trovati
```

### Scenario 2: ❌ Credenziali Non Configurate
```
❌ Credenziali Telethon non configurate (API_ID = 0)
```
**Soluzione**: Verifica che `.env` abbia le credenziali

### Scenario 3: ❌ Errore di Connessione
```
❌ Errore durante lettura messaggi: ...
```
**Soluzione**: Potrebbe richiedere verifica 2FA

### Scenario 4: ❌ Errore di Autenticazione
```
❌ Errore Telethon: Invalid phone number
```
**Soluzione**: Verifica il numero di telefono

## Se Telethon Richiede 2FA

Telethon potrebbe richiedere una verifica la prima volta:
1. Controlla i logs per il codice di verifica
2. Potrebbe inviare un SMS al numero di telefono
3. Inserisci il codice quando richiesto

## Verifica Credenziali

Assicurati che `.env` abbia:
```
TELEGRAM_API_ID=24358896
TELEGRAM_API_HASH=3963ba2988481928ad78d15d4b4388a8
TELEGRAM_PHONE=+447775827823
```

## Se Ancora Non Funziona

Se i logs mostrano errori, condividi l'output completo e farò il debug.

---

**Rebuild e verifica i logs per capire cosa sta succedendo.**
