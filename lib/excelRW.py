import xlrd
import xlwt
import xlutils.copy
import csv,os

class ExcelRW:
    def readExcel(self,dir_execlfile):
        try:
            data = xlrd.open_workbook(dir_execlfile)    # 打開一個Excel表格
            table = data.sheets()[0]               # 打開Excel表格的第一張表
            nrows = table.nrows                    # 獲取每張表的行數
        except FileNotFoundError as fnf_error:
            print(fnf_error)

        list_rtu_row_values=[]
        for row in range(nrows):              # 遍歷每一行
            #print(table.row_values(row))          # 獲取每行的值
            #if table.row_values(row)[11] != "合理價格": # 排除第一行後，獲取每行合理價格的值
            if table.row_values(row)[10] != "價值比": # 排除第一行後，獲取每行價格比的值
                #print(str(table.row_values(row)[1]).strip('.0'), table.row_values(row)[2], table.row_values(row)[11])
                list_row_values=[str(table.row_values(row)[1])[0:4], table.row_values(row)[2], 
                                    table.row_values(row)[10],#column "價值比"
                                    table.row_values(row)[4]]#column 'PBR'
                list_rtu_row_values.append(list_row_values)
                #print(list_rtu_row_values,list_row_values)

        return list_rtu_row_values
        
    def get_stockidx_SeymourExcel(self,dirnamelog,excelfname):

        print('將讀取Excel file:', excelfname, '的資料')
        #logging.error('將讀取Excel file: {}'.format(excelfname))

        # Excel file including path
        dirlog_ExcelFile=os.path.join(dirnamelog,excelfname)
        list_row_value_price=self.readExcel(dirlog_ExcelFile)
        
        list_rtu_stockidx=[]

        # Get  stock idx and company name from Excel files
        for list_row_value in list_row_value_price:
            list_stockidx=[list_row_value[0]]
            list_rtu_stockidx.append(list_stockidx)

        return list_rtu_stockidx

    def get_all_stockidx_SeymourExcel(self,dir_log,list_excel_files):

        list_rtu_all_stockidx=[]

        for excel_file in list_excel_files:
            list_stockidx=self.get_stockidx_SeymourExcel(dir_log,excel_file)
            list_rtu_all_stockidx.extend(list_stockidx)

        return list_rtu_all_stockidx