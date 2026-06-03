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
            sys.exit(1)

auto_install_dependencies()
import scratchattach as sa

# --- CONFIGURATION ENGINE ---
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

# --- THREAD WORKERS ---
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

def worker_check_following(user, pwd, target, results, index):
    try:
        is_following = sa.login(user, pwd).connect_user(target).is_following()
        results[index] = f"{user}: {'YES' if is_following else 'NO'}"
    except Exception:
        results[index] = f"{user}: ERR"

# --- INTERFACE DISPLAY ---
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

# --- PRIVACY WALL ---
def display_data_notice():
    os.system('clear || cls')
    print("=" * 67)
    print("                  LOAD TGC SCRATCH?                  ")
    print("=" * 67)

    try:
        if input("\n Y/N ").strip().upper() != "Y":
            sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

# --- COMMAND TARGET SUB-ROUTINES ---
def handle_target_bind():
    global current_target
    draw_dashboard()
    sys.stdout.write("\nBind Target User: ")
    sys.stdout.flush()
    val = input().strip()
    if val:
        current_target = val
        add_log(f"Configured target: @{val}")

def handle_password_update():
    global current_password
    draw_dashboard()
    sys.stdout.write("\nEnter New Global Password: ")
    sys.stdout.flush()
    pwd_input = input().strip()
    if pwd_input:
        current_password = pwd_input
        save_config(usernames, current_password)
        add_log("Updated global password storage.")

def handle_account_add():
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

def handle_account_remove():
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

def handle_mass_follow():
    if not current_target:
        return add_log("[!] Error: Target user unselected. Hit [f] first.")
    if not usernames:
        return add_log("[!] Error: Worker database empty. Hit [n] first.")
    add_log(f"Spawning follow threads for @{current_target}...")
    threads = []
    for u in usernames:
        t = threading.Thread(target=worker_follow, args=(u, current_password, current_target))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    add_log("Follow actions completed.")

def handle_mass_unfollow():
    if not current_target:
        return add_log("[!] Error: Target user unselected. Hit [f] first.")
    if not usernames:
        return add_log("[!] Error: Worker database empty. Hit [n] first.")
    add_log(f"Spawning unfollow threads for @{current_target}...")
    threads = []
    for u in usernames:
        t = threading.Thread(target=worker_unfollow, args=(u, current_password, current_target))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    add_log("Unfollow actions completed.")

def handle_status_check():
    if not current_target:
        return add_log("[!] Error: Target user unselected. Hit [f] first.")
    if not usernames:
        return add_log("[!] Error: Worker database empty. Hit [n] first.")
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

def handle_target_stats():
    if not current_target:
        return add_log("[!] Error: Target user unselected. Hit [f] first.")
    try:
        stats = sa.get_user(current_target).stats()
        add_log(f"Profile: @{current_target} | Followers: {stats.get('followers', 'N/A')}")
    except Exception as e:
        add_log(f"Lookup error: {str(e)[:25]}")

def handle_view_database():
    if not usernames:
        add_log("Worker Pool Registry is empty.")
    else:
        add_log(f"Active Pool Registry: {', '.join(usernames)}")

# --- CORE EXECUTIVE LOOP ---
def main():
    display_data_notice()
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
        elif cmd == 'f': handle_target_bind()
        elif cmd == 'p': handle_password_update()
        elif cmd == 'n': handle_account_add()
        elif cmd == 'r': handle_account_remove()
        elif cmd == 'g': handle_mass_follow()
        elif cmd == 'c': handle_mass_unfollow()
        elif cmd == 'i': handle_status_check()
        elif cmd == 's': handle_target_stats()
        elif cmd == 'l': handle_view_database()

if __name__ == "__main__":
    main()
