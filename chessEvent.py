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

######### Generic class for TK Date Widget with pop-up calendar

class tkDateWidget(tk.Frame):
    _validFormats = { 'YYYY.MM.DD': 1, 'MM/DD/YYYY': 1, 'Mon D, YYYY': 1, 'Month D, YYYY': 1, 'DD-MON-YYYY': 1, 'YYYY-MM-DD': 1 }
    _monthsLong = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
    _monthsShort = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    _monthsShortUC = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    _daysInMonth = [31,29,31,30,31,30,31,31,30,31,30,31]

    def __init__(self, parent, params):
        super().__init__(parent)
        self.format = 'MM/DD/YYYY';
        self.minYear = 1900
        self.maxYear = 2099
        if 'format' in params:
            if self._validFormats[params['format']] == 1:
                self.format = params['format']
            else:
                print("INVALID DATE FORMAT: "+params['format']+", using default "+self.format)
        if 'minYear' in params:
            if int(params['minYear']) >= 0 and int(params['minYear']) < 9999:
                self.minYear = params['minYear']
        if 'maxYear' in params:
            if int(params['maxYear']) >= 0 and int(params['maxYear']) < 9999:
                self.maxYear = params['maxYear']
        self.listYears = list(range(self.minYear,self.maxYear+1))
        self.listDays = []
        if re.search("DD", self.format):
            for d in list(range(1,10)):
                self.listDays.append("0"+str(d))
            for d in list(range(10,32)):
                self.listDays.append(str(d))
        else:
            for d in list(range(1,32)):
                self.listDays.append(str(d))
        self.monthWidth = 2
        self.listMonths = []
        if re.search("Month", self.format):
            self.monthWidth = 10
            for m in self._monthsLong:
                self.listMonths.append(m)
        elif re.search("Mon", self.format):
            self.monthWidth = 3
            for m in self._monthsShort:
                self.listMonths.append(m)
        elif re.search("MON", self.format):
            self.monthWidth = 3
            for m in self._monthsShortUC:
                self.listMonths.append(m)
        else:
            for m in list(range(1,10)):
                self.listMonths.append("0"+str(m))
            self.listMonths.append("10")
            self.listMonths.append("11")
            self.listMonths.append("12")
        self.strvarYear = StringVar(self, self.listYears[0])
        self.strvarMonth = StringVar(self, self.listMonths[0])
        self.strvarDay = StringVar(self, self.listDays[0])
        self.frameDateEntry = Frame(self)
        self.cboxYears = ttk.Combobox(self.frameDateEntry, textvariable=self.strvarYear, values=self.listYears, width=4, state="readonly")
        self.cboxMonths = ttk.Combobox(self.frameDateEntry, textvariable=self.strvarMonth, values=self.listMonths, width=self.monthWidth, state="readonly")
        self.cboxDays = ttk.Combobox(self.frameDateEntry, textvariable=self.strvarDay, values=self.listDays, width=2, state="readonly")
        if self.format == 'YYYY.MM.DD' or self.format == 'YYYY-MM-DD':
            delim = '-'
            if self.format == 'YYYY.MM.DD':
                delim = '.'
            self.cboxYears.grid(column=0, row=0)
            tk.Label(self.frameDateEntry, text=delim).grid(column=1, row=0)
            self.cboxMonths.grid(column=2, row=0)
            tk.Label(self.frameDateEntry, text=delim).grid(column=3, row=0)
            self.cboxDays.grid(column=4, row=0)
        elif self.format == 'Mon D, YYYY' or self.format == 'Month D, YYYY':
            self.cboxMonths.grid(column=0, row=0)
            tk.Label(self.frameDateEntry, text=" ").grid(column=1, row=0)
            self.cboxDays.grid(column=2, row=0)
            tk.Label(self.frameDateEntry, text=", ").grid(column=3, row=0)
            self.cboxYears.grid(column=4, row=0)
        elif self.format == 'DD-MON-YYYY': 
            self.cboxDays.grid(column=0, row=0)
            tk.Label(self.frameDateEntry, text="-").grid(column=1, row=0)
            self.cboxMonths.grid(column=2, row=0)
            tk.Label(self.frameDateEntry, text="-").grid(column=3, row=0)
            self.cboxYears.grid(column=4, row=0)
        else: ###if self.format == 'MM/DD/YYYY':
            self.cboxMonths.grid(column=0, row=0)
            tk.Label(self.frameDateEntry, text="/").grid(column=1, row=0)
            self.cboxDays.grid(column=2, row=0)
            tk.Label(self.frameDateEntry, text="/").grid(column=3, row=0)
            self.cboxYears.grid(column=4, row=0)
        self.buttonToggleCalendar = tk.Button(self.frameDateEntry, text="...", command=self.toggleCalendarDisplay)
        self.buttonToggleCalendar.grid(column=5, row=0)
        self.frameDateEntry.grid(column=0, row=0)
        self.frameCalendar = self.createCalendarFrame()
        self.frameCalendar.grid(column=0, row=1, columnspan=5)
        self.frameCalendar.grid_forget()
        self.boolCalendarOpen = False
        self.strvarYear.trace('w', self.changeMonthOrYear)
        self.strvarMonth.trace('w', self.changeMonthOrYear)
        
    def changeMonthOrYear(self, *args):
        ### recreate the daily calendar grid
        self.frameCalendarGrid.grid_forget()
        self.frameCalendarGrid = self.createCalendarGridFrame(self.framePopup)
        self.frameCalendarGrid.grid(column=0, row=1)
        self.buttonPrevYear.config(state=tk.NORMAL)
        self.buttonPrevMonth.config(state=tk.NORMAL)
        self.buttonNextYear.config(state=tk.NORMAL)
        self.buttonNextMonth.config(state=tk.NORMAL)
        if int(self.strvarYear.get()) == self.minYear:
            self.buttonPrevYear.config(state=tk.DISABLED)
            if self.getMonthNumber(self.strvarMonth.get()) == 1:
                self.buttonPrevMonth.config(state=tk.DISABLED)
        if int(self.strvarYear.get()) == self.maxYear:
            self.buttonNextYear.config(state=tk.DISABLED)
            if self.getMonthNumber(self.strvarMonth.get()) == 12:
                self.buttonNextMonth.config(state=tk.DISABLED)

    def toggleCalendarDisplay(self):
        if self.boolCalendarOpen:
            self.hideCalendar()
        else:
            self.frameCalendar.grid(column=0, row=1, columnspan=5)
            self.buttonToggleCalendar.config(text="X")
            self.boolCalendarOpen = True

    def hideCalendar(self):
        self.frameCalendar.grid_forget()
        self.buttonToggleCalendar.config(text="...")
        self.boolCalendarOpen = False

    def getMonthNumber(self, month):
        if re.search("Month", self.format):
            return self._monthsLong[month]
        elif re.search("Mon", self.format):
            return self._monthsShort[month]
        elif re.search("MON", self.format):
            return self._monthsShortUC[month]
        else:
            return int(month)
        
    def createCalendarFrame(self):
        self.framePopup = Frame(self, highlightbackground="black", highlightthickness=2)
        frameHeader = Frame(self.framePopup)
        self.buttonPrevMonth = tk.Button(frameHeader, text="<", command=self.prevMonth)
        self.buttonPrevMonth.grid(column=0, row=0)
        self.cboxPopupMonths = ttk.Combobox(frameHeader, textvariable=self.strvarMonth, values=self.listMonths, width=self.monthWidth, state="readonly")
        self.cboxPopupMonths.grid(column=1, row=0)
        self.buttonNextMonth = tk.Button(frameHeader, text=">", command=self.nextMonth)
        self.buttonNextMonth.grid(column=2, row=0)
        self.buttonPrevYear = tk.Button(frameHeader, text="<<", command=self.prevYear)
        self.buttonPrevYear.grid(column=3, row=0)
        self.cboxPopupYears = ttk.Combobox(frameHeader, textvariable=self.strvarYear, values=self.listYears, width=4, state="readonly")
        self.cboxPopupYears.grid(column=4, row=0)
        self.buttonNextYear = tk.Button(frameHeader, text=">>", command=self.nextYear)
        self.buttonNextYear.grid(column=5, row=0)
        frameHeader.grid(column=0, row=0)
        if int(self.strvarYear.get()) == self.minYear:
            self.buttonPrevYear.config(state=tk.DISABLED)
            if self.getMonthNumber(self.strvarMonth.get()) == 1:
                self.buttonPrevMonth.config(state=tk.DISABLED)
        if int(self.strvarYear.get()) == self.maxYear:
            self.buttonNextYear.config(state=tk.DISABLED)
            if self.getMonthNumber(self.strvarMonth.get()) == 12:
                self.buttonNextMonth.config(state=tk.DISABLED)
        self.frameCalendarGrid = self.createCalendarGridFrame(self.framePopup)
        self.frameCalendarGrid.grid(column=0, row=1)
        return self.framePopup
        
    def createCalendarGridFrame(self, parent):
        frameGrid = Frame(parent)
        weekdays = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
        for idx in list(range(0,len(weekdays))):
            tk.Label(frameGrid, text=weekdays[idx]).grid(column=idx, row=0)
        datetimeFirstDayOfMonth = datetime.datetime(int(self.strvarYear.get()), self.getMonthNumber(self.strvarMonth.get()), 1)
        strFirstWeekdayInMonth = datetimeFirstDayOfMonth.strftime("%a")
        numMonthDays = self._daysInMonth[self.getMonthNumber(self.strvarMonth.get())-1]
        if self.getMonthNumber(self.strvarMonth.get()) == 2 and ((int(self.strvarYear.get()) % 4) != 0):
            numMonthDays -= 1
        day = 0
        rowNum = 1
        while day < numMonthDays:
            for idx in list(range(0,len(weekdays))):
                if day == 0:
                    if weekdays[idx] != strFirstWeekdayInMonth:
                        tk.Label(frameGrid, text="").grid(column=idx, row=rowNum)
                    else:
                        day += 1
                        tk.Button(frameGrid, text=str(day), width=3, command=partial(self.pickedDate,day)).grid(column=idx, row=rowNum)
                elif day < numMonthDays:
                    day += 1
                    tk.Button(frameGrid, text=str(day), width=3, command=partial(self.pickedDate,day)).grid(column=idx, row=rowNum)
                else:
                    tk.Label(frameGrid, text="").grid(column=idx, row=rowNum)
            rowNum += 1
        return frameGrid

    def prevMonth(self):
        mon = self.getMonthNumber(self.strvarMonth.get())
        if mon == 1:
            if int(self.strvarYear.get()) == self.listYears[0]:
                return
            else:
                mon = 12
                self.strvarYear.set(str(int(self.strvarYear.get())-1))
        else:
            mon -= 1
        self.strvarMonth.set(self.listMonths[mon-1])

    def nextMonth(self):
        mon = self.getMonthNumber(self.strvarMonth.get())
        if mon == 12:
            if int(self.strvarYear.get()) == self.maxYear:
                return
            else:
                mon = 1
                self.strvarYear.set(str(int(self.strvarYear.get())+1))
        else:
            mon += 1
        self.strvarMonth.set(self.listMonths[mon-1])

    def prevYear(self):
        if int(self.strvarYear.get()) == self.listYears[0]:
            return
        else:
            self.strvarYear.set(str(int(self.strvarYear.get())-1))

    def nextYear(self):
        if int(self.strvarYear.get()) == self.maxYear:
            return
        else:
            self.strvarYear.set(str(int(self.strvarYear.get())+1))

    def pickedDate(self, day):
        self.strvarDay.set(self.listDays[day-1])
        self.hideCalendar()
    
    def getValue(self):
        if self.format == 'YYYY.MM.DD' or self.format == 'YYYY-MM-DD':
            delim = '-'
            if self.format == 'YYYY.MM.DD':
                delim = '.'
            return self.strvarYear.get()+delim+self.strvarMonth.get()+delim+self.strvarDay.get()
        elif self.format == 'Mon D, YYYY' or self.format == 'Month D, YYYY':
            return self.strvarMonth.get()+" "+self.strvarDay.get()+", "+self.strvarYear.get()
        elif self.format == 'DD-MON-YYYY': 
            return self.strvarDay.get()+"-"+self.strvarMonth.get()+"-"+self.strvarYear.get()
        else: ###if self.format == 'MM/DD/YYYY':
            return self.strvarMonth.get()+"/"+self.strvarDay.get()+"/"+self.strvarYear.get()

