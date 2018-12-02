## 2018/12/02 Adapter from GSpreadAmy1210.py
##              
#################################################################################
# Import library to know the time
import time,datetime
import os,sys

from lib.googleSS import GoogleSS as googleSS
from lib.readConfig import ReadConfig as readConfig
#from lib.dataAnalysis import PandasSqliteAnalysis as data_analysis

strabspath=os.path.abspath(__file__)
strdirname=os.path.dirname(strabspath)
dirnamelog=os.path.join(strdirname,"log")
#dirdatafolder = os.path.join(strdirname,'data')
path_db = os.path.join(dirnamelog,'TWTSEOTCDaily.db')

# read parameter from config.ini
localReadConfig = readConfig('config.ini')
gspreadsheet = localReadConfig.get_GSpread("sheet")
GDriveJSON =  localReadConfig.get_GSpread("gsheetJSON")
list_worksheet_spread = localReadConfig.get_WorkSheet_Account("worksheet").split(',')
str_delay_sec = localReadConfig.get_WorkSheet_Account("delay_sec")
str_first_year_month_day = localReadConfig.get_SeymourExcel("first_year_month_day")

print('將讀取試算表' ,gspreadsheet , '的資料')

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# Declare GoogleSS() from googleSS.py
localGoogleSS=googleSS(str_delay_sec,dirnamelog,path_db,str_first_year_month_day)
localGoogleSS.auth_gss_client(GDriveJSON, scope)

for worksheet_spread in list_worksheet_spread:
    # measure time consumption
    start = time.time()

    localGoogleSS.open_GSworksheet(gspreadsheet,worksheet_spread)

    print('將讀取及更新試算表', gspreadsheet, '中WorkSheet:', worksheet_spread, '的資料')
    #inital row count value 2
    row_count = 2

    localGoogleSS.update_GSpreadworksheet_datafolderCSV(row_count)

    duration = time.time() - start
    print('Update data of {} duration: {:.2f} seconds'.format(worksheet_spread,duration))                                                     