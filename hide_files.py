import argparse
import glob
import os
import logging
import sys
from pathlib import Path
parser = argparse.ArgumentParser()
logging.basicConfig(level=logging.INFO)
parser.add_argument("-d","--dir",help="Target directory")
parser.add_argument("-r", "--recursive",  action='store_true', help="Recurive Mode. Subdirectories encrypted")
decrypt_group = parser.add_mutually_exclusive_group(required=True)
decrypt_group.add_argument("--decrypt", action='store_true', help="Decryption process")
decrypt_group.add_argument("-k","--key", type=int, help="Decryption Key (Integer)")
args=parser.parse_args()
args.recursive=True
def mystify_folder(path):
    history = path / "_.xyz"
    key=None
    if args.key:
        key=args.key
    if history.exists():
        with open(history, "r") as file:
            key=int(file.read())
            logging.info("Decrypting : {}".format(str(path)))
            if args.decrypt:
                key=-key
            else:
                key+=key
    else:
        logging.warning("Nothing encrypted found : {}".format(str(path)))
    for f in path.iterdir():
        if f.is_dir() and args.recursive is True:
            if list(f.iterdir()):
                mystify_folder(f)
            cipher_text = encrypt(f.name,key=key)
            os.rename(f, f.parent/ cipher_text)
        elif f.name=="_.xyz":
            continue
        elif f.is_file():
            cipher_text = encrypt(f.name,key=key)
            os.rename(f, f.parent/ cipher_text)
    if not args.decrypt:
        with open(path/"_.xyz", "w+") as f:
            f.write(str(args.key))
            logging.info("Encryption successful : {}".format(str(path)))
def encrypt(text, key):
    result = ""
    for i in range(len(text)): 
        char = text[i]
        # Encrypt uppercase characters 
        if char.isalpha():
            if (char.isupper()): 
                result += chr((ord(char) +key -65) % 26 + 65)
            else: 
                result += chr((ord(char) + key - 97) % 26 + 97)
        elif char.isnumeric():
            result+=chr((ord(char)+key-49)%9+49)
        else:
            result+=char
        #Encrypt lowercase characters 
    return result
def cleanup(path):
    logging.info("Cleaning up : {}".format(str(path)))
    if args.recursive:
        files = [x for x in path.glob("**/*")]
    else:
        files = [x for x in path.glob("*")]
    files = [x for x in files if x.name == "_.xyz"]
    for x in files:
        x.unlink()
    if args.decrypt:
        files = [x for x in path.glob("**/*")]
        files = [x for x in files if x.name=="_.xyz"]
        for x in files:
            mystify_folder(x.parent)
if __name__ == '__main__':
    path=Path(args.dir)
    mystify_folder(path)
    if(args.decrypt):
        cleanup(path)