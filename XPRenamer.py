#!/usr/bin/env python3

# X-Plane Aircraft Renamer, v1.0
# Copyright (c) 2019 NachtRaveVL      <nachtravevl@gmail.com>
# Licensed under the MIT license: https://opensource.org/licenses/MIT

# Install Python 3 here: https://www.python.org/downloads/

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import glob
import os
from shutil import copy2
import threading
import traceback
import winreg

defaultManufacturers = ["Airbus", "Antonov", "BAE", "Beechcraft", "Bell", "Boeing", "Bombardier", "Cessna", "Cirrus", "Columbia", "Dassault",
                        "De Havilland", "Diamond", "Dornier", "Douglas", "Eclipse", "Embraer", "Eurocopter", "Eurofighter", "Fairchild",
                        "Fokker", "Glasair", "Gulfstream", "Grumman", "Hawker", "Honda", "Ilyushin", "Kamov", "Lancair", "Learjet", "Lockheed",
                        "Lockheed Martin", "McDonnell", "McDonnell Douglas", "Mikoyan", "Mil", "Mitsubishi", "Mooney", "North American",
                        "Northrop Grumman", "Piaggio", "Pilatus", "Piper", "Pitts", "Raytheon", "Robinson", "Saab", "Sikorsky", "Stearman",
                        "Stinson", "Sukhoi", "Tupolev"]
ww1Manufacturers = ["Aeromarine ", "Airco", "Anatra", "Ansaldo", "Armstrong Whitworth", "Avro", "Bernard", "Blériot", "Breguet", "Bristol",
                    "Burgess","Caproni", "Caudron", "Curtiss", "Dorand", "Fairey", "Farman", "FBA", "Felixstowe", "Fokker", "Grigorovich",
                    "Hanriot", "Lebed", "Letord", "Macchi", "Martin", "Martinsyde" "Morane-Saulnier", "Mosca", "Nieuport", "Norman Thompson",
                    "Paul Schmitt", "Pomilio", "Ponnier", "R.E.P.", "Royal Aircraft Factory", "Salmson", "Savoia-Pomilio", "Short", "SIA",
                    "Sopwith", "SPAD", "Standard", "Tellier", "Thomas-Morse", "Vendôme", "Vickers", "Voisin", "Westland", "Weymann", "Wibault",
                    "Wight", "Wright", "Wright-Martin", "Yokosuka"]
ww2Manufacturers = ["Aeronca", "Aichi", "Amiot", "Arado", "Arkhangelsky", "Armstrong Whitworth", "Avia", "Avro", "Blackburn", "Bloch",
                    "Blohm & Voss", "Boulton", "Breda", "Breguet", "Bristol", "Brewster", "CAMS", "Canadian Vickers", "Caproni", "CANT",
                    "Caudron", "Chyetverikov", "Consolidated", "Curtiss", "Curtiss-Wright", "Dewoitine", "Fairey", "Farman", "Fiat", "Fieseler",
                    "FMA", "Focke-Wulf", "Fokker", "Gloster", "Gotha", "Handley", "Handley Page", "Heinkel", "Henschel", "Horten", "IAR", "IMAM",
                    "Junkers", "Kaproni", "Kawanishi", "Kawasaki", "Keystone", "Kharkov", "Kokusai", "Kyushu", "Lavochkin",
                    "Lavochkin-Gorbunov-Gudkov", "Letov", "Lisunov", "Loire", "Loire-Nieuport", "Lublin", "Macchi", "Martin", "Mikoyan-Gurevich",
                    "Messerschmitt", "Morane-Saulnier", "Nakajima", "Northrop", "Petlyakov", "Polikarpov", "Potez", "PWS", "PZL", "Reggiane",
                    "Renard", "Republic", "Rockwell", "Rogožarski", "RWD", "Savoia-Marchetti", "Short", "Seversky", "Siebel", "Supermarine",
                    "Tachikawa", "Vickers", "Vought", "Vultee", "Watanabe" "Weiss", "Westland", "Yakovlev", "Yermolayev", "Yokosuka"]
