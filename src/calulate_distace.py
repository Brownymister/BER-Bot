import math

def distace_in_km_by_coordinates(x1, y1, x2, y2) -> float:
    lat1 = float(x1) * math.pi / 180
    lon1 = float(y1) * math.pi / 180
    lat2 = float(x2) * math.pi / 180
    lon2 = float(y2) * math.pi / 180

    dist = 6378.388 * math.acos((math.sin(lat1) * math.sin(lat2)) + (math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)))

    #distace in km
    return round(dist, 12)