#!/usr/bin/env python3
"""
Bot Coordinatore Centrale - Orchestratore per Worker Bot
Gestisce la schedulazione e coordina i worker per scraping deals Amazon
"""

import os
import logging
import asyncio
import requests
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import quote
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DealCoordinator:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.bot = Bot(token=self.bot_token)
        
        # Worker endpoints
        self.workers = {}
        
        # Worker UK
        worker_uk_url = os.getenv('WORKER_UK_URL', 'http://worker-uk:8001')
        logger.info(f"DEBUG: WORKER_UK_URL env var = {os.getenv('WORKER_UK_URL')}")
        logger.info(f"DEBUG: Using worker_uk_url = {worker_uk_url}")
        if worker_uk_url:
            self.workers['UK'] = {
                'url': worker_uk_url,
                'channel': os.getenv('UK_CHANNEL', '@DealScoutUKBot'),
                'channel_id': int(os.getenv('UK_CHANNEL_ID', -1001232723285)),
                'affiliate_tag': 'ukbestdeal02-21'
            }
            logger.info(f"Worker UK configurato: {worker_uk_url}")
        
        # Worker IT (opzionale)
        if os.getenv('WORKER_IT_URL'):
            self.workers['IT'] = {
                'url': os.getenv('WORKER_IT_URL'),
                'channel': os.getenv('IT_CHANNEL', '@AmazonITDealScout'),
                'channel_id': os.getenv('IT_CHANNEL_ID'),
                'affiliate_tag': 'srzone00-21'
            }
        
        self.scheduler = AsyncIOScheduler()
        
    async def call_worker(self, country: str, worker_config: Dict) -> List[Dict]:
        """Chiama un worker specifico e recupera i deals"""
        try:
            logger.info(f"Chiamando worker {country}: {worker_config['url']}")
            
            response = requests.get(
                f"{worker_config['url']}/scrape",
                timeout=30
            )
            
            if response.status_code == 200:
                deals = response.json()
                logger.info(f"Worker {country}: {len(deals)} deals trovati")
                return deals
            else:
                logger.error(f"Worker {country} errore HTTP: {response.status_code}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error(f"Worker {country}: timeout dopo 30s")
            return []
        except requests.exceptions.ConnectionError:
            logger.error(f"Worker {country}: connessione fallita")
            return []
        except Exception as e:
            logger.error(f"Worker {country}: errore generico: {e}")
            return []
    
    def build_affiliate_link(self, asin: str, country: str, affiliate_tag: str) -> str:
        """Costruisce link affiliato Amazon"""
        domain_map = {
            'UK': 'amazon.co.uk',
            'IT': 'amazon.it'
        }
        domain = domain_map.get(country, 'amazon.com')
        return f"https://{domain}/dp/{asin}?tag={affiliate_tag}"
    
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
    
    def format_deal_message(self, deal: Dict, affiliate_link: str) -> str:
        """Formatta il messaggio del deal per Telegram"""
        discount = deal.get('discount_pct', 0)
        current_price = deal['current_price_pence'] / 100
        list_price = deal['list_price_pence'] / 100
        
        currency = '£' if deal['country'] == 'UK' else '€'
        
        message = f"""🔥 **DEAL ALERT** 🔥

📦 {deal['title']}

💰 **Prezzo**: {currency}{current_price:.2f}
~~{currency}{list_price:.2f}~~

🎯 **Sconto**: -{discount}%
💾 **ASIN**: {deal['asin']}"""
        
        return message
    
    async def post_deal(self, deal: Dict, worker_config: Dict):
        """Posta un singolo deal sul canale Telegram con bottoni"""
        try:
            affiliate_link = self.build_affiliate_link(
                deal['asin'], 
                deal['country'], 
                worker_config['affiliate_tag']
            )
            
            message = self.format_deal_message(deal, affiliate_link)
            reply_markup = self.build_sharing_buttons(deal, affiliate_link)
            
            # Usa channel_id se disponibile, altrimenti channel name
            chat_id = worker_config.get('channel_id') or worker_config['channel']
            
            # Posta con immagine se disponibile
            if deal.get('image_url'):
                try:
                    await self.bot.send_photo(
                        chat_id=chat_id,
                        photo=deal['image_url'],
                        caption=message,
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    logger.warning(f"Errore invio foto, provo senza: {e}")
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
            else:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
            logger.info(f"Deal postato: {deal['asin']} su {worker_config['channel']}")
            
        except TelegramError as e:
            logger.error(f"Errore Telegram posting deal {deal['asin']}: {e}")
        except Exception as e:
            logger.error(f"Errore generico posting deal {deal['asin']}: {e}")
    
    async def process_deals(self):
        """Processo principale: chiama tutti i worker e posta i deals"""
        logger.info("🚀 Avvio ciclo di processing deals")
        
        total_deals = 0
        
        for country, worker_config in self.workers.items():
            logger.info(f"Processing worker {country}...")
            
            # Chiama worker
            deals = await self.call_worker(country, worker_config)
            
            if not deals:
                logger.warning(f"Nessun deal da worker {country}")
                continue
            
            # Posta ogni deal
            for deal in deals:
                try:
                    await self.post_deal(deal, worker_config)
                    total_deals += 1
                    
                    # Pausa tra post per evitare rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Errore processing deal {deal.get('asin', 'unknown')}: {e}")
                    continue
        
        logger.info(f"✅ Ciclo completato. {total_deals} deals processati")
    
    def start_scheduler(self):
        """Avvia lo scheduler per esecuzione ogni 10 minuti"""
        self.scheduler.add_job(
            self.process_deals,
            trigger=IntervalTrigger(minutes=10),
            id='deal_processing',
            name='Process Deals Every 10 Minutes',
            replace_existing=True
        )
        
        # Esecuzione immediata al primo avvio
        self.scheduler.add_job(
            self.process_deals,
            trigger='date',
            run_date=datetime.now(),
            id='initial_run',
            name='Initial Deal Processing'
        )
        
        self.scheduler.start()
        logger.info("📅 Scheduler avviato - processing ogni 10 minuti")
    
    async def run(self):
        """Avvia il coordinatore"""
        logger.info("🤖 Avvio Deal Coordinator")
        
        # Test connessione bot
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Bot connesso: @{bot_info.username}")
        except Exception as e:
            logger.error(f"Errore connessione bot: {e}")
            return
        
        # Avvia scheduler
        self.start_scheduler()
        
        # Mantieni il processo attivo
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown richiesto")
            self.scheduler.shutdown()

async def main():
    coordinator = DealCoordinator()
    await coordinator.run()

if __name__ == "__main__":
    asyncio.run(main())