import os
import sys
import threading
import time
import scratchattach as sa

# --- HARDWARE STORAGE CONFIG ---
ACCOUNTS_FILE = "accounts.txt"
PASSWORD = "tscoder!"
DEFAULT_USERNAMES = [
    "SUPERHELLO2121", "THESUPERHELLO", "THESUPERDUPERHELLO",
    "THESUPERDUPEE", "AMERICANOILS_CO", "IRANHASBADOIL",
    "SUPERRRRMANNN", "IAMSUPERFROG", "Hellonewyork13"
]

def load_usernames():
    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "w") as f:
            for u in DEFAULT_USERNAMES:
                f.write(f"{u}\n")
        return DEFAULT_USERNAMES.copy()
    with open(ACCOUNTS_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_usernames(username_list):
    with open(ACCOUNTS_FILE, "w") as f:
        for u in username_list:
            f.write(f"{u}\n")

usernames = load_usernames()
system_logs = []
current_target = "None"

def add_log(msg):
    system_logs.append(msg)
    if len(system_logs) > 3:
        system_logs.pop(0)

# --- WORKER FUNCTIONS ---
def worker_follow(user, pwd, target):
    try:
        sa.login(user, pwd).connect_user(target).follow()
        add_log(f"[+] {user} -> Followed @{target}")
    except Exception as e:
        add_log(f"[!] {user} -> Err: {str(e)[:25]}")

def worker_unfollow(user, pwd, target):
    try:
        sa.login(user, pwd).connect_user(target).unfollow()
        add_log(f"[-] {user} -> Unfollowed @{target}")
    except Exception as e:
        add_log(f"[!] {user} -> Err: {str(e)[:25]}")

# --- RENDERING ENGINE ---
def draw_dashboard():
    # Clear terminal safely
    os.system('clear || cls')

    # 1. Official Large LazyVim Title Logo with floating 'z' entries
    print("\n" * 1)
    print("                      _        _ _____   ____  _     _         z")
    print("                     | |      / /|___ /  / ___|| |   | |        z")
    print("                     | |     / /   |_ \\  \\___ \\| |_  | |__      z")
    print("                     | |___ / /   ___) |  ___) |  _| | '_ \\    ")
    print("                     |_____/_/   |____/  |____/ \\__| |_| |_|   ")

    # 2. Status Row Indicator
    print("\n" * 1)
    print(f"                         [*] Target profile coordinate: {current_target}")
    print("\n")

    # 3. Exact Layout Clone of the Real LazyVim Main Menu Grid Mapping
    # Pure plaintext ensures absolute zero text-crushing or line overlapping
    print("                        Find target profile                  f")
    print("                        New worker account                   n")
    print("                        Remove worker account                r")
    print("                        Grep / Mass follow target            g")
    print("                        Config / Mass unfollow target        c")
    print("                        Session / Inspect target stats       s")
    print("                        Lazy Extras / View accounts database l")
    print("                        Quit workspace automation engine     q")

    # 4. Signature Real-Time Plugins Footer Line
    print("\n" * 1)
    print(f"                    [*] LazyScratch loaded {len(usernames)} modules in 12.5ms")

    # 5. Live Streams Output Panel Split
    print("\n --- System Streams")
    if not system_logs:
        print("    Alpha environment active. Awaiting shortcut command maps.")
    else:
        for log in system_logs:
            print(f"    {log}")

    print("\n :: ", end="")
    sys.stdout.flush()

# --- CONTROLLER APPLICATION ENGINE ---
def main():
    global current_target, usernames
    while True:
        draw_dashboard()
        try:
            cmd = input().strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if cmd == 'q':
            os.system('clear')
            print("Vim instance detached safely.")
            break

        elif cmd == 'f':
            draw_dashboard()
            sys.stdout.write("\n    Bind Target User: ")
            sys.stdout.flush()
            val = input().strip()
            if val:
                current_target = val
                add_log(f"Configured target handle: @{val}")

        elif cmd == 'n':
            draw_dashboard()
            sys.stdout.write("\n    Accounts to append (comma-separated): ")
            sys.stdout.flush()
            names = input().strip()
            if names:
                for n in [x.strip() for x in names.split(",") if x.strip()]:
                    if n not in usernames:
                        usernames.append(n)
                        add_log(f"Registered connection instance: {n}")
                save_usernames(usernames)

        elif cmd == 'r':
            draw_dashboard()
            sys.stdout.write("\n    Accounts to drop (comma-separated): ")
            sys.stdout.flush()
            names = input().strip()
            if names:
                for n in [x.strip() for x in names.split(",") if x.strip()]:
                    if n in usernames:
                        usernames.remove(n)
                        add_log(f"Unlinked connection instance: {n}")
                save_usernames(usernames)

        elif cmd == 'g':
            if current_target == "None":
                add_log("[!] Error: Target user unselected. Hit [f] key map first.")
            else:
                add_log(f"Spawning follow process arrays targeting @{current_target}...")
                threads = []
                for u in usernames:
                    t = threading.Thread(target=worker_follow, args=(u, PASSWORD, current_target))
                    threads.append(t)
                    t.start()
                for t in threads: t.join()

        elif cmd == 'c':
            if current_target == "None":
                add_log("[!] Error: Target user unselected. Hit [f] key map first.")
            else:
                add_log(f"Spawning unfollow process arrays targeting @{current_target}...")
                threads = []
                for u in usernames:
                    t = threading.Thread(target=worker_unfollow, args=(u, PASSWORD, current_target))
                    threads.append(t)
                    t.start()
                for t in threads: t.join()

        elif cmd == 's':
            if current_target == "None":
                add_log("[!] Error: Target user unselected. Hit [f] key map first.")
            else:
                try:
                    user = sa.get_user(current_target)
                    stats = user.stats()
                    add_log(f"Profile: @{user.username} | Followers: {stats.get('followers', 0)}")
                except Exception as e:
                    add_log(f"Lookup error: {str(e)[:25]}")

        elif cmd == 'l':
            add_log(f"Active Worker Pool Registry: {', '.join(usernames)}")

if __name__ == "__main__":
    main()
