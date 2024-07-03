#  Web Crawler  - UCI project

This Python web crawler is designed to crawl the web and downloading the content of each crawled page. This crawler respects the politeness delay for each site and checks if crawling is allowed using robots.txt. Plus it finds the top 50 most frequently occurring words in the crawled content and saves them in summary.txt
Furthermore, each crawled page will downloaded and saved in a json file in data folder on your system.

# Features:
Crawls web and downlaods each web page.

Processes the content to extract new links.

Avoid traps or loops

Counts the occurrence of each word.

Identifies the top 50 most frequent words.

Outputs the results to summary.txt.

# Dependencies
If you do not have Python 3.6+:

Windows: https://www.python.org/downloads/windows/

Linux: https://docs.python-guide.org/starting/install3/linux/

MAC: https://docs.python-guide.org/starting/install3/osx/

Check if pip is installed by opening up a terminal/command prompt and typing the commands python3 -m pip. This should show the help menu for all the commands possible with pip. If it does not, then get pip by following the instructions at https://pip.pypa.io/en/stable/installing/

To install the dependencies for this project run the following two commands after ensuring pip is installed for the version of python you are using. Admin privileges might be required to execute the commands. Also make sure that the terminal is at the root folder of this project.

python -m pip install packages/spacetime-2.1.1-py3-none-any.whl
python -m pip install -r packages/requirements.txt

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

