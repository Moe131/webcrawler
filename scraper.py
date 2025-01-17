import re , os
import pickle
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from utils.tokenizer import *
from utils.simhash import *
import json

# Dictionary to store common words
commonWords = {}
# Set of unique urls
uniqueURLs = set()
# Dictionary to store robots.txt for urls
robots_cache = {}
# sim hashes of content to detect exact/near duplicate
sim_hashes = set()
# Dictionary of number of times a URL without query has been crawled to  avoid traps
URLCrawlsCount = dict()
# Config
config = None


def scraper(url, resp):
    if not is_response_valid(resp) or not is_content_language_valid(resp) or not is_content_type_valid(resp) or is_duplicate(resp) :
        return list()
    parse(resp)
    links = extract_next_links(url, resp)
    count(url)
    save_progress()
    createSummaryFile() # Create summary file to show the progress
    return [link for link in links if is_valid(link)]

def is_response_valid(resp):
    # Checks if the response is valid
    if resp.status != 200 or resp.raw_response is None:
        return False
    return True

def is_content_type_valid(resp):
    # Checks if the content type is valid
    content_type = resp.raw_response.headers.get('Content-Type')
    if content_type and not 'text/html' in content_type: 
        return False
    return True

def is_content_language_valid(resp):
    # Checks if the content language is valid
    content_lang = resp.raw_response.headers.get('Content-Language')
    if content_lang and 'en' != content_lang: 
        return False
    return True


def extract_next_links(url, resp):
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # parse the HTML using BeautifulSoup
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    # finding all the <a> elements (links) in the HTML file (Note: loops and traps are not handled)
    scrapedLinks = list()    
    for linkElement in soup.find_all("a", href=True) : 
            linkURL = linkElement.get("href", "")
            if linkURL.startswith("https://") or linkURL.startswith("http://") or linkURL.startswith("/"): # do not add if its not a link
                    parsed = urlparse(linkURL)
                    next_url = parsed._replace(fragment= "").geturl()
                    scrapedLinks.append(urljoin(url, next_url))
    return scrapedLinks 


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not isWithinSeeds(url):
            return False
        if is_url_query_trap(parsed):
            return False
        if not isScrapable(url):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|txt)$", parsed.geturl().lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def isWithinSeeds(url):
    """Check if a URL is within the seed URLs defined in the config."""
    if not config.crawl_all_urls :
        valid = [url.startswith(seed) for seed in config.seed_urls]
        if not any(valid):
            return False
    return True


def is_url_query_trap(parsed):
    """ Checks if URL without query part has been already crawled more than the TRESHOLD, if so its a trap"""
    TRESHOLD = 5
    url = parsed._replace(fragment = "", query="").geturl()
    if url in URLCrawlsCount and URLCrawlsCount[url] > 5:
        return True
    else:
        return False


def is_duplicate(resp):
    """ Checks if content is exact or near duplicate of already scraped web pages. """
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    content = soup.get_text()
    # store the hash and check if its exat duplicate
    tokenFreq = tokenize(content)
    simhash = simHash(tokenFreq)
    # check exact dupliacte
    if simhash in sim_hashes: 
        return True
    # check near dupliactes
    for sh in sim_hashes:
        if are_near_duplicate(sh, simhash):
            return True
    # store the hash if its not already stored
    sim_hashes.add(simhash)
    return False


def createSummaryFile():
    """ Creates summary.txt with the numer of unique URLs and the
        top 50 words in the crawled pages """
    with open("summary.txt" , 'w') as summaryfile:
        # sorted the dictionary and obtains the 50 most common words
        summaryfile.write("The top 50 common words in the crawled URLs are :\n")
        for word, count in top_words():
            summaryfile.write(f"{word} : {count}\n")
        summaryfile.write("\nTotal Unique URLs found : ")
        summaryfile.write(str(len(uniqueURLs)))

def add_words(dictionary):
    """ adds the words and their counts of each URL to the global dictionary  """
    # update the commonWords dictionary from summary.txt if its empty
    for word, count in dictionary.items():
        if word in commonWords:
            commonWords[word] += count
        else:
            commonWords[word] = count


def count(url):
    """ Counts 3 things:
      First: The total number of unique URLs visited, 
      Second: The number of subdomains visited, 
      Third: The nubmer of times a URL without query part has been crawled """
    # If URL is unique add it to the list of unique URLs
    if "www." in url:
        url = url.replace("www.", "")
    parsed = urlparse(url)
    urldeletedFragment = parsed._replace(fragment = "").geturl() 
    uniqueURLs.add(urldeletedFragment)

    # Count the number of crawls for URL without query 
    URLwithoutQuery = parsed._replace(fragment = "", query="").geturl()
    if URLwithoutQuery in URLCrawlsCount:
        URLCrawlsCount[URLwithoutQuery] += 1
    else:
        URLCrawlsCount[URLwithoutQuery] = 1


def top_words():
    """ Finds the 50 most common words in the entire set of pages """
    # sorted the dictionary and obtains the 50 most common words
    return sorted(commonWords.items(), key=lambda x: x[1], reverse=True)[:50]


def isScrapable(url):
    """ This method checks the /robots.txt of a url and returns True if
        we are allowed to scrape it and False otherwise"""
    try:
        hostPath = removePath(url)
        robotsURL = hostPath + "/robots.txt"
        if robotsURL in robots_cache:
            rbParser = robots_cache[robotsURL]
        else:
            rbParser = RobotFileParser()
            rbParser.set_url(robotsURL)
            rbParser.read()
            robots_cache[robotsURL] = rbParser

        return rbParser.can_fetch("*", url)

    except Exception as e:
        return False
    

def removePath(url):
    """ This method keep the host name of the domain and reomves
      all the remaining path"""
    parsedURL = urlparse(url)
    return f"{parsedURL.scheme}://{parsedURL.netloc}"


def save_progress():
    """ Stores all the data from scraped URLs to save the progress in case program is stopped """
    os.makedirs('pickles', exist_ok=True)
    with open("pickles/crawled.pickle", "wb") as f:
        pickle.dump((commonWords, uniqueURLs, robots_cache, sim_hashes, URLCrawlsCount), f)


def load_progress(restart):
    """ Loads all the data from previous scraped URLs"""
    os.makedirs('pickles', exist_ok=True)
    global commonWords, uniqueURLs, robots_cache, sim_hashes, URLCrawlsCount
    if restart: # If crawler is restarted all data will be reset
        return
    try:
        with open("pickles/crawled.pickle", "rb") as f:
            commonWords, uniqueURLs, robots_cache, sim_hashes , URLCrawlsCount = pickle.load(f)
    except FileNotFoundError:
        # If the file doesn't exist
        commonWords = {}
        uniqueURLs = set()
        robots_cache = {}
        sim_hashes = set()
        URLCrawlsCount= dict()


######################################################################
# You can modify this method to parse the page however you want.
####################################################################
def parse(resp):
    """ Parse the web page """
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        # read the parsed content and check for duplication
    content = soup.get_text(separator=' ',strip=True)
    add_words(tokenize(content))

    # download content is json format
    download_page(resp.raw_response.url, soup)


def download_page(url, soup):
    """ saves the content in json format """
    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)
    # Extract title and content
    title = soup.find("title").get_text(separator=' ',strip=True) if soup.find("title") else url
    data = {'url': url, 'title': title, 'content': soup.get_text(separator=' ',strip=True)}
    # Save the JSON data to a file
    url = url.lstrip("https://").rstrip("/").replace("/","-")
    with open(f'data/{url}.json', 'w') as f:
            json.dump(data, f)