import requests
import cbor
import time

from utils.response import Response

def download(url, config, logger=None):
    # limt request time to 30s and max of 5 tries
    MAX_TRY = 5
    while(MAX_TRY > 0):
        try:
            resp = requests.get(url,timeout=30)
            break
        except requests.exceptions.Timeout:
            print("Request Timed out. Trying again")
            MAX_TRY -= 1
    try:
        if resp and resp.content:
            resp_dict = { "url" :  url, "status" : resp.status_code ,  "response": resp  }
            return Response(resp_dict)
    except (EOFError, ValueError) as e:
        pass
    logger.error(f" Error {resp} with url {url}.")
    return Response({
        "error": f" Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})