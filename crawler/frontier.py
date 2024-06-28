import os
import pickle

from threading import Thread, RLock
from queue import Queue, Empty

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()

        
        if not os.path.exists(self.config.save_file) or  restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
            with open(self.config.save_file, "wb") as f:
                pickle.dump(dict() ,f)
        
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        with open(self.config.save_file, "rb" ) as f :
            self.save = pickle.load(f)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.append(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        try:
            return self.to_be_downloaded.pop()
        except IndexError:
            return None

    def add_url(self, url):
        # does not add url to frontier if its url does not start with seed urls
        url = normalize(url)
        if not self.config.crawl_all_urls:
            valid = [url.startswith(seed) for seed in self.config.seed_urls]
            if not any(valid):
                return
                    
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            self.save[urlhash] = (url, False)
            self.save_to_file()
            self.to_be_downloaded.append(url)
    
    def mark_url_complete(self, url):
         # normalize() was added to make sure when a url is scraped it will not get added to frontier again
        urlhash = normalize(get_urlhash(url)) 
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        self.save[urlhash] = (url, True)
        self.save_to_file()
    
    def save_to_file(self):
        with open(self.config.save_file, "wb") as f:
            pickle.dump(self.save, f)