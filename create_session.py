from telethon import TelegramClient
import asyncio

async def create_session():
    api_id = 24358896
    api_hash = "3963ba2988481928ad78d15d4b4388a8"
    phone = "+447775827823"
    
    client = TelegramClient('session_uk', api_id, api_hash)
    await client.start(phone=phone)
    await client.disconnect()
    print("✅ Sessione creata!")

asyncio.run(create_session())
