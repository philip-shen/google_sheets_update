import os,sys,logging,time
from datetime import datetime, timedelta
from os import mkdir
from os.path import isdir
import requests
import json, yaml
import sqlite3
from sqlite3 import Error

class DB_sqlite:
    def __init__(self, path_db_file):
        self.path_db_file = path_db_file

    def create_connection(self):
        """ create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect(self.path_db_file)
            #print(sqlite3.version)
            return conn
        except Error as e:
            print(e)
        
        return None

    def create_table(self,conn, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_tseotcdaily_many(self, conn, list_tseotcdailyinfo_s):

        sql = ''' INSERT INTO TseOtcDaily(trade_date,
                                        trade_volumn,
                                        trade_amount,
                                        open_price,
                                        high_price,
                                        low_price,
                                        close_price,
                                        change,
                                        tran_saction,
                                        stkidx,
                                        cmp_name)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
        try:
            cur = conn.cursor()
            # How to insert a list of lists into a table? [Python]
            #https://stackoverflow.com/questions/51503490/how-to-insert-a-list-of-lists-into-a-table-python

            # How do I use prepared statements for inserting MULTIPLE records in SQlite using Python / Django?
            # To use parameterized queries, and to provide more than one set of parameters
            #https://stackoverflow.com/questions/5616895/how-do-i-use-prepared-statements-for-inserting-multiple-records-in-sqlite-using
            list_tuple_tseotcdailyinfo_s = [tuple(l) for l in list_tseotcdailyinfo_s]
            #print(list_tuple_tseotcdailyinfo_s)
            cur.executemany(sql, list_tuple_tseotcdailyinfo_s)

        except sqlite3.Error as err:
            print("Error occurred: %s" % err)
        else:
            print('Total {} record(s) to insert table.'.format(cur.rowcount))
        
        return cur.lastrowid
        
class Crawler:
    def __init__(self,list_stkidx_stkname, prefix="data"):
        ''' Make directory if not exist when initialize '''
        if not isdir(prefix):
            mkdir(prefix)
        self.prefix = prefix
        self.list_stkidx_stkname = list_stkidx_stkname

    def _get_tse_data(self, date_tuple):
        date_str = '{0}{1:02d}{2:02d}'.format(date_tuple[0], date_tuple[1], date_tuple[2])
        url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX'

        query_params = {
            'date': date_str,
            'response': 'json',
            'type': 'ALL',
            '_': str(round(time.time() * 1000) - 500)
        }

        # Get json data
        page = requests.get(url, params=query_params)

        if not page.ok:
            logging.error("Can not get TSE data at {}".format(date_str))
            return

        content = page.json()
        #print(content)
        # For compatible with original data
        #date_str_mingguo = '{0}/{1:02d}/{2:02d}'.format(date_tuple[0] - 1911, date_tuple[1], date_tuple[2])
        date_str_AD = '{0}/{1:02d}/{2:02d}'.format(date_tuple[0], date_tuple[1], date_tuple[2])

        #2018/10/18 apply josn and yaml
        list_json_dump = json.dumps(content)
        list_yaml_dump = yaml.safe_load(list_json_dump)
        
        #2018/10/22 JSON parser of data5
        #''' "6582",
        #    "申豐",
        #    "0",
        #    "0",
        #    "0",
        #    "--",
        #    "--",
        #    "--",
        #    "--",
        #    " ",
        #    "0.00",
        #    "48.60",
        #    "1",
        #    "48.95",
        #    "2",
        #    "14.95"'''
        #''' "6605",
        #    "帝寶",
        #    "84,221",
        #    "73",
        #    "5,731,437",
        #    "69.60",
        #    "69.60",
        #    "67.60",
        #    "68.30",
        #    "<p style= color:green>-</p>",
        #    "1.40",
        #    "68.30",
        #    "4",
        #    "68.50",
        #    "2",
        #    "10.01"'''
        
        print("Check TSE stock")
        list_tse_dailyinfo = []

        # 2018/10/22 using module json,yaml 
        for yaml_dump in list_yaml_dump['data5']:
            # Check stock idx if meets from Seymour's
            for stkidx in self.list_stkidx_stkname:
                if stkidx[0] == yaml_dump[0]:
                    sign = '-' if yaml_dump[9].find('green') > 0 else ''
                    #print(date_str_AD,# 西元日期
                    #        yaml_dump[2],# 成交股數
                    #        yaml_dump[4],# 成交金額
                    #        yaml_dump[5],# 開盤價
                    #        yaml_dump[6],# 最高價
                    #        yaml_dump[7],# 最低價
                    #        yaml_dump[8],# 收盤價
                    #        sign + yaml_dump[10],# 漲跌價差
                    #        yaml_dump[3],# 成交筆數
                    #        yaml_dump[0],#代碼
                    #        yaml_dump[1])#名稱
                    list_tse_dailyinfo.append( [date_str_AD,# 西元日期
                                                yaml_dump[2],# 成交股數
                                                yaml_dump[4],# 成交金額
                                                yaml_dump[5],# 開盤價
                                                yaml_dump[6],# 最高價
                                                yaml_dump[7],# 最低價
                                                yaml_dump[8],# 收盤價
                                                sign + yaml_dump[10],# 漲跌價差
                                                yaml_dump[3],# 成交筆數
                                                yaml_dump[0],#代碼
                                                yaml_dump[1]] )#名稱]

        #path_file = os.path.join(self.prefix,'{}{}{}.json'.format(date_tuple[0], date_tuple[1], date_tuple[2]))
        #self._dump_json2file(path_file,content)

        #print(list_tse_dailyinfo)
        
        #for data in content['data5']:
        #    sign = '-' if data[9].find('green') > 0 else ''
        #    row = self._clean_row([
                #date_str_mingguo, # 日期
        #        date_str_AD, # 西元日期
        #        data[2], # 成交股數
        #        data[4], # 成交金額
        #        data[5], # 開盤價
        #        data[6], # 最高價
        #        data[7], # 最低價
        #        data[8], # 收盤價
        #        sign + data[10], # 漲跌價差
        #        data[3], # 成交筆數
        #        data[0],#代碼
        #        data[1]#名稱
        #    ])

            #print(self.list_stkidx_stkname)
            
            # Check stock idx if meets from Seymour's 
            # 2018/10/18 remark by testing purpose
            #for stkidx in self.list_stkidx_stkname:
                #print("stkidx:",stkidx[0],"data[0]:",data[0])
            #    if stkidx[0] == data[0]:
            #        print("TSE stock idx:",data[0],"stock name:",data[1])
            #        self._record(data[0].strip(), row)

        # for web refuse connection
        time.sleep(1)

        return list_tse_dailyinfo

    def _get_otc_data(self, date_tuple):
        date_str = '{0}/{1:02d}/{2:02d}'.format(date_tuple[0] - 1911, date_tuple[1], date_tuple[2])
        ttime = str(int(time.time()*100))
        url = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d={}&_={}'.format(date_str, ttime)
        page = requests.get(url)

        if not page.ok:
            logging.error("Can not get OTC data at {}".format(date_str))
            return

        #print(page)
        result = page.json()
        #print(result)

        if result['reportDate'] != date_str:
            logging.error("Get error date OTC data at {}".format(date_str))
            return

        print("Check OTC stock")
        list_otc_dailyinfo = []

        date_str_AD = '{0}/{1:02d}/{2:02d}'.format(date_tuple[0], date_tuple[1], date_tuple[2])
        
        #2018/10/22 apply josn and yaml
        list_json_dump = json.dumps(result)
        list_yaml_dump = yaml.safe_load(list_json_dump)
        #path_file = os.path.join(self.prefix,'{}{}{}_OTC.json'.format(date_tuple[0], date_tuple[1], date_tuple[2]))
        #self._dump_json2file(path_file,result)
        #'''"mmData":[
        #    [
        #    "4415",
        #    "台原藥",
        #    "3.70",
        #    "0.00 ",
        #    "3.70",
        #    "3.70",
        #    "3.70",
        #    "3.70",
        #    "3,000",
        #    "11,100",
        #    "1",
        #    "3.50",
        #    "3.88",
        #    "36,627,168",
        #    "3.70",
        #    "4.07",
        #    "3.33"
        #    ]
        #],'''
        #'''"mmData":[
        #    [
        #    "9951",
        #    "皇田",
        #    "72.10",
        #    "+1.00",
        #    "70.40",
        #    "72.80",
        #    "70.20",
        #    "71.67",
        #    "112,200",
        #    "8,041,400",
        #    "109",
        #    "72.10",
        #    "72.20",
        #    "74,900,000",
        #    "72.10",
        #    "79.30",
        #    "64.90"
        #],'''
        
        # 2018/10/22 using module json,yaml 
        for table in [list_yaml_dump['mmData'],list_yaml_dump['aaData']]:
            for yaml_dump in table:
                # Check stock idx if meets from Seymour's 
                for stkidx in self.list_stkidx_stkname:
                    if stkidx[0] == yaml_dump[0]:
                        #print(date_str_AD,
                        #        yaml_dump[8],# 成交股數
                        #        yaml_dump[9],# 成交金額
                        #        yaml_dump[4],# 開盤價
                        #        yaml_dump[5],# 最高價
                        #        yaml_dump[6],# 最低價
                        #        yaml_dump[2],# 收盤價
                        #        yaml_dump[3],# 漲跌價差
                        #        yaml_dump[10],# 成交筆數
                        #        yaml_dump[0],#代碼
                        #        yaml_dump[1])#名稱
                        
                        list_otc_dailyinfo.append( [date_str_AD,
                                                    yaml_dump[8],# 成交股數
                                                    yaml_dump[9],# 成交金額
                                                    yaml_dump[4],# 開盤價
                                                    yaml_dump[5],# 最高價
                                                    yaml_dump[6],# 最低價
                                                    yaml_dump[2],# 收盤價
                                                    yaml_dump[3],# 漲跌價差
                                                    yaml_dump[10],# 成交筆數
                                                    yaml_dump[0],#代碼
                                                    yaml_dump[1]] )#名稱

        #for table in [result['mmData'], result['aaData']]:
        #    for tr in table:
        #        row = self._clean_row([
                    #date_str,
        #            date_str_AD,
        #            tr[8], # 成交股數
        #            tr[9], # 成交金額
        #            tr[4], # 開盤價
        #            tr[5], # 最高價
        #            tr[6], # 最低價
        #            tr[2], # 收盤價
        #            tr[3], # 漲跌價差
        #            tr[10], # 成交筆數
        #            tr[0],#代碼
        #            tr[1]#名稱
        #        ])

                # Check stock idx if meets from Seymour's 
                # 2018/10/18 remark by testing purpose
                #for stkidx in self.list_stkidx_stkname:
                #    if stkidx[0] == tr[0]:
                #        print("OTC stock idx:",tr[0],"stock name:",tr[1])
                #        self._record(tr[0], row)

        # for web refuse connection
        time.sleep(1)

        return list_otc_dailyinfo

    def get_data_tosqilte(self, date_tuple):
        print('Crawling {} '.format(date_tuple))
        list_tse_dailytradeinfo_s = self._get_tse_data(date_tuple)
        list_otc_dailytradeinfo_s = self._get_otc_data(date_tuple)

        return list_tse_dailytradeinfo_s, list_otc_dailytradeinfo_s

class CrawlTSEOTC:

    def __init__(self,list_dir_file,log_path,str_first_y_m_d,str_last_y_m_d):
        self.list_dir_file = list_dir_file
        self.log_path = log_path
        self.str_first_y_m_d = str_first_y_m_d
        self.str_last_y_m_d = str_last_y_m_d

    # crawl TSE and OTC stock price to limit from first to last day 
    def crawl_date_fromfirst_tolast_tosqlite(self,list_stockidx_stockname,pt_db_sqlite,conn):
        # Set logging
        if not os.path.isdir(self.log_path):
            os.makedirs(self.log_path)
        logging.basicConfig(filename='{}/crawl-error.log'.format(self.log_path),
            level=logging.ERROR,
            format='%(asctime)s\t[%(levelname)s]\t%(message)s',
            datefmt='%Y/%m/%d %H:%M:%S')

        # treat first date and last date
        first_date = self.str_first_y_m_d.split(',')
        last_date = self.str_last_y_m_d.split(',')
        #print(last_date)
        first_day = datetime(int(first_date[0]), int(first_date[1]), int(first_date[2]))
        last_day = datetime(int(last_date[0]), int(last_date[1]), int(last_date[2]))
        first_date_str_AD = '{0}/{1:02d}/{2:02d}'.format(first_date[0], int(first_date[1]), int(first_date[2]))
        last_date_str_AD = '{0}/{1:02d}/{2:02d}'.format(last_date[0], int(last_date[1]), int(last_date[2]))

        print("From First Date:", first_date_str_AD, "To Last Date:", last_date_str_AD, "Store to TWTSEOTCDaily.db")

        crawler = Crawler(list_stockidx_stockname)    
        
        max_error = 5
        error_times = 0
        list_tse_dailytradeinfo_s = []
        list_otc_dailytradeinfo_s = []

        while error_times < max_error and first_day >= last_day:
            try:
                # Get daily TSE OTC tradeinfo 
                list_tse_dailytradeinfo_s, list_otc_dailytradeinfo_s = \
                    crawler.get_data_tosqilte((first_day.year, first_day.month, first_day.day))

                # Insert total lists to sqlite directly
                pt_db_sqlite.create_tseotcdaily_many(conn, list_tse_dailytradeinfo_s)
                pt_db_sqlite.create_tseotcdaily_many(conn, list_otc_dailytradeinfo_s)    
                
                # Save (commit) the changes daily
                conn.commit()

                error_times = 0
            except:
                date_str = first_day.strftime('%Y/%m/%d')
                logging.error('Crawl raise error {}'.format(date_str))
                error_times += 1
                continue
            finally:
                first_day -= timedelta(1)                    