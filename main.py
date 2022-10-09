from cli import cli
from brutus import Brutus

if __name__ == '__main__':
    args = cli()

    target = args.target
    dictionnary = args.dictionnary
    charset = args.charset if args.charset else '0123456789'
    min_pwd_length = args.min_pwd_length if args.min_pwd_length else 1
    max_pwd_length = args.max_pwd_length if args.max_pwd_length else 8
    worker = args.worker if args.worker else 8

    brutus = Brutus(target, dictionnary, charset, min_pwd_length, max_pwd_length, worker)
    
    if dictionnary:
        brutus.dictionnary_attack()
    else:
        brutus.bruteforce_attack()