######### Generic Base classes for Data Objects and Database (local/json-text-file based DB)

class GenericObj:
    _CLASS_PARAMS = {}
    def __init__(self, params):
        self.id = 0
        for key in params:
            if self._CLASS_PARAMS[key] > 0:
                setattr(self, key, params[key])
    def toDict(self):
        retDict = {}
        for key in self._CLASS_PARAMS:
            if hasattr(self, key):
                retDict[key] = getattr(self, key)
        return retDict

class GenericDB:
    def __init__(self, dbname):
        self.records = {}
        self.dbname = dbname
        self.fname = dbname + ".json"
        self.nextid = 1
 
    def _toObj(self, raw):
        pass

    def load(self):
        if os.path.exists(self.fname):
            f = open(self.fname, "r")
            fdata = f.read()
            rawdata = json.loads(fdata)
            self.nextid = rawdata["nextid"]
            self.dbname = rawdata["dbname"]
            for rec in rawdata["records"]:
                recObj = self._toObj(rec)
                self.records[recObj.id] = recObj

    def addRecord(self, rec):
        if rec.id > 0:
            if rec.id in self.records:
                rec.id = self.getNextID()
        else:
            rec.id = self.getNextID()
        self.records[rec.id] = rec

    def getNextID(self):
        giveID = self.nextid
        self.nextid += 1
        while self.nextid in self.records:
            self.nextid += 1
        return giveID

    def getRecordWithID(self, recid):
        return self.records[int(recid)]
                
    def getRecordsWithAttr(self, attrib, val):
        retRecords = []
        for rid in self.records:
            rec = self.records[rid]
            if hasattr(rec, attrib) and getattr(rec, attrib) == val:
                retRecords.append(rec)
        return retRecords
                
    def getAllRecords(self):
        retRecords = []
        for rid in self.records:
            rec = self.records[rid]
            retRecords.append(rec)
        return retRecords
                
    def updateRecordWithID(self, recid, attrib, value):
        setattr(self.records[int(recid)], attrib, value)
                
    def deleteRecordWithID(self, recid):
        del self.records[int(recid)]
                
    def save(self):
        filePath = os.path.dirname(self.fname)
        if len(filePath) > 0:
            os.makedirs(filePath, exist_ok=True)
        f = open(self.fname, "w")
        rawdata = {"nextid": self.nextid, "dbname": self.dbname, "records": [] }
        for pid in self.records:
            rawdata["records"].append(self.records[pid].toDict())
        fdata = json.dumps(rawdata)
        f.write(fdata)
        f.close()

########### Player DATA OBJECT AND DATABASE

class Player(GenericObj):
    _CLASS_PARAMS = {"id": 1, "name": 1, "age": 1, "grade": 1, "rating": 1, "gender": 1, "score": 1, "gamesW": 1, "gamesB": 1, \
                     "group": 1, "oppScore": 1, "status": 1}
    def __str__(self):
        return self.group.ljust(6," ")+" "+str(self.score).center(4," ")+" ["+str(self.oppScore).ljust(4," ") + "] "+self.name + " (" + str(self.id) + ")"

class PlayerDB(GenericDB):
    def _toObj(self, raw):
        return Player(raw)

########### Matchup DATA OBJECT AND DATABASE

