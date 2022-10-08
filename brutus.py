import time
import filetype
import pikepdf

from zipfile import ZipFile
from multiprocessing import Pool, cpu_count
from itertools import product
from tqdm import tqdm

class Brutus(object):
    def __init__(
        self, target: str,
        charset: str = "0123456789",
        min_password_length: int = 1,
        max_password_length: int = 8,
        max_concurent_worker: int = 8
    ):

        self.target = target
        self.charset = charset
        self.min_password_length = min_password_length
        self.max_password_length = max_password_length

        if max_concurent_worker <= cpu_count():
            self.max_concurent_worker = max_concurent_worker 
        else:
            self.max_concurent_worker = cpu_count()

        # Get corresponding function regarding the extension
        ext = self.get_target_type()
        self._forcing_function = getattr(self, 'open_' + ext)

        self._tqdm_total = 0


    def get_target_type(self):
        supported_type = ["pdf", "zip"]

        try:
            type = filetype.guess_extension(self.target)
        except Exception as err:
            print(err)

        else:
            if type in supported_type:
                return type
            else:
                raise TypeError(
                    "\033[1;31mThis extension is not yet supported"
                )
    

    def generator(self):
        for i in product(self.charset, repeat=self.generator_length):
            yield ''.join(i)


    def bruteforce_attack(self):
        exec_start = time.perf_counter()

        for i in range(self.min_password_length, self.max_password_length):
            self._tqdm_total = len(self.charset) ** i
            self.generator_length = i
            
            print(f"\n[#] Bruteforcing passwords length {i}")
            
            result = self._start()

            if result is not None:
                exec_time = round(time.perf_counter() - exec_start, 2)

                print(f"\n[+]\033[1;32m Password FOUND: {result}\033[1;0m\n")
                print(f"[#] Attack finished in {exec_time} seconds") 
                break
            
            i += 1


    def _start(self):
        bar = tqdm(total=self._tqdm_total)

        with Pool(self.max_concurent_worker) as executor:

            for result in executor.imap_unordered(
                self._forcing_function,
                self.generator()
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
            with pikepdf.open(self.target, password=passwd):
                return passwd

        except pikepdf.PasswordError:
            pass
        except Exception as error:
            print(error)

        return None


    def open_zip(self, passwd):
        pwd = bytes(passwd, 'utf-8')
        
        with ZipFile(self.target) as zip:
            try:
                zip.extractall(pwd=pwd)
                return passwd
            except:
                pass

        return None


if __name__ == '__main__':

    brutus = Brutus('/data/test-protected.pdf')
    brutus.bruteforce_attack()
