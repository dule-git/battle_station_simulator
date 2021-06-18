from fastkml import kml

LON = 0
LAT = 1
ALT = 2

X = 0
Y = 1
Z = 2

g = 9.81
ro = 1.2

INTERVAL = 100

def read_system_location(kml_file):
    with open(kml_file, 'rt', encoding="utf-8") as file:
        doc = file.read()
    k = kml.KML()
    k.from_string(doc.encode('utf-8'))
    
    root = list(k.features())
    placemarks = list(root[0].features())

    for p in placemarks:
        if p.name == 'SYSTEM_LOCATION':
            SYSTEM_LAT = p.geometry.coords[0][LAT]
            SYSTEM_LON = p.geometry.coords[0][LON]
            SYSTEM_ALT = p.geometry.coords[0][ALT] 
            return SYSTEM_LAT, SYSTEM_LON, SYSTEM_ALT
    