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
from telethon.errors import SessionPasswordNeededError

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
        
        logger.info(f"🤖 Worker UK v2 inizializzato")
        logger.info(f"📺 Canale sorgente: {self.source_channel_id}")
        logger.info(f"📤 Canale pubblicazione: {self.publish_channel_id}")

    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """Estrae ASIN da URL Amazon - supporta vari formati"""
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
                # Valida che sia un ASIN valido (10 caratteri alfanumerici)
                if re.match(r'^[A-Z0-9]{10}$', asin):
                    logger.debug(f"ASIN trovato: {asin} da URL: {url}")
                    return asin
        
        logger.debug(f"ASIN non trovato in URL: {url}")
        return None

    def parse_message(self, text: str) -> Optional[Dict]:
        """
        Parsa il formato specifico di NicePriceDeals:
        About £X.XX (prezzo)
        YY% Price drop (sconto)
        https://www.amazon.co.uk/dp/ASIN/... (link)
        Descrizione prodotto
        #ad
        """
        try:
            if not text or len(text.strip()) < 10:
                logger.debug("Messaggio troppo corto")
                return None

            logger.debug(f"Parsing messaggio: {text[:100]}...")

            # Estrai prezzo (£X.XX)
            price_match = re.search(r'About\s+£([\d.]+)', text)
            if not price_match:
                logger.debug("Prezzo non trovato")
                return None
            
            current_price_pounds = float(price_match.group(1))
            current_price_pence = int(current_price_pounds * 100)
            logger.debug(f"Prezzo trovato: £{current_price_pounds}")

            # Estrai sconto (YY%)
            discount_match = re.search(r'(\d+)%\s+Price drop', text)
            discount_pct = int(discount_match.group(1)) if discount_match else 0
            logger.debug(f"Sconto trovato: {discount_pct}%")

            # Calcola prezzo originale da sconto
            if discount_pct > 0:
                list_price_pence = int(current_price_pence / (1 - discount_pct / 100))
            else:
                list_price_pence = current_price_pence

            # Estrai URL Amazon
            url_match = re.search(r'https://www\.amazon\.co\.uk/[^\s\n]+', text)
            if not url_match:
                logger.debug("URL Amazon non trovato")
                return None
            
            amazon_url = url_match.group(0)
            logger.debug(f"URL trovato: {amazon_url}")

            # Estrai ASIN
            asin = self.extract_asin_from_url(amazon_url)
            if not asin:
                logger.warning(f"ASIN non estratto correttamente da: {amazon_url}")
                return None

            logger.info(f"✅ ASIN estratto: {asin}")

            # Evita duplicati
            if asin in self.processed_asins:
                logger.debug(f"ASIN già processato: {asin}")
                return None

            # Estrai descrizione
            lines = text.split('\n')
            title = None
            
            # Cerca la riga con il link Amazon
            for i, line in enumerate(lines):
                if 'amazon.co.uk' in line.lower():
                    # La descrizione è nella riga precedente
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
                                logger.debug(f"Titolo trovato: {title}")
                                break
                    break
            
            # Se non trovato, prova a cercare il testo più lungo
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
            
            # Pulisci titolo
            if title:
                title = re.sub(r'#ad.*', '', title).strip()
                title = re.sub(r'Price and promotions.*', '', title).strip()
            
            if not title or len(title) < 5:
                title = "Amazon Deal"

            logger.info(f"Titolo estratto: {title}")

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

            # Valida deal
            if self.validate_deal(deal):
                self.processed_asins.add(asin)
                logger.info(f"✅ Deal estratto: {asin} - £{current_price_pounds:.2f} ({discount_pct}% off) - {title}")
                return deal
            else:
                logger.debug(f"Deal non valido: {asin}")
                return None

        except Exception as e:
            logger.error(f"Errore parsing messaggio: {e}", exc_info=True)
            return None

    def validate_deal(self, deal: Dict) -> bool:
        """Valida che il deal abbia tutti i campi necessari"""
        required_fields = ['asin', 'title', 'current_price_pence']
        
        for field in required_fields:
            if not deal.get(field):
                logger.debug(f"Campo mancante: {field}")
                return False
        
        # Verifica ASIN format
        asin = deal.get('asin', '')
        if not re.match(r'^[A-Z0-9]{10}$', asin):
            logger.debug(f"ASIN non valido: {asin}")
            return False
        
        # Verifica prezzo ragionevole
        price = deal.get('current_price_pence', 0)
        if price <= 0 or price > 10000000:
            logger.debug(f"Prezzo non valido: {price}")
            return False
        
        # Verifica sconto minimo
        min_discount = int(os.getenv('MIN_DISCOUNT_PERCENT', 10))
        discount = deal.get('discount_pct', 0)
        if discount < min_discount:
            logger.debug(f"Sconto insufficiente: {discount}% < {min_discount}%")
            return False
        
        return True

    async def scrape_channel_telethon(self) -> List[Dict]:
        """Scrape usando Telethon - legge i messaggi REALI da @NicePriceDeals"""
        deals = []
        
        try:
            if not self.api_id or self.api_id == 0:
                logger.warning("❌ Credenziali Telethon non configurate (API_ID = 0)")
                return deals
            
            logger.info(f"🔍 Scraping REALE da @NicePriceDeals con Telethon...")
            logger.info(f"API_ID: {self.api_id}")
            logger.info(f"API_HASH: {self.api_hash[:10]}...")
            logger.info(f"PHONE: {self.phone}")
            
            client = TelegramClient('session_uk', self.api_id, self.api_hash)
            
            try:
                logger.info("🔗 Connessione a Telegram...")
                await client.start(phone=self.phone)
                logger.info("✅ Connesso a Telegram")
                
                logger.info(f"📖 Lettura messaggi da canale {self.source_channel_id}...")
                
                # Leggi i messaggi dal canale
                message_count = 0
                async for message in client.iter_messages(self.source_channel_id, limit=50):
                    try:
                        message_count += 1
                        
                        if not message.text:
                            logger.debug(f"Messaggio {message.id}: nessun testo")
                            continue
                        
                        logger.debug(f"Messaggio {message.id}: {message.text[:50]}...")
                        
                        # Aggiorna last_message_id
                        if message.id > self.last_message_id:
                            self.last_message_id = message.id
                        
                        # Parsa il messaggio
                        deal = self.parse_message(message.text)
                        if deal:
                            deals.append(deal)
                            logger.info(f"✅ Deal trovato: {deal['asin']}")
                    
                    except Exception as e:
                        logger.debug(f"Errore processing messaggio {message.id}: {e}")
                        continue
                
                logger.info(f"✅ Letti {message_count} messaggi, {len(deals)} deals trovati")
                
            except Exception as e:
                logger.error(f"❌ Errore durante lettura messaggi: {e}", exc_info=True)
            
            finally:
                logger.info("🔌 Disconnessione da Telegram...")
                await client.disconnect()
                logger.info("✅ Disconnesso")
        
        except Exception as e:
            logger.error(f"❌ Errore Telethon: {e}", exc_info=True)
        
        return deals

    async def scrape_channel(self) -> List[Dict]:
        """Scrape del canale - prova Telethon, fallback a niente"""
        logger.info(f"🔍 Scraping canale {self.source_channel_id}...")
        
        # Prova Telethon
        deals = await self.scrape_channel_telethon()
        
        if not deals:
            logger.warning("Nessun deal trovato - Telethon non configurato o canale vuoto")
        
        self.last_scrape_time = datetime.now()
        logger.info(f"✅ Scraping completato: {len(deals)} deals trovati")
        
        return deals

    def build_affiliate_link(self, asin: str) -> str:
        """Costruisce link affiliato Amazon UK"""
        return f"https://amazon.co.uk/dp/{asin}?tag={self.affiliate_tag}"

    def build_sharing_buttons(self, deal: Dict, affiliate_link: str) -> InlineKeyboardMarkup:
        """Costruisce i bottoni di sharing per social media"""
        
        # Testo per il sharing
        share_text = f"🔥 {deal['title']}\n💰 £{deal['current_price_pence']/100:.2f} ({deal['discount_pct']}% off)\n🛒 {affiliate_link}"
        share_text_encoded = quote(share_text)
        
        # Bottoni
        keyboard = [
            [
                # Bottone Amazon
                InlineKeyboardButton(
                    "🛒 VIEW ON AMAZON",
                    url=affiliate_link
                )
            ],
            [
                # Bottoni sharing
                InlineKeyboardButton(
                    "💬 WhatsApp",
                    url=f"https://wa.me/?text={share_text_encoded}"
                ),
                InlineKeyboardButton(
                    "👍 Facebook",
                    url=f"https://www.facebook.com/sharer/sharer.php?u={quote(affiliate_link)}"
                )
            ],
            [
                InlineKeyboardButton(
                    "𝕏 Twitter",
                    url=f"https://twitter.com/intent/tweet?text={share_text_encoded}&url={quote(affiliate_link)}"
                ),
                InlineKeyboardButton(
                    "✈️ Telegram",
                    url=f"https://t.me/share/url?url={quote(affiliate_link)}&text={share_text_encoded}"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    def format_deal_message(self, deal: Dict, amazon_url: str) -> str:
        """Formatta il messaggio del deal per Telegram con link Amazon per immagine"""
        current_price_pounds = deal['current_price_pence'] / 100
        list_price_pounds = deal['list_price_pence'] / 100
        discount = deal['discount_pct']
        
        # Includi il link Amazon nel messaggio per mostrare l'immagine
        message = f"""🔥 **DEAL ALERT** 🔥

📦 {deal['title']}

💰 **Prezzo**: £{current_price_pounds:.2f}
~~£{list_price_pounds:.2f}~~

🎯 **Sconto**: -{discount}%
💾 **ASIN**: `{deal['asin']}`

{amazon_url}"""
        
        return message

    async def post_deal(self, deal: Dict) -> bool:
        """Posta un singolo deal sul canale Telegram con bottoni"""
        try:
            affiliate_link = self.build_affiliate_link(deal['asin'])
            amazon_url = deal.get('amazon_url', affiliate_link)
            message = self.format_deal_message(deal, amazon_url)
            reply_markup = self.build_sharing_buttons(deal, affiliate_link)
            
            # Posta il messaggio
            await self.bot.send_message(
                chat_id=self.publish_channel_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )
            logger.info(f"✅ Deal postato: {deal['asin']}")
            
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Errore Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Errore generico: {e}", exc_info=True)
            return False

# Flask app per esporre endpoint HTTP
app = Flask(__name__)
worker = None

@app.route('/scrape', methods=['GET'])
def scrape_endpoint():
    """Endpoint per il coordinatore - restituisce deals in formato JSON"""
    try:
        if not worker:
            return jsonify({'error': 'Worker non inizializzato'}), 500
        
        # Esegui scraping
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        deals = loop.run_until_complete(worker.scrape_channel())
        loop.close()
        
        logger.info(f"📊 Endpoint /scrape: {len(deals)} deals")
        return jsonify(deals)
        
    except Exception as e:
        logger.error(f"❌ Errore endpoint /scrape: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'worker': 'DealScout UK v2',
        'country': worker.country if worker else 'unknown',
        'source_channel': worker.source_channel_id if worker else 'unknown',
        'publish_channel': worker.publish_channel_id if worker else 'unknown',
        'processed_deals': len(worker.processed_asins) if worker else 0,
        'last_scrape': worker.last_scrape_time.isoformat() if worker and worker.last_scrape_time else None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/stats', methods=['GET'])
def stats():
    """Statistiche worker"""
    return jsonify({
        'processed_asins': len(worker.processed_asins) if worker else 0,
        'last_scrape_time': worker.last_scrape_time.isoformat() if worker and worker.last_scrape_time else None,
        'uptime': 'running'
    })

def main():
    global worker
    
    try:
        worker = DealWorkerUK()
        
        # Test connessione bot
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
        logger.error(f"❌ Errore avvio worker: {e}")
        raise

if __name__ == "__main__":
    main()
