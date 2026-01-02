#!/usr/bin/env python3
"""
Worker UK - Deal Scout
Scraper specializzato per offerte Amazon UK da @NicePriceDeals
Espone endpoint HTTP per il coordinatore centrale
"""

import os
import re
import logging
import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from flask import Flask, jsonify
from telegram import Bot, Update
from telegram.error import TelegramError
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from config import (
    BOT_TOKEN, SOURCE_CHANNEL_ID, PUBLISH_CHANNEL_ID,
    WORKER_COUNTRY, AFFILIATE_TAG, WORKER_PORT, WORKER_HOST,
    SCRAPE_LOOKBACK_HOURS, MIN_DISCOUNT_PERCENT, MAX_PRICE_PENCE,
    AMAZON_PATTERNS, PRICE_PATTERNS, DISCOUNT_PATTERNS,
    LOG_LEVEL, LOG_FORMAT
)

# Configurazione logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class DealWorkerUK:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.source_channel_id = SOURCE_CHANNEL_ID
        self.publish_channel_id = PUBLISH_CHANNEL_ID
        self.country = WORKER_COUNTRY
        self.affiliate_tag = AFFILIATE_TAG
        
        self.bot = Bot(token=self.bot_token)
        
        # Cache per evitare duplicati
        self.processed_asins = set()
        self.last_scrape_time = None
        
        logger.info(f"🤖 Worker UK inizializzato")
        logger.info(f"📺 Canale sorgente: {SOURCE_CHANNEL_ID}")
        logger.info(f"📤 Canale pubblicazione: {PUBLISH_CHANNEL_ID}")

    def extract_asin_from_text(self, text: str) -> Optional[str]:
        """Estrae ASIN da testo contenente link Amazon"""
        for pattern in AMAZON_PATTERNS['asin']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                asin = match.group(1)
                # Valida formato ASIN
                if re.match(r'^[A-Z0-9]{10}$', asin):
                    return asin
        return None
    
    def extract_prices_from_text(self, text: str) -> Dict[str, Optional[int]]:
        """
        Estrae prezzi dal testo (in pence)
        Ritorna: {'current': pence, 'list': pence}
        """
        prices = {'current': None, 'list': None}
        
        # Cerca tutti i prezzi nel testo
        found_prices = []
        for pattern in PRICE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Converti in pence (£ a pence)
                    price_pence = int(match[0]) * 100 + int(match[1])
                    found_prices.append(price_pence)
        
        # Rimuovi duplicati e ordina
        found_prices = sorted(list(set(found_prices)))
        
        if len(found_prices) >= 2:
            # Prezzo più basso = corrente, più alto = listino
            prices['current'] = found_prices[0]
            prices['list'] = found_prices[-1]
        elif len(found_prices) == 1:
            prices['current'] = found_prices[0]
        
        return prices
    
    def extract_discount_from_text(self, text: str) -> Optional[int]:
        """Estrae percentuale sconto dal testo"""
        for pattern in DISCOUNT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    discount = int(match.group(1))
                    if 0 < discount <= 100:
                        return discount
                except (ValueError, IndexError):
                    continue
        return None
    
    def calculate_discount(self, current_pence: int, list_pence: int) -> int:
        """Calcola percentuale sconto da prezzi"""
        if list_pence and current_pence and list_pence > current_pence:
            discount = round(((list_pence - current_pence) / list_pence) * 100)
            return max(0, min(100, discount))  # Clamp 0-100
        return 0
    
    def extract_image_url(self, message) -> Optional[str]:
        """Estrae URL immagine dal messaggio Telegram"""
        try:
            if message.photo:
                # Prendi la foto con risoluzione più alta
                largest_photo = max(message.photo, key=lambda p: p.width * p.height)
                file = self.bot.get_file(largest_photo.file_id)
                return file.file_path
            elif message.video:
                # Estrai thumbnail da video
                if message.video.thumbnail:
                    file = self.bot.get_file(message.video.thumbnail.file_id)
                    return file.file_path
        except Exception as e:
            logger.debug(f"Errore estrazione immagine: {e}")
        return None
    
    def extract_title_from_text(self, text: str) -> str:
        """Estrae titolo dal testo del messaggio"""
        # Prendi prima riga o prima frase
        lines = text.strip().split('\n')
        title = lines[0] if lines else text
        
        # Rimuovi link e simboli speciali
        title = re.sub(r'https?://\S+', '', title)
        title = re.sub(r'[£€][\d.,]+', '', title)
        title = re.sub(r'\d+%\s*off', '', title)
        title = title.strip()
        
        # Limita lunghezza
        if len(title) > 200:
            title = title[:197] + '...'
        
        return title or "Amazon Deal"
    
    def validate_deal(self, deal: Dict) -> Tuple[bool, str]:
        """
        Valida che il deal abbia tutti i campi necessari
        Ritorna: (is_valid, reason)
        """
        # Campi obbligatori
        required_fields = ['asin', 'title', 'current_price_pence']
        for field in required_fields:
            if not deal.get(field):
                return False, f"Campo mancante: {field}"
        
        # Valida ASIN
        asin = deal.get('asin', '')
        if not re.match(r'^[A-Z0-9]{10}$', asin):
            return False, f"ASIN non valido: {asin}"
        
        # Valida prezzo
        price = deal.get('current_price_pence', 0)
        if price <= 0:
            return False, "Prezzo non valido (<=0)"
        if price > MAX_PRICE_PENCE:
            return False, f"Prezzo troppo alto (>{MAX_PRICE_PENCE})"
        
        # Valida sconto minimo
        discount = deal.get('discount_pct', 0)
        if discount < MIN_DISCOUNT_PERCENT:
            return False, f"Sconto insufficiente (<{MIN_DISCOUNT_PERCENT}%)"
        
        # Valida titolo
        title = deal.get('title', '')
        if len(title) < 3:
            return False, "Titolo troppo corto"
        
        return True, "OK"
    
    def parse_message_to_deal(self, message) -> Optional[Dict]:
        """Converte un messaggio Telegram in deal strutturato"""
        try:
            # Estrai testo
            text = message.text or message.caption or ""
            if not text:
                return None
            
            # Verifica che contenga link Amazon
            if not any(domain in text.lower() for domain in ['amazon.co.uk', 'amzn.to', 'amzn.eu']):
                return None
            
            # Estrai ASIN
            asin = self.extract_asin_from_text(text)
            if not asin:
                logger.debug("ASIN non trovato nel messaggio")
                return None
            
            # Evita duplicati
            if asin in self.processed_asins:
                logger.debug(f"ASIN già processato: {asin}")
                return None
            
            # Estrai prezzi
            prices = self.extract_prices_from_text(text)
            if not prices['current']:
                logger.debug(f"Prezzo non trovato per {asin}")
                return None
            
            # Estrai sconto
            discount = self.extract_discount_from_text(text)
            if not discount and prices['list']:
                discount = self.calculate_discount(prices['current'], prices['list'])
            
            # Estrai titolo
            title = self.extract_title_from_text(text)
            
            # Costruisci deal
            deal = {
                'asin': asin,
                'title': title,
                'current_price_pence': prices['current'],
                'list_price_pence': prices['list'] or prices['current'],
                'discount_pct': discount or 0,
                'image_url': self.extract_image_url(message),
                'country': self.country,
                'channel_id': self.source_channel_id,
                'message_id': message.message_id,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Valida deal
            is_valid, reason = self.validate_deal(deal)
            if not is_valid:
                logger.debug(f"Deal non valido ({asin}): {reason}")
                return None
            
            # Aggiungi a cache
            self.processed_asins.add(asin)
            
            logger.info(f"✅ Deal estratto: {asin} - {title[:50]}")
            return deal
                
        except Exception as e:
            logger.error(f"Errore parsing messaggio: {e}")
            return None
    
    async def scrape_channel(self) -> List[Dict]:
        """
        Scrape del canale Telegram per deals Amazon
        Legge gli ultimi messaggi dal canale sorgente
        """
        deals = []
        
        try:
            logger.info(f"🔍 Scraping canale {self.source_channel_id}...")
            
            # Ottieni ultimi messaggi dal canale
            # Nota: Questo richiede che il bot sia membro del canale
            messages = await self.bot.get_chat_history(
                chat_id=self.source_channel_id,
                limit=100  # Ultimi 100 messaggi
            )
            
            for message in messages:
                deal = self.parse_message_to_deal(message)
                if deal:
                    deals.append(deal)
            
            self.last_scrape_time = datetime.now()
            logger.info(f"✅ Scraping completato: {len(deals)} deals trovati")
            
        except AttributeError:
            # get_chat_history non disponibile in questa versione
            logger.warning("get_chat_history non disponibile - usando metodo alternativo")
            deals = await self._scrape_channel_alternative()
        except TelegramError as e:
            logger.error(f"❌ Errore Telegram: {e}")
        except Exception as e:
            logger.error(f"❌ Errore generico scraping: {e}")
        
        return deals
    
    async def _scrape_channel_alternative(self) -> List[Dict]:
        """
        Metodo alternativo di scraping usando update handler
        Richiede che il bot sia configurato con webhook/polling
        """
        logger.warning("Usando metodo alternativo di scraping")
        # Questo sarà implementato con polling se necessario
        return []
    
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
            
            # Posta con immagine se disponibile
            if deal.get('image_url'):
                try:
                    await self.bot.send_photo(
                        chat_id=self.publish_channel_id,
                        photo=deal['image_url'],
                        caption=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.warning(f"Errore invio foto, provo senza: {e}")
                    await self.bot.send_message(
                        chat_id=self.publish_channel_id,
                        text=message,
                        parse_mode='Markdown',
                        disable_web_page_preview=False
                    )
            else:
                await self.bot.send_message(
                    chat_id=self.publish_channel_id,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
            
            logger.info(f"✅ Deal postato: {deal['asin']}")
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Errore Telegram posting deal {deal['asin']}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Errore generico posting deal {deal['asin']}: {e}")
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
        'worker': 'DealScout UK',
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
        logger.info(f"🌐 Server HTTP su {WORKER_HOST}:{WORKER_PORT}")
        
        app.run(
            host=WORKER_HOST,
            port=WORKER_PORT,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"❌ Errore avvio worker: {e}")
        raise

if __name__ == "__main__":
    main()