class Matchup(GenericObj):
    _CLASS_PARAMS = {"id": 1, "idWhitePlayer": 1, "idBlackPlayer": 1, "round": 1, "group": 1, "table": 1, "result": 1,
                     "nameWhitePlayer": 1, "nameBlackPlayer": 1}

    def strPlayerResult(self, pid):
        oppName = ""
        color = "White"
        outcome = "???"
        if self.idWhitePlayer == pid:
            oppName = self.nameBlackPlayer
            if self.result == "White Win":
                outcome = "Won"
            elif self.result == "Black Win":
                outcome = "Lost"
            elif self.result == "Draw":
                outcome = "Drew"
        else:
            color = "Black"
            oppName = self.nameWhitePlayer
            if self.result == "White Win":
                outcome = "Lost"
            elif self.result == "Black Win":
                outcome = "Won"
            elif self.result == "Draw":
                outcome = "Drew"
        return "Rnd "+str(self.round) + " - Tbl " + str(self.table) + " - " + outcome + " as " + color + "  vs  " + oppName.upper()
    
    def __str__(self):
        wname = self.nameWhitePlayer[:20]
        bname = self.nameBlackPlayer[:20]
        if self.result == "White Win":
            wname = self.nameWhitePlayer[:20].upper()
        else:
            if self.result == "Black Win":
                bname = self.nameBlackPlayer[:20].upper()
        return str(self.round) + " - " + str(self.table).center(3," ") + " [" + self.group + "] " \
               + wname.ljust(20," ") + " (W) vs " \
               + bname.ljust(20," ") + " (B) [" + self.result.center(9," ") + "] (" + str(self.id) + ")"

class MatchupDB(GenericDB):
    def _toObj(self, raw):
        return Matchup(raw)

    def load(self):
        super().load()
        self.rebuildOppCount()

    def rebuildOppCount(self):
        self.oppCount = {}
        for rid in self.records:
            rec = self.records[rid]
            if rec.idWhitePlayer in self.oppCount:
                if rec.idBlackPlayer in self.oppCount[rec.idWhitePlayer]:
                    self.oppCount[rec.idWhitePlayer][rec.idBlackPlayer] += 1
                else:
                    self.oppCount[rec.idWhitePlayer][rec.idBlackPlayer] = 1
            else:
                self.oppCount[rec.idWhitePlayer] = {}
                self.oppCount[rec.idWhitePlayer][rec.idBlackPlayer] = 1
            if rec.idBlackPlayer in self.oppCount:
                if rec.idWhitePlayer in self.oppCount[rec.idBlackPlayer]:
                    self.oppCount[rec.idBlackPlayer][rec.idWhitePlayer] += 1
                else:
                    self.oppCount[rec.idBlackPlayer][rec.idWhitePlayer] = 1
            else:
                self.oppCount[rec.idBlackPlayer] = {}
                self.oppCount[rec.idBlackPlayer][rec.idWhitePlayer] = 1

    def getMaxRound(self):
        intRound = 1
        for rid in self.records:
            if self.records[rid].round > intRound:
                intRound = self.records[rid].round
        return intRound

    def getNextRound(self):
        intRound = 0
        for rid in self.records:
            if self.records[rid].round > intRound:
                intRound = self.records[rid].round
        return intRound + 1

    def anyPendingMatchups(self):
        for rid in self.records:
            if self.records[rid].result == "":
                return True
        return False

    def getPlayerMatchups(self, pid):
        plrMatchups = []
        for rid in self.records:
            rec = self.records[rid]
            if (rec.idWhitePlayer == pid or rec.idBlackPlayer == pid):
                plrMatchups.append(rec)
        return plrMatchups
        
    def alreadyPlayed(self, pidA, pidB):
        if pidA in self.oppCount:
            if pidB in self.oppCount[pidA]:
                if self.oppCount[pidA][pidB] > 0:
                    return True
        return False

    def haveMultipleMatchups(self, pidA, pidB):
        if pidA in self.oppCount:
            if pidB in self.oppCount[pidA]:
                if self.oppCount[pidA][pidB] > 1:
                    return True
        return False


########### Event DATA OBJECT AND DATABASE

class Event(GenericObj):
    _CLASS_PARAMS = {"id": 1, "name": 1, "date": 1, "groups": 1, "currentRound": 1, "status": 1}
    def __str__(self):
        return f"{self.name} ({self.id}), Date {self.date}, Round {self.currentRound}, Groups: " + ",".join(self.groups)

class EventDB(GenericDB):
    def _toObj(self, raw):
        return Event(raw)

########### MAIN APPLICATION OBJECT - APPLICATION LOGIC, DB INSTANCES, AND Tk GUI PANEL
###########    has dict of frames that RAISE the active frame to the top depending on current need

class ChessEventApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        fontDefault = font.nametofont('TkDefaultFont')
        dictDefaultFontSettings = fontDefault.actual()
        self.appFonts = {}
        self.appFonts['fontHeader'] = font.Font(family=dictDefaultFontSettings['family'], name='appHeaderFont', size=18, weight='bold')
        self.appFonts['fontBigger'] = font.Font(family=dictDefaultFontSettings['family'], name='appBiggerFont', size=14)
        self.appFonts['fontCredits'] = font.Font(family=dictDefaultFontSettings['family'], name='appCreditsFont', size=dictDefaultFontSettings['size'], slant='italic')
        self.title("Chess Event Manager")
        self.geometry("1200x800")
        self.eventDB = EventDB("chessEvents")
        self.eventDB.load()
        edata = {"id": 0, "name": "Dummy", "date": "", "status": "active", "groups": []}
        self.activeEvent = Event(edata)
        self.playerDB = PlayerDB("dummy")
        self.matchupDB = MatchupDB("dummy")
        self.frames = {}
        self.frames["ChessEventMainMenuFrame"] = ChessEventMainMenuFrame(container, self)
        self.frames["ChessEventMainMenuFrame"].grid(row=0, column=0, sticky="nsew")
        self.frames["ChessEventNewEventFrame"] = ChessEventNewEventFrame(container, self)
        self.frames["ChessEventNewEventFrame"].grid(row=0, column=0, sticky="nsew")
        self.frames["ChessEventEventHomeFrame"] = ChessEventEventHomeFrame(container, self)
        self.frames["ChessEventEventHomeFrame"].grid(row=0, column=0, sticky="nsew")
        self.frames["ChessEventNewPlayerFrame"] = ChessEventNewPlayerFrame(container, self)
        self.frames["ChessEventNewPlayerFrame"].grid(row=0, column=0, sticky="nsew")
        self.showFrame("ChessEventMainMenuFrame")

    def showFrame(self, cont):
        frame = self.frames[cont]
        if cont == "ChessEventEventHomeFrame":
            frame.createWidgets()
        frame.tkraise()

    def returnToMainMenu(self):
        self.showFrame("ChessEventMainMenuFrame")

    def addNewPlayer(self):
        self.showFrame("ChessEventNewPlayerFrame")
 
    def setActiveEventWithId(self, eventId):
        self.activeEvent = self.eventDB.getRecordWithID(eventId)
        self.playerDB = PlayerDB("dbData/event" + str(eventId) + "/players")
        self.playerDB.load()
        self.matchupDB = MatchupDB("dbData/event" + str(eventId) + "/matchups")
        self.matchupDB.load()
        self.frames["ChessEventEventHomeFrame"].setActiveEvent(self.activeEvent)
        self.frames["ChessEventNewPlayerFrame"].createWidgets()
        self.frames["ChessEventMainMenuFrame"].createWidgets()
        ### this is being done by the showFrame below:
        #self.frames["ChessEventEventHomeFrame"].createWidgets()
        self.showFrame("ChessEventEventHomeFrame")

    def makePlayerActive(self, pid):
        self.playerDB.updateRecordWithID(pid, "status", "active")
        self.playerDB.save()

    def putPlayerOnHold(self, pid):
        self.playerDB.updateRecordWithID(pid, "status", "hold")
        self.playerDB.save()

    def withdrawPlayer(self, pid):
        self.playerDB.updateRecordWithID(pid, "status", "withdrawn")
        self.playerDB.save()

    def archiveCurrentEvent(self):
        self.eventDB.updateRecordWithID(self.activeEvent.id, "status", "archived")
        self.eventDB.save()
        self.setActiveEventWithId(self.activeEvent.id)

    def reactivateCurrentEvent(self):
        self.eventDB.updateRecordWithID(self.activeEvent.id, "status", "active")
        self.eventDB.save()
        self.setActiveEventWithId(self.activeEvent.id)

    def deleteCurrentEvent(self):
        if messagebox.askyesno(message='Are you sure that you want to delete this event? There is no way to reverse this!', icon='question', title='Delete Event'):
            self.eventDB.deleteRecordWithID(self.activeEvent.id)
            self.eventDB.save()
            edata = {"id": 0, "name": "Dummy", "date": "", "status": "active", "groups": []}
            self.activeEvent = Event(edata)
            self.playerDB = PlayerDB("dummy")
            self.matchupDB = MatchupDB("dummy")
            self.frames["ChessEventEventHomeFrame"].setActiveEvent(self.activeEvent)
            self.frames["ChessEventEventHomeFrame"].createWidgets()
            self.frames["ChessEventNewPlayerFrame"].createWidgets()
            self.frames["ChessEventMainMenuFrame"].createWidgets()
            self.showFrame("ChessEventMainMenuFrame")
 

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

