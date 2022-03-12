import requests as rq
import json
from rich import print

api = ""

with open("api.json") as f:
    jsonfile = json.load(f)
    api = jsonfile['api']
    print(api)

payload = {
    "k" : api, 
    "b" : 3432624
}
response = rq.get("https://osu.ppy.sh/api/get_beatmaps", params=payload)

print(response.json()[0])