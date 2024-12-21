from itertools import product
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip44Coins, Bip49Coins, Bip84Coins, Bip44Changes

mnemo = Mnemonic("english")


def recover_mnemonic(partial_mnemonic, wordlist, max_missing=3):
    missing_indices = [i for i, word in enumerate(
        partial_mnemonic) if word is None]
    if len(missing_indices) > max_missing:
        raise ValueError("Too many missing words for recovery")

    possible_combinations = product(wordlist, repeat=len(missing_indices))
    valid_mnemonics = []

    for combination in possible_combinations:
        test_mnemonic = partial_mnemonic[:]
        for idx, word in zip(missing_indices, combination):
            test_mnemonic[idx] = word

        test_mnemonic_str = " ".join(test_mnemonic)
        if mnemo.check(test_mnemonic_str):
            valid_mnemonics.append(test_mnemonic_str)

    return valid_mnemonics


def derive_public_address(mnemonic, bip_class, coin, change_type=Bip44Changes.CHAIN_EXT, account_index=0, address_index=0):
    # Generate the seed
    seed = Bip39SeedGenerator(mnemonic).Generate()
    # Use the specified BIP class (Bip44, Bip49, Bip84) to generate the key pair
    bip_wallet = bip_class.FromSeed(seed, coin)
    # Get the address for the specified change type and index
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


partial_mnemonic = [
    "about", "about", "about", "about", None,
    "about", "about", "about", "about", "about", "about", None
]
wordlist = mnemo.wordlist

# Automatically calculate max_missing.
max_missing = partial_mnemonic.count(None)

try:
    results = recover_mnemonic(
        partial_mnemonic, wordlist, max_missing=max_missing)
    if results:
        print("Recovered Mnemonics and Public Addresses:")
        for mnemonic in results:
            try:
                # Derive BIP44 (Legacy)
                address_bip44 = derive_public_address(
                    mnemonic, Bip44, Bip44Coins.BITCOIN)
                # Derive BIP49 (P2WPKH-in-P2SH)
                address_bip49 = derive_public_address(
                    mnemonic, Bip49, Bip49Coins.BITCOIN)
                # Derive BIP84 (Native SegWit)
                address_bip84 = derive_public_address(
                    mnemonic, Bip84, Bip84Coins.BITCOIN)

                print(f"Mnemonic: {mnemonic}")
                print(f"BIP44 Address: {address_bip44}")
                print(f"BIP49 Address: {address_bip49}")
                print(f"BIP84 Address: {address_bip84}\n")
            except Exception as e:
                print(f"Error deriving address: {e}")
    else:
        print("No valid mnemonics found.")
except ValueError as e:
    print(f"Error: {e}")
