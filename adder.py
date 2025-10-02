import os
import time
import random
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, UserNotMutualContactError
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.channels import InviteToChannelRequest
from config import api_id, api_hash, group_link

def load_numbers():
    with open("number.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def load_sessions():
    return [f.replace(".session", "") for f in os.listdir("sessions") if f.endswith(".session")]

def get_group(client):
    try:
        if "joinchat" in group_link or "+" in group_link:
            hash = group_link.split("/")[-1].replace("+", "")
            return client(ImportChatInviteRequest(hash))
        else:
            return client.get_entity(group_link)
    except Exception as e:
        print(f"[!] Could not get group: {e}")
        return None

def log(msg):
    print(msg)
    with open("logs.txt", "a") as f:
        f.write(msg + "\n")

def run_adder():
    phone_numbers = load_numbers()
    sessions = load_sessions()
    added_total = 0

    for session_name in sessions:
        client = TelegramClient(f"sessions/{session_name}", api_id, api_hash)
        try:
            client.start()
            me = client.get_me()
            log(f"[+] Logged in: {me.first_name} ({session_name})")

            group = get_group(client)
            if not group:
                continue

            added = 0
            for phone in phone_numbers[:]:
                try:
                    contact = InputPhoneContact(client_id=random.randint(1000, 9999999), phone=phone, first_name="User", last_name="")
                    result = client(ImportContactsRequest([contact]))
                    user = result.users[0]

                    client(InviteToChannelRequest(channel=group, users=[user.id]))
                    log(f"[✓] Added: {phone}")
                    phone_numbers.remove(phone)
                    added += 1
                    added_total += 1
                    time.sleep(random.randint(10, 20))

                except UserPrivacyRestrictedError:
                    log(f"[!] Privacy restricted: {phone}")
                except UserNotMutualContactError:
                    log(f"[!] Not a mutual contact: {phone}")
                except FloodWaitError as e:
                    log(f"[!] Flood wait: {e.seconds} sec. Sleeping...")
                    time.sleep(e.seconds + 5)
                except Exception as e:
                    log(f"[!] Failed to add {phone}: {e}")
                    time.sleep(5)

                if added >= 50:
                    log(f"[!] Reached limit for {session_name}")
                    break

            client.disconnect()
        except Exception as e:
            log(f"[!] Error with {session_name}: {e}")
            continue

        if added_total >= 1000:
            log("[✓] Target reached: 1000 members")
            break

if __name__ == "__main__":
    run_adder()