#         1         2         3         4         5         6         7         8         9
#123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#-----------------------------------------------------------------------------------------
# Pair | Player Name                     |Total|Round|Round|Round|Round|Round|Round|Round| 
# Num  | USCF ID / Rtg (Pre->Post)       | Pts |  1  |  2  |  3  |  4  |  5  |  6  |  7  | 
#-----------------------------------------------------------------------------------------
#    1 | MATTHEW J O'BRIEN               |7.0  |W  10|W   4|W   8|W   2|W   3|W   6|W   7|
#      |                                 |     |B    |W    |B    |W    |B    |W    |B    |
#-----------------------------------------------------------------------------------------
    def createCrossTable(self, group):
        plrGames = { 999: [], 998: [], 997: [] }
        plrRanks = { 999: 0, 998: 0, 997: 0 }
        playerList = sorted(self.playerDB.getRecordsWithAttr("group", group), key=lambda x: (x.score, x.oppScore, x.name), reverse=True)
        i = 1
        rounds = 1
        for p in playerList:
            plrGames[p.id] = []
            plrRanks[p.id] = i
            i += 1
        for m in self.matchupDB.getRecordsWithAttr("group", group):
            if m.round > rounds:
                rounds = m.round
            wPlr = { "color": "W", "opp": str(plrRanks[m.idBlackPlayer]), "round": m.round }
            bPlr = { "color": "B", "opp": str(plrRanks[m.idWhitePlayer]), "round": m.round }
            if m.result == "":
                wPlr['result'] = "?"
                bPlr['result'] = "?"
            elif m.result == "White Win":
                wPlr['result'] = "W"
                bPlr['result'] = "L"
                if m.idBlackPlayer > 990:
                    wPlr['result'] = "B"
                    wPlr['opp'] = ""
                    wPlr['color'] = ""
            elif m.result == "Black Win":
                wPlr['result'] = "L"
                bPlr['result'] = "W"
                if m.idBlackPlayer > 990:
                    wPlr['result'] = "X"
                    wPlr['opp'] = ""
                    wPlr['color'] = ""
            elif m.result == "Draw":
                wPlr['result'] = "D"
                bPlr['result'] = "D"
                if m.idBlackPlayer > 990:
                    wPlr['result'] = "H"
                    wPlr['opp'] = ""
                    wPlr['color'] = ""
            plrGames[m.idWhitePlayer].append(wPlr)
            plrGames[m.idBlackPlayer].append(bPlr)

        ### cross tab header
        strR = "Results for Section: " + group + "\n"
        strR += ("-" * (47 + (6 * rounds))) + "\n Pair | Player Name                     |Total|" + ("Round|" * rounds) \
               + "\n Num  |                                 | Pts |"
        for rnd in list(range(1,(rounds+1))):
            strR += str(rnd).center(5," ") + "|"
        strR += "\n" + ("-" * (47 + (6 * rounds))) + "\n"
        for p in playerList:
            r1 = str(plrRanks[p.id]).rjust(5," ") + " | " + p.name[:31].ljust(32," ") + "|" + str(p.score).ljust(5," ") + "|"
            r2 = "      |" + (" " * 33) + "|     |"
            for pm in plrGames[p.id]:
                r1 += pm['result'] + pm['opp'].rjust(4," ") + "|"
                r2 += pm['color'].ljust(5," ") + "|"
            strR += r1 + "\n" + r2 + "\n"
            strR += ("-" * (47 + (6 * rounds))) + "\n"
        return strR
        
    def recomputeScores(self):
        plrOpponentIDs = { 999: [], 998: [], 997: [] }
        plrScores = { 999: 0, 998: 0, 997: 0 }
        plrWhiteGames = { 999: 0, 998: 0, 997: 0 }
        plrBlackGames = { 999: 0, 998: 0, 997: 0 }
        for p in self.playerDB.getAllRecords():
            plrOpponentIDs[p.id] = []
            plrScores[p.id] = 0
            plrWhiteGames[p.id] = 0
            plrBlackGames[p.id] = 0
        for m in self.matchupDB.getAllRecords():
            if m.result == "":
                continue
            if m.result == "White Win":
                plrScores[m.idWhitePlayer] += 1
            elif m.result == "Black Win":
                plrScores[m.idBlackPlayer] += 1
            elif m.result == "Draw":
                plrScores[m.idWhitePlayer] += 0.5
                plrScores[m.idBlackPlayer] += 0.5
            plrWhiteGames[m.idWhitePlayer] += 1
            plrBlackGames[m.idBlackPlayer] += 1
            plrOpponentIDs[m.idWhitePlayer].append(m.idBlackPlayer)
            plrOpponentIDs[m.idBlackPlayer].append(m.idWhitePlayer)
        for p in self.playerDB.getAllRecords():
            oppScore = 0
            for oppid in plrOpponentIDs[p.id]:
                if oppid < 990:
                    oppScore += plrScores[oppid]
            self.playerDB.updateRecordWithID(p.id, "score", plrScores[p.id])
            self.playerDB.updateRecordWithID(p.id, "oppScore", oppScore)
            self.playerDB.updateRecordWithID(p.id, "gamesW", plrWhiteGames[p.id])
            self.playerDB.updateRecordWithID(p.id, "gamesB", plrBlackGames[p.id])
        self.playerDB.save()
        
    def generateNewMatchups(self, intRound):
        table = 1
        for group in self.activeEvent.groups:
            firstPlayer = None
            plrList = []
            for plr in sorted(self.playerDB.getRecordsWithAttr("group", group), key=lambda x: (x.score, x.oppScore, x.name), reverse=True):
                if plr.status == "hold":
                    mdata = { "round": intRound, "table": 998, "result": "Draw", "group": group }
                    mdata["idWhitePlayer"] = plr.id
                    mdata["nameWhitePlayer"] = plr.name
                    mdata["idBlackPlayer"] = 998
                    mdata["nameBlackPlayer"] = "Hold"
                    matchup = Matchup(mdata)
                    self.matchupDB.addRecord(matchup)
                elif plr.status == "withdrawn":
                    mdata = { "round": intRound, "table": 999, "result": "Black Win", "group": group }
                    mdata["idWhitePlayer"] = plr.id
                    mdata["nameWhitePlayer"] = plr.name
                    mdata["idBlackPlayer"] = 999
                    mdata["nameBlackPlayer"] = "Withdrawn"
                    matchup = Matchup(mdata)
                    self.matchupDB.addRecord(matchup)
                else:
                    plrList.append(plr)
            while len(plrList) > 1:
                firstPlayer = plrList.pop(0)
                mdata = { "round": intRound, "table": table, "result": "", "group": group }
                oppPlayerIDX = -1
                for idx in list(range(0,len(plrList))):
                    if not self.matchupDB.alreadyPlayed(firstPlayer.id, plrList[idx].id):
                        oppPlayerIDX = idx
                        break
                if oppPlayerIDX == -1:
                    oppPlayerIDX = 0
                secondPlayer = plrList.pop(oppPlayerIDX)
                if firstPlayer.gamesW > secondPlayer.gamesW:
                    mdata["idWhitePlayer"] = secondPlayer.id
                    mdata["nameWhitePlayer"] = secondPlayer.name
                    mdata["idBlackPlayer"] = firstPlayer.id
                    mdata["nameBlackPlayer"] = firstPlayer.name
                else:
                    mdata["idWhitePlayer"] = firstPlayer.id
                    mdata["nameWhitePlayer"] = firstPlayer.name
                    mdata["idBlackPlayer"] = secondPlayer.id
                    mdata["nameBlackPlayer"] = secondPlayer.name
                matchup = Matchup(mdata)
                self.matchupDB.addRecord(matchup)
                table += 1
            if len(plrList) == 1:
                mdata = { "round": intRound, "table": 997, "result": "White Win", "group": group }
                mdata["idWhitePlayer"] = plrList[0].id
                mdata["nameWhitePlayer"] = plrList[0].name
                mdata["idBlackPlayer"] = 997
                mdata["nameBlackPlayer"] = "Bye"
                matchup = Matchup(mdata)
                self.matchupDB.addRecord(matchup)
