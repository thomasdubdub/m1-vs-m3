import json

path_outline_width = 3
path_width = 3
path_lead_time = 0
path_trail_time = 100000
path_resolution = 5
point_outline_width = 2
point_pixel_size = 6
point_height_reference = "NONE"
m1_color = [255, 102, 0, 150] # orange
m3_color = [0, 153, 255, 150] # blue
color = [m1_color, m3_color]

def get_start_stop(df):
    starttime = str(min(df['datetime_begin'])).replace(" ", "T").replace(".000", "Z")
    stoptime = str(max(df['datetime_end'])).replace(" ", "T").replace(".000", "Z")
    availability = starttime + "/" + stoptime
    return (starttime, stoptime, availability)

def get_4D_coords(group):
    coords = []
    t = 0
    for _,row in group.iterrows():
        coords.extend([t, row['lon_begin'], row['lat_begin'], row['alt_begin (m)']])
        t += row['duration']
    return coords

def get_path(group, path_id, starttime, availability, color):
    path = {
        "id": path_id,
        "availability": availability,
        "position": {
            "epoch": starttime,
            "cartographicDegrees": get_4D_coords(group)
        },
        "path": {
            "material": {
                "polylineOutline": {
                    "color": {
                        "rgba": color
                    },
                    "outlineColor": {
                        "rgba": color 
                    },
                    "outlineWidth": path_outline_width
                }
            },
            "width": path_width,
            "leadTime": path_lead_time,
            "trailTime": path_trail_time,
            "resolution": path_resolution
        }
    }
    return path
    
def get_point(group, point_id, starttime, availability, color):
    point = {
        "id": point_id,
        "availability": availability,
        "position": {
            "epoch": starttime,
            "cartographicDegrees": get_4D_coords(group)
        },
        "point": {
            "color": {
                "rgba": [255,255,255,200] # white center instead of color
            },
            "outlineColor": {
                "rgba": color
            },
            "outlineWidth": point_outline_width,
            "pixelSize": point_pixel_size,
            "heightReference": point_height_reference
        }   
    }
    return point

def czml(df_list, file_path, path=True, point=True):
    czml_output = []
    starttime, _, availability = get_start_stop(df_list[0])
    global_element = {
                "id": "document", 
                "name": "m1vsm3", 
                "version": "1.0", 
                "author": "your_name", "clock": {"interval": availability, 
                                                  "currentTime": starttime, 
                                                  "multiplier": 100
                                                }
                }
    czml_output.append(global_element)
    index = 0
    for df in df_list:
        for name, group in df.groupby('flight_identifier'):
            starttime, _, availability = get_start_stop(group)
            name = str(name) + str(index)
            if path:
                czml_output.append(get_path(group, name, starttime, availability, color[index]))
            if point:
                czml_output.append(get_point(group, name, starttime, availability, color[index]))
        index += 1
    with open(file_path, 'w') as outfile:
        json.dump(czml_output, outfile)