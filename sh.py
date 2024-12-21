import argparse
import threading
from itertools import product
from mnemonic import Mnemonic
from bip_utils import (Bip39SeedGenerator, Bip44, Bip49,
                       Bip84, Bip44Coins, Bip49Coins, Bip84Coins, Bip44Changes)

mnemo = Mnemonic("english")


def recover_mnemonic(partial_mnemonic, wordlist, max_missing=4):
    """Recover the full mnemonic given a partial one."""
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


def derive_public_address(mnemonic, bip_class, coin, change_type=Bip44Changes.CHAIN_EXT, account_index=0, address_index=0):
    """Derive the public address from the mnemonic."""
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


def run_recovery(partial_phrase, target_address=None, derivation_type=None, show_all=0, output_file=None):
    """Run the recovery process."""
    bip_classes = {
        "BIP44": (Bip44, Bip44Coins.BITCOIN),
        "BIP49": (Bip49, Bip49Coins.BITCOIN),
        "BIP84": (Bip84, Bip84Coins.BITCOIN),
    }

    partial_phrase = [word if word not in ('?', '') else None for word in partial_phrase.split()]
    matched = False

    results = []

    try:
        recovered = recover_mnemonic(partial_phrase, mnemo.wordlist)
        for mnemonic in recovered:
            if show_all:
                result = f"Possible Seed Phrase: {mnemonic}\n"
                for name, (bip_class, coin) in bip_classes.items():
                    address = derive_public_address(mnemonic, bip_class, coin)
                    result += f"{name}: {address}\n"
                results.append(result)
                if show_all != -1 and len(results) >= show_all:
                    break
                results.append("-" * 60)
            elif target_address:
                for name, (bip_class, coin) in bip_classes.items():
                    address = derive_public_address(mnemonic, bip_class, coin)
                    if address == target_address:
                        result = (f"Match Found with {name}:\n"
                                  f"Seed Phrase: {mnemonic}\n"
                                  f"Address: {address}")
                        results.append(result)
                        matched = True
                        break
                if matched:
                    break

        if target_address and not matched:
            results.append("No match found. Verify the derivation path or target address.")
    except Exception as e:
        results.append(f"Error: {str(e)}")

    # Output results
    if output_file:
        with open(output_file, 'w') as f:
            f.write("\n".join(results))
        print(f"Results written to {output_file}")
    else:
        for result in results:
            print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Phrase Recovery Tool")
    parser.add_argument("-p", "--partial", required=True,
                        help="Partial Seed Phrase (use '?' for missing words)")
    parser.add_argument("-t", "--target",
                        help="Target Bitcoin Address")
    parser.add_argument("-d", "--derivation", choices=["BIP44", "BIP49", "BIP84"],
                        help="Derivation type (BIP44, BIP49, BIP84)")
    parser.add_argument("-s", "--show", nargs="?", const=-1, type=int,
                        help="Show all possible seed phrases and addresses (limit with a number)")
    parser.add_argument("-o", "--output",
                        help="File to save the output")

    args = parser.parse_args()

    if not args.target and not args.show:
        parser.error("You must specify either --target or --show.")

    # Start recovery in a separate thread
    thread = threading.Thread(target=run_recovery, args=(
        args.partial, args.target, args.derivation, args.show, args.output))
    thread.start()
    thread.join()
