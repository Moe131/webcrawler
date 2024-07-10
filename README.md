# Web Crawler - UCI Project

This Python web crawler is designed to crawl the web by extracting new links from web pages and downloading the content of each crawled page. It respects the politeness delay for each site and checks if crawling is allowed using robots.txt. Additionally, it finds the top 50 most frequently occurring words in the crawled content and saves them in `summary.txt`. Each crawled page will be downloaded and saved in a JSON file in the `data` folder on your system.

## Features

- Crawls the web and downloads each web page.
- Processes the content to extract new links.
- Avoids traps or loops and avoids downloading duplicate pages.
- Counts the occurrence of each word.
- Identifies the top 50 most frequent words.
- Outputs the results to `summary.txt`.

# Dependencies

To install the dependencies for this project run the following two commands after ensuring pip is installed for the version of python you are using. Admin privileges might be required to execute the commands. Also make sure that the terminal is at the root folder of this project.
```
python -m pip install packages/spacetime-2.1.1-py3-none-any.whl
python -m pip install -r packages/requirements.txt
```

# Run the crawler

 ## step 1: Configure the crawler by updating config.ini file :


- provide your seed urls separated by comma

```
SEEDURL = https://www.ics.uci.edu,https://www.cs.uci.edu  
```

- If you want to allow all urls to be crawled, inside config.ini set CRAWLALL to TRUE. Otherwise, only URLs that begin with the seed URLs will be crawled.

```
CRAWLALL = TRUE
```
- You can change the time wait in seconds between each request.

```
POLITENESS = 0.5
```

 ## Step 2: Run the crawler by running the following command

```
python3 launch.py
```

If you wish to restart the crawler, run :
```
python3 launch.py --restart
```

# Custom Parsing
You can customize the way you want to parse each web page. To customize the parsing, modify the **'parse()'** method inside **'scraper.py'**.

```
def parse(resp):
    """ Parse the web page """
    # Your Custom Parsing
```
