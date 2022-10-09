import os
import argparse

def cli():
    parser = argparse.ArgumentParser(
        prog='Brutus', 
        description='Bruteforce & dictionnary attacks',
        usage='%(prog)s [options] taregt'
    )

    parser.add_argument('--target', '-t', type=str, required=True, help='Path to the target')
    parser.add_argument('--dictionnary', '-d', type=str, help='Path to dictionnary file or folder')
    parser.add_argument('--charset', '-c', type=str, help='Charset for password generation')
    parser.add_argument('--min-pwd-length', '-a', type=int, help='Minimum password length to generate')
    parser.add_argument('--max-pwd-length', '-b', type=int, help='Maximum password length to generate')
    parser.add_argument('--worker', '-w', type=int, help='Number of simulatneous workers')

    args = parser.parse_args()

    if not os.path.isfile(args.target):
        raise('Target not found')
    
    return args