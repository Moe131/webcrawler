import requests
import cbor
import time

from utils.response import Response

def download(url, config, logger=None):
    resp = requests.get(url)
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