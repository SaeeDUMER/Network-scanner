import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import socket
import time
import random

# ---------------- CORE FUNCTIONS ----------------

def ping(ip):
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "300", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except:
        return False


def get_device_name(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"


def scan_ports(ip):
    common_ports = [21, 22, 23, 53, 80, 110, 139, 443, 445, 3306, 8080]
    open_ports = []

    for port in common_ports:
        try:
            s = socket.socket()
            s.settimeout(0.2)
            s.connect((ip, port))
            open_ports.append(port)
            s.close()
        except:
            pass

    return open_ports


# ---------------- GLOBAL DATA ----------------

online_devices = []
offline_count = 0


# ---------------- SCANNER ----------------

def scan_network():
    global offline_count, online_devices

    output_box.delete("1.0", tk.END)
    device_list.delete(0, tk.END)

    online_devices = []
    offline_count = 0

    base = ip_base.get()
    start = int(start_range.get())
    end = int(end_range.get())

    total = end - start
    progress_bar["maximum"] = total

    for i, host in enumerate(range(start, end + 1)):
        ip = f"{base}.{host}"

        status_var.set(f"Scanning {ip} ...")
        scan_label.config(text=f">>> ACTIVE SCAN: {ip}")

        if ping(ip):
            name = get_device_name(ip)
            ports = scan_ports(ip)

            online_devices.append(ip)

            # LEFT: LOG
            output_box.insert(tk.END, f"[ONLINE] {ip} | {name}\n")
            output_box.insert(tk.END, f"Ports: {ports if ports else 'None'}\n\n")

            # RIGHT: DEVICE LIST
            device_list.insert(tk.END, f"{ip} ({name})")

        else:
            offline_count += 1
            output_box.insert(tk.END, f"[OFFLINE] {ip}\n")

        progress_bar["value"] = i
        root.update()
        time.sleep(0.05)

    status_var.set("SCAN COMPLETE ✔")
    update_chart()


# ---------------- CHART (ONLINE DEVICES) ----------------

def update_chart():
    chart_canvas.delete("all")

    total = len(online_devices) + offline_count
    if total == 0:
        return

    online = len(online_devices)
    offline = offline_count

    online_percent = (online / total) * 360
    offline_percent = (offline / total) * 360

    # Circle chart background
    chart_canvas.create_oval(50, 50, 250, 250, outline="#222", width=20)

    # Online arc (green)
    chart_canvas.create_arc(
        50, 50, 250, 250,
        start=0,
        extent=online_percent,
        outline="green",
        width=20,
        style="arc"
    )

    # Labels
    chart_canvas.create_text(150, 270,
                             text=f"Online: {online} | Offline: {offline}",
                             fill="white",
                             font=("Courier", 10))


# ---------------- UI ----------------

root = tk.Tk()
root.title("NETWORK SCANNER PRO")
root.geometry("1000x600")
root.configure(bg="#0f0f0f")

# Title animation
scan_label = tk.Label(root, text=">>> NETWORK SCANNER <<<",
                      fg="#00ff00", bg="#0f0f0f",
                      font=("Courier", 18, "bold"))
scan_label.pack(pady=5)

# INPUT PANEL
top_frame = tk.Frame(root, bg="#0f0f0f")
top_frame.pack()

tk.Label(top_frame, text="Base IP:", fg="white", bg="#0f0f0f").grid(row=0, column=0)
ip_base = tk.Entry(top_frame)
ip_base.insert(0, "192.168.1")
ip_base.grid(row=0, column=1)

tk.Label(top_frame, text="Start:", fg="white", bg="#0f0f0f").grid(row=0, column=2)
start_range = tk.Entry(top_frame, width=5)
start_range.insert(0, "1")
start_range.grid(row=0, column=3)

tk.Label(top_frame, text="End:", fg="white", bg="#0f0f0f").grid(row=0, column=4)
end_range = tk.Entry(top_frame, width=5)
end_range.insert(0, "50")
end_range.grid(row=0, column=5)

tk.Button(top_frame, text="START SCAN",
          bg="#00ff00", fg="black",
          command=lambda: threading.Thread(target=scan_network, daemon=True).start()
          ).grid(row=0, column=6, padx=10)

# STATUS
status_var = tk.StringVar()
status_var.set("READY")
tk.Label(root, textvariable=status_var,
         fg="cyan", bg="#0f0f0f").pack()

# PROGRESS BAR
progress_bar = ttk.Progressbar(root, length=800)
progress_bar.pack(pady=5)

# MAIN AREA
main_frame = tk.Frame(root, bg="#0f0f0f")
main_frame.pack(fill="both", expand=True)

# LEFT OUTPUT
output_box = tk.Text(main_frame, bg="black", fg="#00ff00", width=50)
output_box.pack(side="left", fill="both", expand=True)

# RIGHT PANEL
right_frame = tk.Frame(main_frame, bg="#0f0f0f")
right_frame.pack(side="right", fill="both")

tk.Label(right_frame, text="ONLINE DEVICES",
         fg="white", bg="#0f0f0f",
         font=("Courier", 12, "bold")).pack()

device_list = tk.Listbox(right_frame, bg="black", fg="white", width=30)
device_list.pack(pady=5)

tk.Label(right_frame, text="NETWORK CHART",
         fg="white", bg="#0f0f0f",
         font=("Courier", 12, "bold")).pack()

chart_canvas = tk.Canvas(right_frame, width=300, height=300, bg="#0f0f0f")
chart_canvas.pack()

root.mainloop()