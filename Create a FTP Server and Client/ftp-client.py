
from ftplib import FTP
#import ftplib
import os #adicionado

ftp = FTP('')
ftp.connect('localhost',1026)
ftp.login()
ftp.cwd('') #replace with your directory
ftp.retrlines('LIST')

def uploadFile():
 filename = 'upload.txt' #replace with your file in your home folder
 #filename = os.path.splitext("upload.txt") 
 ftp.storbinary('STOR '+filename, open(filename, 'rb'))
 #ftp.storlines('STOR '+"upload.txt", open("upload.txt", 'rb'))
 ftp.quit()

def downloadFile():
 filename = 'download.txt' #replace with your file in the directory ('directory_name') 
 localfile = open(filename, 'wb')
 ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
 ftp.quit()
 localfile.close()

uploadFile()
#downloadFile()
