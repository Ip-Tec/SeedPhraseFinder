import threading
import tkinter as tk
from tkinter import ttk, messagebox
from itertools import product
import psutil
import time
from mnemonic import Mnemonic
from bip_utils import (Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip44Coins, Bip49Coins, Bip84Coins, Bip44Changes)

# Initialize the Mnemonic instance
mnemo = Mnemonic("english")

# Function to derive public addresses for BIP44, BIP49, BIP84
def derive_addresses(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44_wallet = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
    bip49_wallet = Bip49.FromSeed(seed, Bip49Coins.BITCOIN)
    bip84_wallet = Bip84.FromSeed(seed, Bip84Coins.BITCOIN)

    bip44_address = (
        bip44_wallet.Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
        .PublicKey()
        .ToAddress()
    )
    bip49_address = (
        bip49_wallet.Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
        .PublicKey()
        .ToAddress()
    )
    bip84_address = (
        bip84_wallet.Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
        .PublicKey()
        .ToAddress()
    )

    return bip44_address, bip49_address, bip84_address


# Combination Generator Class
class CombinationGenerator:
    def __init__(self, partial_phrase, wordlist, result_file, progress_callback):
        self.partial_phrase = partial_phrase
        self.wordlist = wordlist
        self.result_file = result_file
        self.progress_callback = progress_callback
        self.running = True
        self.paused = False
        self.lock = threading.Lock()

    def stop(self):
        self.running = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def run(self):
        missing_indices = [i for i, word in enumerate(self.partial_phrase) if word in (None, '?')]
        total_combinations = len(self.wordlist) ** len(missing_indices)
        self.progress_callback(0, total_combinations)

        try:
            with open(self.result_file, "w") as f:
                f.write("Seed Phrase,BIP44 Address,BIP49 Address,BIP84 Address\n")
                for count, combination in enumerate(product(self.wordlist, repeat=len(missing_indices))):
                    if not self.running:
                        break

                    while self.paused:
                        time.sleep(1)

                    test_phrase = self.partial_phrase[:]
                    for idx, word in zip(missing_indices, combination):
                        test_phrase[idx] = word

                    mnemonic = " ".join(test_phrase)
                    if mnemo.check(mnemonic):
                        bip44, bip49, bip84 = derive_addresses(mnemonic)
                        f.write(f"{mnemonic},{bip44},{bip49},{bip84}\n")

                    if count % 1000 == 0:
                        self.progress_callback(count, total_combinations)
        except Exception as e:
            messagebox.showerror("Error", str(e))


# Monitor System Load
def monitor_system_load(generator):
    while generator.running:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        if cpu_usage > 90 or memory_usage > 90:  # Thresholds can be adjusted
            generator.pause()
            messagebox.showwarning("System Overload", "Pausing due to high CPU/Memory usage.")
            while cpu_usage > 90 or memory_usage > 90:
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                time.sleep(1)
            generator.resume()
        time.sleep(1)


# GUI Application
def start_combination_generation():
    partial_phrase = entry_seed_phrase.get().split()
    partial_phrase = [word if word not in ('?', '') else None for word in partial_phrase]
    result_file = "seed_recovery_results.csv"

    generator = CombinationGenerator(partial_phrase, mnemo.wordlist, result_file, update_progress)
    generator_thread = threading.Thread(target=generator.run)
    monitor_thread = threading.Thread(target=monitor_system_load, args=(generator,))
    
    generator_thread.start()
    monitor_thread.start()


def update_progress(current, total):
    progress_percent = (current / total) * 100
    progress_label.config(text=f"Progress: {progress_percent:.2f}%")
    root.update()


# GUI Setup
root = tk.Tk()
root.title("Seed Phrase Recovery Tool")
root.geometry("500x400")

label_title = tk.Label(root, text="Seed Phrase Recovery Tool", font=("Arial", 16))
label_title.pack(pady=10)

frame_input = tk.Frame(root)
frame_input.pack(pady=10)

label_seed_phrase = tk.Label(frame_input, text="Partial Seed Phrase:")
label_seed_phrase.grid(row=0, column=0, sticky="w", padx=5)
entry_seed_phrase = tk.Entry(frame_input, width=50)
entry_seed_phrase.grid(row=0, column=1, padx=5, pady=5)

button_start = tk.Button(root, text="Start Recovery", command=start_combination_generation, bg="green", fg="white")
button_start.pack(pady=20)

progress_label = tk.Label(root, text="Progress: 0%", font=("Arial", 12))
progress_label.pack(pady=10)

root.mainloop()
