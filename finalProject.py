import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
import os
import re
from functools import partial
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


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
    
######## OBJECT THAT IS THE MAIN MENU Frame - used to create or load an event

class MetroAnalysisMainMenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.mainApp = controller
        self.createWidgets()
        
    def createWidgets(self):
        labelIntro = tk.Label(self, text="Welcome to the Metro Analysis Tool!", font=self.mainApp.appFonts['fontBigger'])
        labelIntro.grid(column=0, row=0, columnspan=3, sticky="ew")
        
        ttk.Button(self, text="New Report", command=self.runNewReport).grid(column=0, row=1, padx=4, pady=4)
        #ttk.Button(self, text="View Saved Reports", command=self.viewSavedReport).grid(column=1, row=1, padx=4, pady=4)
        ttk.Button(self, text="Quit", command=self.mainApp.destroy).grid(column=2, row=1, padx=4, pady=4)

        # Image display
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, 'Metro.gif')
        if os.path.exists(image_path):
            imgHouse = PhotoImage(file=image_path)
            lblImage = ttk.Label(self, image=imgHouse)
            lblImage.photo = imgHouse
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

    def forecastZip(self, df, zip_code, months):
        # Filter for the ZIP code and sort
        df_zip = df[df['Zip Code'] == zip_code]
        
        predFull = []
        predHalf = []
        predQuarter = []
        slopeNational = 5
        slopeGiven = int(self.nationalAppreciation.get())

        '''
        Base slope would be the original values: 
        calcSlopeFull = (df_zip['Value'].iloc[-1] - df_zip['Value'].iloc[0]) / len(df_zip['Value'])
        calcSlopeHalf = (df_zip['Value'].iloc[-1] - df_zip['Value'].iloc[int(len(df_zip['Value'])/2)]) / (len(df_zip['Value'])/2)
        calcSlopeQuarter = (df_zip['Value'].iloc[-1] - df_zip['Value'].iloc[int(len(df_zip['Value'])/4)]) / (len(df_zip['Value'])/4)

        However, in order to reflect the users projected appreciation, 
        an offset needed to be made to the latest home value to handle both increasing and increasing slopes 
        appropriately. My initial attempts were to scale the slope by the ratio of the userAppreciation/actualAppreciation, 
        but this failed for negative slopes.
        '''
        
        userAppreciationRateChange = (slopeGiven - slopeNational)/100
        calcSlopeFull = (df_zip['Value'].iloc[-1] + (df_zip['Value'].iloc[-1] * userAppreciationRateChange * (len(df_zip['Value'])/12)) - df_zip['Value'].iloc[0]) / len(df_zip['Value'])
        calcSlopeHalf = (df_zip['Value'].iloc[-1] + (df_zip['Value'].iloc[-1] * userAppreciationRateChange * (len(df_zip['Value'])/24)) - df_zip['Value'].iloc[int(len(df_zip['Value'])/2)]) / (len(df_zip['Value'])/2)
        calcSlopeQuarter = (df_zip['Value'].iloc[-1] + (df_zip['Value'].iloc[-1] * userAppreciationRateChange * (len(df_zip['Value'])/48)) - df_zip['Value'].iloc[int(len(df_zip['Value']) * (3/4))]) / (len(df_zip['Value'])/4)

        startingVal = df_zip['Value'].iloc[-1]
        predFull.append(startingVal + calcSlopeFull)
        predHalf.append(startingVal + calcSlopeHalf)
        predQuarter.append(startingVal + calcSlopeQuarter)
        
        # Compute Forecast Values
        for m in range(1,months):
            predFull.append(predFull[m-1] + calcSlopeFull)
            predHalf.append(predHalf[m-1] + calcSlopeHalf)
            predQuarter.append(predQuarter[m-1] + calcSlopeQuarter) 

        # Future dates
        last_date = df_zip['Date'].max()
        future_dates = pd.date_range(start=last_date + pd.offsets.MonthEnd(1), periods=months, freq='M')
        return df_zip, future_dates, predFull, predHalf, predQuarter

        
    def checkInputs(self):
        # Check for empty strings
        zip1 = self.groupingValue1.get()
        zip2 = self.groupingValue2.get()
        app = self.nationalAppreciation.get()
        len = self.estimateLength.get()
        start = self.reportStartDate.get()

        if (self.groupingValue1.get() == '' 
            or self.groupingValue2.get() == ''
            or self.nationalAppreciation.get() == '' 
            or self.estimateLength.get() == '' 
            or self.reportStartDate.get() == ''):
            messagebox.showwarning("Warning", "You have left one of the necessary fields empty.")
            return False
        elif (re.search(r'\d+', zip1) == None or re.search(r'\d+', zip2) == None or re.search(r'\d+', len) == None or re.search(r'\d+', app) == None):
            messagebox.showwarning("Warning", "You have one of the numerical fields with the wrong type.")
            return False
        
        return True


    def generateQuery(self):
        # Fetch user values
        zip1 = self.groupingValue1.get()
        zip2 = self.groupingValue2.get()

        # Create the SELECT statement
        query = f"""
        SELECT * FROM Zip
        WHERE RegionName IN ('{zip1}', '{zip2}')
        """
        return query


    def generateResults(self, *args):
        
        if not self.checkInputs():
            return  

        # Path declaration
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # For Testing (PA only)
        #db_path = os.path.join(BASE_DIR, "Test.db")
        
        # For all of USA
        db_path = os.path.join(BASE_DIR, "Data.db")
        
        # Connect to DB
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Perform Query on DB
        query = self.generateQuery()
        df = pd.read_sql_query(query, connection)
        cursor.close()
        connection.close()

        # DF preparation
        startDate = self.reportStartDate.get()
        id_vars = ['RegionID', 'SizeRank', 'RegionName', 'RegionType', 'StateName', 'State', 'City', 'Metro', 'CountyName']
        df_long = pd.melt(df, id_vars=id_vars, var_name='Date', value_name='Value')
        df_long = df_long.rename(columns={'RegionName': 'Zip Code'})
        df_long['Date'] = pd.to_datetime(df_long['Date'])
        df_long['Value'] = pd.to_numeric(df_long['Value'], errors='coerce')
        df_long = df_long[(df_long['Date'] > f'{startDate}-01')]
        df_cleaned = df_long.dropna(subset=['Value'])

        # Extract zip codes
        zip1 = self.groupingValue1.get()
        zip2 = self.groupingValue2.get()

        # Perform prediction
        length = self.estimateLength.get()
        monthsMatch = re.search(r'\d+', length)
        if monthsMatch and int(monthsMatch.group()) > 0:
            months = int(monthsMatch.group())

            # Run forecast for both ZIPs
            df1, dates1, predsF1, predsH1, predsQ1 = self.forecastZip(df_cleaned, int(zip1), months)
            df2, dates2, predsF2, predsH2, predsQ2 = self.forecastZip(df_cleaned, int(zip2), months)

            # Plot 
            plt.figure(figsize=(14, 7))

            # Historical
            plt.plot(df1['Date'], df1['Value'], label=f'Historical {zip1}')
            plt.plot(df2['Date'], df2['Value'], label=f'Historical {zip2}')

            # Forecasts
            plt.plot(dates1, predsF1, '--', label=f'Full Interval Forecast {zip1}')
            plt.plot(dates2, predsF2, '--', label=f'Full Interval Forecast {zip2}')
            plt.plot(dates1, predsH1, '--', label=f'Half Interval Forecast {zip1}')
            plt.plot(dates2, predsH2, '--', label=f'Half Interval Forecast {zip2}')
            plt.plot(dates1, predsQ1, '--', label=f'Quarter Interval Forecast {zip1}')
            plt.plot(dates2, predsQ2, '--', label=f'Quarter Interval Forecast {zip2}')

            # draw a gray connecting line
            plt.plot(
                [df1['Date'].iloc[-1], dates1[0]],
                [df1['Value'].iloc[-1], predsF1[0]],
                'green', linestyle='dotted'
            )

            plt.plot(
                [df1['Date'].iloc[-1], dates1[0]],
                [df1['Value'].iloc[-1], predsH1[0]],
                'orange', linestyle='dotted'
            )

            plt.plot(
                [df1['Date'].iloc[-1], dates1[0]],
                [df1['Value'].iloc[-1], predsQ1[0]],
                'red', linestyle='dotted'
            )

            plt.plot(
                [df2['Date'].iloc[-1], dates2[0]],
                [df2['Value'].iloc[-1], predsF2[0]],
                'green', linestyle='dotted'
            )

            plt.plot(
                [df2['Date'].iloc[-1], dates2[0]],
                [df2['Value'].iloc[-1], predsH2[0]],
                'orange', linestyle='dotted'
            )

            plt.plot(
                [df2['Date'].iloc[-1], dates2[0]],
                [df2['Value'].iloc[-1], predsQ2[0]],
                'red', linestyle='dotted'
            )

            plt.title(f"{months}-Month Linear Forecast (Zip Codes {zip1} and {zip2})")
            plt.xlabel("Date (by year and month)")
            plt.ylabel("Zillow Housing Homeprice Index (advanced median)")
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            # Save
            save_path = os.path.join(BASE_DIR, "Visuals", f"{months}-Month Linear Forecast (Zip Codes {zip1} and {zip2})")
            plt.savefig(save_path, dpi=300)
            
            # Show plot
            plt.show()
        else:
            # Plot 
            plt.figure(figsize=(14, 7))

            df_zip1 = df_cleaned[df_cleaned['Zip Code'] == int(zip1)]
            df_zip2 = df_cleaned[df_cleaned['Zip Code'] == int(zip2)]
            # Historical            
            plt.plot(df_zip1['Date'], df_zip1['Value'], label=f'Historical {zip1}')
            plt.plot(df_zip2['Date'], df_zip2['Value'], label=f'Historical {zip2}')
            plt.title(f"Historical Data (for Zip Codes {zip1} and {zip2})")
            plt.xlabel("Date (by year and month)")
            plt.ylabel("Zillow Housing Homeprice Index (advanced median)")
            plt.grid(True)
            plt.tight_layout()
            plt.legend()

            # Save
            save_path = os.path.join(BASE_DIR, "Visuals", f"Historical Data (for Zip Codes {zip1} and {zip2})")
            plt.savefig(save_path, dpi=300)
            
            # Show plot
            plt.show()

        pass


    def returnToMainMenu(self, *args):
        self.mainApp.showFrame("MetroAnalysisMainMenuFrame")
        
    def createWidgets(self):
        self.formEventName = StringVar(self, "")
        self.formEventDate = StringVar(self, "")

        self.grid(sticky="nsew", padx=4, pady=4)
        
        groupingCategories = ["Zip Code", "Metro", "County"]

        # Create parameter objects with declarations
        self.groupingType = StringVar(self, "Zip Code")
        self.groupingValue1 = StringVar(self, "18064")
        self.groupingValue2 = StringVar(self, "34287")
        self.reportStartDate = StringVar(self, "2022-01")
        self.reportEndDate = StringVar(self, "2025-03")
        self.nationalAppreciation = StringVar(self, "4")
        self.estimateLength = StringVar(self, "12")

        # Heading 
        tk.Label(self, text="Select Parameters", font=self.mainApp.appFonts['fontHeader']).grid(column=0, row=0, columnspan=4, padx=2, pady=2, sticky="ew")

        # First row of inputs
        tk.Label(self, text="Zip Codes: ").grid(column=0, row=1, padx=2, pady=2, sticky="e")
        tk.Entry(self, textvariable=self.groupingValue1).grid(column=1, row=1, padx=2, pady=2, sticky="w")
        tk.Label(self, text="and").grid(column=2, row=1, padx=2, pady=2, sticky="ew")
        tk.Entry(self, textvariable=self.groupingValue2).grid(column=3, row=1, padx=2, pady=2, sticky="w")
        
        # Second row of inputs
        tk.Label(self, text="Date Range (year-month)").grid(column=0, row=2, padx=2, pady=2, sticky="e")
        tk.Entry(self, textvariable=self.reportStartDate).grid(column=1, row=2, padx=2, pady=2, sticky="w")
        
        tk.Label(self, text="National Appreciation Estimate (percentage as int)").grid(column=0, row=3, padx=2, pady=2, sticky="e")
        tk.Entry(self, textvariable=self.nationalAppreciation).grid(column=1, row=3, padx=2, pady=2, sticky="w")
        
        tk.Label(self, text="Time Series Length (in months)").grid(column=0, row=4, padx=2, pady=2, sticky="e")
        tk.Entry(self, textvariable=self.estimateLength).grid(column=1, row=4, padx=2, pady=2, sticky="w")
        
        ttk.Button(self, text="Generate Report", command=self.generateResults).grid(column=0, row=5, padx=2, pady=2)
        ttk.Button(self, text="Exit", command=self.returnToMainMenu).grid(column=1, row=5, padx=2, pady=2)

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

