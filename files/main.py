import requests
import json
import time
import subprocess
from blkinfo import BlkDiskInfo
from getpass import getpass

wled_device_ip = "192.168.1.76"

def rgb_to_hex(rgb):
    return str('%02x%02x%02x' % rgb).upper()
stats = {}
oldstats = {}

def Animate():
    global stats, oldstats
    headers ={'content-type':'application/json'}

    RED = rgb_to_hex((128, 0, 0))
    GREEN = rgb_to_hex((0, 128, 0))
    BLUE = rgb_to_hex((0, 0, 64))
    BLACK = rgb_to_hex((0, 0, 0))

    while True:
        myblkd = BlkDiskInfo()
        disks = myblkd.get_disks()

        for disk in disks:
            name = disk['name']
            cmd = ("sudo hdparm -C /dev/" + name).split()
            hdresult = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding="ascii")
            spin = hdresult.stdout.split(':')[2].strip()
            # print(spin)
            stats[name] = {'reads': disk['statistics']['reads_completed'], 
                        'writes':disk['statistics']['writes_completed'],
                        'power':spin}

        strip=[""] * len(stats)

        for i, disk in enumerate(disks):
            name = disk['name']
            strip[i] = BLACK
            if stats[name]['power'] in ['unknown', 'active/idle']:
                strip[i] = BLUE
            if stats[name]['reads'] != oldstats[name]['reads']:
                strip[i] = GREEN
            if stats[name]['writes'] != oldstats[name]['writes']:
                strip[i] = RED

        json_data = {"seg":{"i":strip}}
        api_endpoint = f"http://{wled_device_ip}/json/state"
        r = requests.post(api_endpoint,data=json.dumps(json_data),headers=headers)

        oldstats = stats.copy()
        time.sleep(0.1)



    colors = { 'RED':[],
    'WHITE':[],
    'BLUE':[]}
    
    stripColors = ['RED','RED','BLUE','BLUE','RED','WHITE','WHITE','WHITE','WHITE','WHITE',
                'RED','RED','RED','RED','RED','WHITE','WHITE','WHITE','WHITE','WHITE',
                'RED','RED','RED','RED','RED','WHITE','WHITE','WHITE','WHITE','WHITE',
                'RED','RED','RED','RED','RED','WHITE','WHITE','WHITE','WHITE','WHITE',
                'RED','RED','RED','RED','RED','WHITE','WHITE','WHITE','WHITE','WHITE',
                'RED','RED','RED','RED','RED','WHITE','WHITE','WHITE','WHITE','WHITE',
                'RED','RED','RED','RED','RED',
                'BLUE','BLUE','BLUE','WHITE','BLUE','BLUE','BLUE','WHITE',
                'BLUE','BLUE','BLUE','WHITE','BLUE','BLUE','BLUE','WHITE',
                'BLUE','BLUE','BLUE','WHITE','BLUE','BLUE','BLUE','WHITE',
                'BLUE','BLUE','BLUE','WHITE','BLUE','BLUE','BLUE','WHITE','BLUE','BLUE','BLUE',
                'RED','RED','RED','WHITE','WHITE','WHITE',
                'RED','RED','RED','WHITE','WHITE','WHITE',
                'RED','RED','RED','WHITE','WHITE','WHITE',
                'RED','RED','RED','WHITE','WHITE','WHITE',
                'RED','RED','RED','WHITE','WHITE','WHITE',
                'RED','RED','RED','WHITE','WHITE','WHITE',
                'RED','RED','RED',
                'BLUE','BLUE','BLUE','WHITE',
                'BLUE','BLUE','BLUE','WHITE',
                'BLUE','BLUE','BLUE','WHITE',
                'BLUE','BLUE','BLUE','WHITE',
                'BLUE','BLUE'
                ]

    animMS = 0.05
    numLEDS = len(stripColors)
    levels = 11
    brightFactor = 256//(levels+2)
    brights = []
    for i in reversed(range(levels)):
        b = 255 - (i*brightFactor)
        brights.append(b)
    
    for i in brights:
        colors['RED'].append(rgb_to_hex((i, 0, 0)))
        colors['WHITE'].append(rgb_to_hex((i, i, i)))
        colors['BLUE'].append(rgb_to_hex((0, 0, i)))
    
    
    stripBrightness = []
    for i in range(levels):
        stripBrightness.append(i)
    for i in reversed(range(1, levels - 1)):
        stripBrightness.append(i)
            
    numBright = len(stripBrightness)
    strip=[""] * numLEDS
    counter = 0
    while True:
        for i in range(numLEDS):
            colorInd = stripBrightness[(i + counter) % numBright]
            strip[i]=colors[stripColors[i]][colorInd]
        strip[0] = GREEN
        json_data = {"seg":{"i":strip}}
        r = requests.post(api_endpoint,data=json.dumps(json_data),headers=headers)
        time.sleep(animMS)
        counter = (counter + 1) % numBright
    
def main():
    global api_endpoint
    
    headers ={'content-type':'application/json'}
    api_endpoint = f"http://{wled_device_ip}/json/info"

    result = requests.get(api_endpoint, headers=headers)
    info = json.loads(result.text)

    api_endpoint = f"http://{wled_device_ip}/json/state"
    
    json_data = {"on":True,"bri":64,"transition":7,"mainseg":0,"seg":[{"id":0,"start":0,"stop":25,"grp":1,"spc":0,"of":0,"on":True,"frz":False,"bri":255,"cct":127,"col":[[128,128,128],[0,0,0],[255,0,0]],"fx":0,"sx":0,"ix":105,"pal":2,"sel":True,"rev":False,"mi":False},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0},{"stop":0}]}
    
    headers ={'content-type':'application/json'}
    r = requests.post(api_endpoint, data=json.dumps(json_data),headers=headers)

    myblkd = BlkDiskInfo()
    disks = myblkd.get_disks()

    for disk in disks:
        name = disk['name']
        print(name)
        oldstats[name] = {'reads': disk['statistics']['reads_completed'], 
                      'writes':disk['statistics']['writes_completed']}
        
    Animate()
    
if __name__ == "__main__":
    main()