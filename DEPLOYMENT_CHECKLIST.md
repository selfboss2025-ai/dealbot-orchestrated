# ✅ Deployment Checklist

Checklist completa per il deploy del sistema.

## 🔍 Pre-Deployment

### Verifica Prerequisiti
- [ ] Python 3.9+ installato
- [ ] Docker installato (opzionale ma consigliato)
- [ ] Git installato
- [ ] Accesso a Telegram Bot API
- [ ] Accesso a VPS/Northflk (se deploy remoto)

### Verifica Configurazione
- [ ] Token bot UK: `7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w`
- [ ] Canale sorgente: @NicePriceDeals (ID: -1001303541715)
- [ ] Canale destinazione: @DealScoutUKBot (ID: -1001232723285)
- [ ] Bot è membro di @NicePriceDeals
- [ ] Bot è admin di @DealScoutUKBot

### Verifica Dipendenze
- [ ] `pip install -r requirements.txt` completato
- [ ] Nessun errore di installazione
- [ ] `python -c "import telegram"` OK

## 🧪 Test Locale

### Test Worker UK
- [ ] `cd workers/uk`
- [ ] `python worker_uk.py` avviato
- [ ] Nessun errore nei logs
- [ ] Bot connesso: `✅ Bot connesso: @dealscoutuk_bot`

### Test Endpoint
- [ ] `curl http://localhost:8001/health` → 200 OK
- [ ] `curl http://localhost:8001/scrape` → 200 OK
- [ ] `curl http://localhost:8001/stats` → 200 OK

### Test Scraping
- [ ] Almeno 1 deal trovato da @NicePriceDeals
- [ ] ASIN estratto correttamente
- [ ] Prezzi estratti correttamente
- [ ] Sconti calcolati correttamente

### Test Telegram
- [ ] Bot risponde a `/start`
- [ ] Bot è membro di @NicePriceDeals
- [ ] Bot può postare su @DealScoutUKBot

## 🐳 Test Docker

### Build Immagine
- [ ] `docker build -f workers/uk/Dockerfile -t dealscout-uk:latest .` OK
- [ ] Nessun errore di build
- [ ] Immagine creata: `docker images | grep dealscout-uk`

### Run Container
- [ ] `docker run -d --name worker-uk -p 8001:8001 --env-file workers/uk/.env dealscout-uk:latest` OK
- [ ] Container in esecuzione: `docker ps | grep worker-uk`
- [ ] Nessun errore nei logs: `docker logs worker-uk`

### Test Container
- [ ] `curl http://localhost:8001/health` → 200 OK
- [ ] `curl http://localhost:8001/scrape` → 200 OK
- [ ] `curl http://localhost:8001/stats` → 200 OK

### Cleanup
- [ ] `docker stop worker-uk`
- [ ] `docker rm worker-uk`

## 🚀 Deploy Locale (Sviluppo)

### Setup
- [ ] Clona repository
- [ ] Copia `.env.example` → `.env`
- [ ] Configura variabili ambiente
- [ ] Installa dipendenze: `pip install -r requirements.txt`

### Avvio
- [ ] Avvia worker UK: `cd workers/uk && python worker_uk.py`
- [ ] Verifica logs
- [ ] Test endpoint

### Monitoraggio
- [ ] Monitora logs in tempo reale
- [ ] Verifica health check periodicamente
- [ ] Controlla stats

## 🌐 Deploy Remoto (VPS)

### Preparazione Server
- [ ] SSH accesso al server
- [ ] Installa Docker: `curl -fsSL https://get.docker.com | sh`
- [ ] Aggiungi utente a docker group: `sudo usermod -aG docker $USER`
- [ ] Verifica Docker: `docker --version`

### Clona Repository
- [ ] `git clone <your-repo-url>`
- [ ] `cd dealbot-orchestrated`
- [ ] Verifica struttura: `ls -la workers/uk/`

### Deploy Worker UK
- [ ] Rendi script eseguibile: `chmod +x scripts/deploy-worker-uk.sh`
- [ ] Esegui deploy: `./scripts/deploy-worker-uk.sh`
- [ ] Verifica container: `docker ps | grep worker-uk`
- [ ] Verifica logs: `docker logs worker-uk -f`

### Test Remoto
- [ ] `curl http://your-vps-ip:8001/health`
- [ ] `curl http://your-vps-ip:8001/scrape`
- [ ] `curl http://your-vps-ip:8001/stats`

### Configurazione Firewall
- [ ] Apri porta 8001: `sudo ufw allow 8001`
- [ ] Verifica: `sudo ufw status`

## 🔗 Integrazione Coordinatore

