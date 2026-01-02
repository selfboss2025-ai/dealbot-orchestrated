"""
Template Configurazione Worker - Usa come base per nuovi paesi
Copia questo file e personalizza per il tuo paese
"""

import os
from typing import Dict

# ============================================================================
# PERSONALIZZA QUESTI VALORI PER IL TUO PAESE
# ============================================================================

# Configurazione Bot Telegram
BOT_TOKEN = os.getenv('WORKER_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
BOT_USERNAME = '@your_bot_username'
BOT_ID = 0  # Inserisci ID bot

# Canale di destinazione (dove pubblicare i deals)
PUBLISH_CHANNEL_ID = 0  # Inserisci ID canale
PUBLISH_CHANNEL_NAME = '@your_publish_channel'

# Canale sorgente (da cui fare scraping)
SOURCE_CHANNEL_ID = 0  # Inserisci ID canale
SOURCE_CHANNEL_NAME = '@your_source_channel'

# Configurazione Worker
WORKER_COUNTRY = 'XX'  # Codice paese (UK, IT, FR, DE, ES, etc.)
WORKER_NAME = 'DealScout XX Worker'
AFFILIATE_TAG = 'your-affiliate-tag-21'

# ============================================================================
# CONFIGURAZIONE STANDARD (modifica se necessario)
# ============================================================================

# Configurazione Server HTTP
WORKER_PORT = int(os.getenv('WORKER_PORT', 8001))
WORKER_HOST = os.getenv('WORKER_HOST', '0.0.0.0')

# Configurazione Scraping
SCRAPE_LOOKBACK_HOURS = int(os.getenv('SCRAPE_LOOKBACK_HOURS', 6))
MIN_DISCOUNT_PERCENT = int(os.getenv('MIN_DISCOUNT_PERCENT', 10))
MAX_PRICE_PENCE = int(os.getenv('MAX_PRICE_PENCE', 10000000))

# Configurazione Rate Limiting
REQUEST_TIMEOUT_SECONDS = 30
RATE_LIMIT_DELAY = 1

# ============================================================================
# PATTERN AMAZON - PERSONALIZZA PER IL TUO PAESE
# ============================================================================

# Esempio per UK:
# AMAZON_PATTERNS = {
#     'domain': [r'amazon\.co\.uk', r'amzn\.to', r'amzn\.eu'],
#     'asin': [r'amazon\.co\.uk/.*?/dp/([A-Z0-9]{10})', ...]
# }

# Esempio per IT:
# AMAZON_PATTERNS = {
#     'domain': [r'amazon\.it', r'amzn\.eu'],
#     'asin': [r'amazon\.it/.*?/dp/([A-Z0-9]{10})', ...]
# }

AMAZON_PATTERNS = {
    'domain': [
        r'amazon\.xx',  # Modifica con dominio paese
        r'amzn\.to',
        r'amzn\.eu'
    ],
    'asin': [
        r'amazon\.xx/.*?/dp/([A-Z0-9]{10})',  # Modifica dominio
        r'amzn\.to/([A-Za-z0-9]+)',
        r'amzn\.eu/([A-Za-z0-9]+)',
        r'(?:ASIN|asin)[\s:]*([A-Z0-9]{10})'
    ]
}

# ============================================================================
# PATTERN PREZZI - PERSONALIZZA PER VALUTA PAESE
# ============================================================================

# Esempio per UK (£):
# PRICE_PATTERNS = [
#     r'£(\d+)\.(\d{2})',
#     r'(\d+)\.(\d{2})\s*£',
#     ...
# ]

# Esempio per IT (€):
# PRICE_PATTERNS = [
#     r'€(\d+),(\d{2})',
#     r'(\d+),(\d{2})\s*€',
#     ...
# ]

PRICE_PATTERNS = [
    r'CURRENCY(\d+)\.(\d{2})',  # Modifica CURRENCY con simbolo (£, €, etc.)
    r'(\d+)\.(\d{2})\s*CURRENCY',
    r'Price:\s*CURRENCY?(\d+)[.,](\d{2})',
    r'Now:\s*CURRENCY?(\d+)[.,](\d{2})',
    r'Deal:\s*CURRENCY?(\d+)[.,](\d{2})',
    r'Was:\s*CURRENCY?(\d+)[.,](\d{2})',
    r'Save:\s*CURRENCY?(\d+)[.,](\d{2})',
]

# Pattern Sconti (uguale per tutti i paesi)
DISCOUNT_PATTERNS = [
    r'(\d+)%\s*(?:off|discount|sconto)',
    r'Save\s*(\d+)%',
    r'Sconto\s*(\d+)%',
    r'-\s*(\d+)%',
    r'(\d+)%\s*off',
]

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ============================================================================
# CONFIGURAZIONE WORKER (per replicabilità)
# ============================================================================

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
        'XX': WORKER_CONFIG,  # Modifica XX con codice paese
        # Aggiungi altre configurazioni qui
    }
    return configs.get(country_code, WORKER_CONFIG)