import numpy as np

geohash_base32 = "0123456789bcdefghjkmnpqrstuvwxyz"

def get_geojson(geohash, properties={}):
    """Return a geojson "feature" format for a geohash

    Arguments: 
        geohash (str): 1 to 12 character geohash string
        properties (dict): dictionary of any associated properties

    Returns:
        dict of geojson structured feature object
    """
    geohash = geohash.lower()

    feature = {'type': 'Feature',
               'properties': {key: value for key, value in properties.items()},
               'geometry': {'type': 'Polygon',
                            'coordinates': []}}

    feature['geometry']['coordinates'].append(get_polygon(geohash))

    return feature
    

def get_polygon(geohash):
    """Get the polygon vertices of a geohash

    Return the polygon vertices comprising the bounding box of
    a geohash. The polygon follows geojson specifications so the
    first/last points are duplicates.

    Arguments:
        geohash (str): 1 to 12 character geohash string

    Returns:
        list of polygon vertices
    """
    bounds = get_bounds(geohash)
    polygon_vertices = [[bounds['sw']['lon'], bounds['sw']['lat']],
                        [bounds['sw']['lon'], bounds['ne']['lat']],
                        [bounds['ne']['lon'], bounds['ne']['lat']],
                        [bounds['ne']['lon'], bounds['sw']['lat']],
                        [bounds['sw']['lon'], bounds['sw']['lat']]]

    return polygon_vertices


def get_bounds(geohash):
    """Get the southwest and northeast coordinates for the boundaries of a geohash.
    
    Providing the geohash string (1 to 12 characters), this function will return
    the southeast and northeast coordinates for the boundaries of the geohash that
    can be used for plotting and other purposes.
    
    Arguments:
        geohash (str): 1 to 12 character geohash string
        
    Returns:
        dict of southwest and northeast latitude and longitude
        {'sw': {'lat': float, 'lon': float}, 'ne': {'lat': float,  'lon': float}}
    """
    geohash = geohash.lower()

    even_bit = True
    latitude_min = -90.0
    latitude_max = 90.0
    longitude_min = -180.0
    longitude_max = 180.0

    for character in geohash:
        index = geohash_base32.find(character)
        if index == -1:
            raise ValueError("Invalid geohash.")
        
        nvals = np.arange(5)[::-1]
        for n in nvals:
            bitN = index >> n & 1
            if even_bit:
                longitude_midpoint = (longitude_min + longitude_max)/2.
                if bitN == 1:
                    longitude_min = longitude_midpoint
                else:
                    longitude_max = longitude_midpoint
            else:
                latitude_midpoint = (latitude_min + latitude_max)/2.
                if bitN == 1:
                    latitude_min = latitude_midpoint
                else:
                    latitude_max = latitude_midpoint
            even_bit = not even_bit
            
    return {'sw': {'lat': latitude_min, 'lon': longitude_min}, 'ne': {'lat': latitude_max, 'lon': longitude_max}}


def decode(geohash):
    """Decode geohash into a latitude/longitude pair
        
    Provide a geohash string (length between 1 and 12) and this
    funtion will return a (latitude, longitude) tuple whose coordinates
    reside at the center/centroid of the geohash.
    
    Arguments:
        geohash (str): string of geohash characters (1 to 12 characters)
        
    Returns:
        tuple of (latitude, longitude)
    """
    bounds = get_bounds(geohash)
    avg_latitude = np.mean([bounds['sw']['lat'], bounds['ne']['lat']])
    avg_longitude = np.mean([bounds['sw']['lon'], bounds['ne']['lon']])

    return (avg_latitude, avg_longitude)


def encode(latitude, longitude, precision):
    """Encode a latitude/longitude pair as a geohash string.
    
    Providing a latitude and longitude in decimal degrees, and specify
    a geohash precision (number of characters in the string); this function will
    encode the point as a geohash and return the string of characters.
    
    Geohash length        Cell width   Cell height
                 1	<=  5,000 km  x   5,000 km
                 2	<=  1,250 km  x     625 km
                 3	<=    156 km  x     156 km
                 4	<=   39.1 km  x    19.5 km
                 5	<=   4.89 km  x    4.89 km
                 6	<=   1.22 km  x    0.61 km
                 7	<=     153 m  x      153 m
                 8	<=    38.2 m  x     19.1 m
                 9	<=    4.77 m  x     4.77 m
                10	<=    1.19 m  x    0.596 m
                11	<=    149 mm  x     149 mm
                12	<=   37.2 mm  x    18.6 mm

    Arguments:
         latitude (float): latitude in decimal degrees
        longitude (float): longitude in decimal degrees
          precision (int): precision as an int (1 to 12)
          
    Returns:
        string of geohash characters of precision length
    """
    if precision < 1 or precision > 12:
        raise ValueError("precision must be an integer between 1 and 12")
    
    index = 0
    bit = 0
    even_bit = True
    geohash = ''
    
    lat_min = -90.0
    lat_max = 90.0
    lon_min = -180.0
    lon_max = 180.0
    
    while len(geohash) < precision:
        if even_bit:
            lon_mid = (lon_min + lon_max) / 2.
            if longitude >= lon_mid:
                index = index*2 + 1
                lon_min = lon_mid
            else:
                index = index*2
                lon_max = lon_mid
        else:
            lat_mid = (lat_min + lat_max) / 2.
            if latitude >= lat_mid:
                index = index*2 + 1
                lat_min = lat_mid
            else:
                index = index*2
                lat_max = lat_mid
        
        even_bit = not even_bit
        if bit < 4:
            bit += 1
        else:
            geohash += geohash_base32[index]
            bit = 0
            index = 0
    
    return geohash