#{"idWhitePlayer": 1, "idBlackPlayer": 1, "round": 1, "group": 1, "table": 1, "result": 1, "nameWhitePlayer": 1, "nameBlackPlayer": 1}
        self.matchupDB.save()
        self.matchupDB.rebuildOppCount()

    def swapMatchupOpponents(self, matchupIdA, matchupIdB, swapColors):
        mA = self.matchupDB.getRecordWithID(matchupIdA)
        mB = self.matchupDB.getRecordWithID(matchupIdB)
        if mA.group != mB.group:
            strTitle = "Error Swapping Opponents!"
            strMessage = "You can only swap opponents between matchups within the same group!"
            messagebox.showinfo(message=strMessage, title=strTitle, icon="error")
        elif mA.result != "" or mB.result != "":
            strTitle = "Error Swapping Opponents!"
            strMessage = "One of the matchups you chose was already completed! You must select exactly 2 unresolved matchups to change opponents."
            messagebox.showinfo(message=strMessage, title=strTitle, icon="error")
        elif swapColors == False:
            tmpId = mA.idBlackPlayer
            tmpName = mA.nameBlackPlayer
            self.matchupDB.updateRecordWithID(mA.id, "idBlackPlayer", mB.idBlackPlayer)
            self.matchupDB.updateRecordWithID(mA.id, "nameBlackPlayer", mB.nameBlackPlayer)
            self.matchupDB.updateRecordWithID(mB.id, "idBlackPlayer", tmpId)
            self.matchupDB.updateRecordWithID(mB.id, "nameBlackPlayer", tmpName)
        else:
            pAw = self.playerDB.getRecordWithID(mA.idWhitePlayer)
            pAb = self.playerDB.getRecordWithID(mA.idBlackPlayer)
            pBw = self.playerDB.getRecordWithID(mB.idWhitePlayer)
            pBb = self.playerDB.getRecordWithID(mB.idBlackPlayer)
            if pBb.gamesB > pAb.gamesB:
                tmpId = mA.idWhitePlayer
                tmpName = mA.nameWhitePlayer
                self.matchupDB.updateRecordWithID(mA.id, "idWhitePlayer", mB.idBlackPlayer)
                self.matchupDB.updateRecordWithID(mA.id, "nameWhitePlayer", mB.nameBlackPlayer)
                self.matchupDB.updateRecordWithID(mB.id, "idBlackPlayer", tmpId)
                self.matchupDB.updateRecordWithID(mB.id, "nameBlackPlayer", tmpName)
            else:
                tmpId = mB.idWhitePlayer
                tmpName = mB.nameWhitePlayer
                self.matchupDB.updateRecordWithID(mB.id, "idWhitePlayer", mA.idBlackPlayer)
                self.matchupDB.updateRecordWithID(mB.id, "nameWhitePlayer", mA.nameBlackPlayer)
                self.matchupDB.updateRecordWithID(mA.id, "idBlackPlayer", tmpId)
                self.matchupDB.updateRecordWithID(mA.id, "nameBlackPlayer", tmpName)
        self.matchupDB.rebuildOppCount()
        self.matchupDB.save()

######## OBJECT THAT IS THE MAIN MENU Frame - used to create or load an event

class ChessEventMainMenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.mainApp = controller
        self.createWidgets()

    def createNewEvent(self):
        self.mainApp.showFrame("ChessEventNewEventFrame")
        
    def createWidgets(self):
        eventListOpts = []
        self.eventListOptIDs = []
        eventArchivedListOpts = []
        self.eventArchivedListOptIDs = []
        for ev in sorted(self.mainApp.eventDB.getAllRecords(), key=lambda x: x.date, reverse=False):
            if ev.status == "archived":
                eventArchivedListOpts.append(str(ev.date) + " - " + ev.name + "   (" + ",".join(ev.groups) + ")")
                self.eventArchivedListOptIDs.append(ev.id)
            else:
                eventListOpts.append(str(ev.date) + " - " + ev.name + "   (" + ",".join(ev.groups) + ")")
                self.eventListOptIDs.append(ev.id)
        labelIntro = tk.Label(self, text="Welcome to the Chess Event Manager!", font=self.mainApp.appFonts['fontBigger'])
        labelIntro.grid(column=0, row=0, columnspan=3, sticky="ew")
        ttk.Button(self, text="New Event", command=self.createNewEvent).grid(column=0, row=1, columnspan=3, padx=4, pady=4)
        ttk.Label(self, text="Manage Active event:").grid(column=0, row=2, sticky="e", pady=2, padx=2)
        self.cboxEventList = ttk.Combobox(self, values=eventListOpts, width=50, state="readonly")
        self.cboxEventList.grid(column=1, row=2, sticky="ew")
        ttk.Button(self, text="Load", command=self.setActiveEvent).grid(column=2, row=2, padx=2, pady=2, sticky="w")
        ttk.Label(self, text="View Archived event:").grid(column=0, row=3, sticky="e", pady=2, padx=2)
        self.cboxEventArchivedList = ttk.Combobox(self, values=eventArchivedListOpts, width=50, state="readonly")
        self.cboxEventArchivedList.grid(column=1, row=3, sticky="ew")
        ttk.Button(self, text="Load", command=self.setActiveEventFromArchive).grid(column=2, row=3, padx=2, pady=2, sticky="w")
        ttk.Button(self, text="Quit", command=self.mainApp.destroy).grid(column=0, row=4, columnspan=3, padx=4, pady=4)
        if os.path.exists('chess-bg2.gif'):
            imgChess = PhotoImage(file='chess-bg2.gif')
            lblImage = ttk.Label(self, image=imgChess)
            lblImage.photo = imgChess
            lblImage.grid(column=0, row=5, columnspan=3, padx=4, pady=4)
            tk.Label(self, text="Software by Lou Miller - 2/21/2025", font=self.mainApp.appFonts['fontCredits']).grid(column=0, row=6, columnspan=3, sticky="sew")
            self.rowconfigure(5, weight=5)
            self.rowconfigure(6, weight=1)
        else:
            tk.Label(self, text="Software by Lou Miller - 2/21/2025", font=self.mainApp.appFonts['fontCredits']).grid(column=0, row=5, columnspan=3, sticky="sew")
            self.rowconfigure(5, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=1)
        
    def setActiveEvent(self, *args):
        if self.cboxEventList.current() > -1:
            self.mainApp.setActiveEventWithId(self.eventListOptIDs[self.cboxEventList.current()])

    def setActiveEventFromArchive(self, *args):
        if self.cboxEventArchivedList.current() > -1:
            self.mainApp.setActiveEventWithId(self.eventArchivedListOptIDs[self.cboxEventArchivedList.current()])

########## OBJECT THAT IS THE CREATE A NEW EVENT Frame - used to create a new event

class ChessEventNewEventFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.mainApp = controller
        self.createWidgets()

    def createWidgets(self):
        self.formEventName = StringVar(self, "")
        self.formEventDate = StringVar(self, "")
        self.grid(sticky="nsew", padx=4, pady=4)
        tk.Label(self, text="Enter values below for a new event", font=self.mainApp.appFonts['fontBigger']).grid(column=0, row=0, columnspan=2, padx=2, pady=2)
        tk.Label(self, text="Name:").grid(column=0, row=1, padx=2, pady=2, sticky="e")
        tk.Entry(self, textvariable=self.formEventName).grid(column=1, row=1, padx=2, pady=2, sticky="ew")
#        listDateWidgetParams = { "minYear": 2025, "maxYear": 2075, "format": "MM/DD/YYYY" }
        listDateWidgetParams = { "minYear": 2025, "maxYear": 2075, "format": "YYYY-MM-DD" }
