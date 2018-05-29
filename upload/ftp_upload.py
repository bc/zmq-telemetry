from ftplib import FTP_TLS
user = 'brian'
password = open(
    "/Users/briancohn/Documents/GitHub/bc/zmq-telemetry/upload/password.txt").read()

# Connect, but only using SSL version 2 aor 3
from ftplib import FTP_TLS
import ssl
import os
import ftplib
from tqdm import tqdm


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
    ftp.retrlines('LIST home')
    return(ftp)


def tx_with_progress(ftp, input_filepath, destination_filepath, block_size_bytes):
    filesize = os.path.getsize(input_filepath)
    with tqdm(unit='blocks', unit_scale=True, leave=False, miniters=1, desc='Uploading...', total=filesize) as tqdm_instance:
        ftp.storbinary('STOR %s' % destination_filepath, open(input_filepath, "rb"),
                       block_size_bytes, callback=lambda sent: tqdm_instance.update(len(sent)))


def receive_with_progress(ftp, input_filepath, destination_filepath, block_size_bytes):
    filesize = os.path.getsize(input_filepath)
    with tqdm(unit='blocks', unit_scale=True, leave=False, miniters=1, desc='Uploading...', total=filesize) as tqdm_instance:
        ftp.retrbinary('RETR %s' % input_filepath, open(destination_filepath, "wb"),
                       block_size_bytes, callback=lambda sent: tqdm_instance.update(len(sent)))


ftp = connect()

# download a big file
filepath_pensieve = "home/brian_scratch/x1ad.zip"
filepath_local = "/Users/briancohn/Downloads/x1ad.zip"
ftp.retrbinary('RETR %s' % filepath_pensieve, open(filepath_local, 'wb').write)
receive_with_progress(ftp, filepath_pensieve, filepath_local, 12500000)


# upload big file
input_filepath = "/Applications/0ad.zip"
destination_filepath = "home/brian_scratch/x1ad.zip"
tx_with_progress(ftp, input_filepath, destination_filepath,
                 block_size_bytes=12500000)

ftp.quit()
ftp = None
