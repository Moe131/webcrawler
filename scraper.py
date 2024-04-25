import re
import pickle
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from tokenizer import *

# Dictionary to store common words
commonWords = {}
# Set of unique urls
uniqueURLs = set()
# Dictionary to store robots.txt for urls
robots_cache = {}
# Longest page in terms of words
longest_page = ("",0)
# Dictionary of unique subdomains of ics.uci.edu
ICS_subdomains = {}



def scraper(url, resp):
    # if retrieving the page was NOT successful return empty list of links
    if resp.status != 200 or resp.raw_response is None:
        return list()
    # if content type is not HTML ignore it
    content_type = resp.raw_response.headers.get('Content-Type')
    if content_type and not 'text/html' in content_type: 
        return list()
    count_if_unique(url)
    links = extract_next_links(url, resp)
    add_words(find_word_frquency(url, resp))
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
    scrapedLinks = list()    
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        
    # finding all the <a> elements (links) in the HTML file (Note: loops and traps are not handled)
    for linkElement in soup.find_all("a", href=True) : 
            linkURL = linkElement.get("href", "")
            if linkURL.startswith("https://") or linkURL.startswith("http://") or linkURL.startswith("/"): # do not add if its not a link
                    parsed = urlparse(linkURL)
                    next_url = parsed._replace(query= "").geturl()
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
        if not isWithinDomain(parsed):
            return False
        if repetitive(url):
            return False
        if not isScrapable(url):
            return False
        if too_deep(url):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|txt)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise



def isWithinDomain(parsedURL):
    """ Checks if the URL is within *.ics.uci.edu/* ,  *.cs.uci.edu/* ,and
      *.informatics.uci.edu/* , *.stat.uci.edu/* domains """
    hostPath = parsedURL.netloc
    if not ( ("ics.uci.edu" in hostPath) or ("cs.uci.edu" in hostPath) or 
            ("informatics.uci.edu" in hostPath) or ("stat.uci.edu" in hostPath) ):
        return False
    else:
        return True


def find_word_frquency(url, resp) ->  dict :
    """ Reads the content of a URL and returns a dictionary
        with words and their frequencies in that page """
     # if resp.status is not 200 return 
    if resp.status != 200:
        return dict() 
    
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    bodyContent = soup.find("body")
    listOfWords = list()

    # check if url has body
    if bodyContent :
        bodyText = bodyContent.get_text()
    else:
        bodyText = ""

     # check if the page has low text value
    if lowTextValue(bodyText):
        return dict()
    
    # if the file size is too large do not index it and return empty dict
    MAXBODYSIZE = 10000
    if len(bodyText) <= MAXBODYSIZE:
        listOfWords = tokenize(bodyText)
        #Check if longest page
        global longest_page
        if (len(listOfWords) > longest_page[1]):
            longest_page = (url, len(listOfWords))
        return computeWordFrequencies(listOfWords)
    return dict()

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

        summaryfile.write(f"\n\nNumber of subdomains in the ics.uci.edu domain : {len(ICS_subdomains)}\n")
        for key in sorted(ICS_subdomains.keys()):
                summaryfile.write(f"\n{key} : {ICS_subdomains[key]}\n")


def add_words(dictionary):
    """ adds the words and their counts of each URL to the global dictionary  """
    # update the commonWords dictionary from summary.txt if its empty
    for word, count in dictionary.items():
        if word in commonWords:
            commonWords[word] += count
        else:
            commonWords[word] = count


def count_if_unique(url):
    parsed = urlparse(url)
    urldeletedFragment = parsed._replace(fragment = "").geturl() 
    uniqueURLs.add(urldeletedFragment)
    if "ics.uci.edu" in url:
        subdomain = parsed._replace(scheme= "https", path="",fragment = "", query="").geturl()
        if subdomain in ICS_subdomains:
            ICS_subdomains[subdomain] += 1
        else:
            ICS_subdomains[subdomain] = 1


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
    

def repetitive(url):
    """ Checks for repeating segments Note! this is a work in progress. """
    sectionDict = {}
    section = url.split("/")
    current = None
    for i in section:
        if i in sectionDict:
            sectionDict[i] += 1
            if sectionDict[i] >= 3:
                return True
        else:
            sectionDict[i] = 1
    return False


def too_deep(url):
    """ Checks if depth of URL go over a maximum value. """
    depth = urlparse(url).path.strip("/").count("/")
    maxAmount = 10
    if depth > maxAmount:
        return True
    return False

def lowTextValue(bodyContent):
    """ Checks for pages that have low information value. """
    errors = ["Error", "Whoops", "having trouble locating" , "404"]
    for word in errors:
        if word.lower() in bodyContent.lower():
            return True
    if len(bodyContent.split()) < 500:
        return True
    return False

def removePath(url):
    """ This method keep the host name of the domain and reomves
      all the remaining path"""
    parsedURL = urlparse(url)
    return f"{parsedURL.scheme}://{parsedURL.netloc}"

def save_data():
    """ Stores all the data from scraped URLs to save the progress in case program is stopped """
    with open("scrapedData.pickle", "wb") as f:
        pickle.dump((commonWords, uniqueURLs, robots_cache, longest_page, ICS_subdomains), f)


def load_data(restart):
    """ Loads all the data from previous scraped URLs"""
    global commonWords, uniqueURLs, robots_cache, longest_page, ICS_subdomains
    if restart: # If crawler is restarted all data will be reset
        return
    try:
        with open("scrapedData.pickle", "rb") as f:
            commonWords, uniqueURLs, robots_cache, longest_page, ICS_subdomains = pickle.load(f)
    except FileNotFoundError:
        # If the file doesn't exist
        commonWords = {}
        uniqueURLs = set()
        robots_cache = {}
        longest_page = ("", 0)
        ICS_subdomains = {}