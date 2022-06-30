#!/usr/bin/env python

import requests
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup

def getCSRF(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf = soup.find(id="csrf_token").get('value')
    return csrf

def cookiesToDict(cookies):
    simple_cookie = SimpleCookie(cookies)
    cookiesDict = {}
    for key, morsel in simple_cookie.items():
        cookiesDict[key] = morsel.value
    return cookiesDict

def preprocess(req):
    # Initiate response
    r = None

    # Request url
    url = req.get_full_url()

    # Get set cookie
    req_cookies = req.get_header("Cookie")
    if req_cookies:
        decoded_cookies = req_cookies.decode('ascii')
        cookiesDict = cookiesToDict(decoded_cookies)
        if "PHPSESSID" in cookiesDict:
            r = requests.get(url, cookies= {"PHPSESSID": cookiesDict["PHPSESSID"]})
    else:
        # Gets phpsessid from first request
        r = requests.get(url)
        phpsessid = r.cookies.get("PHPSESSID")
        # Sets req phpsessid
        req.add_header("Cookie", f"PHPSESSID={phpsessid}")

    csrf = getCSRF(r.text)
    if req.data:
        data = req.data.decode("utf-8") + f"&csrf_token={csrf}"
        req.data = data.encode()