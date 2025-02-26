# Program to pull propagation data from hamqsl
# Data the to be relayed via twitter.

import telnetlib3
import urllib3
import xmltodict

#Access website and pull data

http = urllib3.PoolManager()
r = http.request('GET', 'http://hamqsl.com/solarxml.php')
#print(str(r.data))

#try to make sense of data

doc = xmltodict.parse(r.data)

#print(doc)

solarIndex = doc['solar']['solardata']['solarflux']
#print('Solar index: ', solarIndex)

updated = doc['solar']['solardata']['updated']
topband = doc['solar']['solardata']['calculatedconditions']['band'][0]['#text']
thirty = doc['solar']['solardata']['calculatedconditions']['band'][1]['#text']
seventeen = doc['solar']['solardata']['calculatedconditions']['band'][2]['#text']
twelve = doc['solar']['solardata']['calculatedconditions']['band'][3]['#text']
topbandn = doc['solar']['solardata']['calculatedconditions']['band'][4]['#text']
thirtyn = doc['solar']['solardata']['calculatedconditions']['band'][5]['#text']
seventeenn = doc['solar']['solardata']['calculatedconditions']['band'][6]['#text']
twelven = doc['solar']['solardata']['calculatedconditions']['band'][7]['#text']


#print('Band      Day    Night')
#print('80m-40m: ', topband, ' ', topbandn)
#print('30m-20m: ', thirty, ' ', thirtyn)
#print('17m-15m: ', seventeen, ' ', seventeenn)
#print('12m-10m: ', twelve, ' ', twelven)

steve = """Updated at {}

Solar Flux Index: {}

Band      Day      Night
80m-40m   {}     {}
30m-20m   {}     {}
17m-15m   {}     {}
12m-10m   {}     {}"""

print(steve.format(updated, solarIndex, topband, topbandn, thirty, thirtyn,seventeen, seventeenn, twelve, twelven))