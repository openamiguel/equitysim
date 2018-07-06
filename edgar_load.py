## This code gets company data from the SEC's Financial Statement Datasets.
## Link: https://www.sec.gov/dera/data/financial-statement-data-sets.html
## Author: Miguel Opeña
## Version: 1.3.0

import logging
import os
import pandas as pd
from psutil import virtual_memory
import urllib.request
import urllib.error
import zipfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

lambda_reg_case = lambda x: " ".join([w.lower().capitalize() for w in x.split(" ")])

def memory_check(filepath, threshold_ratio=10):
    """ Checks if file occupies too much RAM on the computer. 
        Inputs: file path to check, threshold ratio
        Outputs: none as variables
    """
    ram = virtual_memory()
    filesize = os.path.getsize(filepath)
    if filesize > threshold_ratio * ram / 100.0:
        logger.warn("File occupies {}%% of RAM.".format(threshold_ratio))
    return

def download_unzip(folderpath, startyear=2009, endyear=2018):
    """ Downloads and unzips all the data from SEC EDGAR on financial statements.
        Inputs: folder path to write files to, start year of downloaded data, 
            end year of downloaded data
        Outputs: none as variables
    """
    # Gets the base URL for all the downloads
    base_url = "https://www.sec.gov/files/dera/data/financial-statement-data-sets/"
    # Gets data from each year...
    for year in range(startyear, endyear + 1):
        # ...and from each quarter
        for quarter in range(1, 5):
            # Handles proper file format from SEC
            file_name = "{0}q{1}.zip".format(year, quarter)
            logger.debug("Downloading {} from SEC website...".format(file_name))
            # Tries to download data
            try:
                urllib.request.urlretrieve(base_url + file_name, folderpath + file_name)
            # Gracefully handles errors
            except urllib.error.URLError as e:
                logger.error("URLError encountered with {}. Continuing to next file...".format(file_name))
                continue
            # Extracts file as ZIP
            zip_ref = zipfile.ZipFile(folderpath + file_name, 'r')
            zip_ref.extractall(folderpath + file_name.split('.')[0])
            zip_ref.close()
            # Deletes the ZIP
            os.remove(folderpath + file_name)
    return

def get_sic_names(target_url='https://www.sec.gov/info/edgar/siccodes.htm'):
    # Processes the raw data into dataframe
    webpage = pd.read_html(target_url)
    table = webpage[2]
    # Column 0 has codes, Column 3 has industry titles
    sic_names = pd.concat([table[0], table[3]], axis=1)
    sic_names.dropna(how='any', axis=0, inplace=True)
    sic_names.drop(2, inplace=True)
    sic_names.columns = ['sic', 'industry_name']
    # Cleans up the numeric column into integers
    sic_names['sic'] = sic_names['sic'].apply(lambda x: int(x))
    # Cleans up the format of dashes in entries
    sic_names['industry_name'] = sic_names['industry_name'].apply(lambda x: x.replace('-', ' - ') if ' - ' not in x else x)
    # Applies regular case conventions
    sic_names['industry_name'] = sic_names['industry_name'].apply(lambda_reg_case)
    return sic_names

def submission_parse(filepath, outpath):
    """ Parses the data on submission files ONLY.
        Inputs: path of submission file, output path of processed file
        Outputs: True if everything works
    """
    sub_df = pd.read_csv(filepath, sep='\t')
    # Does the easy processing: columns to keep as-is or simply rename
    proc_cols = ['adsh', 'cik', 'name', 'sic', 'former', 'changed', 'wksi', 
                 'form', 'detail', 'instance', 'nciks', 'aciks']
    sub_proc_df = pd.concat([sub_df[col] for col in proc_cols], axis=1)
    col_dict = {'adsh': 'accession_num', 'cik': 'central_index_key', 
                'name': 'company_name', 'former': 'former_name', 
                'changed': 'date_namechange', 
                'wksi': 'well_known_seasoned_issuer'}
    sub_proc_df = sub_proc_df.rename(columns=col_dict)
    # Cleans up the numeric columns into integers
    sub_proc_df['central_index_key'] = sub_proc_df['central_index_key'].apply(lambda x: int(x))
    sub_proc_df['sic'].fillna(-999, inplace=True)
    sub_proc_df['sic'] = sub_proc_df['sic'].apply(lambda x: int(x))
    # "Processes" data source into the dataframe
    sub_proc_df['data_source'] = 'SEC_EDGAR'
    # Transforms company_name and former_name column using regular case
    sub_proc_df['company_name'] = sub_proc_df['company_name'].apply(lambda_reg_case)
    sub_proc_df['former_name'].fillna("", inplace=True)
    sub_proc_df['former_name'] = sub_proc_df['former_name'].apply(lambda_reg_case)
    # Deletes any instance of suffix
    lambda_remove_suffix = lambda x: x.split('/')[0].strip() if '/' in x else x
    sub_proc_df['company_name'] = sub_proc_df['company_name'].apply(lambda_remove_suffix)
    sub_proc_df['former_name'] = sub_proc_df['former_name'].apply(lambda_remove_suffix)
    # Makes date_namechange a nice date-related format
    sub_proc_df['date_namechange'].fillna("", inplace=True)
    sub_proc_df['date_namechange'] = sub_proc_df['date_namechange'].apply(lambda x: str(int(x))[:4] + "-" + str(int(x))[4:6] + "-" + str(int(x))[-2:] if x != '' else x)
    # Changes sic into industry_title using SEC SIC codes
    sic_names = get_sic_names()
    sub_proc_df = sub_proc_df.merge(sic_names, how='left')
    sub_proc_df.drop(labels='sic', axis=1, inplace=True)
    # Builds source column (link to actual XML file)
    # print(sub_proc_df.date_namechange)
    base_link = 'http://www.sec.gov/Archives/edgar/data/'
    sub_proc_df['source'] = base_link + sub_proc_df['central_index_key'].astype(str) + '/' + sub_proc_df['accession_num'].apply(lambda x: x.replace('-','')) + '/' + sub_proc_df['instance']
    # Transforms instance into ticker symbol, renamed to symbol
    lambda_to_symbol = lambda x: x.split('-')[0].upper() if '-' in x else x
    sub_proc_df['instance'] = sub_proc_df['instance'].apply(lambda_to_symbol)
    sub_proc_df = sub_proc_df.rename(columns={'instance':'symbol'})
    # Deletes rows where symbol is not given (useless for my purposes)
    sub_proc_df = sub_proc_df[pd.notnull(sub_proc_df['symbol'])]
    # Writes to file
    sub_proc_df.to_csv(outpath, sep='\t', index=False)
    return True

def number_parse(filepath, outpath):
    return

def presentation_parse(filepath, outpath):
    return

def tag_parse(filepath, outpath):
    return

def parse_in_directory(folderpath):
    for cur_path, directories, files in os.walk(folderpath, topdown=True):
        for file in files:
            path = os.path.join(cur_path,file)
            if "sub" in file:
                submission_parse(path, folderpath + "SUB_FINAL.txt")
            elif "num" in file:
                number_parse(path, folderpath + "NUM_FINAL.txt")
            elif "pre" in file:
                presentation_parse(path, folderpath + "PRE_FINAL.txt")
            elif "tag" in file:
                tag_parse(path, folderpath + "TAG_FINAL.txt")
    return

folder_path = "C:/Users/Miguel/Desktop/EDGAR/"
# download_unzip(folder_path, startyear=2018)
parse_in_directory(folder_path)