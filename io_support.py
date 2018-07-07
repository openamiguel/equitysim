## Contains support functions for file I/O. 
## Author: Miguel Opeña
## Version: 1.0.0

import logging
import os
from psutil import virtual_memory

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_current_symbols(folderpath, function="DAILY", datatype="csv"):
    """ Returns list of all symbols downloaded to given folder. 
        Inputs: path of folder directory, time series function, data type
        Outputs: list of aforementioned
    """
    symbols = []
    # Walks through the given folderpath
    for cur_path, directories, files in os.walk(folderpath):
        for file in files:
            # Skips all irrelevant files
            if datatype not in file or function not in file:
                continue
            # Process the file name for symbol
            symbols.append(file.split('_')[0])
    return symbols

def memory_check(filepath, threshold_ratio=10):
    """ Checks if file occupies too much RAM on the computer. 
        Inputs: file path to check, threshold ratio
        Outputs: none as variables
    """
    ram = virtual_memory()
    filesize = os.path.getsize(filepath)
    # ram[1] gets the available RAM
    if filesize > threshold_ratio * ram[1] / 100.0:
        pct = filesize * 100 / ram[1]
        logger.warning("File occupies %.2f percent of RAM.", pct)
    return

def write_as_append(dataframe, filepath, index=False, header=False, sep='\t'):
    """ Writes dataframe to file in append mode. 
        Inputs: dataframe, file path to append to
        Outputs: True if everything works
    """
    with open(filepath, 'a') as outfile:
        dataframe.to_csv(outfile, sep=sep, header=header)
    outfile.close()
    return True