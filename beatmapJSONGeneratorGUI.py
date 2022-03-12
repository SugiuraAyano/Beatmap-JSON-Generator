import tkinter as tk
import tkinter.simpledialog as tksd
import tkinter.messagebox as tkmb
import requests as rq
import json
import re
from time import sleep

api = ""

with open("api.json") as f:
    jsonfile = json.load(f)
    api = jsonfile['api']

class BeatMap():
    def __init__(self, mapID, modID):
        self.mapID = mapID
        self.modID = modID

class BeatmapJSONGenerator(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("BeatmapJSONGenerator")
        self.geometry("600x800")
        self.resizable(False, True)

        try:
            mapAmount = self.getMapAmount()
        except NameError or TypeError or ValueError:
            tkmb.showerror(title="Oops!", message="Your Map Amount is not a number or input nothing! Please Try Again!")

        mapEntryList = [None] * mapAmount
        
        frame = tk.Frame(self, width=600, height=800)
        frame.pack(expand=True, fill=tk.BOTH)
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)

        lableEntryCanvas = tk.Canvas(frame)
        lableEntryCanvas.grid(row=0, column=0, rowspan=2)
        lableEntryCanvas.columnconfigure(0, weight=0)
        lableEntryCanvas.columnconfigure(1, weight=0)
    
        mapLable = tk.Label(lableEntryCanvas, text="Map URL or ID")
        modLable = tk.Label(lableEntryCanvas, text="Mod ID")
        mapLable.grid(row=0, column=0)
        modLable.grid(row=0, column=1)
        
        for line in range(0, mapAmount):
            mapEntryList[line] = BeatMap(tk.Entry(lableEntryCanvas), tk.Entry(lableEntryCanvas))
            mapEntryList[line].mapID.grid(row=line+1, column=0)
            mapEntryList[line].modID.grid(row=line+1, column=1) 

        btnCanvas = tk.Canvas(frame)
        btnCanvas.grid(row=2, column=0, sticky="S")
        btnCanvas.rowconfigure(0, weight=1)
        btnCanvas.rowconfigure(1, weight=1)
        btnCanvas.columnconfigure(0, weight=1)

        btnGenerate = tk.Button(btnCanvas, text="Generate", command=lambda: self.getBeatmapData(mapEntryList))
        btnGenerate.grid(row=0, column=0)
        btnClearAllValue = tk.Button(btnCanvas, text="Clear All Value", command=lambda: self.clearAllEntry(mapEntryList))
        btnClearAllValue.grid(row=0, column=1) 

    def getMapAmount(self):
        return tksd.askinteger(title="Please Enter Map Amount.", prompt="Map Amount?") 

    def getBeatmapData(self, mapEntryList):
        amount = len(mapEntryList)
        mapRawData = [None] * amount
        mapData = []
        for index, beatmap in enumerate(mapEntryList):
            mapRawData[index] = BeatMap(re.search("\d+$", beatmap.mapID.get()).group(), beatmap.modID.get())

        for index, rawData in enumerate(mapRawData):
            sleep(0.1)
            mods = 0

            if rawData.modID.startswith("EZ"):
                mods = 2
            elif rawData.modID.startswith("HR"):
                mods = 16
            elif rawData.modID.startswith("DT"):
                mods = 64
            elif rawData.modID.startswith("HT"):
                mods = 256

            payload = {
                "k": api, 
                "b": rawData.mapID,
                "mods": mods
            }

            res = rq.get("https://osu.ppy.sh/api/get_beatmaps", params=payload)
            mapData.append({'data': res.json()[0], 'mods': rawData.modID.upper()})\
            
            if mods == 2 : # EZ
                mapData[len(mapData)-1]['data']['diff_size'] = str(round(float(mapData[len(mapData)-1]['data']['diff_size'])/2, 1)) # CS
                mapData[len(mapData)-1]['data']['diff_approach'] = str(round(float(mapData[len(mapData)-1]['data']['diff_approach'])/2, 1)) # AR
                mapData[len(mapData)-1]['data']['diff_overall'] = str(round(float(mapData[len(mapData)-1]['data']['diff_overall'])/2, 1)) # OD
                mapData[len(mapData)-1]['data']['diff_drain'] = str(round(float(mapData[len(mapData)-1]['data']['diff_drain'])/2, 1)) #HP
            elif mods == 16: # HR
                mapData[len(mapData)-1]['data']['diff_size'] = str(round(min(float(mapData[len(mapData)-1]['data']['diff_size'])*1.3, 10), 1)) # CS
                mapData[len(mapData)-1]['data']['diff_approach'] = str(round(min(float(mapData[len(mapData)-1]['data']['diff_approach'])*1.4, 10), 1)) # AR
                mapData[len(mapData)-1]['data']['diff_overall'] = str(round(min(float(mapData[len(mapData)-1]['data']['diff_overall'])*1.4, 10), 1))  # OD
                mapData[len(mapData)-1]['data']['diff_drain'] = str(round(min(float(mapData[len(mapData)-1]['data']['diff_drain'])*1.4, 10), 1))  #HP
            elif mods == 64: #DT
                tempAR = float(mapData[len(mapData)-1]['data']['diff_approach'])
                if tempAR <= 5:
                    tempAR = (1800-((1800-tempAR*120)*2/3))
                else:
                    tempAR = ((1200-((1200-(tempAR-5)*150)*2/3))/150)+5
                
                mapData[len(mapData)-1]['data']['diff_approach'] = str(round(tempAR, 1)) # AR
                mapData[len(mapData)-1]['data']['diff_overall'] = str(round((79.5-((79.5-6*float(mapData[len(mapData)-1]['data']['diff_overall']))*2/3))/6, 1))  # OD
            elif mods == 256: # HT
                tempAR = float(mapData[len(mapData)-1]['data']['diff_approach'])
                if tempAR <= 5:
                    tempAR = (1800-((1800-tempAR*120)*3/2))
                else:
                    tempAR = ((1200-((1200-(tempAR-5)*150)*3/2))/150)+5
                
                mapData[len(mapData)-1]['data']['diff_approach'] = str(round(tempAR, 1)) # AR
                mapData[len(mapData)-1]['data']['diff_overall'] = str(round((79.5-((79.5-6*float(mapData[len(mapData)-1]['data']['diff_overall']))*3/2))/6, 1))  # OD                                 
            
        
        self.writeToJSON(mapData)


    def writeToJSON(self, mapData):
        with open("beatmaps.json", "w+") as file:
            jsonObject = json.dumps(mapData)
            file.write(jsonObject)
            tkmb.showinfo(title="Beatmap Generator", message="Generate Complete!")

    def clearAllEntry(self, mapEntryList):
        for beatmap in mapEntryList:
            beatmap.mapID.delete(0, 'end')
            beatmap.modID.delete(0, 'end')

if __name__ == "__main__":
    app = BeatmapJSONGenerator()
    app.mainloop()
        