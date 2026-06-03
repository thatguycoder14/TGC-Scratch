import os
import sys
import threading
import time
import subprocess

# --- AUTOMATIC DEPENDENCY INSTALLER ---
def auto_install_dependencies():
    try:
        import scratchattach as sa
    except ImportError:
        print("[*] Missing dependencies. Initializing automatic system setup...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "scratchattach"])
            print("[+] Setup successful. Launching workspace engine...")
            time.sleep(1)
        except Exception as e:
            print(f"[!] Critical Error: Could not auto-install library. Details: {e}")
            print("[*] Please run manually: pip install scratchattach")
            sys.exit(1)

# Run dependency shield check before executing any core components
auto_install_dependencies()
import scratchattach as sa

# --- CONFIGURATION STORAGE ENGINE ---
CONFIG_FILE = "config.txt"

def load_config():
    usernames = []
    password = "abc123"

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            lines = f.readlines()
        if lines:
            password = lines[0].strip()
            for line in lines[1:]:
                if line.strip():
                    usernames.append(line.strip())
    else:
        with open(CONFIG_FILE, "w") as f:
            f.write(f"{password}\n")

    return usernames, password

def save_config(username_list, password_str):
    with open(CONFIG_FILE, "w") as f:
        f.write(f"{password_str}\n")
        for u in username_list:
            f.write(f"{u}\n")

usernames, current_password = load_config()
system_logs = []
current_target = None
log_lock = threading.Lock()

def add_log(msg):
    with log_lock:
        system_logs.append(msg)
        if len(system_logs) > 6:
            system_logs.pop(0)

# --- WORKER FUNCTIONS ---
def worker_follow(user, pwd, target):
    try:
        session = sa.login(user, pwd)
        user_obj = session.connect_user(target)
        user_obj.follow()
        add_log(f"[+] {user} -> Followed @{target}")
    except Exception as e:
        add_log(f"[!] {user} -> Err: {str(e)[:25]}")

def worker_unfollow(user, pwd, target):
    try:
        session = sa.login(user, pwd)
        user_obj = session.connect_user(target)
        user_obj.unfollow()
        add_log(f"[-] {user} -> Unfollowed @{target}")
    except Exception as e:
        add_log(f"[!] {user} -> Err: {str(e)[:25]}")

def worker_check_following(user, pwd, target, results, index):
    try:
        session = sa.login(user, pwd)
        user_obj = session.connect_user(target)
        is_following = user_obj.is_following()
        results[index] = f"{user}: {'YES' if is_following else 'NO'}"
    except Exception:
        results[index] = f"{user}: ERR"

# --- RENDERING ENGINE ---
def draw_dashboard():
    os.system('clear || cls')

    print("┌" + "─"*65 + "┐")
    print("│  _____ ____ ____    ____   ____ ____   _  _____ ____ _   _    │")
    print("│ |_   _/ ___/ ___|  / ___| / ___|  _ \\ / \\|_   _/ ___| | | |   │")
    print("│   | || |  | |  _   \\___ \\| |   | |_) / _ \\ | || |   | |_| |   │")
    print("│   | || |__| |_| |   ___) | |___|  _ / ___ \\| || |___|  _  |   │")
    print("│   |_| \\____\\____|  |____/ \\____|_| \\_/_/   \\_\\_\\____|_| |_|   │")
    print("└" + "─"*65 + "┘")

    print(f" Target Profile : {current_target if current_target else 'None'}")
    print(f" Worker Password: {current_password}")
    print("─" * 67)

    print(" [f] Bind target profile      [g] Mass follow target")
    print(" [p] Update worker password   [c] Mass unfollow target")
    print(" [n] Add worker account       [i] Check follow status")
    print(" [r] Remove worker account    [s] Inspect target stats")
    print(" [l] View accounts database   [q] Quit automation engine")
    print("─" * 67)

    print(f" Loaded {len(usernames)} accounts")
    print("─" * 67)

    print("System Streams:")
    if not system_logs:
        print(" Awaiting shortcuts...")
    else:
        for log in system_logs:
            print(f" {log}")
    print("\n:: ", end="")
    sys.stdout.flush()

# --- CONTROLLER APPLICATION ENGINE ---
def main():
    global current_target, usernames, current_password
    while True:
        draw_dashboard()
        try:
            cmd = input().strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if cmd == 'q':
            os.system('clear || cls')
            print("Workspace safely detached.")
            break

        elif cmd == 'f':
            draw_dashboard()
            sys.stdout.write("\nBind Target User: ")
            sys.stdout.flush()
            val = input().strip()
            if val:
                current_target = val
                add_log(f"Configured target: @{val}")

        elif cmd == 'p':
            draw_dashboard()
            sys.stdout.write("\nEnter New Global Password: ")
            sys.stdout.flush()
            pwd_input = input().strip()
            if pwd_input:
                current_password = pwd_input
                save_config(usernames, current_password)
                add_log(f"Updated global password storage.")

        elif cmd == 'n':
            draw_dashboard()
            sys.stdout.write("\nAccounts to append (comma-separated): ")
            sys.stdout.flush()
            names = input().strip()
            if names:
                for n in [x.strip() for x in names.split(',') if x.strip()]:
                    if n not in usernames:
                        usernames.append(n)
                        add_log(f"Registered connection: {n}")
                save_config(usernames, current_password)

        elif cmd == 'r':
            draw_dashboard()
            sys.stdout.write("\nAccounts to drop (comma-separated): ")
            sys.stdout.flush()
            names = input().strip()
            if names:
                for n in [x.strip() for x in names.split(',') if x.strip()]:
                    if n in usernames:
                        usernames.remove(n)
                        add_log(f"Unlinked connection: {n}")
                save_config(usernames, current_password)

        elif cmd == 'g':
            if not current_target:
                add_log("[!] Error: Target user unselected. Hit [f] first.")
            elif not usernames:
                add_log("[!] Error: Worker database empty. Hit [n] first.")
            else:
                add_log(f"Spawning follow threads for @{current_target}...")
                threads = []
                for u in usernames:
                    t = threading.Thread(target=worker_follow, args=(u, current_password, current_target))
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()
                add_log("Follow actions completed.")

        elif cmd == 'c':
            if not current_target:
                add_log("[!] Error: Target user unselected. Hit [f] first.")
            elif not usernames:
                add_log("[!] Error: Worker database empty. Hit [n] first.")
            else:
                add_log(f"Spawning unfollow threads for @{current_target}...")
                threads = []
                for u in usernames:
                    t = threading.Thread(target=worker_unfollow, args=(u, current_password, current_target))
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()
                add_log("Unfollow actions completed.")

        elif cmd == 'i':
            if not current_target:
                add_log("[!] Error: Target user unselected. Hit [f] first.")
            elif not usernames:
                add_log("[!] Error: Worker database empty. Hit [n] first.")
            else:
                add_log("Checking relationship statuses...")
                threads = []
                results = [None] * len(usernames)
                for index, u in enumerate(usernames):
                    t = threading.Thread(target=worker_check_following, args=(u, current_password, current_target, results, index))
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()

                add_log("--- Status Check Results ---")
                for res in results:
                    if res: add_log(res)

        elif cmd == 's':
            if not current_target:
                add_log("[!] Error: Target user unselected. Hit [f] first.")
            else:
                try:
                    user = sa.get_user(current_target)
                    stats = user.stats()
                    followers = stats.get('followers', 'N/A')
                    add_log(f"Profile: @{user.username} | Followers: {followers}")
                except Exception as e:
                    add_log(f"Lookup error: {str(e)[:25]}")

        elif cmd == 'l':
            if not usernames:
                add_log("Worker Pool Registry is empty.")
            else:
                add_log(f"Active Pool Registry: {', '.join(usernames)}")

if __name__ == "__main__":
    main()
