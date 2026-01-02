"""
Configurazione Worker UK - Deal Scout
"""

import os
from typing import Dict

# Configurazione Bot Telegram
BOT_TOKEN = os.getenv('WORKER_BOT_TOKEN', '7768046661:AAGh3C1k0WsykErjCJy-ZgKZRBYnrHFu13w')
BOT_USERNAME = '@dealscoutuk_bot'
BOT_ID = 7768046661

# Canale di destinazione (dove pubblicare i deals)
PUBLISH_CHANNEL_ID = -1001232723285
PUBLISH_CHANNEL_NAME = '@DealScoutUKBot'

# Canale sorgente (da cui fare scraping)
SOURCE_CHANNEL_ID = -1001303541715
SOURCE_CHANNEL_NAME = '@NicePriceDeals'

# Configurazione Server HTTP
WORKER_PORT = int(os.getenv('WORKER_PORT', 8001))
WORKER_HOST = os.getenv('WORKER_HOST', '0.0.0.0')

# Configurazione Worker
WORKER_COUNTRY = 'UK'
WORKER_NAME = 'DealScout UK Worker'
AFFILIATE_TAG = 'ukbestdeal02-21'

# Configurazione Scraping
SCRAPE_LOOKBACK_HOURS = int(os.getenv('SCRAPE_LOOKBACK_HOURS', 6))
MIN_DISCOUNT_PERCENT = int(os.getenv('MIN_DISCOUNT_PERCENT', 10))
MAX_PRICE_PENCE = int(os.getenv('MAX_PRICE_PENCE', 10000000))  # £100,000

# Configurazione Rate Limiting
REQUEST_TIMEOUT_SECONDS = 30
RATE_LIMIT_DELAY = 1  # Secondi tra richieste

# Pattern Amazon UK
AMAZON_PATTERNS = {
    'domain': [
        r'amazon\.co\.uk',
        r'amzn\.to',
        r'amzn\.eu'
    ],
    'asin': [
        r'(?:amazon\.co\.uk|amazon\.com)/(?:[^/]+/)?(?:dp|gp)/([A-Z0-9]{10})',
        r'amzn\.to/([A-Za-z0-9]+)',
        r'amzn\.eu/([A-Za-z0-9]+)',
        r'(?:ASIN|asin)[\s:]*([A-Z0-9]{10})'
    ]
}

# Pattern Prezzi UK (£)
PRICE_PATTERNS = [
    r'£(\d+)\.(\d{2})',           # £29.99
    r'(\d+)\.(\d{2})\s*£',        # 29.99 £
    r'Price:\s*£?(\d+)[.,](\d{2})',
    r'Now:\s*£?(\d+)[.,](\d{2})',
    r'Deal:\s*£?(\d+)[.,](\d{2})',
    r'Was:\s*£?(\d+)[.,](\d{2})',
    r'Save:\s*£?(\d+)[.,](\d{2})',
    r'£\s*(\d+)[.,](\d{2})',
]

# Pattern Sconti
DISCOUNT_PATTERNS = [
    r'(\d+)%\s*(?:off|discount)',
    r'Save\s*(\d+)%',
    r'Sconto\s*(\d+)%',
    r'-\s*(\d+)%',
    r'(\d+)%\s*off',
]

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configurazione per replicabilità
WORKER_CONFIG = {
    'country': WORKER_COUNTRY,
    'bot_token': BOT_TOKEN,
    'bot_username': BOT_USERNAME,
    'publish_channel_id': PUBLISH_CHANNEL_ID,
    'publish_channel_name': PUBLISH_CHANNEL_NAME,
    'source_channel_id': SOURCE_CHANNEL_ID,
    'source_channel_name': SOURCE_CHANNEL_NAME,
    'affiliate_tag': AFFILIATE_TAG,
    'port': WORKER_PORT,
}

def get_config_for_country(country_code: str) -> Dict:
    """
    Ritorna configurazione per un paese specifico
    Utile per creare nuovi worker per altri paesi
    """
    configs = {
        'UK': WORKER_CONFIG,
        # Aggiungi altre configurazioni qui
    }
    return configs.get(country_code, WORKER_CONFIG)