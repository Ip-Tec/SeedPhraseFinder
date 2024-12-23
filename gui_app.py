import os
import psutil
import time
from itertools import product
from mnemonic import Mnemonic
import tkinter as tk
from tkinter import ttk, messagebox
from bip_utils import (Bip39SeedGenerator, Bip44, Bip49,
                       Bip84, Bip44Coins, Bip49Coins, Bip84Coins, Bip44Changes)

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

# Derive public addresses
def derive_addresses(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44_address = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(
        Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
    bip49_address = Bip49.FromSeed(seed, Bip49Coins.BITCOIN).Purpose().Coin().Account(0).Change(
        Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
    bip84_address = Bip84.FromSeed(seed, Bip84Coins.BITCOIN).Purpose().Coin().Account(0).Change(
        Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
    return bip44_address, bip49_address, bip84_address

# Identify derivation type from address
def get_derivation_type(address):
    if address.startswith("1"):
        return "BIP44 (Legacy)"
    elif address.startswith("3"):
        return "BIP49 (SegWit Compatibility)"
    elif address.startswith("bc1"):
        return "BIP84 (Native SegWit)"
    else:
        raise ValueError("Unknown address format. Unable to determine derivation type.")

# Generate combinations and write to file
def generate_combinations(partial_phrase, wordlist, target_address, progress_callback, status_callback):
    missing_indices = [i for i, word in enumerate(partial_phrase) if word in (None, '?')]
    total_combinations = len(wordlist) ** len(missing_indices)
    progress_callback(0, total_combinations)

    results = []  # Store matching results

    try:
        for count, combination in enumerate(product(wordlist, repeat=len(missing_indices))):
            # Replace missing words with the current combination
            test_phrase = partial_phrase[:]
            for idx, word in zip(missing_indices, combination):
                test_phrase[idx] = word

            mnemonic = " ".join(test_phrase)
            if mnemo.check(mnemonic):
                bip44, bip49, bip84 = derive_addresses(mnemonic)

                # Check if the target address matches any derived address
                if target_address in {bip44, bip49, bip84}:
                    results.append({
                        "mnemonic": mnemonic,
                        "bip44": bip44,
                        "bip49": bip49,
                        "bip84": bip84,
                    })
                    status_callback(f"Match Found! Address: {target_address}")

            # Update progress
            if count % BATCH_SIZE == 0:
                progress_callback(count, total_combinations)

            # Check for system overload
            while is_system_overloaded():
                status_callback("System overloaded. Pausing... Retrying shortly.")
                time.sleep(5)  # Wait for 5 seconds before checking again

    except Exception as e:
        raise e

    return results  # Return the matching results

def run_recovery(self, partial_phrase, save_results):
    try:
        target_address = self.entry_address.get()

        # Run the recovery process
        results = generate_combinations(
            partial_phrase,
            mnemo.wordlist,
            target_address,
            self.update_progress,
            self.update_status
        )

        if results:
            if save_results:
                # Save results to a file
                with open("recovery_results.txt", "w") as f:
                    for result in results:
                        f.write(f"Mnemonic: {result['mnemonic']}\n")
                        f.write(f"BIP44: {result['bip44']}\n")
                        f.write(f"BIP49: {result['bip49']}\n")
                        f.write(f"BIP84: {result['bip84']}\n")
                        f.write("\n")
                self.update_status("Recovery complete. Results saved to recovery_results.txt")
            else:
                self.update_status(f"Recovery complete. Found {len(results)} matching seed phrases.")
        else:
            self.update_status("No matching addresses were found.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        self.button_start.config(state="normal")
        self.label_status.config(text="")


def update_status(self, message):
    """Update the status label in the GUI."""
    self.label_status.config(text=message)
    self.label_status.update_idletasks()


# GUI Application
class SeedRecoveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Seed Phrase Recovery Tool")
        self.root.geometry("600x500")

        # Title
        self.label_title = tk.Label(
            root, text="Seed Phrase Recovery Tool", font=("Arial", 16))
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

        self.label_derivation = tk.Label(
            root, text="Derivation Type: Unknown", font=("Arial", 12), fg="blue")
        self.label_derivation.pack(pady=5)

        self.label_status = tk.Label(root, text="", fg="blue")
        self.label_status.pack(pady=5)

        # Save Switch
        self.save_switch_var = tk.BooleanVar(value=True)
        self.save_switch = tk.Checkbutton(
            root, text="Save seed phrases and addresses to file",
            variable=self.save_switch_var)
        self.save_switch.pack(pady=5)

        # Buttons
        self.button_start = tk.Button(root, text="Start Recovery", bg="green", fg="white", command=self.start_recovery)
        self.button_start.pack(pady=10)

        self.progress_bar = ttk.Progressbar(root, mode="determinate", length=400)
        self.progress_bar.pack(pady=5)

    def update_progress(self, current, total):
        self.progress_bar["maximum"] = total
        self.progress_bar["value"] = current
        self.label_status.config(text=f"Processing: {current}/{total} combinations")
        self.root.update_idletasks()

    def start_recovery(self):
        partial_phrase = self.entry_seed_phrase.get().split()
        partial_phrase = [word if word not in ('?', '') else None for word in partial_phrase]

        target_address = self.entry_address.get()

        # Determine derivation type from address
        try:
            derivation_type = get_derivation_type(target_address)
            self.label_derivation.config(
                text=f"Derivation Type: {derivation_type}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self.label_status.config(text="Recovery in progress...")
        self.button_start.config(state="disabled")

        # Check if the user wants to save the results
        save_results = self.save_switch_var.get()

        # Run recovery in a separate thread
        self.root.after(100, lambda: self.run_recovery(partial_phrase, save_results))

    def run_recovery(self, partial_phrase, save_results):
        try:
            target_address = self.entry_address.get()

            # Run the recovery process
            results = generate_combinations(
                partial_phrase,
                mnemo.wordlist,
                target_address,
                self.update_progress,
                self.update_status
            )

            if results:
                if save_results:
                    # Save results to a file
                    with open("recovery_results.txt", "w") as f:
                        for result in results:
                            f.write(f"Mnemonic: {result['mnemonic']}\n")
                            f.write(f"BIP44: {result['bip44']}\n")
                            f.write(f"BIP49: {result['bip49']}\n")
                            f.write(f"BIP84: {result['bip84']}\n")
                            f.write("\n")
                    self.update_status("Recovery complete. Results saved to recovery_results.txt")
                else:
                    self.update_status(f"Recovery complete. Found {len(results)} matching seed phrases.")
            else:
                self.update_status("No matching addresses were found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.button_start.config(state="normal")
            self.label_status.config(text="")

    def update_status(self, message):
        self.label_status.config(text=message)
        self.root.update_idletasks()

# New Function for No Save
def generate_combinations_no_save(partial_phrase, wordlist, progress_callback):
    missing_indices = [i for i, word in enumerate(partial_phrase) if word in (None, '?')]
    total_combinations = len(wordlist) ** len(missing_indices)
    progress_callback(0, total_combinations)

    try:
        for count, combination in enumerate(product(wordlist, repeat=len(missing_indices))):
            # Replace missing words with the current combination
            test_phrase = partial_phrase[:]
            for idx, word in zip(missing_indices, combination):
                test_phrase[idx] = word

            mnemonic = " ".join(test_phrase)
            if mnemo.check(mnemonic):
                bip44, bip49, bip84 = derive_addresses(mnemonic)
                # print(f"Mnemonic: {mnemonic}, BIP44: {bip44}, BIP49: {bip49}, BIP84: {bip84}")

            # Update progress
            if count % BATCH_SIZE == 0:
                progress_callback(count, total_combinations)

            # Check for system overload
            while is_system_overloaded():
                print("System overloaded. Pausing...")
                time.sleep(5)  # Wait for 5 seconds before checking again
    except Exception as e:
        raise e


# Main Function
def main():
    root = tk.Tk()
    app = SeedRecoveryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
