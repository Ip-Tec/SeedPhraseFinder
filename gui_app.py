import threading
import tkinter as tk
from itertools import product
from mnemonic import Mnemonic
from tkinter import ttk, messagebox
from bip_utils import (Bip39SeedGenerator, Bip44, Bip49,
                       Bip84, Bip44Coins, Bip49Coins, Bip84Coins, Bip44Changes)

mnemo = Mnemonic("english")

# Function to recover the mnemonic


def recover_mnemonic(partial_mnemonic, wordlist, max_missing=4):
    missing_indices = [i for i, word in enumerate(
        partial_mnemonic) if word in (None, '?')]
    if len(missing_indices) > max_missing:
        raise ValueError("Too many missing words for recovery")

    possible_combinations = product(wordlist, repeat=len(missing_indices))
    for combination in possible_combinations:
        test_mnemonic = partial_mnemonic[:]
        for idx, word in zip(missing_indices, combination):
            test_mnemonic[idx] = word

        test_mnemonic_str = " ".join(test_mnemonic)
        if mnemo.check(test_mnemonic_str):
            yield test_mnemonic_str

# Function to derive a public address


def derive_public_address(mnemonic, bip_class, coin, change_type=Bip44Changes.CHAIN_EXT, account_index=0, address_index=0):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip_wallet = bip_class.FromSeed(seed, coin)
    address = (
        bip_wallet.Purpose()
        .Coin()
        .Account(account_index)
        .Change(change_type)
        .AddressIndex(address_index)
        .PublicKey()
        .ToAddress()
    )
    return address

# Function to handle address matching


def start_recovery():
    # Start the recovery in a separate thread
    thread = threading.Thread(target=run_recovery)
    thread.start()


def run_recovery():
    # Disable the button and show the loader
    button_start.config(state="disabled")
    progress_bar.pack(pady=10)
    label_loading.pack(pady=5)
    root.update()

    partial_phrase = entry_seed_phrase.get().split()
    partial_phrase = [word if word not in (
        '?', '') else None for word in partial_phrase]
    target_address = entry_target_address.get()
    derivation_type = combo_bip.get()

    bip_classes = {
        "BIP44 (Legacy)": (Bip44, Bip44Coins.BITCOIN),
        "BIP49 (SegWit Compatibility)": (Bip49, Bip49Coins.BITCOIN),
        "BIP84 (Native SegWit)": (Bip84, Bip84Coins.BITCOIN),
    }

    bip_class, coin = bip_classes[derivation_type]
    try:
        recovered = recover_mnemonic(partial_phrase, mnemo.wordlist)
        for mnemonic in recovered:
            address = derive_public_address(mnemonic, bip_class, coin)
            if address == target_address:
                progress_bar.pack_forget()
                label_loading.pack_forget()
                button_start.config(state="normal")
                messagebox.showinfo(
                    "Match Found", f"Seed Phrase: {mnemonic}\nAddress: {address}")
                return
        progress_bar.pack_forget()
        label_loading.pack_forget()
        button_start.config(state="normal")
        messagebox.showwarning("No Match", "No matching seed phrase found.")
    except Exception as e:
        progress_bar.pack_forget()
        label_loading.pack_forget()
        button_start.config(state="normal")
        messagebox.showerror("Error", str(e))


# GUI Setup
root = tk.Tk()
root.title("Seed Phrase Recovery")
root.geometry("500x400")

label_title = tk.Label(
    root, text="Seed Phrase Recovery Tool", font=("Arial", 16))
label_title.pack(pady=10)

frame_input = tk.Frame(root)
frame_input.pack(pady=10)

label_seed_phrase = tk.Label(frame_input, text="Partial Seed Phrase:")
label_seed_phrase.grid(row=0, column=0, sticky="w", padx=5)
entry_seed_phrase = tk.Entry(frame_input, width=50)
entry_seed_phrase.grid(row=0, column=1, padx=5, pady=5)

label_target_address = tk.Label(frame_input, text="Target Address:")
label_target_address.grid(row=1, column=0, sticky="w", padx=5)
entry_target_address = tk.Entry(frame_input, width=50)
entry_target_address.grid(row=1, column=1, padx=5, pady=5)

label_bip = tk.Label(frame_input, text="Derivation Type:")
label_bip.grid(row=2, column=0, sticky="w", padx=5)
combo_bip = ttk.Combobox(frame_input, values=[
                         "BIP44 (Legacy)", "BIP49 (SegWit Compatibility)", "BIP84 (Native SegWit)"], state="readonly")
combo_bip.set("BIP84 (Native SegWit)")  # Default selection
combo_bip.grid(row=2, column=1, padx=5, pady=5)

button_start = tk.Button(root, text="Start Recovery",
                         command=start_recovery, bg="green", fg="white")
button_start.pack(pady=20)

progress_bar = ttk.Progressbar(root, mode="indeterminate")
label_loading = tk.Label(
    root, text="Recovering, please wait...", font=("Arial", 12), fg="blue")

root.mainloop()
