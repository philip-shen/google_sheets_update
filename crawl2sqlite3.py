#2018/10/15 Intial test code to crawl weekly targets csv files.
#2018/10/27 Adapte from test_sqilte3.py for daily crawl.
####################################################
import os,sys,time,logging,datetime
import urllib.request
from lxml import html
import httplib2
from apiclient import discovery

class Flag:
    auth_host_name = 'localhost'
    noauth_local_webserver = False
    auth_host_port = [8080, 8090]
    logging_level = 'ERROR'

try:
    import argparse

    # flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    flags = Flag()
except ImportError:
    flags = None

strabspath=os.path.abspath(__file__)
strdirname=os.path.dirname(strabspath)
#str_split=os.path.split(strdirname)
#prevdirname=str_split[0]
dirnamelib=os.path.join(strdirname,"lib")
dirnamelog=os.path.join(strdirname,"log")
##dirdatafolder = os.path.join(prevdirname,'data')

sys.path.append(dirnamelib)
from lib.excelRW import *
from lib.twstockInfo import *
from lib.googleDrive import GoogleDrivebyFileID as google_drive
from lib.readConfig import *

# Set logging
if not os.path.isdir('log'):
    os.makedirs('log')

logging.basicConfig(filename='log/crawl-error.log',level=logging.ERROR,
                    format='%(asctime)s\t[%(levelname)s]\t%(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

# Get present time to measure time consumption
start = time.time()
local_time = time.localtime(start)
#start_time = local_time
print('Start Time is ', local_time.tm_year,'/',local_time.tm_mon,'/',local_time.tm_mday,' ',local_time.tm_hour,":",local_time.tm_min,":",local_time.tm_sec)


logging.error('Begin Time:')

localReadConfig = ReadConfig('config.ini')
url_moneyhunter =localReadConfig.get_SeymourExcel('url_moneyhunterblog')#'http://twmoneyhunter.blogspot.com/'
str_last_year_month_day = localReadConfig.get_SeymourExcel("last_year_month_day")
str_first_year_month_day = localReadConfig.get_SeymourExcel("first_year_month_day")

xpath_url_file01 = '//*[@id="LinkList1"]/div/ul/li[4]/a/@href'#循環投資
xpath_url_file02 = '//*[@id="LinkList1"]/div/ul/li[3]/a/@href'#波段投機
xpath_url_file03 = '//*[@id="LinkList1"]/div/ul/li[5]/a/@href'#景氣循環
xpath_url_file04 = '//*[@id="LinkList1"]/div/ul/li[6]/a/@href'#公用事業

#Python urllib urlopen not working
#https://stackoverflow.com/questions/25863101/python-urllib-urlopen-not-working
###########################################
with urllib.request.urlopen(url_moneyhunter) as response:
    raw = response.read()
html_doc = html.fromstring(raw)

credential_dir = os.getcwd()

localgoogle_drive = google_drive(dirnamelog,flags)
credentials = localgoogle_drive.get_credentials(credential_dir)
http = credentials.authorize(httplib2.Http())
service = discovery.build('drive', 'v3', http=http)

fileid_file01 = localgoogle_drive.ggdrive_fileid(html_doc,xpath_url_file01)
fileid_file02 = localgoogle_drive.ggdrive_fileid(html_doc,xpath_url_file02)
fileid_file03 = localgoogle_drive.ggdrive_fileid(html_doc,xpath_url_file03)
fileid_file04 = localgoogle_drive.ggdrive_fileid(html_doc,xpath_url_file04)

excel_file05 = localReadConfig.get_SeymourExcel("excelfile05") #"追蹤股_增加遞補"2018/11/10

# check 4 kind target of excel files if under log folder or not then download those or not
list_xlsfile, excel_file01 = localgoogle_drive.check_xlsfile_logfolder(fileid_file01)#"循環投資追蹤股"
localgoogle_drive.download_xlsfile_fromblog(list_xlsfile,fileid_file01)

list_xlsfile, excel_file02 = localgoogle_drive.check_xlsfile_logfolder(fileid_file02)#"波段投機追蹤股"
localgoogle_drive.download_xlsfile_fromblog(list_xlsfile,fileid_file02)

list_xlsfile, excel_file03 = localgoogle_drive.check_xlsfile_logfolder(fileid_file03)#"景氣循環追蹤股"
localgoogle_drive.download_xlsfile_fromblog(list_xlsfile,fileid_file03)

list_xlsfile, excel_file04 = localgoogle_drive.check_xlsfile_logfolder(fileid_file04)#"公用事業追蹤股"
localgoogle_drive.download_xlsfile_fromblog(list_xlsfile,fileid_file04)


#"循環投資追蹤股" #"波段投機追蹤股" #"景氣循環追蹤股" #"公用事業追蹤股"#"追蹤股_增加遞補"
list_excel_file = [excel_file01,excel_file02,excel_file03,excel_file04]
#list_excel_file = [excel_file05]

# Test class by excelRW.py
# read each Excel file content ot get stock idx and name
localexcelrw = ExcelRW()
list_all_stockidx=localexcelrw.get_all_stockidx_SeymourExcel(dirnamelog,list_excel_file)

# 2018/10/24 Initial to sqlite test code
path_db = os.path.join(dirnamelog,'TWTSEOTCDaily.db')
sql_create_TseOtcDaily_table = """ CREATE TABLE IF NOT EXISTS TseOtcDaily (
                                        id integer PRIMARY KEY,
                                        trade_date text NOT NULL,
                                        trade_volumn text,
                                        trade_amount text,
                                        open_price text,
                                        high_price text,
                                        low_price text,
                                        close_price text,
                                        change text,
                                        tran_saction text,
                                        stkidx text,
                                        cmp_name text   
                                    ); """

localtwstock_info_db = DB_sqlite(path_db)
# create a database connection
conn = localtwstock_info_db.create_connection()
if conn is not None:
    # create projects table
    localtwstock_info_db.create_table(conn, sql_create_TseOtcDaily_table)
else:
    print("Error! cannot create the database connection.")

 
# 2018/10/27 Optimize flow to get all stock idxs from Excel files and then execute main_fromfirst_tolast()
localtwstock_info = CrawlTSEOTC([],dirnamelog,str_first_year_month_day,str_last_year_month_day)
localtwstock_info.crawl_date_fromfirst_tolast_tosqlite(list_all_stockidx,localtwstock_info_db,conn)

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

# Get the last time
#local_time = time.localtime(time.time())
#print('Final Time is ', local_time.tm_year,'/',local_time.tm_mon,'/',local_time.tm_mday,' ',local_time.tm_hour,":",local_time.tm_min,":",local_time.tm_sec)
duration = time.time() - start
print('Update data duration: {:.2f} seconds'.format(duration))
logging.error('Finish Time:')