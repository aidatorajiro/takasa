import sys
from config import pathbound_small, pathbound_large

latlon_from = pathbound_small
latlon_to = pathbound_large

uri = "https://lz4.overpass-api.de/api/interpreter"

query = "[out:json];way[highway](%s,%s,%s,%s);(._;>;);out;" % (latlon_from[0], latlon_from[1], latlon_to[0], latlon_to[1])

import requests

r = requests.post(uri, data=query)

with open('mapdata', 'w') as f:
    f.write(r.text)
