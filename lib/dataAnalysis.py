import pandas as pd
import numpy as np
import sqlite3
from sqlite3 import Error

class PandasSqliteAnalysis:
    def __init__(self,stkidx,dirnamelog,path_db,str_first_year_month_day,opt_verbose='OFF'):
        self.stkidx = stkidx
        self.dirnamelog = dirnamelog
        self.path_db = path_db
        self.str_first_year_month_day = str_first_year_month_day
        self.opt_verbose = opt_verbose

        # to filter clsoe price if includes '---' or '--' or not in WHERE
        sql_query_TseOtcDaily_table = """ SELECT DISTINCT  
                                        trade_date AS date,
                                        open_price AS open,
                                        high_price AS high,
                                        low_price AS low,
                                        close_price AS close,
                                        stkidx,
                                        cmp_name AS CmpName
                                        FROM TseOtcDaily
                                        WHERE (
                                        stkidx LIKE {} AND
                                        close_price NOT LIKE '%-'
                                        )  
                                        ORDER BY trade_date ASC; """.format(self.stkidx)
        # get date, open, high, low, close price and volume from TWTSEOTCDaily.db
        #           date    open    high     low   close stkidx cmp_name
        #235  2018/10/22   70.40   72.80   70.20   72.10   9951       皇田
        #236  2018/10/23   72.20   72.70   71.60   71.60   9951       皇田
        #237  2018/10/24   71.80   71.80   70.90   71.70   9951       皇田
        #238  2018/10/25   70.30   70.40   69.30   69.80   9951       皇田
        #239  2018/10/26   70.00   70.60   69.70   70.00   9951       皇田
        
        # create a database connection
        conn = sqlite3.connect(self.path_db)
        if conn is not None:
            # get date and close from TWTSEOTCDaily.db
            df_sql_stockfile = pd.read_sql_query(sql_query_TseOtcDaily_table, conn,
                                    parse_dates = ['date'])
            df = df_sql_stockfile.copy()
        else:
            print("Error! cannot create t he database connection.")

        self.df = df
        # close a database connection
        conn.close()
        
        #print(self.df)
        # get row count
        if self.opt_verbose.lower == 'on':
            #print(self.df)
            print(self.df['date'])
            print("original row counts: {}".format(len(self.df.index)))

    # 2018/11/5 class GoogleSS def update_GSpreadworksheet_datafolderCSV() need
    #           nonetradeday dfinof
    def get_tradedaysANDnonetradeday_dfinfo(self):
        df_delduplicates = self.df.drop_duplicates()
        return df_delduplicates          