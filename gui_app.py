import os
import psutil
import time
from itertools import product
from mnemonic import Mnemonic
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from bip_utils import (Bip39SeedGenerator, Bip44, Bip49,
                       Bip84, Bip44Coins, Bip49Coins, Bip84Coins, Bip44Changes)
import csv

# Initialize mnemonic
mnemo = Mnemonic("english")

# Resource thresholds
CPU_THRESHOLD = 80  # Percentage
MEMORY_THRESHOLD = 80  # Percentage
BATCH_SIZE = 1000  # Number of combinations processed per batch

# File to store results
result_file = "seed_combinations.csv"

# Monitor system resources
def is_system_overloaded():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    return cpu_usage > CPU_THRESHOLD or memory_usage > MEMORY_THRESHOLD

# Recover mnemonic
def recover_mnemonic(partial_mnemonic, wordlist, max_missing=4):
    missing_indices = [i for i, word in enumerate(partial_mnemonic) if word in (None, '?')]
    if len(missing_indices) > max_missing:
        raise ValueError("Too many missing words for recovery")

    possible_combinations = product(wordlist, repeat=len(missing_indices))

    # Load progress if the file exists
    last_combination = None
    if os.path.exists(result_file):
        with open(result_file, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                last_combination = row[0]

    resume = False if not last_combination else True

    for combination in possible_combinations:
        if resume:
            if combination == tuple(last_combination.split()):
                resume = False
            continue

        test_mnemonic = partial_mnemonic[:]
        for idx, word in zip(missing_indices, combination):
            test_mnemonic[idx] = word

        test_mnemonic_str = " ".join(test_mnemonic)
        if mnemo.check(test_mnemonic_str):
            yield test_mnemonic_str

        # Save progress
        with open(result_file, "a") as f:
            writer = csv.writer(f)
            writer.writerow([" ".join(combination)])

# Derive public address
def derive_public_address(mnemonic, bip_class, coin, change_type=Bip44Changes.CHAIN_EXT, account_index=0, address_index=0):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    return bip_class.FromSeed(seed, coin).Purpose().Coin().Account(account_index).Change(change_type).AddressIndex(address_index).PublicKey().ToAddress()

# Detect derivation
def detect_derivation(mnemonic, target_address):
    bip_classes = {
        "BIP44 (Legacy)": (Bip44, Bip44Coins.BITCOIN),
        "BIP49 (SegWit Compatibility)": (Bip49, Bip49Coins.BITCOIN),
        "BIP84 (Native SegWit)": (Bip84, Bip84Coins.BITCOIN),
    }

    for derivation_type, (bip_class, coin) in bip_classes.items():
        try:
            address = derive_public_address(mnemonic, bip_class, coin)
            if address == target_address:
                return derivation_type
        except Exception:
            pass
    return None

# Save recovery result
def save_result(mnemonic, address):
    result = f"Seed Phrase: {mnemonic}\nAddress: {address}"
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if save_path:
        with open(save_path, "w") as file:
            file.write(result)
        messagebox.showinfo("Success", f"Result saved to {save_path}")
    else:
        messagebox.showinfo("Result", result)

# GUI Application
class SeedRecoveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Seed Phrase Recovery Tool")
        self.root.geometry("600x500")

        # Title
        self.label_title = tk.Label(root, text="Seed Phrase Recovery Tool", font=("Arial", 16))
        self.label_title.pack(pady=10)

        # Input Frame
        self.frame_input = tk.Frame(root)
        self.frame_input.pack(pady=10)

        self.label_seed_phrase = tk.Label(self.frame_input, text="Partial Seed Phrase:")
        self.label_seed_phrase.grid(row=0, column=0, sticky="w", padx=5)
        self.entry_seed_phrase = tk.Entry(self.frame_input, width=50)
        self.entry_seed_phrase.grid(row=0, column=1, padx=5, pady=5)

        self.label_address = tk.Label(self.frame_input, text="Target Address:")
        self.label_address.grid(row=1, column=0, sticky="w", padx=5)
        self.entry_address = tk.Entry(self.frame_input, width=50)
        self.entry_address.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        self.button_start = tk.Button(root, text="Start Recovery", bg="green", fg="white", command=self.start_recovery)
        self.button_start.pack(pady=10)

        self.progress_bar = ttk.Progressbar(root, mode="determinate", length=400)
        self.progress_bar.pack(pady=5)

    def start_recovery(self):
        pass  # Implement recovery logic here

# Initialize application
if __name__ == "__main__":
    root = tk.Tk()
    app = SeedRecoveryApp(root)
    root.mainloop()
