import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC
import time,re
from lib.dataAnalysis import *

class GoogleSS:
    def __init__(self,str_delay_sec,dirnamelog,path_db,str_first_year_month_day):
        self.str_delay_sec = str_delay_sec
        self.dirnamelog = dirnamelog
        self.path_db = path_db
        self.str_first_year_month_day = str_first_year_month_day

    def auth_gss_client(self,path,scopes):
        key = SAC.from_json_keyfile_name(path, scopes)
        self.gc = gspread.authorize(key)        

    def open_GSworksheet(self, gspreadsheet,worksheet_spread):
        gss_client_worksheet = self.gc.open(gspreadsheet).worksheet(worksheet_spread)
        self.gss_client_worksheet=gss_client_worksheet

    def update_sheet_celllist(self,str_cellrange,list_cellvalue):
        # print("Cell Range string:", str_cellrange)
        cell_list = self.gss_client_worksheet.range(str_cellrange)

        # 2018/8/12 Solve by issue:483; https://github.com/burnash/gspread/issues/483
        # cell_list[0].value = stock_price_final
        # cell_list[1].value = stock_price_open
        # cell_list[2].value = stock_price_high
        # cell_list[3].value = stock_price_low

        cell_list[0].value = list_cellvalue[0]
        cell_list[1].value = list_cellvalue[1]
        cell_list[2].value = list_cellvalue[2]
        cell_list[3].value = list_cellvalue[3]
        # print("cell_list:", cell_list)
        self.gss_client_worksheet.update_cells(cell_list)
        
    def update_GSpreadworksheet_datafolderCSV(self,row_count):
        list_Gworksheet_rowvalue = self.gss_client_worksheet.row_values(row_count)

        while len(list_Gworksheet_rowvalue) > 0:
            stkidx = str(list_Gworksheet_rowvalue[1])
            str_todaydate = re.sub(r",", "-", self.str_first_year_month_day)#2018-10-16

            #localdata_analysis = data_analysis.PandasSqliteAnalysis(stkidx,self.dirnamelog,
            localdata_analysis = PandasSqliteAnalysis(stkidx,self.dirnamelog,
                                                        self.path_db,
                                                        self.str_first_year_month_day)

            # 2018/11/05 5209 daily info as below:
            # 2018/11/05	0	0	---	---	---	---	---	0	5209	新鼎
            # to slove this issu to update get_tradedaysANDnonetradeday_dfinfo()
            #df_delduplicates_sortasc_tradeday = localdata_analysis.get_tradedays_dfinfo()
            df_delduplicates_sortasc_tradeday = localdata_analysis.get_tradedaysANDnonetradeday_dfinfo()

            #           date  open  high   low  close  Stkidx CmpName
            #329 2018-10-16  44.1  44.9  43.7  43.95    6024     群益期
            df_today_tradeinof = df_delduplicates_sortasc_tradeday[df_delduplicates_sortasc_tradeday['date'] == str_todaydate]                                                        
                                                                    
            ## Check 4 stock prices: 1.final, 2.open, 3.high, 4.low
            stock_price_final = df_today_tradeinof['close'].values.astype(str)[0]
            stock_price_open = df_today_tradeinof['open'].values.astype(str)[0]
            stock_price_high = df_today_tradeinof['high'].values.astype(str)[0]
            stock_price_low = df_today_tradeinof['low'].values.astype(str)[0]
            print(list_Gworksheet_rowvalue[0], list_Gworksheet_rowvalue[1],
                  stock_price_final, stock_price_open, stock_price_high,stock_price_low)

            # update by Cell Range
            str_range = 'D' + str(row_count) + ":" + 'G' + str(row_count)

            ## update cell content
            #2018/08/22 if final price doesn't exist    
            if bool(re.match(r'^-+-$',stock_price_final)) == False:
                list_cellvalue = [float(stock_price_final), float(stock_price_open),
                                  float(stock_price_high), float(stock_price_low)]
                self.update_sheet_celllist(str_range, list_cellvalue)

            # delay delay_sec secs
            # 2018/8/13 prevent ErrorCode:429, Exhaust Resoure
            #print ("Delay ", str_delay_sec, "secs to prevent Google Error Code:429, Exhaust Resoure")
            time.sleep(int(self.str_delay_sec))

            row_count += 1
            list_Gworksheet_rowvalue = self.gss_client_worksheet.row_values(row_count)    