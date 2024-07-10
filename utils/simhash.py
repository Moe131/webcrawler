import hashlib
from utils.tokenizer import *

def find_256bit_hash(word, freq):
    """ Use SHA-256 to hash the string into 32 bytes and find
        the hash considering its frequency """
    sha256_hash = hashlib.sha256(word.encode()).digest()
    result = [0] * 256  # Initialize a list of 256 zeros
    for i, byte in enumerate(sha256_hash):
        for j in range(8):
            if (byte >> j) & 1:  # Check if the j-th bit of the byte is set
                result[i*8 + j] += freq  # Add frequency if the bit is 1
            else:
                result[i*8 + j] -= freq  # Subtract frequency if the bit is 0
    return result
    
def simHash(d):
    """ Returns the sim hash code of the dictionary of words and their frequency"""
    result = [0] * 256  # Initialize a list of 256 zeros
    for token, freq in d.items():
        result = [x + y for x, y in zip(result, find_256bit_hash(token, freq))]
    
    # Convert each integer in the result list to its binary representation
    binary_result = [1 if x > 0 else 0 for x in result]
    
    # Combine the binary representations into a single 256-bit binary string
    binary_string = ''.join(map(str, binary_result))
    
    return binary_string
    
def are_near_duplicate(simhash1, simhash2):
    """ Checks if two texts are near duplicate with a certain Treshold"""
    TRESHOLD = 0.95
    counter = 0
    for i in range(256):
        if simhash1[i] == simhash2[i]:
            counter += 1
    return counter/256.0 > TRESHOLD