#        listDateWidgetParams = { "minYear": 2025, "maxYear": 2075, "format": 'Month D, YYYY' }
        tk.Label(self, text="Date ("+listDateWidgetParams['format']+"):").grid(column=0, row=2, padx=2, pady=2, sticky="ne")
        self.formDateWidget = tkDateWidget(self, listDateWidgetParams)
        self.formDateWidget.grid(column=1, row=2, padx=2, pady=2, sticky="w")
#        tk.Entry(self, textvariable=self.formEventDate).grid(column=1, row=2, padx=2, pady=2, sticky="ew")
        tk.Label(self, text="Groups:").grid(column=0, row=3, padx=2, pady=2, sticky="e")

        frm4 = Frame(self)
        self.textGroupWidget = tk.Text(frm4, width=50, height=8)
        self.textGroupWidget.grid(column=0, row=0, sticky="nsew", padx=2, pady=2)
        sbTextGroupList = ttk.Scrollbar(frm4, orient=VERTICAL, command=self.textGroupWidget.yview)
        sbTextGroupList.grid(column=1, row=0, sticky="nsw")
        self.textGroupWidget['yscrollcommand'] = sbTextGroupList.set
        frm4.grid(column=1, row=3, sticky="nsew", padx=2, pady=2)
        frm4.columnconfigure(0, weight=3)
        frm4.rowconfigure(0, weight=3)

        frm = Frame(self)
        tk.Button(frm, text="Save", command=self.setSaveNewEvent).grid(column=0, row=0, padx=2, pady=2)
        tk.Button(frm, text="Cancel", command=self.cancelCreateNewEvent).grid(column=1, row=0, padx=2, pady=2)
        frm.grid(column=0, row=4, columnspan=2)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=5)
        self.rowconfigure(3, weight=1)
        
    def cancelCreateNewEvent(self, *args):
        self.mainApp.showFrame("ChessEventMainMenuFrame")

    def setSaveNewEvent(self, *args):
        edata = {}
        edata["name"] = self.formEventName.get()
        edata["date"] = self.formDateWidget.getValue()
#        edata["date"] = self.formEventDate.get()
        strEventGroups = self.textGroupWidget.get("1.0", "end");
        arrTokens = re.split(r'[,\n]', strEventGroups)
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

######### OBJECT THAT IS THE EVENT HOME PAGE Frame - used to manage and report on an event in progress

class ChessEventEventHomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.mainApp = controller
        edata = {"id": 0, "name": "Dummy", "date": "", "status": "active", "groups": []}
        self.activeEvent = Event(edata)
        self.playerSortOrder = StringVar(self, "group_score")
        self.playerSortOrder.trace('w', self.changeSortOrder)
        self.formMatchupRound = StringVar(self, "1")
        self.formMatchupRound.trace('w', self.changeMatchupRound)
        self.formResultSet = StringVar(self, "")
        self.createWidgets()

    def changeSortOrder(self, *args):
        self.createWidgets()
        
    def changeMatchupRound(self, *args):
        self.createWidgets()

    def returnToMainMenu(self, *args):
        self.mainApp.showFrame("ChessEventMainMenuFrame")
        
    def createWidgets(self):
        self.grid(sticky="nsew", padx=4, pady=4)
        frm = Frame(self)
        tk.Label(frm, text=self.activeEvent.name, font=self.mainApp.appFonts['fontHeader']).grid(column=0, row=0)
        tk.Button(frm, text="Return to Main Menu", command=self.returnToMainMenu).grid(column=1, row=0, padx=2)
        frm.grid(column=0, row=0, padx=2, pady=2, columnspan=2, sticky="ew")
        frm.columnconfigure(0, weight=3)
        self.createWidgetsPlayerFrame()
        self.createWidgetsMatchupFrame()
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=5)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=3)

    def createWidgetsPlayerFrame(self):
        frm = Frame(self)
        self.playerListOpts = []
        self.playerListOptIDs = []
        fgcolorMap = { "active": "", "hold": "#cc9900", "withdrawn": "#cc3300" }
        fgcolor = []
        if self.playerSortOrder.get() == "name":
            for plr in sorted(self.mainApp.playerDB.getAllRecords(), key=lambda x: x.name, reverse=False):
                self.playerListOpts.append(str(plr))
                self.playerListOptIDs.append(plr.id)
                fgcolor.append(fgcolorMap[plr.status])
        else:
            for plr in sorted(self.mainApp.playerDB.getAllRecords(), key=lambda x: (x.group, x.score, x.oppScore, x.name), reverse=True):
                self.playerListOpts.append(str(plr))
                self.playerListOptIDs.append(plr.id)
                fgcolor.append(fgcolorMap[plr.status])
        self.activePlayer = StringVar(self, "")
        self.playerListVar = StringVar(value=self.playerListOpts)
        tk.Label(frm, text="Players/Scores", font=self.mainApp.appFonts['fontBigger']).grid(column=0, row=0, columnspan=1)
        buttonAddPlayers = tk.Button(frm, text="Add Player(s)", command=self.mainApp.addNewPlayer)
        buttonAddPlayers.grid(column=0, row=1, padx=2, pady=1)
        
        frm4 = Frame(frm)
        fontFixedWidth = font.nametofont('TkFixedFont')
        self.textPlayerListWidget = tk.Listbox(frm4, listvariable=self.playerListVar, width=50, height=30, font=fontFixedWidth)
        if len(self.playerListOpts) > 0:
            if self.playerSortOrder.get() == "name":
                for i in range(0,len(self.playerListOpts),2):
                    self.textPlayerListWidget.itemconfigure(i, background='#f0f0ff')
            else:
                currGroup = self.playerListOpts[0][:7]
                shadeItem = False
                for i in range(0,len(self.playerListOpts)):
                    if currGroup != self.playerListOpts[i][:7]:
                        currGroup = self.playerListOpts[i][:7]
                        shadeItem = not shadeItem
                    if shadeItem:
                        self.textPlayerListWidget.itemconfigure(i, background='#f0f0ff')
        for i in range(0,len(self.playerListOpts)):
            if fgcolor[i] != "":
                self.textPlayerListWidget.itemconfigure(i, foreground=fgcolor[i], selectforeground=fgcolor[i])
        self.textPlayerListWidget.grid(column=0, row=0, sticky="nsew")
        self.textPlayerListWidget.bind('<Double-1>', lambda x: self.showPlayerMatchupHistory()) 
        sbTextPlayerList = ttk.Scrollbar(frm4, orient=VERTICAL, command=self.textPlayerListWidget.yview)
        sbTextPlayerList.grid(column=1, row=0, sticky="nsw")
        self.textPlayerListWidget['yscrollcommand'] = sbTextPlayerList.set
        sbBottomTextPlayerList = ttk.Scrollbar(frm4, orient=HORIZONTAL, command=self.textPlayerListWidget.xview)
        sbBottomTextPlayerList.grid(column=0, row=1, sticky="new")
        self.textPlayerListWidget['xscrollcommand'] = sbBottomTextPlayerList.set
        frm4.grid(column=0, row=2, sticky="nsew")
        frm4.columnconfigure(0, weight=3)
        frm4.rowconfigure(0, weight=3)

        frm2 = Frame(frm)
        tk.Label(frm2, text="sort players by").grid(column=0, row=0)
        tk.Radiobutton(frm2, text='Group/Score', variable=self.playerSortOrder, value='group_score').grid(column=1, row=0)
        tk.Radiobutton(frm2, text='Name', variable=self.playerSortOrder, value='name').grid(column=2, row=0)
        frm2.grid(column=0, row=3)
        frm3 = Frame(frm)
        buttonActivate = tk.Button(frm3, text="Activate Player", command=self.activatePlayer)
        buttonActivate.grid(column=0, row=0, padx=2, pady=1)
        buttonHold = tk.Button(frm3, text="Hold Player", command=self.holdPlayer)
        buttonHold.configure(foreground=fgcolorMap["hold"])
        buttonHold.grid(column=1, row=0, padx=2, pady=1)
        buttonWithdraw = tk.Button(frm3, text="Withdraw Player", command=self.withdrawPlayer)
        buttonWithdraw.configure(foreground=fgcolorMap["withdrawn"])
        buttonWithdraw.grid(column=2, row=0, padx=2, pady=1)
        frm3.grid(column=0, row=4)

        if self.activeEvent.status == "archived":
            buttonAddPlayers.config(state=tk.DISABLED)
            buttonActivate.config(state=tk.DISABLED)
            buttonHold.config(state=tk.DISABLED)
            buttonWithdraw.config(state=tk.DISABLED)

        frm.grid(column=0, row=1, padx=2, pady=2, sticky="nsew")
        frm.columnconfigure(0, weight=3)
        frm.rowconfigure(2, weight=3)

    def createWidgetsMatchupFrame(self):
        frm = Frame(self)
        frm.grid()
        tk.Label(frm, text="Matchups", font=self.mainApp.appFonts['fontBigger']).grid(column=0, row=0, columnspan=1)
        frm2 = Frame(frm)
        frm2.grid()
        tk.Label(frm2, text="Round:").grid(column=0, row=0)
        roundOpts = []
        for intRound in list(range(1,self.mainApp.matchupDB.getMaxRound()+1)):
            roundOpts.append(str(intRound))
        ttk.Combobox(frm2, textvariable=self.formMatchupRound, values=roundOpts, state="readonly").grid(column=1, row=0)
        frm2.grid(column=0, row=1)
        self.matchupListOpts = []
        self.matchupListOptIDs = []
        self.matchupListOptGroups = []
