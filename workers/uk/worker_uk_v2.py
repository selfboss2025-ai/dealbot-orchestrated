#!/usr/bin/env python3
"""
Worker UK - Deal Scout v2
Scraper specializzato per offerte Amazon UK da @NicePriceDeals
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

class DealWorkerUK:
    def __init__(self):
        self.bot_token = os.getenv('WORKER_BOT_TOKEN', '7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w')
        self.source_channel_id = int(os.getenv('SOURCE_CHANNEL_ID', -1001303541715))
        self.publish_channel_id = int(os.getenv('PUBLISH_CHANNEL_ID', -1001232723285))
        self.country = 'UK'
        self.affiliate_tag = 'ukbestdeal02-21'
        
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
        
        logger.info(f"🤖 Worker UK v2 inizializzato")
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
            
            logger.info("🔗 Inizializzazione Telethon con sessione esistente...")
            logger.info(f"API ID: {self.api_id}, API Hash: {self.api_hash[:10]}..., Phone: {self.phone}")
            
            session_path = '/tmp/session_uk'
            logger.info(f"Session path: {session_path}")
            
            # Verifica se il file di sessione esiste
            import os
            session_file = f"{session_path}.session"
            if os.path.exists(session_file):
                logger.info(f"✅ File sessione trovato: {session_file}")
            else:
                logger.error(f"❌ File sessione NON trovato: {session_file}")
                self.telethon_connected = False
                return
            
            self.telethon_client = TelegramClient(session_path, self.api_id, self.api_hash)
            
            # Connetti usando la sessione esistente (non richiede verifica)
            logger.info("Connessione a Telegram...")
            await self.telethon_client.connect()
            logger.info("Connessione stabilita, verifica autorizzazione...")
            
            if await self.telethon_client.is_user_authorized():
                self.telethon_connected = True
                me = await self.telethon_client.get_me()
                logger.info(f"✅ Telethon connesso con successo - User: {me.first_name} (@{me.username})")
            else:
                logger.error("❌ Sessione non autorizzata")
                self.telethon_connected = False
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Telethon: {e}")
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

            # Cerca URL Amazon
            url_match = re.search(r'https://www\.amazon\.co\.uk/[^\s\n]+', text)
            if not url_match:
                return None
            
            original_url = url_match.group(0)
            
            # Estrai ASIN
            asin = self.extract_asin_from_url(original_url)
            if not asin:
                return None

            # Evita duplicati
            if asin in self.processed_asins:
                return None

            # Sostituisci il tag affiliato nell'URL
            # Rimuovi il vecchio tag e aggiungi il nostro
            new_url = re.sub(r'[?&]tag=[^&\s]+', '', original_url)
            if '?' in new_url:
                new_url = f"{new_url}&tag={self.affiliate_tag}"
            else:
                new_url = f"{new_url}?tag={self.affiliate_tag}"
            
            # Sostituisci l'URL nel testo
            new_text = text.replace(original_url, new_url)

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
            logger.info(f"✅ Messaggio copiato: {asin}")
            return deal

        except Exception as e:
            logger.error(f"❌ Errore parsing: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return None

    async def scrape_channel_telethon(self) -> List[Dict]:
        """Scrape con Telethon"""
        deals = []
        
        try:
            if not self.telethon_connected or not self.telethon_client:
                logger.error("❌ Telethon non connesso - impossibile fare scraping")
                logger.error(f"telethon_connected: {self.telethon_connected}, telethon_client: {self.telethon_client is not None}")
                return deals
            
            logger.info("🔍 Scraping con Telethon...")
            
            try:
                logger.info(f"Lettura messaggi da canale {self.source_channel_id}...")
                message_count = 0
                deals_found = 0
                
                async for message in self.telethon_client.iter_messages(self.source_channel_id, limit=50):
                    message_count += 1
                    
                    if message_count <= 3:
                        logger.info(f"Messaggio {message_count}: {message.text[:100] if message.text else 'NO TEXT'}...")
                    
                    if not message.text:
                        continue
                    
                    deal = self.parse_message(message.text)
                    if deal:
                        deals.append(deal)
                        deals_found += 1
                        logger.info(f"✅ Deal {deals_found} trovato: {deal['asin']}")
                
                logger.info(f"✅ Telethon: {message_count} messaggi letti, {len(deals)} deals trovati")
                
            except Exception as e:
                logger.error(f"❌ Errore durante lettura messaggi: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        except Exception as e:
            logger.error(f"❌ Errore Telethon: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return deals

    async def scrape_channel(self) -> List[Dict]:
        """Scrape - Solo Telethon"""
        logger.info("🔍 Scraping...")
        
        # Inizializza Telethon al primo scrape
        if not self.telethon_connected:
            await self.init_telethon()
        
        # Scrape con Telethon
        deals = await self.scrape_channel_telethon()
        
        # Max 5 deals per ciclo
        deals = deals[:5]
        
        self.last_scrape_time = datetime.now()
        logger.info(f"✅ Scraping completato: {len(deals)} deals")
        
        return deals

    async def post_deal(self, deal: Dict) -> bool:
        """Posta deal con messaggio originale"""
        try:
            message_text = deal['message_text']
            affiliate_url = deal['affiliate_url']
            
            # Aggiungi bottoni di sharing
            reply_markup = self.build_sharing_buttons_simple(affiliate_url)
            
            await self.bot.send_message(
                chat_id=self.publish_channel_id,
                text=message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )
            logger.info(f"✅ Deal postato: {deal['asin']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore posting: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def build_sharing_buttons_simple(self, affiliate_link: str) -> InlineKeyboardMarkup:
        """Bottoni sharing semplificati"""
        share_text = f"🔥 Amazon Deal UK\n🛒 {affiliate_link}"
        share_text_encoded = quote(share_text)
        
        keyboard = [
            [InlineKeyboardButton("🛒 VIEW ON AMAZON", url=affiliate_link)],
            [
                InlineKeyboardButton("💬 WhatsApp", url=f"https://wa.me/?text={share_text_encoded}"),
                InlineKeyboardButton("👍 Facebook", url=f"https://www.facebook.com/sharer/sharer.php?u={quote(affiliate_link)}")
            ],
            [
                InlineKeyboardButton("𝕏 Twitter", url=f"https://twitter.com/intent/tweet?text={share_text_encoded}"),
                InlineKeyboardButton("✈️ Telegram", url=f"https://t.me/share/url?url={quote(affiliate_link)}&text={share_text_encoded}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

# Flask app
app = Flask(__name__)
worker = None

@app.route('/scrape', methods=['GET'])
def scrape_endpoint():
    """Endpoint scrape"""
    try:
        if not worker:
            return jsonify({'error': 'Worker non inizializzato'}), 500
        
        # Usa l'event loop esistente se disponibile, altrimenti creane uno nuovo
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
        
    except Exception as e:
        logger.error(f"Errore /scrape: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'worker': 'DealScout UK v2',
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
        worker = DealWorkerUK()
        
        logger.info("🔗 Test connessione bot...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot_info = loop.run_until_complete(worker.bot.get_me())
        loop.close()
        
        logger.info(f"✅ Bot connesso: @{bot_info.username}")
        logger.info(f"🌐 Server HTTP su 0.0.0.0:8001")
        
        app.run(
            host='0.0.0.0',
            port=8001,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Errore avvio: {e}")
        raise

if __name__ == "__main__":
    main()
