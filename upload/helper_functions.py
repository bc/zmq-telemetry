from ftplib import FTP_TLS
import ssl
import os
from tqdm import tqdm


"""Connect to FTP Server for Pensieve
Prints all files in the home directory
@return FTP object set in protected mode. defaults to penseive server
"""


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


"""Transfer a file to a specified filepath on Pensieve, with Progress Bar
Implementation of progress bar via tqdm
@param ftp ftplib object preconnected via connect() call
@param input_filepath str filepath on local computer
@param dest_filepath str filepath on pensieve
@param block_size_bytes int size of each chunk to transfer, in bytes. i.e. 1e5
"""


def tx_with_progress(ftp, input_filepath, dest_filepath, block_size_bytes):

    filesize = os.path.getsize(input_filepath)
    with tqdm(unit='blocks', unit_scale=True, leave=False,
              miniters=1, desc='Sending', total=filesize) as tqdm_instance:
        ftp.storbinary('STOR %s' % dest_filepath, open(input_filepath, "rb"),
                       block_size_bytes,
                       callback=lambda sent: tqdm_instance.update(len(sent)))


"""Receive a file to specified filepath from Pensieve to a local computer
Progress bar has not been implemented thus far, though the filesize has been
ascertained as filesize and is printed to console to indicate the MB of the
impending file.
@param ftp ftplib object preconnected via connect() call
@param input_filepath str filepath on the pensieve server,
    e.g. home/brian/brian_scratch/my_file.csv
@param dest_filepath str local filepath,
    e.g. ~/Downloads/my_file.csv. Destination filename can diverge from
    input filename
@param block_size_bytes int size of each chunk to transfer, in bytes. i.e. 1e5
"""


def receive(ftp, input_filepath, dest_filepath, block_size_bytes):
    ftp.sendcmd("TYPE I")
    size_set_str = "SIZE %s" % input_filepath
    filesize = int(ftp.sendcmd(size_set_str).split(" ")[1])
    print("Downloading %s MB" % str(filesize / 1e6))
    lf = open(dest_filepath, "wb")
    ftp.retrbinary('RETR ' + input_filepath, callback=lf.write)
    lf.close()
