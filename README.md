# Seed Phrase Finder  

Seed Phrase Finder is a Python-based desktop application designed to assist users in recovering incomplete or partially forgotten cryptocurrency seed phrases (mnemonics). It uses a brute-force approach to reconstruct valid seed phrases by filling in missing words based on the BIP39 wordlist.  

## Key Features

- Recover seed phrases with missing words.
- Automatically select the derivation path if not specified.
- Validate the target address with the correct derivation path, even if the user provides the wrong one.
- Display the seed phrase and all possible derivation paths using the `--show` option.
- Write results to a file using the `--output` option.

## Requirements

- Python 3.7+
- `mnemonic`
- `bip_utils`

Install dependencies using:

```bash
pip install mnemonic bip-utils
```

## Usage

### Recover a Seed Phrase

Recover a seed phrase by providing a partial phrase and replacing unknown words with `?`.  

```bash
python sh.py --partial "word1 word2 ? ? word5 word6" --show
```

### Match a Target Address

Validate a target Bitcoin address against the derived public addresses from the recovered seed phrase.  

```bash
python sh.py --partial "word1 word2 ? ? word5 word6" --target "target_address_here"
```

### Show All Possible Seed Phrases and Addresses

Display all possible seed phrases and their corresponding public addresses, optionally limiting the results with a number.  

```bash
python sh.py --partial "word1 word2 ? ? word5 word6" --show
python sh.py --partial "word1 word2 ? ? word5 word6" --show 20
```

### Write Output to a File

Save the results to a file using the `--output` option.

```bash
python sh.py --partial "word1 word2 ? ? word5 word6" --show --output results.txt
python sh.py --partial "word1 word2 ? ? word5 word6" --target "target_address_here" --output match_results.txt
```

### Specify a Derivation Path

Specify the derivation path (BIP44, BIP49, or BIP84). If not provided, the tool automatically checks all paths.

```bash
python sh.py --partial "word1 word2 ? ? word5 word6" --target "target_address_here" --derivation BIP44
```

### Additional Notes

- Use the `--show` option to display all derivation paths and public addresses.
- Combine the `--show` option with `--output` to save results to a file.

## Example Output

### Command

```bash
python sh.py --partial "abandon abandon ? ? ? abandon abandon abandon abandon abandon abandon about" --show 5
```

### Output

```text
Possible Seed Phrase: abandon abandon ability able abort abandon abandon abandon abandon abandon abandon about
BIP44: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
BIP49: 3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy
BIP84: bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwfkp7q
------------------------------------------------------------
```

## License

This tool is open-source and available under the MIT license.

### Key Updates

- Added the `--output` feature and examples for saving results to a file.
- Explained auto-selection of derivation paths and validation against a target address.
- Provided examples for using the new features like `--show` and `--output`.
