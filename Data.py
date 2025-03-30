def generateQuery(self):
    #sqlite3 Metro.db <<EOS
    #.mode csv
    #.import rawData.csv Zip
    #EOS
    
    table = self.grouptingType.get()
    start_date = self.reportStartDate.get()
    end_date = self.reportEndDate.get()
    #grouping_type = self.groupingType.get()
    national_appreciation = self.nationalAppreciation.get()
    estimate_length = self.estimateLength.get()

    # Create the SELECT statement
    query = f"""
    SELECT * FROM '{table}'
    WHERE report_date BETWEEN '{start_date}' AND '{end_date}'
    AND national_appreciation = '{national_appreciation}'
    AND estimate_length = '{estimate_length}'
    """
    return query
    
    pass
