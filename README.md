# Seed Phrase Finder  

Seed Phrase Finder is a Python-based desktop application designed to assist users in recovering incomplete or partially forgotten cryptocurrency seed phrases (mnemonics). It uses a brute-force approach to reconstruct valid seed phrases by filling in missing words based on the BIP39 wordlist.  

## Key Features

- **Mnemonic Recovery:** Recover incomplete or partially forgotten seed phrases with up to four missing words.  
- **Derivation Type Support:** Supports BIP44 (Legacy), BIP49 (SegWit Compatibility), and BIP84 (Native SegWit).  
- **Public Address Matching:** Verifies reconstructed seed phrases by generating corresponding Bitcoin addresses to match a target address.  
- **User-Friendly Interface:** Built with Tkinter, providing an intuitive GUI for easy usage.  
- **Efficient Processing:** Implements threading to ensure smooth operation without freezing the user interface.  

### How to Use

1. Launch the application by running the `SeedPhraseFinder.exe` (or the Python script if the .exe is unavailable).  
2. Enter your **partial seed phrase** in the "Partial Seed Phrase" field. Use a question mark (`?`) or leave blank for missing words. For example:  
   ``bash
   abandon ability ? ? ? about above absent absorb abstract absurd ? ?
   ``
3. Input your **target Bitcoin address** in the "Target Address" field.  
4. Select the **derivation type** from the dropdown menu:  
   - BIP44 (Legacy)  
   - BIP49 (SegWit Compatibility)  
   - BIP84 (Native SegWit)  
5. Click the **Start Recovery** button.  
6. Wait for the tool to recover valid seed phrases. If a match is found, a popup will display the matching seed phrase and the corresponding Bitcoin address.  

### Built With

- **Python 3.x:** Main programming language.  
- **Tkinter:** For the graphical user interface.  
- **Mnemonic Library:** For seed phrase generation and validation.  
- **bip_utils:** For Bitcoin address derivation and validation.  

### Use Cases

- Cryptocurrency wallet recovery.  
- Validation of seed phrases against known public addresses.  

### Why Use Seed Phrase Finder?

If you've lost part of your seed phrase or want to recover an old wallet with missing information, this tool provides a reliable and straightforward solution for reconstructing valid mnemonics and verifying them against your target Bitcoin address.  
