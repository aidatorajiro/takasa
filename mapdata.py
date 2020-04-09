import sys

latlon_from = [float(sys.argv[1]), float(sys.argv[2])]
latlon_to = [float(sys.argv[3]), float(sys.argv[4])]

uri = "https://lz4.overpass-api.de/api/interpreter"

query = "[out:json];way[highway](%s,%s,%s,%s);(._;>;);out;" % (latlon_from[0], latlon_from[1], latlon_to[0], latlon_to[1])

import requests

r = requests.post(uri, data=query)

with open('mapdata', 'w') as f:
    f.write(r.text)
