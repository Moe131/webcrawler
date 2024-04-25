import sys


# Time complexity of this method is constant O(1) because it only
# iterates through a constant sized string
def isAlphaNum(ch:str) -> bool:
    ''' Checks if a character is number or american letter  '''
    english_letters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    if ch in english_letters:
        return True
    else:
        return False


# Time complexity of this method is linear  O(n) if n is 
# the number of 100bytes in file. The method iterates through 
# the characters(bytes) one by one. Since the inner for loop iterates
# overs a fixed number of bytes it does not change the time complexity.
def tokenize(text: str) -> list:
	''' reads in a text and returns a list of the tokens in that string '''
	tokensList = []
	token = ""
	for ch in text + " ":
		if isAlphaNum(ch):
			token += ch
		else:
			if token != "":
				tokensList.append(token.lower())
				token = "" 
	return tokensList


# Time complexity of this method is linear  O(n) if n is the
# number  of tokens in the list. The method iterates through 
# the tokens  one by one in one for loop
def computeWordFrequencies(tokensList: list) -> dict:
	''' counts the number of occurrences of each
	token in the token list and returns them in a dictionary '''
	d = {}
	stopwords = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 
                 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 
                 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', 
                 "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 
                 "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 
                 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", 
                 "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 
				 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 
				 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', 
				 "she'd", "she'll", "she's",'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 
				 'their', 'theirs', 'them', 'themselves','then', 'there', "there's", 'these', 'they', "they'd", "they'll", 
				 "they're", "they've", 'this', 'those', 'through', 'to','too', 'under', 'until', 'up', 'very', 'was', "wasn't", 
				 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 
				 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", 
				 "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'}
	for word in tokensList:
		if word not in stopwords:
			if not word in d.keys():
				d[word] = 1
			else:
				d[word]+= 1
	return d


# Time complexity of this method is log-linear  O(n log n). The sorted() 
# method has a complexity of O(n log n) and the for loop has a time
# time complexity of O(n). Therefore the time complexity of thr whole
# method is the higher order term which is n log n
def printFrequencies(frequencies: dict) -> None:
	''' prints out the word frequency count'''
	sortedTuple = sorted(frequencies.items(), key= lambda x:x[1], reverse = True)
	for key, value in sortedTuple:
		print(str(key) + " = " + str(value))