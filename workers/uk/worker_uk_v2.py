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
        """Parsa il formato di NicePriceDeals"""
        try:
            if not text or len(text.strip()) < 10:
                return None

            # Estrai prezzo
            price_match = re.search(r'About\s+£([\d.]+)', text)
            if not price_match:
                return None
            
            current_price_pounds = float(price_match.group(1))
            current_price_pence = int(current_price_pounds * 100)

            # Estrai sconto
            discount_match = re.search(r'(\d+)%\s+Price drop', text)
            discount_pct = int(discount_match.group(1)) if discount_match else 0

            if discount_pct > 0:
                list_price_pence = int(current_price_pence / (1 - discount_pct / 100))
            else:
                list_price_pence = current_price_pence

            # Estrai URL Amazon
            url_match = re.search(r'https://www\.amazon\.co\.uk/[^\s\n]+', text)
            if not url_match:
                return None
            
            amazon_url = url_match.group(0)

            # Estrai ASIN
            asin = self.extract_asin_from_url(amazon_url)
            if not asin:
                return None

            # Evita duplicati
            if asin in self.processed_asins:
                return None

            # Estrai descrizione
            lines = text.split('\n')
            title = None
            
            for i, line in enumerate(lines):
                if 'amazon.co.uk' in line.lower():
                    if i > 0:
                        for j in range(i - 1, -1, -1):
                            candidate = lines[j].strip()
                            if (candidate and 
                                'About' not in candidate and 
                                'Price drop' not in candidate and
                                '£' not in candidate and
                                '%' not in candidate and
                                len(candidate) > 5):
                                title = candidate
                                break
                    break
            
            if not title:
                for line in lines:
                    line = line.strip()
                    if (line and 
                        'About' not in line and 
                        'Price drop' not in line and
                        'amazon' not in line.lower() and
                        '#ad' not in line and
                        'Price and promotions' not in line and
                        len(line) > 10):
                        title = line
                        break
            
            if title:
                title = re.sub(r'#ad.*', '', title).strip()
                title = re.sub(r'Price and promotions.*', '', title).strip()
            
            if not title or len(title) < 5:
                title = "Amazon Deal"

            # Costruisci deal
            deal = {
                'asin': asin,
                'title': title,
                'current_price_pence': current_price_pence,
                'list_price_pence': list_price_pence,
                'discount_pct': discount_pct,
                'amazon_url': amazon_url,
                'country': self.country,
                'channel_id': self.source_channel_id,
                'scraped_at': datetime.now().isoformat()
            }

            if self.validate_deal(deal):
                self.processed_asins.add(asin)
                logger.info(f"✅ Deal estratto: {asin} - £{current_price_pounds:.2f} ({discount_pct}% off)")
                return deal

        except Exception as e:
            logger.error(f"Errore parsing: {e}")
        
        return None

    def validate_deal(self, deal: Dict) -> bool:
        """Valida il deal"""
        required_fields = ['asin', 'title', 'current_price_pence']
        
        for field in required_fields:
            if not deal.get(field):
                return False
        
        asin = deal.get('asin', '')
        if not re.match(r'^[A-Z0-9]{10}$', asin):
            return False
        
        price = deal.get('current_price_pence', 0)
        if price <= 0 or price > 10000000:
            return False
        
        min_discount = int(os.getenv('MIN_DISCOUNT_PERCENT', 10))
        discount = deal.get('discount_pct', 0)
        if discount < min_discount:
            return False
        
        return True

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
                        logger.info(f"✅ Deal {deals_found} trovato: {deal['asin']} - {deal['title'][:50]}")
                
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
        
        # Max 2 deals
        deals = deals[:2]
        
        self.last_scrape_time = datetime.now()
        logger.info(f"✅ Scraping completato: {len(deals)} deals")
        
        return deals

    def build_affiliate_link(self, asin: str) -> str:
        """Link affiliato"""
        return f"https://amazon.co.uk/dp/{asin}?tag={self.affiliate_tag}"

    def build_sharing_buttons(self, deal: Dict, affiliate_link: str) -> InlineKeyboardMarkup:
        """Bottoni sharing"""
        share_text = f"🔥 {deal['title']}\n💰 £{deal['current_price_pence']/100:.2f} ({deal['discount_pct']}% off)\n🛒 {affiliate_link}"
        share_text_encoded = quote(share_text)
        
        keyboard = [
            [InlineKeyboardButton("🛒 VIEW ON AMAZON", url=affiliate_link)],
            [
                InlineKeyboardButton("💬 WhatsApp", url=f"https://wa.me/?text={share_text_encoded}"),
                InlineKeyboardButton("👍 Facebook", url=f"https://www.facebook.com/sharer/sharer.php?u={quote(affiliate_link)}")
            ],
            [
                InlineKeyboardButton("𝕏 Twitter", url=f"https://twitter.com/intent/tweet?text={share_text_encoded}&url={quote(affiliate_link)}"),
                InlineKeyboardButton("✈️ Telegram", url=f"https://t.me/share/url?url={quote(affiliate_link)}&text={share_text_encoded}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    def format_deal_message(self, deal: Dict, amazon_url: str) -> str:
        """Formato messaggio"""
        current_price_pounds = deal['current_price_pence'] / 100
        list_price_pounds = deal['list_price_pence'] / 100
        discount = deal['discount_pct']
        
        message = f"""🔥 **DEAL ALERT** 🔥

📦 {deal['title']}

💰 **Prezzo**: £{current_price_pounds:.2f}
~~£{list_price_pounds:.2f}~~

🎯 **Sconto**: -{discount}%
💾 **ASIN**: `{deal['asin']}`

{amazon_url}"""
        
        return message

    async def post_deal(self, deal: Dict) -> bool:
        """Posta deal"""
        try:
            affiliate_link = self.build_affiliate_link(deal['asin'])
            amazon_url = deal.get('amazon_url', affiliate_link)
            message = self.format_deal_message(deal, amazon_url)
            reply_markup = self.build_sharing_buttons(deal, affiliate_link)
            
            await self.bot.send_message(
                chat_id=self.publish_channel_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )
            logger.info(f"✅ Deal postato: {deal['asin']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Errore posting: {e}")
            return False

# Flask app
app = Flask(__name__)
worker = None

@app.route('/scrape', methods=['GET'])
def scrape_endpoint():
    """Endpoint scrape"""
    try:
        if not worker:
            return jsonify({'error': 'Worker non inizializzato'}), 500
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        deals = loop.run_until_complete(worker.scrape_channel())
        loop.close()
        
        logger.info(f"📊 Endpoint /scrape: {len(deals)} deals")
        return jsonify(deals)
        
    except Exception as e:
        logger.error(f"Errore /scrape: {e}")
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
