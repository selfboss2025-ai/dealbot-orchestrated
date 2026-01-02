#!/usr/bin/env python3
"""
Worker UK - Deal Scout v2
Scraper specializzato per offerte Amazon UK da @NicePriceDeals
Parsing corretto del formato dei messaggi
"""

import os
import re
import logging
from typing import List, Dict, Optional
from datetime import datetime
from flask import Flask, jsonify
from telegram import Bot
from telegram.error import TelegramError

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
        
        logger.info(f"🤖 Worker UK v2 inizializzato")
        logger.info(f"📺 Canale sorgente: {self.source_channel_id}")
        logger.info(f"📤 Canale pubblicazione: {self.publish_channel_id}")

    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """Estrae ASIN da URL Amazon"""
        # Pattern: /dp/ASIN o /gp/product/ASIN
        match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
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
            # Estrai prezzo (£X.XX)
            price_match = re.search(r'About\s+£([\d.]+)', text)
            if not price_match:
                return None
            current_price_pounds = float(price_match.group(1))
            current_price_pence = int(current_price_pounds * 100)

            # Estrai sconto (YY%)
            discount_match = re.search(r'(\d+)%\s+Price drop', text)
            discount_pct = int(discount_match.group(1)) if discount_match else 0

            # Calcola prezzo originale da sconto
            if discount_pct > 0:
                list_price_pence = int(current_price_pence / (1 - discount_pct / 100))
            else:
                list_price_pence = current_price_pence

            # Estrai URL Amazon
            url_match = re.search(r'https://www\.amazon\.co\.uk/[^\s]+', text)
            if not url_match:
                return None
            amazon_url = url_match.group(0)

            # Estrai ASIN
            asin = self.extract_asin_from_url(amazon_url)
            if not asin:
                return None

            # Evita duplicati
            if asin in self.processed_asins:
                logger.debug(f"ASIN già processato: {asin}")
                return None

            # Estrai descrizione (prima riga dopo il prezzo, prima del link)
            # Cerca il testo tra il prezzo e il link
            lines = text.split('\n')
            title = "Amazon Deal"
            for i, line in enumerate(lines):
                if 'amazon.co.uk' in line.lower():
                    # La descrizione è nelle righe precedenti
                    if i > 0:
                        title = lines[i - 1].strip()
                    break

            # Pulisci titolo
            title = re.sub(r'#ad.*', '', title).strip()
            if len(title) < 3:
                title = "Amazon Deal"

            # Costruisci deal
            deal = {
                'asin': asin,
                'title': title,
                'current_price_pence': current_price_pence,
                'list_price_pence': list_price_pence,
                'discount_pct': discount_pct,
                'image_url': None,
                'country': self.country,
                'channel_id': self.source_channel_id,
                'scraped_at': datetime.now().isoformat()
            }

            # Valida deal
            if self.validate_deal(deal):
                self.processed_asins.add(asin)
                logger.info(f"✅ Deal estratto: {asin} - £{current_price_pounds:.2f} ({discount_pct}% off)")
                return deal
            else:
                logger.debug(f"Deal non valido: {asin}")
                return None

        except Exception as e:
            logger.error(f"Errore parsing messaggio: {e}")
            return None

    def validate_deal(self, deal: Dict) -> bool:
        """Valida che il deal abbia tutti i campi necessari"""
        required_fields = ['asin', 'title', 'current_price_pence']
        
        for field in required_fields:
            if not deal.get(field):
                return False
        
        # Verifica ASIN format
        asin = deal.get('asin', '')
        if not re.match(r'^[A-Z0-9]{10}$', asin):
            return False
        
        # Verifica prezzo ragionevole
        price = deal.get('current_price_pence', 0)
        if price <= 0 or price > 10000000:  # Max £100,000
            return False
        
        # Verifica sconto minimo
        min_discount = int(os.getenv('MIN_DISCOUNT_PERCENT', 10))
        discount = deal.get('discount_pct', 0)
        if discount < min_discount:
            logger.debug(f"Sconto insufficiente: {discount}% < {min_discount}%")
            return False
        
        return True

    async def scrape_channel(self) -> List[Dict]:
        """
        Scrape del canale Telegram per deals Amazon
        Per ora usa messaggi di test
        """
        deals = []
        
        try:
            logger.info(f"🔍 Scraping canale {self.source_channel_id}...")
            
            # TODO: Implementare lettura reale da Telegram
            # Per ora usiamo messaggi di test per verificare il parsing
            
            # Messaggi di test nel formato di NicePriceDeals
            test_messages = [
                """About £2.49 💥 50% Price drop https://www.amazon.co.uk/dp/B0DS63GM2Z/?tag=frb-dls-21&psc=1&smid=a3p5rokl5a1ole
Ravensburger Disney Stitch Mini Memory Game - Matching Picture Snap Pairs Game
#ad Price and promotions are accurate at the time of posting but can change or expire at anytime""",
                
                """About £9.99 💥 40% Price drop https://www.amazon.co.uk/dp/B0ABCDEF12/?tag=frb-dls-21
Sony WH-CH720 Wireless Headphones
#ad Price and promotions are accurate at the time of posting but can change or expire at anytime""",
            ]
            
            for message_text in test_messages:
                deal = self.parse_message(message_text)
                if deal:
                    deals.append(deal)
            
            self.last_scrape_time = datetime.now()
            logger.info(f"✅ Scraping completato: {len(deals)} deals trovati")
            
        except Exception as e:
            logger.error(f"❌ Errore scraping: {e}")
        
        return deals

    def build_affiliate_link(self, asin: str) -> str:
        """Costruisce link affiliato Amazon UK"""
        return f"https://amazon.co.uk/dp/{asin}?tag={self.affiliate_tag}"

    def format_deal_message(self, deal: Dict) -> str:
        """Formatta il messaggio del deal per Telegram"""
        affiliate_link = self.build_affiliate_link(deal['asin'])
        
        current_price_pounds = deal['current_price_pence'] / 100
        list_price_pounds = deal['list_price_pence'] / 100
        discount = deal['discount_pct']
        
        message = f"""🔥 **DEAL ALERT** 🔥

📦 {deal['title']}

💰 **Prezzo**: £{current_price_pounds:.2f}
~~£{list_price_pounds:.2f}~~

🎯 **Sconto**: -{discount}%
💾 **ASIN**: `{deal['asin']}`

🛒 [**ACQUISTA ORA**]({affiliate_link})

#AmazonUK #Deal #Sconto"""
        
        return message

    async def post_deal(self, deal: Dict) -> bool:
        """Posta un singolo deal sul canale Telegram"""
        try:
            message = self.format_deal_message(deal)
            
            await self.bot.send_message(
                chat_id=self.publish_channel_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            
            logger.info(f"✅ Deal postato: {deal['asin']}")
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Errore Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Errore generico: {e}")
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
        
        # Esegui scraping (sincrono per semplicità)
        import asyncio
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
        import asyncio
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
