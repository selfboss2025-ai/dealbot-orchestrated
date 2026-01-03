#!/usr/bin/env python3
"""
Script per creare la sessione Telethon IT
Eseguire localmente per autenticare l'account Telegram
"""
from telethon import TelegramClient

async def main():
    api_id = 24358896
    api_hash = "3963ba2988481928ad78d15d4b4388a8"
    phone = "+447775827823"
    
    client = TelegramClient('session_it', api_id, api_hash)
    await client.start(phone=phone)
    print("✅ Sessione IT creata con successo!")
    print("📁 File: session_it.session")
    print("📋 Copia questo file in workers/it/session_it.session")
    await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
