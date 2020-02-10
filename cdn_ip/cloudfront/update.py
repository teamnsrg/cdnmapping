#!/usr/bin/env python3

import json
import urllib.request
import ssl
from pprint import pprint

cont = ssl.SSLContext()

# https://ip-ranges.amazonaws.com/ip-ranges.json
contents = urllib.request.urlopen('https://ip-ranges.amazonaws.com/ip-ranges.json', context=cont)
data = json.loads(contents.read())

for d in data['prefixes']:
    if d['service'] == 'CLOUDFRONT':
        print(d['ip_prefix'])
