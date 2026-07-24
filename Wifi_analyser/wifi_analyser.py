import subprocess
import re
import matplotlib.pyplot as plt
import sqlite3
from tkinter import Tk, Label, Button, Listbox, messagebox
import math
def init_db():
    conn = sqlite3.connect('wifi_signal.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ssid TEXT NOT NULL,
            signal_strength INTEGER NOT NULL,
            quality INTEGER NOT NULL,
            signal_db REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
def clear_historical_data():
    conn = sqlite3.connect('wifi_signal.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM signals')
    conn.commit()
    conn.close()
def insert_signal_data(ssid, signal_strength, quality, signal_db):
    conn = sqlite3.connect('wifi_signal.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO signals (ssid, signal_strength, quality, signal_db)
        VALUES (?, ?, ?, ?)
    ''', (ssid, signal_strength, quality, signal_db))
    conn.commit()
    conn.close()
def get_historical_data():
    conn = sqlite3.connect('wifi_signal.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM signals ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows
def get_connected_network():
    result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
    output = result.stdout
    network_info = {}
    ssid = re.search(r'SSID\s+:\s(.+)', output)
    signal_strength = re.search(r'Signal\s+:\s(\d+)%', output)
    if ssid and signal_strength:
        network_info["SSID"] = ssid.group(1).strip()
        network_info["Signal Strength (%)"] = int(signal_strength.group(1))
        network_info["Quality"] = int(signal_strength.group(1))  
        network_info["Signal Strength (dB)"] = calculate_signal_db(network_info["Signal Strength (%)"])
    return [network_info] if network_info else []
def calculate_signal_db(signal_percentage):
    if signal_percentage <= 0:
        return float('-inf')
    return 10 * math.log10(signal_percentage)
def get_quality_text(quality):
    if quality >= 75:
        return "Excellent"
    elif quality >= 50:
        return "Good"
    elif quality >= 25:
        return "Fair"
    else:
        return "Poor"
def plot_connected_network(network):
    if not network:
        messagebox.showinfo("Wi-Fi Analyzer", "No connected network detected.")
        return
    ssid = network[0]["SSID"]
    signal_strength = network[0]["Signal Strength (%)"]
    quality = network[0]["Quality"]
    quality_text = get_quality_text(quality)
    signal_db = network[0]["Signal Strength (dB)"]
    insert_signal_data(ssid, signal_strength, quality, signal_db)
    plt.figure(figsize=(5, 5))
    plt.bar(["Signal Strength (%)", "Quality (%)", "Signal Strength (dB)"], 
            [signal_strength, quality, signal_db], color=["skyblue", "lightgreen", "salmon"])
    plt.title(f"Connected Network: {ssid} ({quality_text})")
    plt.ylim(-100, 100)
    plt.ylabel("Percentage (%) / dB")
    plt.show()
def update_connected_network():
    network = get_connected_network()
    display_connected_network(network)
    plot_connected_network(network)
def display_connected_network(network):
    listbox.delete(0, 'end')
    if network:
        listbox.insert('end', f"Connected Network SSID: {network[0]['SSID']}")
        listbox.insert('end', f"Signal Strength: {network[0]['Signal Strength (%)']}%")
        listbox.insert('end', f"Quality: {network[0]['Quality']}% ({get_quality_text(network[0]['Quality'])})")
        listbox.insert('end', f"Signal Strength (dB): {network[0]['Signal Strength (dB)']:.2f} dB")
    else:
        listbox.insert('end', "No connected network found.")
def view_historical_data():
    historical_data = get_historical_data()
    listbox.delete(0, 'end')
    for row in historical_data:
        listbox.insert('end', f"{row[1]} - Strength: {row[2]}%, Quality: {row[3]}%, Signal (dB): {row[4]:.2f} dB at {row[5]}")
root = Tk()
root.protocol("WM_DELETE_WINDOW", lambda: (clear_historical_data(), root.destroy()))
root.title("Wi-Fi Analyzer")
root.geometry("400x400")
init_db()
label = Label(root, text="Connected Wi-Fi Network", font=("Arial", 14))
label.pack(pady=10)
listbox = Listbox(root, width=50)
listbox.pack(pady=10)
update_button = Button(root, text="Display Connected Wi-Fi", command=update_connected_network)
update_button.pack(pady=10)
history_button = Button(root, text="View Historical Data", command=view_historical_data)
history_button.pack(pady=10)
root.mainloop()
