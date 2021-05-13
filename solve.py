from scipy.sparse import csr_matrix, csc_matrix, coo_matrix, lil_matrix
import numpy as np
import json
import shelve
import scipy

#method = one of 'NORMAL_MINFIX', 'DIVMAX', 'DIVDEV', 'LENGTH', 'ELEVATION', 'NORMAL_CLIP', 'MULTIPLY'
def solve(pathstart_nodeid, pathend_nodeid, method = 'MULTIPLY', coeffs = (1, 1)):
    
    print('Loading database')
    
    with open('mapdata') as f:
        jsondata = json.load(f)
    
    elevation_shelve = shelve.open('elevation.shel')
    elevation = elevation_shelve['elevation']
    elevation_shelve.close()
    
    waydata = list(filter(lambda x: x['type'] == 'way', jsondata['elements']))
    nodedata = list(filter(lambda x: x['type'] == 'node', jsondata['elements']))
    
    print('Creating node table')
    
    # node id to matrix index
    nodeid_to_index = {}
    
    # matrix index to node id
    index_to_nodeid = {}
    
    # node id to json data
    nodeid_to_data = {}
    
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
    
    
    import math
    
    print('Calculating loss')
    
    # calculate length and elevation loss
    connection = []
    loss_len = []
    loss_elev = []
    
    for w in waydata:
        for i in range(len(w['nodes']) - 1):
            startpoint = nodeid_to_data[w['nodes'][i]]
            endpoint = nodeid_to_data[w['nodes'][i + 1]]
            elev1 = get_elevation(startpoint['lat'], startpoint['lon'])
            elev2 = get_elevation(endpoint['lat'], endpoint['lon'])
            connection.append([startpoint, endpoint])
            ll = math.sqrt((startpoint['lat'] - endpoint['lat'])**2 + (startpoint['lon'] - endpoint['lon'])**2)
            le = abs(elev1 - elev2)/ll
            loss_len.append(ll)
            loss_elev.append(le)
    
    # calculate final loss
    def normalize(x):
        x = np.array(x)
        x = (x - x.mean()) / x.std()
        return x
    
    def divmax(x):
        x = np.array(x)
        return x / x.max()
    
    def divdev(x):
        x = np.array(x)
        return x / x.std()
    
    if method == 'NORMAL_MINFIX':
        loss_len = normalize(loss_len)
        loss_elev = normalize(loss_elev)
        loss_len += -loss_len.min() + 0.1
        loss_elev += -loss_elev.min() + 0.1
        loss = loss_len*coeffs[0] + loss_elev*coeffs[1]
    if method == 'DIVMAX':
        loss_len = divmax(loss_len)
        loss_elev = divmax(loss_elev)
        loss = loss_len*coeffs[0] + loss_elev*coeffs[1]
    if method == 'DIVDEV':
        loss_len = divdev(loss_len)
        loss_elev = divdev(loss_elev)
        loss = loss_len*coeffs[0] + loss_elev*coeffs[1]
    if method == 'LENGTH':
        loss = loss_len
    if method == 'ELEVATION':
        loss = loss_elev
    if method == 'NORMAL_CLIP':
        loss_len = normalize(loss_len)
        loss_elev = normalize(loss_elev)
        loss = loss_len*coeffs[0] + loss_elev*coeffs[1]
        nazo_sum = np.abs(loss).sum()
        loss = np.where(loss>0, loss, nazo_sum)
    if method == 'MULTIPLY':
        loss = np.array(loss_len)*np.array(loss_elev)
    
    print('Making graph matrix')
    
    # prepare matrix
    mat = lil_matrix((len(nodedata), len(nodedata)))
    
    for i, [startpoint, endpoint] in enumerate(connection):
        ind1 = nodeid_to_index[startpoint['id']]
        ind2 = nodeid_to_index[endpoint['id']]
        mat[ind1,ind2] = loss[i]
        mat[ind2,ind1] = loss[i]
    
    print('Solving graph')
    
    matcsr = mat.tocsr()
    
    start_index = nodeid_to_index[pathstart_nodeid]
    destination_index = nodeid_to_index[pathend_nodeid]
    
    result = scipy.sparse.csgraph.shortest_path(matcsr, return_predecessors=True, indices=start_index)[1]
    
    current_index = destination_index
    index_list = [destination_index]
    
    while True:
        current_index = result[current_index]
        index_list.append(current_index)
        if current_index == start_index:
            break
    
    print('Done! Writing results...')
    
    with open('nodeids.results', 'w') as f:
        f.write(str(list(map(lambda x: index_to_nodeid[x], index_list))))
    
    with open('overpass_query.results', 'w') as f:
        f.write('(\n')
        for x in index_list:
            f.write('node(%s);\n' % index_to_nodeid[x])
        f.write(');\n')
        f.write('out;')
