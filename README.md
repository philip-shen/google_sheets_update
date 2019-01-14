# google_sheets_update_and_google_drive_download
1. Crawl OpenHighLowClose daily trade data of specific companys based on files that download form Google drive
2. And update daily trade data of holding companys on Google sheets

                            ＄＄＄＄＄＄投資從理財開始，理財作記帳著手 ＄＄＄＄＄＄
                                                                    此程式獻給在股海浮沈的你，從記帳開始著手

## Apply Google API service first
Apply Google Sheets API CA refers Reference 01 first.
And then apply Google Drive API CA naming 'client_secrets.json' refers Reference 02 for more detail.

## Usage
Step 1. Locate Google Sheets API CA and Google Drive API CA under folder 'google_sheets_update'

Step 2. Upload account01.xlsx to your Google drive and save as google sheets format.

Step 3. Open share privilege of account01 with your Google Sheets API CA that can edit it.

![alt tag](https://i.imgur.com/iMavF6u.png)

Step 4. pip
```  
pip install -r requirements.txt
``` 

Step 5. Crawl daily trade data first.
![alt tag](https://i.imgur.com/M8KydHY.png)

Step 6. Update account01 content
![alt tag](https://i.imgur.com/FUxmRJO.png)

sheet:mouse02

Before:
![alt tag](https://i.imgur.com/kFNwy3r.png)
After:
![alt tag](https://i.imgur.com/M7Q80LC.png)

sheet:mouse03

Before:
![alt tag](https://i.imgur.com/4b46WsE.png)
After:
![alt tag](https://i.imgur.com/pDi0NWM.png)

## Environment Configuration
* Windows 10
* Python 3.6
* Refer requirements.txt to pip necessary modules.

## Reference 
* [01 How to get Google Drive CA/Python & Google Drive 專案](https://medium.com/@yysu/%E7%B2%BE%E9%80%9Apython-30-days-day-3-54a0347a574b)
* [02 Google Developers Console Setting/使用Python上傳資料到Google試算表](https://sites.google.com/site/zsgititit/home/python-cheng-shi-she-ji/shi-yongpython-shang-chuan-zi-liao-daogoogle-shi-suan-biao)
* [Taiwan Stock Exchange Crawler](https://github.com/Asoul/tsec)
* [Google Spreadsheets Python API](https://github.com/burnash/gspread/blob/master/README.md)
* [Accessing folders, subfolders and subfiles using PyDrive (Python)](https://stackoverflow.com/questions/34101427/accessing-folders-subfolders-and-subfiles-using-pydrive-python?lq=1)
* [GDrive.py(by FileID)](https://gist.github.com/rajarsheem/1d9790f0e9846fb429d7)
* []()