#{"idWhitePlayer": 1, "idBlackPlayer": 1, "round": 1, "group": 1, "table": 1, "result": 1, "nameWhitePlayer": 1, "nameBlackPlayer": 1}
        for matchup in sorted(self.mainApp.matchupDB.getRecordsWithAttr("round", int(self.formMatchupRound.get())), key=lambda x: x.table, reverse=False):
            if self.mainApp.matchupDB.haveMultipleMatchups(matchup.idWhitePlayer, matchup.idBlackPlayer):
                self.matchupListOpts.append(str(matchup) + " DUPLICATE")
            else:
                self.matchupListOpts.append(str(matchup))
            self.matchupListOptIDs.append(matchup.id)
            self.matchupListOptGroups.append(matchup.group)
        self.matchupListVar = StringVar(value=self.matchupListOpts)
        fontFixedWidth = font.nametofont('TkFixedFont')
        
        frm4 = Frame(frm)
        self.textMatchupListWidget = tk.Listbox(frm4, listvariable=self.matchupListVar, width=90, height=30, font=fontFixedWidth, exportselection=False, selectmode="multiple")
        if len(self.matchupListOpts) > 0:
            currGroup = self.matchupListOptGroups[0]
            shadeItem = False
            for i in range(1,len(self.matchupListOpts)):
                if currGroup != self.matchupListOptGroups[i]:
                    currGroup = self.matchupListOptGroups[i]
                    shadeItem = not shadeItem
                if shadeItem:
                    self.textMatchupListWidget.itemconfigure(i, background='#f0f0ff')
        self.textMatchupListWidget.grid(column=0, row=0, sticky="nsew")
        sbTextMatchupList = ttk.Scrollbar(frm4, orient=VERTICAL, command=self.textMatchupListWidget.yview)
        sbTextMatchupList.grid(column=1, row=0, sticky="nsw")
        self.textMatchupListWidget['yscrollcommand'] = sbTextMatchupList.set
        sbBottomTextMatchupList = ttk.Scrollbar(frm4, orient=HORIZONTAL, command=self.textMatchupListWidget.xview)
        sbBottomTextMatchupList.grid(column=0, row=1, sticky="new")
        self.textMatchupListWidget['xscrollcommand'] = sbBottomTextMatchupList.set
        frm4.grid(column=0, row=2, sticky="nsew")
        frm4.columnconfigure(0, weight=3)
        frm4.rowconfigure(0, weight=3)

        frm3 = Frame(frm)
        tk.Label(frm3, text="Set Result:").grid(column=0, row=0)
        buttonSetWhiteWins = tk.Button(frm3, text="White Win", command=self.setMatchupResultWhite)
        buttonSetWhiteWins.grid(column=1, row=0, padx=2, pady=1)
        buttonSetBlackWins = tk.Button(frm3, text="Black Win", command=self.setMatchupResultBlack)
        buttonSetBlackWins.grid(column=2, row=0, padx=2, pady=1)
        buttonSetDraw = tk.Button(frm3, text="Draw", command=self.setMatchupResultDraw)
        buttonSetDraw.grid(column=3, row=0, padx=2, pady=1)
        buttonClearResult = tk.Button(frm3, text="(clear)", command=self.setMatchupResultClear)
        buttonClearResult.grid(column=4, row=0, padx=2, pady=1)
        frm3.grid(column=0, row=3)

        frm5 = Frame(frm)
        self.buttonGenerateNextRoundMatchups = tk.Button(frm5, text="Generate New Round Matchups", command=self.generateNewMatchups)
        self.buttonGenerateNextRoundMatchups.grid(column=0, row=0, padx=2, pady=1)
        buttonSwapOppSameColors = tk.Button(frm5, text="Swap Opponents, Same Colors", command=self.swapMatchupOpponentsKeepColors)
        buttonSwapOppSameColors.grid(column=1, row=0, padx=2, pady=1)
        buttonSwapOppChangeColors = tk.Button(frm5, text="Swap Opponents, Change Colors", command=self.swapMatchupOpponentsChangeColors)
        buttonSwapOppChangeColors.grid(column=2, row=0, padx=2, pady=1)
        if self.mainApp.matchupDB.anyPendingMatchups():
            self.buttonGenerateNextRoundMatchups.config(state=tk.DISABLED)
        else:
            self.buttonGenerateNextRoundMatchups.config(state=tk.NORMAL)
        frm5.grid(column=0, row=4, padx=2, pady=1)

        frm6 = Frame(frm)
        tk.Button(frm6, text="Create CrossTables Report", command=self.mainApp.saveCrossTableReport).grid(column=0, row=0, padx=2, pady=1)
        if self.activeEvent.status == "archived":
            tk.Button(frm6, text="Re-Activate This Event", command=self.mainApp.reactivateCurrentEvent).grid(column=1, row=0, padx=2, pady=1)
        else:
            tk.Button(frm6, text="Archive This Event", command=self.mainApp.archiveCurrentEvent).grid(column=1, row=0, padx=2, pady=1)
        buttonDeleteEvent = tk.Button(frm6, text="Delete This Archived Event", command=self.mainApp.deleteCurrentEvent)
        buttonDeleteEvent.grid(column=2, row=0, padx=2, pady=1)
        frm6.grid(column=0, row=5, padx=2, pady=1)

        if self.activeEvent.status == "archived":
            buttonSetWhiteWins.config(state=tk.DISABLED)
            buttonSetBlackWins.config(state=tk.DISABLED)
            buttonSetDraw.config(state=tk.DISABLED)
            buttonClearResult.config(state=tk.DISABLED)
            buttonSwapOppSameColors.config(state=tk.DISABLED)
            buttonSwapOppChangeColors.config(state=tk.DISABLED)
            self.buttonGenerateNextRoundMatchups.config(state=tk.DISABLED)
        else:
            buttonDeleteEvent.config(state=tk.DISABLED)

        frm.grid(column=1, row=1, padx=2, pady=2, sticky="nsew")
        frm.columnconfigure(0, weight=3)
        frm.rowconfigure(2, weight=3)

    def swapMatchupOpponentsKeepColors(self):
        self.swapMatchupOpponents(False)

    def swapMatchupOpponentsChangeColors(self):
        self.swapMatchupOpponents(True)

    def swapMatchupOpponents(self, swapColors):
        matchupIdA = 0
        matchupIdB = 0
        tooManySelected = False
        for idx in self.textMatchupListWidget.curselection():
            if matchupIdA == 0:
                matchupIdA = self.matchupListOptIDs[int(idx)]
            elif matchupIdB == 0:
                matchupIdB = self.matchupListOptIDs[int(idx)]
            else:
                tooManySelected = True
        if tooManySelected or matchupIdB == 0:
            strTitle = "Error Swapping Opponents!"
            strMessage = "You must select exactly 2 unresolved matchups to change opponents."
            messagebox.showinfo(message=strMessage, title=strTitle, icon="error")
        else:
            self.mainApp.swapMatchupOpponents(matchupIdA, matchupIdB, swapColors)
            self.createWidgets()
        
    def setMatchupResultWhite(self):
        self.setMatchupResult("White Win")
        
    def setMatchupResultBlack(self):
        self.setMatchupResult("Black Win")
        
    def setMatchupResultDraw(self):
        self.setMatchupResult("Draw")
        
    def setMatchupResultClear(self):
        self.setMatchupResult("")
        
    def setMatchupResult(self, result):
        resultWasSet = False
        for idx in self.textMatchupListWidget.curselection():
            matchupRec = self.mainApp.matchupDB.getRecordWithID(self.matchupListOptIDs[int(idx)])
            if matchupRec.result != result:
                self.mainApp.matchupDB.updateRecordWithID(self.matchupListOptIDs[int(idx)],"result",result)
                resultWasSet = True
        if resultWasSet:
            self.mainApp.matchupDB.save()
            self.mainApp.recomputeScores()
            self.formResultSet.set("")
            self.createWidgets()

    def setActiveEvent(self, event):
        self.activeEvent = event
        self.createWidgets()

    def showPlayerMatchupHistory(self):
        for idx in self.textPlayerListWidget.curselection():
            pid = self.playerListOptIDs[idx]
            plr = self.mainApp.playerDB.getRecordWithID(pid)
            strTitle = "Matchups for " + plr.name
            strMessage = ""
            for matchup in self.mainApp.matchupDB.getPlayerMatchups(pid):
                strMessage += matchup.strPlayerResult(pid) + "\n"
            messagebox.showinfo(message=strMessage, title=strTitle)
    
    def activatePlayer(self):
        for idx in self.textPlayerListWidget.curselection():
            self.mainApp.makePlayerActive(self.playerListOptIDs[idx])
        self.createWidgets()

    def holdPlayer(self):
        for idx in self.textPlayerListWidget.curselection():
            self.mainApp.putPlayerOnHold(self.playerListOptIDs[idx])
        self.createWidgets()

    def withdrawPlayer(self):
        for idx in self.textPlayerListWidget.curselection():
            self.mainApp.withdrawPlayer(self.playerListOptIDs[idx])
        self.createWidgets()

    def generateNewMatchups(self):
        if self.mainApp.matchupDB.anyPendingMatchups():
            return
        intRound = self.mainApp.matchupDB.getNextRound()
        self.mainApp.generateNewMatchups(intRound)
        self.formMatchupRound.set(intRound)
        self.createWidgets()