modManufacturers = ["Aviastar-SP", "Beriev", "Brumby", "Canadair", "Comac", "Daher-Socata", "Extra", "General Dynamics", "Irkut", "Kazan",
                    "Lancair", "Quest", "Rockwell Collins", "Socata", "Sokol", "SyberJet", "Yakovlev"]

def get_xp10_path():
    REG_PATH = r"Software\Drzewiecki Design\X-Plane10"
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, "Path")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

def get_xp11_path():
    REG_PATH = r"Software\Drzewiecki Design\X-Plane11"
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, "Path")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        self.master.title("X-Plane Aircraft Renamer")
        self.pack(fill=BOTH, expand=1)
        
        self.xpPathVar = StringVar()
        xpPath = get_xp11_path() or get_xp10_path()
        if xpPath:
            self.xpPathVar.set(xpPath)

        self.isRefreshingAircraft = False
        self.isOpeningAircraft = False
        self.isSavingAircraft = False

        self.currAircraft = None
        self.currAircraftHeaderBlob = None
        self.currAircarftFooterBlob = None
        self.currAircraftAcfPropTable = {}
        self.isCurrAircraftModified = False

        self.currAircraftFilenameVar = StringVar(value="None", name="filename")
        self.currAircraftNameVar = StringVar(value="", name="acf/_name")
        self.currAircraftCallsignVar = StringVar(value="", name="acf/_callsign")
        self.currAircraftTailNumVar = StringVar(value="", name="acf/_tailnum")
        self.currAircraftICAOCodeVar = StringVar(value="", name="acf/_ICAO")
        self.currAircraftManufacturerVar = StringVar(value="", name="acf/_manufacturer")
        self.currAircraftIsUltralightVar = BooleanVar(value=False, name="acf/_is_ultralight")
        self.currAircraftIsExperimentalVar = BooleanVar(value=False, name="acf/_is_experimental")
        self.currAircraftIsGenAviationVar = BooleanVar(value=False, name="acf/_is_general_aviation")
        self.currAircraftIsAirlinerVar = BooleanVar(value=False, name="acf/_is_airliner")
        self.currAircraftIsMilitaryVar = BooleanVar(value=False, name="acf/_is_military")
        self.currAircraftIsCargoVar = BooleanVar(value=False, name="acf/_is_cargo")
        self.currAircraftIsGliderVar = BooleanVar(value=False, name="acf/_is_glider")
        self.currAircraftIsSeaplaneVar = BooleanVar(value=False, name="acf/_is_seaplane")
        self.currAircraftIsHelicopterVar = BooleanVar(value=False, name="acf/_is_helicopter")
        self.currAircraftIsVTOLVar = BooleanVar(value=False, name="acf/_is_vtol")
        self.currAircraftIsSciFiVar = BooleanVar(value=False, name="acf/_is_sci_fi")
        self.currAircraftAuthorVar = StringVar(value="", name="acf/_author")
        self.currAircraftFileVerVar = StringVar(value="", name="acf/_version")
        self.currAircraftStudioVar = StringVar(value="", name="acf/_studio")
        self.currAircraftDescriptionVar = StringVar(value="", name="acf/_descrip")
        self.currAircraftNotesVar = StringVar(value="", name="acf/_notes")

        self.aircraftVarsTable = {}
        self.aircraftVarsTable[self.currAircraftNameVar._name] = self.currAircraftNameVar
        self.aircraftVarsTable[self.currAircraftCallsignVar._name] = self.currAircraftCallsignVar
        self.aircraftVarsTable[self.currAircraftTailNumVar._name] = self.currAircraftTailNumVar
        self.aircraftVarsTable[self.currAircraftICAOCodeVar._name] = self.currAircraftICAOCodeVar
        self.aircraftVarsTable[self.currAircraftManufacturerVar._name] = self.currAircraftManufacturerVar
        self.aircraftVarsTable[self.currAircraftIsUltralightVar._name] = self.currAircraftIsUltralightVar
        self.aircraftVarsTable[self.currAircraftIsExperimentalVar._name] = self.currAircraftIsExperimentalVar
        self.aircraftVarsTable[self.currAircraftIsGenAviationVar._name] = self.currAircraftIsGenAviationVar
        self.aircraftVarsTable[self.currAircraftIsAirlinerVar._name] = self.currAircraftIsAirlinerVar
        self.aircraftVarsTable[self.currAircraftIsMilitaryVar._name] = self.currAircraftIsMilitaryVar
        self.aircraftVarsTable[self.currAircraftIsCargoVar._name] = self.currAircraftIsCargoVar
        self.aircraftVarsTable[self.currAircraftIsGliderVar._name] = self.currAircraftIsGliderVar
        self.aircraftVarsTable[self.currAircraftIsSeaplaneVar._name] = self.currAircraftIsSeaplaneVar
        self.aircraftVarsTable[self.currAircraftIsHelicopterVar._name] = self.currAircraftIsHelicopterVar
        self.aircraftVarsTable[self.currAircraftIsVTOLVar._name] = self.currAircraftIsVTOLVar
        self.aircraftVarsTable[self.currAircraftIsSciFiVar._name] = self.currAircraftIsSciFiVar
        self.aircraftVarsTable[self.currAircraftAuthorVar._name] = self.currAircraftAuthorVar
        self.aircraftVarsTable[self.currAircraftFileVerVar._name] = self.currAircraftFileVerVar
        self.aircraftVarsTable[self.currAircraftStudioVar._name] = self.currAircraftStudioVar
        self.aircraftVarsTable[self.currAircraftDescriptionVar._name] = self.currAircraftDescriptionVar
        self.aircraftVarsTable[self.currAircraftNotesVar._name] = self.currAircraftNotesVar
        
        for key in self.aircraftVarsTable:
            self.aircraftVarsTable[key].trace('w', self.mark_opened_dirty)
        
        self.manufacturerList = set(defaultManufacturers)
        self.manufacturerList = self.manufacturerList.union(ww1Manufacturers)
        self.manufacturerList = self.manufacturerList.union(ww2Manufacturers)
        self.manufacturerList = self.manufacturerList.union(modManufacturers)
        self.manufacturerList = sorted(self.manufacturerList)
        
        pathFrame = Frame(self, padx=5, pady=5)
        pathFrame.pack(fill=X)
        
        self.pathLabel = Label(pathFrame, text="X-Plane Path:")
        self.pathLabel.grid(row=0, column=0)
        self.pathEntry = Entry(pathFrame, width=72, textvariable=self.xpPathVar, state="readonly")
        self.pathEntry.grid(row=0, column=1, padx=(5,0))
        self.changePathButton = Button(pathFrame, text="Change", command=self.change_xp_path)
        self.changePathButton.grid(row=0, column=2, padx=(5,0))
        self.rescanPathButton = Button(pathFrame, text="Rescan", command=self.rescan_aircraft)
        self.rescanPathButton.grid(row=0, column=3, padx=(5,0))
        
        listFrame = Frame(self, padx=5, pady=5)
        listFrame.pack(fill=X)
        
        self.aircraftListLabel = Label(listFrame, text="Detected Aircraft:")
        self.aircraftListLabel.pack()

        self.aircraftList = Listbox(listFrame, height=8, selectmode=SINGLE)
        self.aircraftList.bind('<<ListboxSelect>>', self.aircraft_selected)
        self.aircraftList.pack(fill=X)        
        self.aircraftListScrollbar = Scrollbar(self.aircraftList, orient="vertical")
        self.aircraftListScrollbar.config(command=self.aircraftList.yview)
        self.aircraftListScrollbar.pack(side=RIGHT, fill=Y)
        self.aircraftList.config(yscrollcommand=self.aircraftListScrollbar.set)

        infoFrame = Frame(self, padx=5, pady=5)
        infoFrame.pack(fill=X)

        self.currAircraftFileLabel = Label(infoFrame, text="Current Aircraft File:")
        self.currAircraftFileLabel.grid(row=0, column=0, sticky="e")
        self.currAircraftFileEntry = Entry(infoFrame, width=84, textvariable=self.currAircraftFilenameVar, state="readonly")
        self.currAircraftFileEntry.grid(row=0, column=1, padx=(5,0), sticky="w")

        self.currAircraftNameLabel = Label(infoFrame, text="Name for XPlane-UI:")
        self.currAircraftNameLabel.grid(row=1, column=0, pady=(5,0), sticky="e")
        self.currAircraftNameEntry = Entry(infoFrame, width=84, textvariable=self.currAircraftNameVar)
        self.currAircraftNameEntry.grid(row=1, column=1, padx=(5,0), pady=(5,0), sticky="w")

        self.currAircraftCallsignLabel = Label(infoFrame, text="Call-sign for ATC:")
        self.currAircraftCallsignLabel.grid(row=2, column=0, pady=(5,0), sticky="e")
        self.currAircraftCallsignEntry = Entry(infoFrame, width=84, textvariable=self.currAircraftCallsignVar)
        self.currAircraftCallsignEntry.grid(row=2, column=1, padx=(5,0), pady=(5,0), sticky="w")
        
        self.currAircraftTailNumLabel = Label(infoFrame, text="Tail number for ATC:")
        self.currAircraftTailNumLabel.grid(row=3, column=0, pady=(5,0), sticky="e")
        self.currAircraftTailNumEntry = Entry(infoFrame, width=84, textvariable=self.currAircraftTailNumVar)
        self.currAircraftTailNumEntry.grid(row=3, column=1, padx=(5,0), pady=(5,0), sticky="w")

        self.currAircraftICAOCodeLabel = Label(infoFrame, text="ICAO code for ATC:")
        self.currAircraftICAOCodeLabel.grid(row=4, column=0, pady=(5,0), sticky="e")
        self.currAircraftICAOCodeEntry = Entry(infoFrame, width=84, textvariable=self.currAircraftICAOCodeVar)
        self.currAircraftICAOCodeEntry.grid(row=4, column=1, padx=(5,0), pady=(5,0), sticky="w")

        self.currAircraftManufacturerLabel = Label(infoFrame, text="Manufacturer:")
        self.currAircraftManufacturerLabel.grid(row=5, column=0, pady=(5,0), sticky="e")
        self.currAircraftManufacturerCombobox = ttk.Combobox(infoFrame, width=81, textvariable=self.currAircraftManufacturerVar, values=self.manufacturerList)
        self.currAircraftManufacturerCombobox.grid(row=5, column=1, padx=(5,0), pady=(5,0), sticky="w")

        self.currAircraftClassificationLabel = Label(infoFrame, text="Classification:")
        self.currAircraftClassificationLabel.grid(row=6, column=0, pady=(5,0), sticky="ne")

        classFrame = Frame(infoFrame)
        classFrame.grid(row=6, column=1, pady=(5,0), sticky="w")

        self.currAircraftIsUltralightCheckbutton = Checkbutton(classFrame, text="Ultralight", variable=self.currAircraftIsUltralightVar)
        self.currAircraftIsUltralightCheckbutton.grid(row=0, column=0, sticky="w")
        self.currAircraftIsExperimentalCheckbutton = Checkbutton(classFrame, text="Experimental", variable=self.currAircraftIsExperimentalVar)
        self.currAircraftIsExperimentalCheckbutton.grid(row=1, column=0, pady=(0,0), sticky="w")
        self.currAircraftIsGenAviationCheckbutton = Checkbutton(classFrame, text="General Aviation", variable=self.currAircraftIsGenAviationVar)
        self.currAircraftIsGenAviationCheckbutton.grid(row=2, column=0, pady=(0,0), sticky="w")
        self.currAircraftIsAirlinerCheckbutton = Checkbutton(classFrame, text="Airliner", variable=self.currAircraftIsAirlinerVar)
        self.currAircraftIsAirlinerCheckbutton.grid(row=3, column=0, pady=(0,0), sticky="w")
        self.currAircraftIsMilitaryCheckbutton = Checkbutton(classFrame, text="Military", variable=self.currAircraftIsMilitaryVar)
        self.currAircraftIsMilitaryCheckbutton.grid(row=4, column=0, pady=(0,0), sticky="w")
        self.currAircraftIsCargoCheckbutton = Checkbutton(classFrame, text="Cargo", variable=self.currAircraftIsCargoVar)
        self.currAircraftIsCargoCheckbutton.grid(row=5, column=0, pady=(0,0), sticky="w")

        self.currAircraftIsGliderCheckbutton = Checkbutton(classFrame, text="Glider", variable=self.currAircraftIsGliderVar)
        self.currAircraftIsGliderCheckbutton.grid(row=0, column=1, padx=(5,0), sticky="w")
        self.currAircraftIsSeaplaneCheckbutton = Checkbutton(classFrame, text="Seaplane", variable=self.currAircraftIsSeaplaneVar)
        self.currAircraftIsSeaplaneCheckbutton.grid(row=1, column=1, padx=(5,0), sticky="w")
        self.currAircraftIsHelicopterCheckbutton = Checkbutton(classFrame, text="Helicopter", variable=self.currAircraftIsHelicopterVar)
        self.currAircraftIsHelicopterCheckbutton.grid(row=2, column=1, padx=(5,0), sticky="w")
        self.currAircraftIsVTOLCheckbutton = Checkbutton(classFrame, text="VTOL", variable=self.currAircraftIsVTOLVar)
        self.currAircraftIsVTOLCheckbutton.grid(row=3, column=1, padx=(5,0), sticky="w")
        self.currAircraftIsSciFiCheckbutton = Checkbutton(classFrame, text="Science Fiction", variable=self.currAircraftIsSciFiVar)
        self.currAircraftIsSciFiCheckbutton.grid(row=4, column=1, padx=(5,0), sticky="w")

        self.currAircraftAuthorLabel = Label(infoFrame, text="Aircraft Author:")
        self.currAircraftAuthorLabel.grid(row=7, column=0, pady=(5,0), sticky="e")
        self.currAircraftAuthorEntry = Entry(infoFrame, width=84, textvariable=self.currAircraftAuthorVar)
        self.currAircraftAuthorEntry.grid(row=7, column=1, padx=(5,0), pady=(5,0), sticky="w")

        self.currAircraftFileVerLabel = Label(infoFrame, text="File Version:")
        self.currAircraftFileVerLabel.grid(row=8, column=0, pady=(5,0), sticky="e")
        self.currAircraftFileVerEntry = Entry(infoFrame, width=84, textvariable=self.currAircraftFileVerVar)
        self.currAircraftFileVerEntry.grid(row=8, column=1, padx=(5,0), pady=(5,0), sticky="w")

        self.currAircraftStudioLabel = Label(infoFrame, text="Design Studio:")
        self.currAircraftStudioLabel.grid(row=9, column=0, pady=(5,0), sticky="e")
        self.currAircraftStudioEntry = Entry(infoFrame, width=84, textvariable=self.currAircraftStudioVar)
        self.currAircraftStudioEntry.grid(row=9, column=1, padx=(5,0), pady=(5,0), sticky="w")

        self.currAircraftDescriptionLabel = Label(infoFrame, text="Aircraft Description:")
        self.currAircraftDescriptionLabel.grid(row=10, column=0, pady=(5,0), sticky="e")
        self.currAircraftDescriptionEntry = Entry(infoFrame, width=84, textvariable=self.currAircraftDescriptionVar)
        self.currAircraftDescriptionEntry.grid(row=10, column=1, padx=(5,0), pady=(5,0), sticky="w")

        self.currAircraftNotesLabel = Label(infoFrame, text="Notes:")
        self.currAircraftNotesLabel.grid(row=11, column=0, pady=(5,0), sticky="e")
        self.currAircraftNotesEntry = Entry(infoFrame, width=84, textvariable=self.currAircraftNotesVar)
        self.currAircraftNotesEntry.grid(row=11, column=1, padx=(5,0), pady=(5,0), sticky="w")

        self.saveAircraftButton = Button(infoFrame, text="Save Aircraft", command=self.save_aircraft)
        self.saveAircraftButton.grid(row=12, column=0, columnspan=2, pady=(5,0))

        self.clear_scanned_aircraft()
        self.clear_opened_aircraft()
        self.update_enabled_widgets()
        self.rescan_aircraft(suppressDialogs=True)

    def clear_scanned_aircraft(self):
        self.aircraftList.delete(0, END)

    def clear_opened_aircraft(self):
        self.currAircraft = None
        self.currAircraftHeaderBlob = None
        self.currAircarftFooterBlob = None
        self.currAircraftAcfPropTable = None
        self.isCurrAircraftModified = False
        self.currAircraftFilenameVar.set("None")

        for key in self.aircraftVarsTable:
            var = self.aircraftVarsTable[key]
            if type(var) == StringVar:
                var.set("")
            else:
                var.set(0)

    def update_enabled_widgets(self):
        pathEntry = "disabled"
        if not (self.isRefreshingAircraft or self.isOpeningAircraft or self.isSavingAircraft):
            pathEntry = "normal"
        self.changePathButton.config(state=pathEntry)
        self.rescanPathButton.config(state=pathEntry)
        
        aircraftEntry = "disabled"
        if self.currAircraft and not (self.isOpeningAircraft or self.isSavingAircraft):
            aircraftEntry = "normal"
        self.currAircraftNameEntry.config(state=aircraftEntry)
        self.currAircraftCallsignEntry.config(state=aircraftEntry)
        self.currAircraftTailNumEntry.config(state=aircraftEntry)
        self.currAircraftICAOCodeEntry.config(state=aircraftEntry)
        self.currAircraftManufacturerCombobox.config(state=aircraftEntry)
        self.currAircraftIsUltralightCheckbutton.config(state=aircraftEntry)
        self.currAircraftIsExperimentalCheckbutton.config(state=aircraftEntry)
        self.currAircraftIsGenAviationCheckbutton.config(state=aircraftEntry)
        self.currAircraftIsAirlinerCheckbutton.config(state=aircraftEntry)
        self.currAircraftIsMilitaryCheckbutton.config(state=aircraftEntry)
        self.currAircraftIsCargoCheckbutton.config(state=aircraftEntry)
        self.currAircraftIsGliderCheckbutton.config(state=aircraftEntry)
        self.currAircraftIsSeaplaneCheckbutton.config(state=aircraftEntry)
        self.currAircraftIsHelicopterCheckbutton.config(state=aircraftEntry)
        self.currAircraftIsVTOLCheckbutton.config(state=aircraftEntry)
        self.currAircraftIsSciFiCheckbutton.config(state=aircraftEntry)
        self.currAircraftAuthorEntry.config(state=aircraftEntry)
        self.currAircraftFileVerEntry.config(state=aircraftEntry)
        self.currAircraftStudioEntry.config(state=aircraftEntry)
        self.currAircraftDescriptionEntry.config(state=aircraftEntry)
        self.currAircraftNotesEntry.config(state=aircraftEntry)

        saveEntry = "disabled"
        if self.currAircraft and not (self.isOpeningAircraft or self.isSavingAircraft) and self.isCurrAircraftModified:
            saveEntry = "normal"
        self.saveAircraftButton.config(state=saveEntry)
        
    def change_xp_path(self):
        if self.isRefreshingAircraft or self.isOpeningAircraft or self.isSavingAircraft:
            return
        
        xpPath = filedialog.askdirectory(initialdir = self.xpPathVar.get(), title = "Select X-Plane Path")
        if xpPath and len(xpPath):
            self.xpPathVar.set(xpPath)
            self.rescan_aircraft()    
   
    def rescan_aircraft(self, suppressDialogs=False):
        if self.isRefreshingAircraft or self.isOpeningAircraft or self.isSavingAircraft:
            return

        self.isRefreshingAircraft = True
        self.clear_scanned_aircraft()
        self.clear_opened_aircraft()
        self.update_enabled_widgets()

        xpPath = self.xpPathVar.get()
        acPath = os.path.join(xpPath, "Aircraft")
        if not os.path.exists(acPath):
            if not suppressDialogs:
                messagebox.showerror("Error", "Folder path \"" + xpPath + "\" does not contain an Aircraft folder.")
            self.isRefreshingAircraft = False
            self.update_enabled_widgets()
            return
        
        threading.Thread(target=self.rescan_aircraft_thread, args=[acPath, suppressDialogs]).start()

    def rescan_aircraft_thread(self, acPath, suppressDialogs):
        assert self.isRefreshingAircraft
        xpPath = os.path.join(self.xpPathVar.get(), '')
        print("Scanning: " + acPath)
        
        aircraftFiles = glob.iglob(os.path.join(acPath, "**\\*.acf"), recursive=True)
        for acFile in aircraftFiles:
            self.aircraftList.insert(END, acFile[acFile.startswith(xpPath) and len(xpPath):])
        
        self.isRefreshingAircraft = False
        self.update_enabled_widgets()

    def aircraft_selected(self, event):
        if self.isOpeningAircraft or self.isSavingAircraft or not len(self.aircraftList.curselection()):
            return

        try:
            acFile = self.aircraftList.get(self.aircraftList.curselection()[0])
        except:
            return

        if acFile and len(acFile):
            acFile = os.path.join(self.xpPathVar.get(), acFile)
            self.open_aircraft(acFile)

    def open_aircraft(self, acFile, suppressDialogs=False):
        if self.isOpeningAircraft or self.isSavingAircraft or self.currAircraft == acFile:
            return

        if self.isCurrAircraftModified and not suppressDialogs and messagebox.askyesno("File Modified", "Do you wish to save \"" + self.currAircraftFilenameVar.get() + "\" before loading a new aircraft?"):
            self.save_aircraft(supressErrors, openAcFileAfter=acFile)
            return
        
        self.isOpeningAircraft = True
        self.clear_opened_aircraft()
        self.update_enabled_widgets()

        if not os.path.exists(acFile):
            if not suppressDialogs:
                messagebox.showerror("Error", "Aircraft file \"" + acFile + "\" no longer exists.")
            self.isOpeningAircraft = False
            self.update_enabled_widgets()
            return

        if not os.access(acFile, os.R_OK):
            if not suppressDialogs:
                messagebox.showerror("Error", "Aircraft file \"" + acFile + "\" cannot be read from.")
            self.isOpeningAircraft = False
            self.update_enabled_widgets()
            return

        threading.Thread(target=self.open_aircraft_thread, args=[acFile, suppressDialogs]).start()

    def open_aircraft_thread(self, acFile, suppressDialogs):
        assert self.isOpeningAircraft
        xpPath = os.path.join(self.xpPathVar.get(), '')
        print("Opening: " + acFile)
        
        self.currAircraft = acFile
        self.currAircraftHeaderBlob = []
        self.currAircraftFooterBlob = []
        self.currAircraftAcfPropTable = {}
        self.isCurrAircraftModified = False
        self.currAircraftFilenameVar.set(acFile[acFile.startswith(xpPath) and len(xpPath):])
        
        try:
            file = open(acFile, 'r')
            
            stage = 0
            for line in file:
                if stage == 0:
                    if line.startswith("P acf/"):
                        stage = 1
                    else:
                        self.currAircraftHeaderBlob.append(line)

                        if len(self.currAircraftHeaderBlob) == 1 and self.currAircraftHeaderBlob[0] != "I\n":
                            raise Exception("Invalid file header.")
                        if len(self.currAircraftHeaderBlob) == 3 and self.currAircraftHeaderBlob[2] != "ACF\n":
                            raise Exception("Invalid file header.")
                        
                        continue
                if stage == 1:
                    if not line.startswith("P acf/"):
                        stage = 2
                    else:
                        kvPair = line.rstrip()[2:].split(" ", 1)
                        self.currAircraftAcfPropTable[kvPair[0]] = kvPair[1]
                        continue
                if stage == 2:
                    self.currAircraftFooterBlob.append(line)
                    continue
            
            file.close()
            
            if not len(self.currAircraftHeaderBlob) or not len(self.currAircraftFooterBlob) or not len(self.currAircraftAcfPropTable):
                raise Exception("Invalid file structure.")

            for key in self.aircraftVarsTable:
                var = self.aircraftVarsTable[key]
                if type(var) == StringVar:
                    var.set(self.currAircraftAcfPropTable.get(key, ""))
                else:
                    var.set(self.currAircraftAcfPropTable.get(key, 0))
        except:
            traceback.print_exc()
            if not suppressDialogs:
                messagebox.showerror("Error", "Aircraft file \"" + acFile + "\" is invalid or cannot be properly read from.")
            try:
                file.close()
            except:
                pass
            self.clear_opened_aircraft()
        
        self.isOpeningAircraft = False
        self.update_enabled_widgets()

    def mark_opened_dirty(self, *args):
        if self.isOpeningAircraft or self.isSavingAircraft or not self.currAircraft:
            return

        isModified = False
        for key in [args[0]] + list(self.aircraftVarsTable.keys()):
            var = self.aircraftVarsTable[key]
            if type(var) == StringVar:
                if var.get().strip() != self.currAircraftAcfPropTable.get(key, ""):
                    isModified = True
                    break
            elif type(var) == BooleanVar:
                if int(var.get()) != int(self.currAircraftAcfPropTable.get(key, 0)):
                    isModified = True
                    break

        self.isCurrAircraftModified = isModified
        self.update_enabled_widgets()

    def save_aircraft(self, suppressDialogs=False, openAcFileAfter=None):
        if self.isOpeningAircraft or self.isSavingAircraft or not self.currAircraft:
            return

        self.isSavingAircraft = True
        acFile = self.currAircraft
        backupAcFile = acFile + "~"
        self.update_enabled_widgets()

        if os.path.exists(acFile) and not os.access(acFile, os.W_OK):
            if not suppressDialogs:
                messagebox.showerror("Error", "Aircraft file \"" + acFile + "\" cannot be written to.")
            self.isSavingAircraft = False
            self.update_enabled_widgets()
            return

        if os.path.exists(backupAcFile) and not os.access(backupAcFile, os.W_OK):
            if not suppressDialogs:
                messagebox.showerror("Error", "Aircraft backup file \"" + backupAcFile + "\" cannot be written to.")
            self.isSavingAircraft = False
            self.update_enabled_widgets()
            return
        
        threading.Thread(target=self.save_aircraft_thread, args=[acFile, suppressDialogs, openAcFileAfter]).start()

    def save_aircraft_thread(self, acFile, suppressDialogs, openAcFileAfter):
        assert self.isSavingAircraft
        backupAcfPropTable = self.currAircraftAcfPropTable.copy()
        backupAcFile = acFile + "~"
        print("Saving: " + acFile)
        
        try:
            try:
                if os.path.exists(backupAcFile):
                    os.remove(backupAcFile)
            except:
                pass
            copy2(acFile, backupAcFile)

            for key in self.aircraftVarsTable:
                var = self.aircraftVarsTable[key]
                if type(var) == StringVar:
                    self.currAircraftAcfPropTable[key] = var.get().strip()
                elif type(var) == BooleanVar:
                    self.currAircraftAcfPropTable[key] = int(var.get())
            
            file = open(acFile, 'w')
            
            for line in self.currAircraftHeaderBlob:
                file.write(line)

            for key in sorted(self.currAircraftAcfPropTable):
                val = self.currAircraftAcfPropTable.get(key, "")
                if key in self.aircraftVarsTable and type(val) == str and val == "":
                    continue
                if type(val) != str:
                    val = str(val)
                file.write("P " + key + " " + val + "\n")

            for line in self.currAircraftFooterBlob:
                file.write(line)
            
            file.close()

            try:
                if os.path.exists(backupAcFile):
                    os.remove(backupAcFile)
            except:
                pass

            self.isCurrAircraftModified = False
        except:
            traceback.print_exc()
            if not suppressDialogs:
                messagebox.showerror("Error", "Aircraft file \"" + acFile + "\" cannot be properly written to.")
            try:
                file.close()
            except:
                pass
            if os.path.exists(backupAcFile):
                try:
                    if os.path.exists(acFile):
                        os.remove(acFile)
                except:
                    pass
                copy2(backupAcFile, acFile)
                try:
                    os.remove(backupAcFile)
                except:
                    pass
            self.currAircraftAcfPropTable = backupAcfPropTable
        
        self.isSavingAircraft = False
        if openAcFileAfter:
            self.open_aircraft(openAcFileAfter, suppressDialogs)
        else:
            self.update_enabled_widgets()

root = Tk()
root.geometry("640x680")
root.resizable(False, False)
app = Window(root)
root.mainloop()
