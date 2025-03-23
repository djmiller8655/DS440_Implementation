import json
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
import os
import re
import datetime
from functools import partial

########### MAIN APPLICATION OBJECT - APPLICATION LOGIC, DB INSTANCES, AND Tk GUI PANEL
###########    has dict of frames that RAISE the active frame to the top depending on current need

class MetroAnalysisApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        # Font dictionary
        fontDefault = font.nametofont('TkDefaultFont')
        dictDefaultFontSettings = fontDefault.actual()
        self.appFonts = {}
        self.appFonts['fontHeader'] = font.Font(family=dictDefaultFontSettings['family'], name='appHeaderFont', size=18, weight='bold')
        self.appFonts['fontBigger'] = font.Font(family=dictDefaultFontSettings['family'], name='appBiggerFont', size=14)
        self.appFonts['fontCredits'] = font.Font(family=dictDefaultFontSettings['family'], name='appCreditsFont', size=dictDefaultFontSettings['size'], slant='italic')
        
        self.title("Metro Analysis")
        self.geometry("1200x800")
        self.frames = {}
        self.frames["MetroAnalysisMainMenuFrame"] = MetroAnalysisMainMenuFrame(container, self)
        self.frames["MetroAnalysisMainMenuFrame"].grid(row=0, column=0, sticky="nsew")
        self.frames["MetroAnalysisParameterFrame"] = MetroAnalysisParameterFrame(container, self)
        self.frames["MetroAnalysisParameterFrame"].grid(row=0, column=0, sticky="nsew")
        self.frames["MetroAnalysisResultsFrame"] = MetroAnalysisResultsFrame(container, self)
        self.frames["MetroAnalysisResultsFrame"].grid(row=0, column=0, sticky="nsew")

        # Enable user to access saved reports
        self.frames["MetroAnalysisSavedResultsFrame"] = MetroAnalysisSavedResultsFrame(container, self)
        self.frames["MetroAnalysisSavedResultsFrame"].grid(row=0, column=0, sticky="nsew")
        self.showFrame("MetroAnalysisMainMenuFrame")
        
    def showFrame(self, cont):
        frame = self.frames[cont]
        if cont == "MetroAnalysisEventHomeFrame":
            frame.createWidgets()
        frame.tkraise()

    def returnToMainMenu(self):
        self.showFrame("MetroAnalysisMainMenuFrame")

    def deleteCurrentEvent(self):
        if messagebox.askyesno(message='Are you sure that you want to delete this event? There is no way to reverse this!', icon='question', title='Delete Event'):
            self.showFrame("MetroAnalysisMainMenuFrame")
 
    '''
    def saveCrossTableReport(self):
        fname = "CrossTable-Event"+str(self.activeEvent.id)+".txt"
        f = open(fname, "w")
        fdata = "Cross Tables for "+self.activeEvent.name+" on "+self.activeEvent.date + "\n\n"
        for group in self.activeEvent.groups:
            fdata += self.createCrossTable(group) + "\n"
        f.write(fdata)
        f.close()
        strMessage = "Crosstables were saved to: " + os.getcwd() + "\\" + fname
        messagebox.showinfo(message=strMessage)
    '''
    
    
######## OBJECT THAT IS THE MAIN MENU Frame - used to create or load an event

class MetroAnalysisMainMenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.mainApp = controller
        self.createWidgets()
        
    def createWidgets(self):
        labelIntro = tk.Label(self, text="Welcome to the Metro Analysis Tool!", font=self.mainApp.appFonts['fontBigger'])
        labelIntro.grid(column=0, row=0, columnspan=3, sticky="ew")
        
        ttk.Button(self, text="New Report", command=self.runNewReport).grid(column=0, row=1, columnspan=3, padx=4, pady=4)
        ttk.Button(self, text="View Saved Reports", command=self.viewSavedReport).grid(column=2, row=2, padx=2, pady=2, sticky="w")
        ttk.Button(self, text="Quit", command=self.mainApp.destroy).grid(column=0, row=4, columnspan=3, padx=4, pady=4)

        # Image display
        if os.path.exists('chess-bg2.gif'):
            imgChess = PhotoImage(file='chess-bg2.gif')
            lblImage = ttk.Label(self, image=imgChess)
            lblImage.photo = imgChess
            lblImage.grid(column=0, row=5, columnspan=3, padx=4, pady=4)
            tk.Label(self, text="Software by Daniel Miller - 2/21/2025", font=self.mainApp.appFonts['fontCredits']).grid(column=0, row=6, columnspan=3, sticky="sew")
            self.rowconfigure(5, weight=5)
            self.rowconfigure(6, weight=1)
        else:
            tk.Label(self, text="Software by Daniel Miller - 2/21/2025", font=self.mainApp.appFonts['fontCredits']).grid(column=0, row=5, columnspan=3, sticky="sew")
            self.rowconfigure(5, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=1)
        
    def runNewReport(self, *args):
        self.mainApp.showFrame("MetroAnalysisParameterFrame")

    def viewSavedReport(self, *args):
        self.mainApp.showFrame("MetroAnalysisSavedResultsFrame")

########## OBJECT THAT IS THE CREATE A NEW EVENT Frame - used to create a new event

class MetroAnalysisParameterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.mainApp = controller
        self.createWidgets()

    def createWidgets(self):
        self.formEventName = StringVar(self, "")
        self.formEventDate = StringVar(self, "")
        self.reportStartDate = StringVar(self, "")
        self.reportEndDate = StringVar(self, "")

        self.grid(sticky="nsew", padx=4, pady=4)
        groupingValues = ["Zip Code", "Metro", "County"]
        self.groupingType = StringVar(self, "Zip Code")
        self.groupingValues = StringVar(self, "")
        self.nationalAppreciation = StringVar(self, "")
        self.estimateLength = StringVar(self, "")

        tk.Label(self, text="Select Parameters", font=self.mainApp.appFonts['fontHeader']).grid(column=0, row=0, columnspan=4, padx=2, pady=2, sticky="ew")

        ttk.Combobox(self, textvariable=self.groupingType, values=groupingValues, state="readonly").grid(column=1, row=1, padx=2, pady=2, sticky="w")
        tk.Label(self, text="Select Location Grouping of Homeprice Breakdown").grid(column=0, row=1, padx=2, pady=2, sticky="e")
        tk.Entry(self, textvariable=self.reportStartDate).grid(column=3, row=1, padx=2, pady=2, sticky="w")
        tk.Label(self, text="Values: ").grid(column=2, row=1, padx=2, pady=2, sticky="e")

        tk.Entry(self, textvariable=self.reportStartDate).grid(column=1, row=2, padx=2, pady=2, sticky="w")
        tk.Entry(self, textvariable=self.reportEndDate).grid(column=3, row=2, padx=2, pady=2, sticky="w")
        tk.Label(self, text="Date Range (year/month)").grid(column=0, row=2, padx=2, pady=2, sticky="e")
        tk.Label(self, text="To").grid(column=2, row=2, padx=2, pady=2, sticky="e")

        tk.Entry(self, textvariable=self.nationalAppreciation).grid(column=1, row=3, padx=2, pady=2, sticky="w")
        tk.Label(self, text="National Appreciation Estimate (percentage as int)").grid(column=0, row=3, padx=2, pady=2, sticky="e")

        tk.Entry(self, textvariable=self.estimateLength).grid(column=1, row=4, padx=2, pady=2, sticky="w")
        tk.Label(self, text="Time Series Length (in months)").grid(column=0, row=4, padx=2, pady=2, sticky="e")
        
        '''
        frm = Frame(self)
        tk.Button(frm, text="Save", command=self.setSaveNewEvent).grid(column=0, row=0, padx=2, pady=2)
        tk.Button(frm, text="Cancel", command=self.cancelCreateNewEvent).grid(column=1, row=0, padx=2, pady=2)
        frm.grid(column=0, row=4, columnspan=2)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=5)
        self.rowconfigure(3, weight=1)
        '''

    '''
    def cancelCreateNewEvent(self, *args):
        self.mainApp.showFrame("ChessEventMainMenuFrame")
    '''

    '''
    def setSaveNewEvent(self, *args):
        
        # Grab the values and run the search --- for my use
        edata = {}
        edata["name"] = self.formEventName.get()
        edata["date"] = self.formEventDate.get()
        edata["groups"] = []
        for tok in arrTokens:
            if len(tok.strip()) > 0:
                edata["groups"].append(tok.strip())
        edata["status"] = "active"
        self.mainApp.eventDB.load()
        evt = Event(edata)
        self.mainApp.eventDB.addRecord(evt)
        self.mainApp.eventDB.save()
        self.mainApp.setActiveEventWithId(evt.id)
    '''
######### OBJECT THAT IS THE EVENT RESULT PAGE Frame - used to show the final generated report and allow saving

class MetroAnalysisResultsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.mainApp = controller
        self.createWidgets()
    
    def returnToMainMenu(self, *args):
        self.mainApp.showFrame("MetroAnalysisMainMenuFrame")
     
    def saveResults(self, *args):
        pass
        
    def createWidgets(self):
        tk.Label(self, text="Analysis Report", font=self.mainApp.appFonts['fontHeader']).grid(column=0, row=0, columnspan=4, padx=2, pady=2, sticky="ew")
        ttk.Button(self, text="Save", command=self.saveResults).grid(column=0, row=1, padx=2, pady=2)
        ttk.Button(self, text="Exit", command=self.returnToMainMenu).grid(column=1, row=1, padx=2, pady=2)

class MetroAnalysisSavedResultsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.mainApp = controller
        self.createWidgets()
    
    def returnToMainMenu(self, *args):
        self.mainApp.showFrame("MetroAnalysisMainMenuFrame")
     
    def saveResults(self, *args):
        pass
        
    def createWidgets(self):
        tk.Label(self, text="Previous Report", font=self.mainApp.appFonts['fontHeader']).grid(column=0, row=0, columnspan=4, padx=2, pady=2, sticky="ew")
        ttk.Button(self, text="Save", command=self.saveResults).grid(column=0, row=1, padx=2, pady=2)
        ttk.Button(self, text="Exit", command=self.returnToMainMenu).grid(column=1, row=1, padx=2, pady=2)
###################################################
### Change to the user's Document Directory and start the program!!

workingDir = os.path.join(os.path.expanduser("~"), "Documents", "MetroAnalysisApp")
os.makedirs(workingDir, exist_ok=True)
os.chdir(workingDir)
myMetroAnalysisApp = MetroAnalysisApp()
myMetroAnalysisApp.mainloop()

