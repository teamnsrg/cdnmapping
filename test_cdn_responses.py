#!/usr/bin/env python3

import subprocess
import random
import csv
from pprint import pprint

cdn = 'quantil'

f = open('out.csv','r')
reader = csv.reader(f)

ips = set()
domains = set()

for row in reader:
    if row[2] == cdn:
        ips.add(row[1])
        domains.add(row[0])
f.close()


success = 0
failure = 0

fcodes = {}

while(True):

    domain = random.sample(domains,1)[0]
    ip = random.sample(ips,1)[0]

    print('Trying %s at %s...' % (domain, ip),)

    good = False

    output = subprocess.getoutput("curl -k -I --resolve %s:443:%s https://%s" % (domain,ip,domain))
    code = ''
    try:
        code = ''
        for line in output.split('\n'):
            if line.startswith('HTTP'):
                code = line.split()[1]
        if code == '':
            print('Did not get initial code:')
            print(output)
    except:
        print('EXCEPTION: ', output)
        continue
    if code.startswith('2'):
        good = True
    elif code.startswith('3'):
        tries = 0
        while code.startswith('3') and tries < 5:
            tries += 1
            # Set new domain
            retries = False
            for line in output.split('\n'):
                if line.startswith('Location:') or line.startswith('location:'):
                    retries = True
                    if line.split()[-1].startswith('http://'):
                        domain = line.split()[-1].replace('http://','').strip('/')
                        print('New domain is %s, only we are now using http' % domain)
                        output = subprocess.getoutput("curl -k -s -I -m10 --resolve %s:80:%s http://%s" % (domain,ip,domain))
                    else:
                        domain = line.split()[-1].replace('https://','').strip('/')
                        print('New domain is %s' % domain)
                        output = subprocess.getoutput("curl -k -s -I -m10 --resolve %s:443:%s https://%s" % (domain,ip,domain))
                    try:
                        code = ''
                        for line in output.split('\n'):
                            if line.startswith('HTTP'):
                                code = line.split()[1]
                    except:
                        print('EXCEPTION: ', output)
                        continue
                    if code.startswith('2'):
                        good = True
                    else:
                        pass
            if not retries:
                print('DID NOT RETRY:')
                print(output)

    if good:
        success += 1
    else:
        print('Failed (Code %s)' % code)
        if code not in fcodes:
            fcodes[code] = 0
        fcodes[code] += 1
        failure += 1
    
    print('----------------------------------------------')
    print('CDN: %s' % cdn)
    print('Picking randomly from %d domains and %d IPs hosted on %s' % (len(domains), len(ips), cdn))
    print('success: %d, failure: %d, success rate: %f' % (success, failure, success / (success +failure)))
    print('Failure codes:')
    pprint(fcodes)
    print('----------------------------------------------')
    if success + failure >= 100:
        quit()


