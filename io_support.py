## Contains support functions for file I/O. 
## Author: Miguel Opeña
## Version: 1.1.0

import logging
import os
import pandas as pd
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

def merge_chunked(filepath, leftframe, sep='\t', csize=500000, encoding='iso8859-1'):
    """ Reads dataframe in chunks and inner-joins with dataframe on left
        Inputs: file path to read dataframe, column to merge on, reference list, 
            file delimiter (default: tab), chunk size (default: 100000)
        Outputs: True if everything works
    """
    chunks = pd.read_csv(filepath, sep=sep, chunksize=csize, encoding=encoding)
    out_df = pd.DataFrame()
    for chunk in chunks:
        logger.debug("Currently reading row %8d...", chunk.index[0])
        chunk_filter = leftframe.merge(chunk, how='inner')
        out_df = pd.concat([out_df, chunk_filter], axis=0)
    return out_df

def write_as_append(dataframe, filepath, index=False, header=False, sep='\t'):
    """ Writes dataframe to file in append mode. 
        Inputs: dataframe, file path to append to
        Outputs: True if everything works
    """
    with open(filepath, 'a') as outfile:
        dataframe.to_csv(outfile, sep=sep, header=header)
    outfile.close()
    return True