######### OBJECT TO CREATE A NEW PLAYER(s) Frame - used to add players to play in an event

class ChessEventNewPlayerFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.mainApp = controller
        self.checkRatingWrapper = (self.mainApp.register(self.valCheckRating), '%P')
        self.formPlayerGroup = StringVar(self, "")
        self.formPlayerGrade = StringVar(self, "")
        self.formPlayerAge = StringVar(self, "")
        self.formPlayerRating = StringVar(self, "")
        self.formPlayerGender = StringVar(self, "")
        self.createWidgets()

    def valCheckRating(newval):
        return re.match('^[0-9]*$', newval) is not None and len(newval) <= 4

    def createWidgets(self):
        playerGroupOpts = self.mainApp.activeEvent.groups
        playerAgeOpts = [""]
        for age in list(range(1,99)):
            playerAgeOpts.append(str(age))
        playerGradeOpts = ["K","1","2","3","4","5","6","7","8","9","10","11","12","Col"]
        playerGenderOpts = ["","Male","Female"]
        #{"id": 1, "name": 1, "age": 1, "grade": 1, "rating": 1, "gender": 1, "score": 1, "gamesW": 1, "gamesB": 1, "group": 1}
        self.grid(sticky="nsew", padx=4, pady=4)
        tk.Label(self, text="Enter data below for new players, enter a new name on each line to create multiple players that share all other data values", font=self.mainApp.appFonts['fontBigger']).grid(column=0, row=0, columnspan=3)
        tk.Label(self, text="Name(s):").grid(column=0, row=1, padx=2, pady=2, sticky="e")

        frm4 = Frame(self)
        self.textPlayerNameWidget = tk.Text(frm4, width=30, height=8)
        self.textPlayerNameWidget.grid(column=0, row=0, sticky="nsew", padx=2, pady=2)
        sbTextPlayerNameList = ttk.Scrollbar(frm4, orient=VERTICAL, command=self.textPlayerNameWidget.yview)
        sbTextPlayerNameList.grid(column=1, row=0, sticky="nsw")
        self.textPlayerNameWidget['yscrollcommand'] = sbTextPlayerNameList.set
        frm4.grid(column=1, row=1, sticky="nsew", padx=2, pady=2)
        frm4.columnconfigure(0, weight=3)
        frm4.rowconfigure(0, weight=3)

        tk.Label(self, text="Group:").grid(column=0, row=2, padx=2, pady=2, sticky="e")
        ttk.Combobox(self, textvariable=self.formPlayerGroup, values=playerGroupOpts, state="readonly").grid(column=1, row=2, padx=2, pady=2, sticky="w")
        tk.Label(self, text="Age:").grid(column=0, row=3, padx=2, pady=2, sticky="e")
        ttk.Combobox(self, textvariable=self.formPlayerAge, values=playerAgeOpts, state="readonly").grid(column=1, row=3, padx=2, pady=2, sticky="w")
        tk.Label(self, text="Gender:").grid(column=0, row=4, padx=2, pady=2, sticky="e")
        ttk.Combobox(self, textvariable=self.formPlayerGender, values=playerGenderOpts, state="readonly").grid(column=1, row=4, padx=2, pady=2, sticky="w")
        tk.Label(self, text="Grade:").grid(column=0, row=5, padx=2, pady=2, sticky="e")
        ttk.Combobox(self, textvariable=self.formPlayerGrade, values=playerGradeOpts, state="readonly").grid(column=1, row=5, padx=2, pady=2, sticky="w")
        tk.Label(self, text="Rating:").grid(column=0, row=6, padx=2, pady=2, sticky="e")
        tk.Entry(self, textvariable=self.formPlayerRating, validatecommand=self.checkRatingWrapper).grid(column=1, row=6, padx=2, pady=2, sticky="w")
        frm = Frame(self)
        frm.grid()
        tk.Button(frm, text="Save", command=self.setSaveNewPlayer).grid(column=0, row=0, padx=2, pady=2)
        tk.Button(frm, text="Cancel", command=self.cancelAddNewPlayer).grid(column=1, row=0, padx=2, pady=2)
        frm.grid(column=0, row=7, columnspan=3, padx=2, pady=2)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=3)
        
    def clearForm(self):
        self.formPlayerGrade.set("")
        self.formPlayerGender.set("")
        self.formPlayerGroup.set("")
        self.formPlayerRating.set("")
        self.formPlayerAge.set("")
        self.textPlayerNameWidget.delete("1.0", "end");

    def cancelAddNewPlayer(self, *args):
        self.clearForm()
        self.mainApp.showFrame("ChessEventEventHomeFrame")

    def setSaveNewPlayer(self, *args):
        pdata = {"gamesW": 0, "gamesB": 0, "score": 0, "oppScore": 0, "status": "active"}
        pdata["grade"] = self.formPlayerGrade.get()
        pdata["gender"] = self.formPlayerGender.get()
        pdata["group"] = self.formPlayerGroup.get()
        pdata["rating"] = self.formPlayerRating.get()
        pdata["age"] = self.formPlayerAge.get()

        self.mainApp.playerDB.load()
        strPlayerNames = self.textPlayerNameWidget.get("1.0", "end");
        arrTokens = re.split(r'[,\n]', strPlayerNames)
        for tok in arrTokens:
            if len(tok.strip()) > 0:
                pdata["name"] = tok.strip()
                plr = Player(pdata)
                self.mainApp.playerDB.addRecord(plr)
        self.mainApp.playerDB.save()
        self.clearForm()
        self.mainApp.showFrame("ChessEventEventHomeFrame")


###################################################
### Change to the user's Document Directory and start the program!!

workingDir = os.path.join(os.path.expanduser("~"), "Documents", "ChessEventPlanner")
os.makedirs(workingDir, exist_ok=True)
os.chdir(workingDir)
myChessEventApp = ChessEventApp()
myChessEventApp.mainloop()

