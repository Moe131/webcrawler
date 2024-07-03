import re
import pickle
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from tokenizer import *
from simhash import *
import json

# Dictionary to store common words
commonWords = {}
# Set of unique urls
uniqueURLs = set()
# Dictionary to store robots.txt for urls
robots_cache = {}
# Longest page in terms of words
longest_page = ("",0)
# sim hashes of content to detect exact/near duplicate
sim_hashes = set()
# Dictionary of number of times a URL without query has been crawled to  avoid traps
URLCrawlsCount = dict()
# Config
config = None


def scraper(url, resp):
    # if retrieving the page was NOT successful return empty list of links
    if resp.status != 200 or resp.raw_response is None:
        return list()
    # if content type is not HTML ignore it
    content_type = resp.raw_response.headers.get('Content-Type')
    content_lang = resp.raw_response.headers.get('Content-Language')
    if content_type and not 'text/html' in content_type: 
        return list()
    if content_lang and 'en' != content_lang: 
        return list()
    count(url)
    links = extract_next_links(url, resp)
    createSummaryFile()  # later we should we move this to the end of launch.py
    save_data()
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
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
    
    # read the parsed content and check for duplication
    content = read_content(url, soup)
    if len(content) == 0: #If content is not worth scraping return 
        return list()
    add_words(content)

    # download content is json format
    download_page(resp.raw_response.url, soup)

    # finding all the <a> elements (links) in the HTML file (Note: loops and traps are not handled)
    scrapedLinks = list()    
    for linkElement in soup.find_all("a", href=True) : 
            linkURL = linkElement.get("href", "")
            if linkURL.startswith("https://") or linkURL.startswith("http://") or linkURL.startswith("/"): # do not add if its not a link
                    parsed = urlparse(linkURL)
                    next_url = parsed._replace(fragment= "").geturl()
                    scrapedLinks.append(urljoin(url, next_url))
    return scrapedLinks 

def download_page(url, soup):
    """ saves the content in json format """
    data = {'url':url, 'content':soup.get_text(strip=True)}
    # Save the JSON data to a file
    with open(f'data/{url.replace("/","")}.json', 'w') as f:
            json.dump(data, f)

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


def is_duplicate(tokenFreq):
    """ Checks if a text represented as dictionary of words with their frequencies
        is exact or near duplicate of already scraped websites. """
    # store the hash and check if its exat duplicate
    simhash = simHash(tokenFreq)
    if simhash in sim_hashes: # exact dupliacte
        return True
    
    for sh in sim_hashes:
        if are_near_duplicate(sh, simhash):
            return True
    # store the hash if its not already stored
    sim_hashes.add(simhash)
    return False


def read_content(url, soup) ->  dict :
    """ Reads the content of a URL and returns a dictionary
        with words and their frequencies in that page. If content is duplicate
         or low value returns an empty dictionary """
    bodyContent = soup.find("body")
    # check if url has body
    if bodyContent :
        bodyText = bodyContent.get_text()
    else:
        bodyText = ""
    
    # check if the page has low text value
    if lowTextValue(bodyText):
        return dict()

    tokenFreq = tokenize(bodyText)

    #if duplicate return 
    if is_duplicate(tokenFreq):
        return dict()
    
    #Check if longest page
    global longest_page
    pageLength = sum(tokenFreq.values())
    if pageLength > longest_page[1]:
        longest_page = (url, pageLength)
    return tokenFreq


def createSummaryFile():
    """ Creates summary.txt with the numer of unique URLs and the
        top 50 words in the crawled pages """
    with open("summary.txt" , 'w') as summaryfile:
        #lists the page with the most words
        summaryfile.write(f"The longest page in terms of words is at: {longest_page[0]} with {longest_page[1]} words\n\n")
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
    

def lowTextValue(text):
    """ Checks for pages that have low information value. """
    errors = ["Error", "Whoops", "having trouble locating"]
    isError = False
    wordCount = len(text.split())
    for word in errors:
        if word.lower() in text.lower():
            IsError = True
    # Page has error message content
    if wordCount < 500 and isError :
        return True
    # Page has no content
    if wordCount < 50 :
        return True
    return False


def removePath(url):
    """ This method keep the host name of the domain and reomves
      all the remaining path"""
    parsedURL = urlparse(url)
    return f"{parsedURL.scheme}://{parsedURL.netloc}"


def save_data():
    """ Stores all the data from scraped URLs to save the progress in case program is stopped """
    with open("crawled.pickle", "wb") as f:
        pickle.dump((commonWords, uniqueURLs, robots_cache, longest_page, sim_hashes, URLCrawlsCount), f)


def load_data(restart):
    """ Loads all the data from previous scraped URLs"""
    global commonWords, uniqueURLs, robots_cache, longest_page, sim_hashes, URLCrawlsCount
    if restart: # If crawler is restarted all data will be reset
        return
    try:
        with open("crawled.pickle", "rb") as f:
            commonWords, uniqueURLs, robots_cache, longest_page, sim_hashes , URLCrawlsCount = pickle.load(f)
    except FileNotFoundError:
        # If the file doesn't exist
        commonWords = {}
        uniqueURLs = set()
        robots_cache = {}
        longest_page = ("", 0)
        sim_hashes = set()
        URLCrawlsCount= dict()
