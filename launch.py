from configparser import ConfigParser
from argparse import ArgumentParser

from utils.config import Config
from crawler import Crawler
import scraper
import os

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    scraper.config = config
    scraper.load_progress(restart)
    crawler = Crawler(config, restart)
    crawler.start()


if __name__ == "__main__":
    # Check if directory exists
    if not os.path.exists("data"):
        os.makedirs("data")
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)


