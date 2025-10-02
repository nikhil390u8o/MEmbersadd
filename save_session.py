from telethon.sync import TelegramClient

api_id = 1234567  # Replace with your API ID
api_hash = 'your_api_hash'  # Replace with your API Hash

phone = input("Enter phone: ")
client = TelegramClient(f"sessions/{phone}", api_id, api_hash)
client.start()
print(f"[✓] Session saved: {phone}")
