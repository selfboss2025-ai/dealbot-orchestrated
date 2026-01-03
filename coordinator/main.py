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
        worker_uk_url = os.getenv('WORKER_UK_URL', 'http://127.0.0.1:8001')
        if worker_uk_url:
            self.workers['UK'] = {
                'url': worker_uk_url,
                'channel': os.getenv('UK_CHANNEL', '@DealScoutUKBot'),
                'channel_id': int(os.getenv('UK_CHANNEL_ID', -1001232723285)),
                'affiliate_tag': 'ukbestdeal02-21'
            }
            logger.info(f"Worker UK configurato: {worker_uk_url}")
        
        # Worker IT (opzionale)
        worker_it_url = os.getenv('WORKER_IT_URL', 'http://127.0.0.1:8002')
        if worker_it_url:
            self.workers['IT'] = {
                'url': worker_it_url,
                'channel': os.getenv('IT_CHANNEL', '@AmazonITDealScout'),
                'channel_id': int(os.getenv('IT_CHANNEL_ID', -1001080585126)),
                'affiliate_tag': 'srzone00-21'
            }
            logger.info(f"Worker IT configurato: {worker_it_url}")
        
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
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Worker {country}: connessione fallita - {e}")
            return []
        except Exception as e:
            logger.error(f"Worker {country}: errore generico - {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
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
    
    async def post_deal(self, deal: Dict, worker_config: Dict):
        """Posta un singolo deal sul canale Telegram"""
        try:
            # Il worker ha già preparato il messaggio con l'URL affiliato corretto
            message_text = deal.get('message_text')
            affiliate_url = deal.get('affiliate_url')
            
            if not message_text or not affiliate_url:
                logger.error(f"Deal {deal.get('asin', 'unknown')} mancante di message_text o affiliate_url")
                return
            
            # Rimuovi il link dal testo per nasconderlo
            import re
            message_text_clean = re.sub(r'https://www\.amazon\.co\.uk/[^\s\n]+', '', message_text)
            message_text_clean = re.sub(r'https://www\.amazon\.it/[^\s\n]+', '', message_text_clean)
            message_text_clean = re.sub(r'https://amzn\.(to|eu)/[^\s\n]+', '', message_text_clean)
            message_text_clean = message_text_clean.strip()
            
            # Crea bottoni di sharing
            share_text = f"🔥 Amazon Deal\n🛒 {affiliate_url}"
            share_text_encoded = quote(share_text)
            
            keyboard = [
                [InlineKeyboardButton("🛒 VIEW ON AMAZON", url=affiliate_url)],
                [
                    InlineKeyboardButton("💬 WhatsApp", url=f"https://wa.me/?text={share_text_encoded}"),
                    InlineKeyboardButton("👍 Facebook", url=f"https://www.facebook.com/sharer/sharer.php?u={quote(affiliate_url)}")
                ],
                [
                    InlineKeyboardButton("𝕏 Twitter", url=f"https://twitter.com/intent/tweet?text={share_text_encoded}"),
                    InlineKeyboardButton("✈️ Telegram", url=f"https://t.me/share/url?url={quote(affiliate_url)}&text={share_text_encoded}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Usa channel_id se disponibile, altrimenti channel name
            chat_id = worker_config.get('channel_id') or worker_config['channel']
            
            # Invia come messaggio con preview automatica di Telegram
            # L'URL affiliato è nei bottoni, Telegram mostrerà l'anteprima automaticamente
            await self.bot.send_message(
                chat_id=chat_id,
                text=message_text_clean,
                parse_mode='Markdown',
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )
            
            logger.info(f"Deal postato: {deal['asin']} su {worker_config['channel']}")
            
        except TelegramError as e:
            logger.error(f"Errore Telegram posting deal {deal.get('asin', 'unknown')}: {e}")
        except Exception as e:
            logger.error(f"Errore generico posting deal {deal.get('asin', 'unknown')}: {e}")
    
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
        """Avvia lo scheduler per esecuzione ogni 15 minuti"""
        self.scheduler.add_job(
            self.process_deals,
            trigger=IntervalTrigger(minutes=15),
            id='deal_processing',
            name='Process Deals Every 15 Minutes',
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
        logger.info("📅 Scheduler avviato - processing ogni 15 minuti")
    
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