from scipy.sparse import csr_matrix, csc_matrix, coo_matrix, lil_matrix
import numpy as np
import json
import shelve

with open("mapdata") as f:
    jsondata = json.load(f)

elevation_shelve = shelve.open('elevation.shel')
elevation = elevation_shelve['elevation']
elevation_shelve.close()

waydata = list(filter(lambda x: x['type'] == 'way', jsondata['elements']))
nodedata = list(filter(lambda x: x['type'] == 'node', jsondata['elements']))

# node id to matrix index
nodeid_to_index = {}

# matrix index to node id
index_to_nodeid = {}

# node id to json data
nodeid_to_data = {}

# node id to height
nodeid_to_elevation = {}

# prepare utility hash objects
for i, n in enumerate(nodedata):
    nodeid_to_index[n['id']] = i
    index_to_nodeid[i] = n['id']
    nodeid_to_data[n['id']] = n

def get_elevation(lat, lon):
    for e in elevation:
        xnum = e[4].shape[1]
        ynum = e[4].shape[0]
        xstart = e[0]
        ystart = e[1]
        xsize = e[2]
        ysize = e[3]
        xend = xstart + xsize*xnum
        yend = ystart + ysize*ynum
        if ystart <= lat < yend and xstart <= lon < xend:
            n = int((lat - ystart) / ysize)
            m = int((lon - xstart) / xsize)
            return e[4][n,m]
        else:
            continue
    return None

# prepare matrix
mat = csr_matrix((len(nodedata), len(nodedata)),dtype=np.float32)

for w in waydata:
    for i in range(len(w['nodes']) - 1):
        startpoint = nodeid_to_data[w['nodes'][i]]
        endpoint = nodeid_to_data[w['nodes'][i + 1]]
        elev1 = get_elevation(startpoint['lat'], startpoint['lon'])
        elev2 = get_elevation(endpoint['lat'], endpoint['lon'])
        loss_elev = abs(elev1 - elev2)
        print(loss_elev)






