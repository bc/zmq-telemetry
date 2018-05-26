import os
import ftplib
import ntpath
from tqdm import tqdm
from glob import glob

def ftp_transfer(ftp,input_filepath, filename, chunk_size = 2048):
        filesize = os.path.getsize(input_filepath)
        TheFile = open(input_filepath, 'wb').write
        with tqdm(unit='blocks', unit_scale=True, leave=False, miniters=1, desc='Uploading...', total=filesize) as tqdm_instance:
            ftp.storbinary('STOR ' + filename, TheFile, chunk_size,
                           callback=lambda sent: tqdm_instance.update(len(sent)))
        TheFile.close()