### Configurazione Coordinatore
- [ ] Modifica `.env` coordinatore
- [ ] Aggiungi `WORKER_UK_URL=http://your-vps-ip:8001`
- [ ] Aggiungi `UK_CHANNEL=@DealScoutUKBot`
- [ ] Aggiungi `UK_CHANNEL_ID=-1001232723285`

### Test Coordinatore
- [ ] Avvia coordinatore: `python coordinator/main.py`
- [ ] Verifica connessione a worker UK
- [ ] Verifica logs per errori

### Test Integrazione
- [ ] Coordinatore chiama `/scrape` di worker UK
- [ ] Coordinatore riceve deals
- [ ] Coordinatore posta su @DealScoutUKBot

## 📊 Monitoraggio Post-Deploy

### Health Check
- [ ] Esegui health check: `curl http://localhost:8001/health`
- [ ] Verifica status: "healthy"
- [ ] Verifica timestamp aggiornato

### Scrape Test
- [ ] Esegui scrape: `curl http://localhost:8001/scrape`
- [ ] Verifica numero deals
- [ ] Verifica formato JSON

### Logs
- [ ] Monitora logs: `docker logs worker-uk -f`
- [ ] Nessun errore critico
- [ ] Nessun warning ricorrente

### Performance
- [ ] Response time < 1 secondo
- [ ] CPU usage < 50%
- [ ] Memory usage < 200MB

## 🔄 Operazioni Ricorrenti

### Giornaliero
- [ ] Verifica health check
- [ ] Controlla logs per errori
- [ ] Verifica numero deals processati

### Settimanale
- [ ] Analizza statistiche
- [ ] Verifica performance
- [ ] Controlla storage logs

### Mensile
- [ ] Aggiorna dipendenze: `pip install --upgrade -r requirements.txt`
- [ ] Pulisci logs vecchi
- [ ] Backup configurazione

## 🆘 Troubleshooting

### Worker Non Risponde
- [ ] Verifica container: `docker ps | grep worker-uk`
- [ ] Controlla logs: `docker logs worker-uk`
- [ ] Restart: `docker restart worker-uk`
- [ ] Verifica porta: `lsof -i :8001`

### Nessun Deal Trovato
- [ ] Verifica bot sia membro di @NicePriceDeals
- [ ] Controlla canale ha messaggi
- [ ] Aumenta SCRAPE_LOOKBACK_HOURS
- [ ] Verifica pattern parsing

### Errore Telegram
- [ ] Verifica token bot
- [ ] Verifica permessi canali
- [ ] Controlla rate limiting
- [ ] Verifica connessione internet

### Errore Porta
- [ ] Verifica porta libera: `lsof -i :8001`
- [ ] Cambia porta in `.env`
- [ ] Restart container

## 📝 Documentazione

### Leggi Prima di Deploy
- [ ] `QUICK_START.md` - Avvio rapido
- [ ] `SETUP_UK_WORKER.md` - Setup dettagliato
- [ ] `ARCHITECTURE.md` - Architettura

### Riferimento Durante Deploy
- [ ] `workers/uk/README.md` - Docs worker
- [ ] `README.md` - Overview generale

### Troubleshooting
- [ ] `IMPLEMENTATION_SUMMARY.md` - Riepilogo
- [ ] Logs: `docker logs worker-uk -f`

## 🎯 Milestone

### Milestone 1: Setup Locale ✅
- [x] Worker UK funzionante in locale
- [x] Endpoint testati
- [x] Scraping funzionante

### Milestone 2: Docker ✅
- [x] Immagine Docker creata
- [x] Container funzionante
- [x] Endpoint testati

### Milestone 3: Deploy Remoto ⏳
- [ ] Worker UK su VPS
- [ ] Endpoint raggiungibili
- [ ] Monitoraggio attivo

### Milestone 4: Coordinatore ⏳
- [ ] Coordinatore su Northflk
- [ ] Integrazione con worker UK
- [ ] Scheduling funzionante

### Milestone 5: Espansione ⏳
- [ ] Worker IT creato
- [ ] Worker FR creato
- [ ] Coordinatore orchestra tutti

## 🎉 Completamento

- [ ] Tutti i test passati
- [ ] Documentazione aggiornata
- [ ] Monitoraggio configurato
- [ ] Team informato
- [ ] Backup effettuato

## 📞 Contatti Emergenza

| Ruolo | Contatto | Note |
|-------|----------|------|
| DevOps | - | Deploy e infrastruttura |
| Developer | - | Debugging e fix |
| Admin | - | Accesso server |

## 📋 Note Finali

- Mantieni backup di `.env` e token
- Monitora logs regolarmente
- Aggiorna dipendenze mensilmente
- Testa nuove versioni in staging
- Documenta cambiamenti

---

**Data Inizio**: Gennaio 2026
**Status**: ⏳ In Preparazione
**Prossimo Step**: Eseguire checklist pre-deployment