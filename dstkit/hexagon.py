from h3 import h3

def encode(lat, lon, resolution=3):
    """Encode a lat/lon pair to an h3 address"""
    return h3.geo_to_h3(lat, lon, res=resolution)

def decode(h3_address):
    """Decode an h3 address to a lat/lon pair"""
    return h3.h3_to_geo(h3_address)

def hexagon_from_h3(h3_address):
    """Get a geojson hexagon from h3 address"""
    return {"type": "Polygon",
            "coordinates": [h3.h3_to_geo_boundary(h3_address, geo_json=True)]
           }

def hexagon_from_location(lat, lon, resolution=3):
    """Get a geojson hexagon from a lat/lon pair"""
    return {"type": "Polygon",
            "coordinates": [h3.h3_to_geo_boundary(encode(lat, lon, res=resolution), geo_json=True)]
           }
