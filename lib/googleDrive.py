import glob, os, re
import sys, time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

#2018/11/16 https://github.com/ITCoders/SyncIt/blob/master/src/drive_sync.py
######################################################################
class GoogleCloudDrive:
    def __init__(self,str_localdir):
        self.str_localdir = str_localdir
        #done_paths = []
        self.done_paths = []
        #browsed = []
        self.browsed = []

    def querylocalfiles(self,re_pattern):
        #os.chdir(self.str_localdir)
        #for file in glob.glob("*.{}".format(str_filetype)):
        list_filename = []
        for f in os.listdir(self.str_localdir):
            try:
                if re.search(re_pattern, f):
                    print("Search file: {} in {}".format(f,self.str_localdir))
                    list_filename.append(f)
            except FileNotFoundError as e:
                print(e)

        if len(list_filename) > 0:
            print('Total {} file(s) under {}.'.format(len(list_filename),self.str_localdir))
        elif len(list_filename) == 0:
            print('No {} like file(s) under {}.'.format(re_pattern,self.str_localdir))
        
        return list_filename  

#rajarsheem/GDrive.py(by FileID)
#https://gist.github.com/rajarsheem/1d9790f0e9846fb429d7
###################################
import io,os
from mimetypes import MimeTypes
from urllib.parse import urlparse
import httplib2
from apiclient import discovery

try:
	from googleapiclient.errors import HttpError
	
	import oauth2client
	from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
	from oauth2client import client
	from oauth2client import tools
except ImportError:
    print('goole-api-python-client is not installed. Try:')
    print('sudo pip install --upgrade google-api-python-client')
    sys.exit(1)
import sys

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secrets.json'
APPLICATION_NAME = 'GDrive'

class GoogleDrivebyFileID:
    def __init__(self, str_downloadpath,flags):
        self.str_downloadpath = str_downloadpath
        self.flags = flags
        
    def get_credentials(self,credential_dir):
        #home_dir = os.path.expanduser('~')
        #credential_dir = os.path.join(home_dir, '.credentials')
        #credential_dir = os.getcwd()
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,CLIENT_SECRET_FILE)
                                       #'drive-python-quickstart.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            # if flags:
            credentials = tools.run_flow(flow, store, self.flags)
            # else:  # Needed only for compatibility with Python 2.6
            #     credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        
        self.credentials = credentials
        return credentials
    
    def getfilename_byfileid(self,service,file_id):
        name = service.files().get(fileId=file_id).execute()['name']
        print('Check file:{} by file_id:{} on Google Drive.'.format(name,file_id))
        return name

    #Get filename by fileid from google drive
    #Chk current xls files under log folder.
    #########################################
    def check_xlsfile_logfolder(self,fileid_file):
        #get filename by fileid from google drive
        #########################################
        '''localgoogle_drive = google_drive.GoogleDrivebyFileID(dirnamelog,flags)
        credentials = self.get_credentials(credential_dir)
        '''
        http = self.credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)

        filename_fileid_file = self.getfilename_byfileid(service,fileid_file)

        #Chk current xls files under log folder.
        ######################################
        localgoogle_drive = GoogleCloudDrive(self.str_downloadpath)
        #re_exp = r'\.xls$'
        re_exp = r'{}'.format(filename_fileid_file)
        list_xls_filename = localgoogle_drive.querylocalfiles(re_exp)

        return list_xls_filename,filename_fileid_file

    #Download filename by fileid from google drive
    #########################################
    def download_xlsfile_fromblog(self,list_filename,fileid_file):
        # if files not exist
        if len(list_filename) == 0:
            
            '''localgoogle_drive = google_drive.GoogleDrivebyFileID(dirnamelog,flags)
            credentials = self.get_credentials(credential_dir)
            '''
            http = self.credentials.authorize(httplib2.Http())
            service = discovery.build('drive', 'v3', http=http)
            self.download(service,fileid_file)
        else:# if files exist
            for filename in list_filename:
                print('{} are already on {}.'.format(filename,self.str_downloadpath))

    #Get filename by fileid from google drive
    #Chk current xls files under log folder.
    #########################################
    def check_xlsfile_MHunterblog_logfolder(self,service,fileid,dirnamelog):
        #get filename by fileid from google drive
        #########################################
        filename_fileid_file = self.getfilename_byfileid(service,fileid)

        #Chk current xls files under log folder.
        ######################################
        localgoogle_drive = GoogleCloudDrive(dirnamelog)
        #re_exp = r'\.xls$'
        re_exp = r'{}'.format(filename_fileid_file)
        list_xls_filename = localgoogle_drive.querylocalfiles(re_exp)

        return list_xls_filename,filename_fileid_file

    def ggdrive_fileid(self,html_doc,xpath_url_file):
        parsed = urlparse(html_doc.xpath(xpath_url_file)[0])# 1st item fo list
    
        #ParseResult(scheme='https', netloc='drive.google.com', path='/file/d/1YaK7owM9M37fnEeXTxoSW_N3JZU5K4Ba/view', params='', query='usp=sharing', fragment='')
        #/file/d/1YaK7owM9M37fnEeXTxoSW_N3JZU5K4Ba/view
        # get fileid by path parm
        fileid = parsed.path.split('/')[-2]
        return fileid

    def download(self,service,file_id):#, path=os.getcwd()
        request = service.files().get_media(fileId=file_id)
        name = service.files().get(fileId=file_id).execute()['name']
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            #print(int(status.progress() * 100))
            print('Download progess: {}%'.format(int(status.progress() * 100)))
        
        #f = open(path + '/' + name, 'wb')
        f = open(self.str_downloadpath + '/' + name, 'wb')
        f.write(fh.getvalue())
        #print('File downloaded at', path)
        print('{} downloaded at {}'.format(name,self.str_downloadpath))
        f.close()    