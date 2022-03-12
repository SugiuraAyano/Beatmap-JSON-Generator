from time import sleep
import sys
import requests as rq
import json

api = ""

with open("api.json") as f:
    jsonfile = json.load(f)
    api = jsonfile['api']


if __name__ == "__main__":
    args = len(sys.argv[1:])
    argv = sys.argv[1:]

    if (args != 1):
        print("Usage: python beatmapGenerator.py <csvFileName>")
        sys.exit(1)
    else:
        mapData = []
        with open(argv[0]) as csvFile:
            rawData = list(
                map(lambda x: x.strip().split(','), csvFile.readlines()))
            for beatmap in rawData:
                sleep(0.1)
                mods = 0
                if beatmap[1].startswith("HR"):
                    mods = 16
                elif beatmap[1].startswith("DT"):
                    mods = 64

                payload = {
                    "k": api,
                    "b": beatmap[0],
                    "mods": mods
                }

                res = rq.get(
                    "https://osu.ppy.sh/api/get_beatmaps", params=payload)
                mapData.append(
                    {'data': res.json()[0], 'mods': beatmap[1].upper()})

                if mods == 2:  # EZ
                    mapData[len(mapData)-1]['data']['diff_size'] = str(
                        round(float(mapData[len(mapData)-1]['data']['diff_size'])/2, 1))  # CS
                    mapData[len(mapData)-1]['data']['diff_approach'] = str(
                        round(float(mapData[len(mapData)-1]['data']['diff_approach'])/2, 1))  # AR
                    mapData[len(mapData)-1]['data']['diff_overall'] = str(
                        round(float(mapData[len(mapData)-1]['data']['diff_overall'])/2, 1))  # OD
                    mapData[len(mapData)-1]['data']['diff_drain'] = str(
                        round(float(mapData[len(mapData)-1]['data']['diff_drain'])/2, 1))  # HP
                elif mods == 16:  # HR
                    mapData[len(mapData)-1]['data']['diff_size'] = str(
                        round(min(float(mapData[len(mapData)-1]['data']['diff_size'])*1.3, 10), 1))  # CS
                    mapData[len(mapData)-1]['data']['diff_approach'] = str(round(
                        min(float(mapData[len(mapData)-1]['data']['diff_approach'])*1.4, 10), 1))  # AR
                    mapData[len(mapData)-1]['data']['diff_overall'] = str(round(
                        min(float(mapData[len(mapData)-1]['data']['diff_overall'])*1.4, 10), 1))  # OD
                    mapData[len(mapData)-1]['data']['diff_drain'] = str(round(
                        min(float(mapData[len(mapData)-1]['data']['diff_drain'])*1.4, 10), 1))  # HP
                elif mods == 64:  # DT
                    tempAR = float(mapData[len(mapData)-1]
                                   ['data']['diff_approach'])
                    if tempAR <= 5:
                        tempAR = (1800-((1800-tempAR*120)*2/3))
                    else:
                        tempAR = ((1200-((1200-(tempAR-5)*150)*2/3))/150)+5

                    # AR
                    mapData[len(mapData) -
                            1]['data']['diff_approach'] = str(round(tempAR, 1))
                    mapData[len(mapData)-1]['data']['diff_overall'] = str(round((79.5-(
                        (79.5-6*float(mapData[len(mapData)-1]['data']['diff_overall']))*2/3))/6, 1))  # OD
                elif mods == 256:  # HT
                    tempAR = float(mapData[len(mapData)-1]
                                   ['data']['diff_approach'])
                    if tempAR <= 5:
                        tempAR = (1800-((1800-tempAR*120)*3/2))
                    else:
                        tempAR = ((1200-((1200-(tempAR-5)*150)*3/2))/150)+5

                    # AR
                    mapData[len(mapData) -
                            1]['data']['diff_approach'] = str(round(tempAR, 1))
                    mapData[len(mapData)-1]['data']['diff_overall'] = str(round((79.5-(
                        (79.5-6*float(mapData[len(mapData)-1]['data']['diff_overall']))*3/2))/6, 1))  # OD

        with open("beatmaps.json", "w+") as file:
            jsonObject = json.dumps(mapData)
            file.write(jsonObject)
