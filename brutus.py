from genericpath import isfile
import os
import time
import filetype
import pikepdf

from zipfile import ZipFile
from multiprocessing import Pool, cpu_count
from itertools import product
from tqdm import tqdm

import sys

class Brutus(object):
    def __init__(
        self, target: str,
        dictionnary: str = None,
        charset: str = '0123456789',
        min_password_length: int = 1,
        max_password_length: int = 8,
        max_concurent_worker: int = 8
    ):
        self._supported_type = ['pdf', 'zip']
        self._dictionnary_passwords = [None]
        self._forcing_function = None
        self._tqdm_total = 0
        self._generator_length = 0

        self.target = target
        self.dictionnary = dictionnary
        self.charset = charset
        self.min_password_length = min_password_length
        self.max_password_length = max_password_length

        if max_concurent_worker <= cpu_count():
            self.max_concurent_worker = max_concurent_worker 
        else:
            self.max_concurent_worker = cpu_count()


    @property
    def target(self):
        return self._target
    
    @target.setter
    def target(self, target):
        ext = self.get_target_type(target)

        if not ext in self._supported_type:
            raise TypeError(
                "\033[1;31mThis extension is not yet supported"
            )
        
        self._target = target
        self._forcing_function = getattr(self, 'open_' + ext)


    def get_target_type(self, target):
        try:
            type = filetype.guess_extension(target)
        except Exception as err:
            print(err)
        else:
            return type
    
    
    def generate_password(self):
        for i in product(self.charset, repeat=self._generator_length):
            yield ''.join(i)


    def get_dictionnary_passwords(self):
        with open(self._passwd_file, 'r', encoding='UTF-8') as passwd_file:
            while True:
                passwd = passwd_file.readline()

                if not passwd:
                    break 

                yield ''.join(passwd)


    def get_dictionnary(self):
        dct = os.path.expanduser(self.dictionnary)

        if os.path.isdir(dct):
            dict_list = []

            for dic in os.listdir(dct):
                dict_list.append(os.path.join(dct, dic))
            return dict_list 

        elif os.path.isfile(dct):
            return [dct]
        else:
            raise FileNotFoundError(
                '\033[1;31mDictionnary NOT FOUND'
            )


    def count_dictionnary_line(self, dictionnary: str):
        with open(dictionnary, 'r', encoding='UTF-8') as dict:
            return len(dict.readlines())


    def dictionnary_attack(self):
        dict_list = self.get_dictionnary()
        exec_start = time.perf_counter()

        for dict in dict_list:
            self._passwd_file = dict
            self._tqdm_total = self.count_dictionnary_line(dict)

            print(f"\n[#] Dictionnary attack using {dict}")

            result = self._start(self.get_dictionnary_passwords)
            
            if result is not None:
                exec_time = round(time.perf_counter() - exec_start, 2)

                print(f"\n[+]\033[1;32m Password FOUND: {result}\033[1;0m\n")
                print(f"[#] Attack finished in {exec_time} seconds") 
                break

    
    def bruteforce_attack(self):
        exec_start = time.perf_counter()

        for i in range(self.min_password_length, self.max_password_length):
            self._tqdm_total = len(self.charset) ** i
            self._generator_length = i
            
            print(f"\n[#] Bruteforcing passwords length {i}")

            result = self._start(self.generate_password)

            if result is not None:
                exec_time = round(time.perf_counter() - exec_start, 2)

                print(f"\n[+]\033[1;32m Password FOUND: {result}\033[1;0m\n")
                print(f"[#] Attack finished in {exec_time} seconds") 
                break
            
            i += 1


        



    def _start(self, iterator):
        bar = tqdm(total=self._tqdm_total)

        with Pool(self.max_concurent_worker) as executor:
            for result in executor.imap_unordered(
                self._forcing_function,
                iterator()
                #self._dictionnary_passwords
            ):
                bar.update()

                if result is not None:                
                    bar.refresh()
                    bar.__del__()                
                    executor.terminate()

                    return result
        bar.refresh()
        bar.__del__()

        return None


    def open_pdf(self, passwd):
        try:
            with pikepdf.open(self._target, password=passwd):
                return passwd

        except pikepdf.PasswordError:
            pass
        except Exception as error:
            print(error)

        return None


    def open_zip(self, passwd):
        pwd = bytes(passwd, 'utf-8')
        
        with ZipFile(self._target) as zip:
            try:
                zip.extractall(pwd=pwd)
                return passwd
            except:
                pass

        return None


if __name__ == '__main__':

    brutus = Brutus('/data/test-protected.pdf')
    brutus.bruteforce_attack()
