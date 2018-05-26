from ftplib import FTP_TLS
user = 'brian'
password = open(
    "/Users/briancohn/Documents/GitHub/bc/zmq-telemetry/upload/password.txt").read()

# Connect, but only using SSL version 2 aor 3
from ftplib import FTP_TLS
import ssl
import os
import ftplib


def upload(ftp, file):
    ext = os.path.splitext(file)[1]
    if ext in (".txt", ".htm", ".html"):
        ftp.storlines("STOR " + file, open(file))
    else:
        ftp.storbinary("STOR " + file, open(file, "rb"), 1024)


def connect():
    global user, password
    ftp = FTP_TLS()
    ftp.ssl_version = ssl.PROTOCOL_SSLv23
    ftp.debugging = 2
    ftp.connect('pensieve.usc.edu', 41590)
    ftp.login(user, password)
    ftp.prot_p()
    print(ftp.nlst('home'))
    return(ftp)


ftp = connect()
ftp.prot_p()
ftp.retrlines('LIST')

# download sample file
filepath_pensieve = "home/brian_scratch/hi.md"
filepath_local = "/Users/briancohn/Downloads/hi.md"
ftp.retrbinary('RETR %s' % filepath_pensieve, open(filepath_local, 'wb').write)


# upload big file
a = open("/Applications/0ad.zip", "rb")
ftp.storbinary('STOR home/brian_scratch/x1.zip',
               open("/Applications/0ad.zip", "rb"), 1024)
ftp.storbinary('STOR hi2.md', open("hi2.md", 'rb'))


upload(ftp, "/Applications/0ad.zip")
upload(ftp, "/Applications/Unity/PlaybackEngines/WebGLSupport/BuildTools/uglify-js/node_modules/yargs/node_modules/cliui/LICENSE.txt")
upload(ftp, "hi2.md")
upload(ftp, "sightings.jpg")
