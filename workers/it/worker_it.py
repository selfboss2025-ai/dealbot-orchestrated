#!/usr/bin/env python3
"""
Worker IT - Deal Scout Italia
Scraper specializzato per offerte Amazon IT da @salvatore_aranzulla_offerte
Legge i messaggi REALI dal canale usando Telethon
"""

import os
import re
import logging
import asyncio
import json
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import quote
from flask import Flask, jsonify
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telethon import TelegramClient

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DealWorkerIT:
    def __init__(self):
        self.bot_token = os.getenv('WORKER_IT_BOT_TOKEN', '7948123806:AAF3nwK3n_kpyzcq1YWL71M5jPccvZYJF2w')
        self.source_channel_id = int(os.getenv('SOURCE_CHANNEL_IT_ID', -1001771623915))
        self.publish_channel_id = int(os.getenv('PUBLISH_CHANNEL_IT_ID', -1001080585126))
        self.country = 'IT'
        self.affiliate_tag = 'srzone00-21'
        
        self.bot = Bot(token=self.bot_token)
        self.processed_asins = set()
        self.last_scrape_time = None
        self.last_message_id = 0
        
        # Telethon client
        self.api_id = int(os.getenv('TELEGRAM_API_ID', '0'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH', '')
        self.phone = os.getenv('TELEGRAM_PHONE', '')
        
        self.telethon_client = None
        self.telethon_connected = False
        
        logger.info(f"🤖 Worker IT inizializzato")
        logger.info(f"📺 Canale sorgente: {self.source_channel_id}")
        logger.info(f"📤 Canale pubblicazione: {self.publish_channel_id}")
        logger.info(f"Telethon API ID: {self.api_id}, Phone: {self.phone}")

    async def init_telethon(self):
        """Inizializza Telethon con sessione pre-autenticata"""
        if self.telethon_connected:
            return
        
        try:
            if not self.api_id or self.api_id == 0:
                logger.warning("Telethon non configurato (API_ID = 0)")
                return
            
            logger.info("🔗 Inizializzazione Telethon IT con sessione esistente...")
            logger.info(f"API ID: {self.api_id}, API Hash: {self.api_hash[:10]}..., Phone: {self.phone}")
            
            session_path = '/tmp/session_it'
            logger.info(f"Session path: {session_path}")
            
            # Verifica se il file di sessione esiste
            import os
            session_file = f"{session_path}.session"
            if os.path.exists(session_file):
                logger.info(f"✅ File sessione IT trovato: {session_file}")
            else:
                logger.error(f"❌ File sessione IT NON trovato: {session_file}")
                self.telethon_connected = False
                return
            
            self.telethon_client = TelegramClient(session_path, self.api_id, self.api_hash)
            
            # Connetti usando la sessione esistente (non richiede verifica)
            logger.info("Connessione a Telegram IT...")
            await self.telethon_client.connect()
            logger.info("Connessione stabilita, verifica autorizzazione...")
            
            if await self.telethon_client.is_user_authorized():
                self.telethon_connected = True
                me = await self.telethon_client.get_me()
                logger.info(f"✅ Telethon IT connesso con successo - User: {me.first_name} (@{me.username})")
            else:
                logger.error("❌ Sessione IT non autorizzata")
                self.telethon_connected = False
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Telethon IT: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.telethon_connected = False

    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """Estrae ASIN da URL Amazon"""
        if not url:
            return None
            
        url_clean = url.split('?')[0].split('&')[0]
        
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_clean)
            if match:
                asin = match.group(1)
                if re.match(r'^[A-Z0-9]{10}$', asin):
                    return asin
        
        return None

    def parse_message(self, text: str) -> Optional[Dict]:
        """Copia il messaggio e sostituisce solo il tag affiliato"""
        try:
            if not text or len(text.strip()) < 10:
                return None

            # Cerca URL Amazon IT (formato lungo o corto)
            url_match = re.search(r'https://(?:www\.)?amazon\.it/[^\s\n]+', text)
            if not url_match:
                # Cerca link corti amzn.to o amzn.eu
                url_match = re.search(r'https://amzn\.(?:to|eu)/[^\s\n]+', text)
            
            if not url_match:
                return None
            
            original_url = url_match.group(0)
            
            # Se è un link corto, espandilo per ottenere l'ASIN
            if 'amzn.to' in original_url or 'amzn.eu' in original_url:
                try:
                    import requests
                    # Segui il redirect per ottenere l'URL completo
                    response = requests.head(original_url, allow_redirects=True, timeout=5)
                    expanded_url = response.url
                    
                    # Estrai ASIN dall'URL espanso
                    asin = self.extract_asin_from_url(expanded_url)
                    if not asin:
                        logger.debug(f"ASIN non trovato dopo espansione: {expanded_url}")
                        return None
                    
                    # Costruisci il nuovo URL con il nostro tag
                    new_url = f"https://www.amazon.it/dp/{asin}?tag={self.affiliate_tag}"
                    
                except Exception as e:
                    logger.error(f"Errore espansione link corto {original_url}: {e}")
                    return None
            else:
                # URL lungo - estrai ASIN direttamente
                asin = self.extract_asin_from_url(original_url)
                if not asin:
                    return None
                
                # Sostituisci il tag affiliato nell'URL
                new_url = re.sub(r'[?&]tag=[^&\s]+', '', original_url)
                if '?' in new_url:
                    new_url = f"{new_url}&tag={self.affiliate_tag}"
                else:
                    new_url = f"{new_url}?tag={self.affiliate_tag}"

            # Evita duplicati
            if asin in self.processed_asins:
                return None

            # Sostituisci l'URL nel testo
            new_text = text.replace(original_url, new_url)
            
            # Sostituisci anche il link affiliate disclosure
            new_text = new_text.replace(
                '#affiliate: https://tecnologia.libero.it/contatti',
                '#affiliate: https://gomining.uk/amzn'
            )

            # Costruisci deal con il messaggio completo
            deal = {
                'asin': asin,
                'message_text': new_text,
                'original_url': original_url,
                'affiliate_url': new_url,
                'country': self.country,
                'scraped_at': datetime.now().isoformat()
            }

            self.processed_asins.add(asin)
            logger.info(f"✅ Messaggio IT copiato: {asin} (da {original_url})")
            return deal

        except Exception as e:
            logger.error(f"❌ Errore parsing IT: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return None

    async def scrape_channel_telethon(self) -> List[Dict]:
        """Scrape con Telethon"""
        deals = []
        
        try:
            if not self.telethon_connected or not self.telethon_client:
                logger.error("❌ Telethon IT non connesso - impossibile fare scraping")
                logger.error(f"telethon_connected: {self.telethon_connected}, telethon_client: {self.telethon_client is not None}")
                return deals
            
            logger.info("🔍 Scraping IT con Telethon...")
            
            try:
                logger.info(f"Lettura messaggi da canale IT {self.source_channel_id}...")
                message_count = 0
                deals_found = 0
                
                async for message in self.telethon_client.iter_messages(self.source_channel_id, limit=50):
                    message_count += 1
                    
                    if message_count <= 3:
                        logger.info(f"Messaggio IT {message_count}: {message.text[:100] if message.text else 'NO TEXT'}...")
                    
                    if not message.text:
                        continue
                    
                    deal = self.parse_message(message.text)
                    if deal:
                        deals.append(deal)
                        deals_found += 1
                        logger.info(f"✅ Deal IT {deals_found} trovato: {deal['asin']}")
                
                logger.info(f"✅ Telethon IT: {message_count} messaggi letti, {len(deals)} deals trovati")
                
            except Exception as e:
                logger.error(f"❌ Errore durante lettura messaggi IT: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        except Exception as e:
            logger.error(f"❌ Errore Telethon IT: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return deals

    async def scrape_channel(self) -> List[Dict]:
        """Scrape - Solo Telethon"""
        logger.info("🔍 Scraping IT...")
        
        # Inizializza Telethon al primo scrape
        if not self.telethon_connected:
            await self.init_telethon()
        
        # Scrape con Telethon
        deals = await self.scrape_channel_telethon()
        
        # Max 5 deals per ciclo
        deals = deals[:5]
        
        self.last_scrape_time = datetime.now()
        logger.info(f"✅ Scraping IT completato: {len(deals)} deals")
        
        return deals

# Flask app
app = Flask(__name__)
worker = None

@app.route('/scrape', methods=['GET'])
def scrape_endpoint():
    """Endpoint scrape"""
    try:
        if not worker:
            return jsonify({'error': 'Worker IT non inizializzato'}), 500
        
        # Usa l'event loop esistente se disponibile, altrimenti creane uno nuovo
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        deals = loop.run_until_complete(worker.scrape_channel())
        
        logger.info(f"📊 Endpoint /scrape IT: {len(deals)} deals")
        return jsonify(deals)
        
    except Exception as e:
        logger.error(f"Errore /scrape IT: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'worker': 'DealScout IT',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/stats', methods=['GET'])
def stats():
    """Stats"""
    return jsonify({
        'processed_asins': len(worker.processed_asins) if worker else 0,
        'last_scrape_time': worker.last_scrape_time.isoformat() if worker and worker.last_scrape_time else None,
    })

def main():
    global worker
    
    try:
        worker = DealWorkerIT()
        
        logger.info("🔗 Test connessione bot IT...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot_info = loop.run_until_complete(worker.bot.get_me())
        loop.close()
        
        logger.info(f"✅ Bot IT connesso: @{bot_info.username}")
        logger.info(f"🌐 Server HTTP IT su 0.0.0.0:8002")
        
        app.run(
            host='0.0.0.0',
            port=8002,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Errore avvio worker IT: {e}")
        raise

if __name__ == "__main__":
    main()
