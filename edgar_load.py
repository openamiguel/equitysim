## This code gets company data from the SEC's Financial Statement Datasets.
## Link: https://www.sec.gov/dera/data/financial-statement-data-sets.html
## Author: Miguel Opeña
## Version: 1.7.6

import csv
import logging
import os
import pandas as pd
from psutil import virtual_memory
import urllib.request
import urllib.error
import zipfile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

lambda_reg_case = lambda x: " ".join([w.lower().capitalize() for w in x.split(" ")])

writeheader = [True, True, True, True]
csize = 1000000

# Move to separate file?
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

# Move to separate file?
def write_as_append(dataframe, filepath, index=False, header=False, sep='\t'):
    """ Writes dataframe to file in append mode. 
        Inputs: dataframe, file path to append to
        Outputs: True if everything works
    """
    with open(filepath, 'a') as outfile:
        dataframe.to_csv(outfile, sep=sep, header=header)
    outfile.close()
    return True

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
            logger.debug("Extracting {} from ZIP file...".format(file_name.split('.')[0]))
            zip_ref = zipfile.ZipFile(folderpath + file_name, 'r')
            zip_ref.extractall(folderpath + file_name.split('.')[0])
            zip_ref.close()
            # Deletes the ZIP
            logger.debug("Deleting {} ZIP file...".format(file_name.split('.')[0]))
            os.remove(folderpath + file_name)
    return

def get_sic_names(target_url='https://www.sec.gov/info/edgar/siccodes.htm'):
    """ Scrapes the SEC website for data on SIC codes.
        Inputs: URL of aforementioned website
        Outputs: dataframe of SIC codes and names
    """
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
    sub_df = pd.read_csv(filepath, sep='\t', encoding='iso8859-1', quoting=csv.QUOTE_NONE)
    # Does the easy processing: columns to keep as-is or simply rename
    proc_cols = ['adsh', 'cik', 'name', 'sic', 'former', 'changed', 'wksi', 
                 'form', 'detail', 'instance', 'nciks', 'aciks']
    sub_proc_df = pd.concat([sub_df[col] for col in proc_cols], axis=1)
    col_dict = {'adsh': 'accession_num', 'cik': 'central_index_key', 
                'name': 'company_name', 'former': 'former_name', 
                'changed': 'date_of_name_change', 
                'wksi': 'is_well_known_seasoned_issuer'}
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
    # Makes date_of_name_change a nice date-related format
    sub_proc_df['date_of_name_change'].fillna("", inplace=True)
    sub_proc_df['date_of_name_change'] = sub_proc_df['date_of_name_change'].apply(lambda x: str(int(x))[:4] + "-" + str(int(x))[4:6] + "-" + str(int(x))[-2:] if x != '' else x)
    # Changes sic into industry_name using SEC SIC codes
    sic_names = get_sic_names()
    sub_proc_df = sub_proc_df.merge(sic_names, how='left')
    sub_proc_df.drop(labels='sic', axis=1, inplace=True)
    # Builds source column (link to actual XML file)
    # print(sub_proc_df.date_of_name_change)
    base_link = 'http://www.sec.gov/Archives/edgar/data/'
    sub_proc_df['source'] = base_link + sub_proc_df['central_index_key'].astype(str) + '/' + sub_proc_df['accession_num'].apply(lambda x: x.replace('-','')) + '/' + sub_proc_df['instance']
    # Transforms instance into ticker symbol, renamed to symbol
    lambda_to_symbol = lambda x: x.split('-')[0].upper() if '-' in x else x
    sub_proc_df['instance'] = sub_proc_df['instance'].apply(lambda_to_symbol)
    sub_proc_df = sub_proc_df.rename(columns={'instance':'symbol'})
    # Deletes rows where symbol is not given (useless for my purposes)
    sub_proc_df = sub_proc_df[pd.notnull(sub_proc_df['symbol'])]
    # Writes to file
    write_as_append(sub_proc_df, outpath, header=writeheader[0])
    writeheader[0] = False
    return True

def number_parse(filepath, outpath):
    """ Parses the data on number files ONLY.
        Inputs: path of number file, output path of processed file
        Outputs: True if everything works
    """
    num_df = pd.read_csv(filepath, sep='\t', encoding='iso8859-1', quoting=csv.QUOTE_NONE)
    # Does the easy processing: columns to keep as-is or simply rename
    proc_cols = ['adsh', 'tag', 'version', 'ddate', 'qtrs', 'uom', 'value']
    num_proc_df = pd.concat([num_df[col] for col in proc_cols], axis=1)
    col_dict = {'adsh': 'accession_num', 'tag': 'tag_name', 
                'version': 'tag_version', 'ddate': 'end_date_rounded', 
                'qtrs': 'num_quarters'}
    num_proc_df = num_proc_df.rename(columns=col_dict)
    # Writes to file
    write_as_append(num_proc_df, outpath, header=writeheader[1])
    writeheader[1] = False
    return True

def presentation_parse(filepath, outpath):
    """ Parses the data on presentation files ONLY.
        Inputs: path of presentation file, output path of processed file
        Outputs: True if everything works
    """
    pre_df = pd.read_csv(filepath, sep='\t', encoding='iso8859-1', quoting=csv.QUOTE_NONE)
    # Does the easy processing: columns to keep as-is or simply rename
    proc_cols = ['adsh', 'report', 'stmt', 'line', 'tag', 'version']
    pre_proc_df = pd.concat([pre_df[col] for col in proc_cols], axis=1)
    col_dict = {'adsh': 'accession_num', 'tag': 'tag_name', 
                'version': 'tag_version'}
    pre_proc_df = pre_proc_df.rename(columns=col_dict)
    # Combines statement and report data into new column and deletes the old one
    pre_proc_df['statement_report'] = pre_proc_df['stmt'] + "_" + pre_proc_df['report'].astype(str)
    pre_proc_df.drop(labels=['stmt', 'report'], axis=1, inplace=True)
    write_as_append(pre_proc_df, outpath, header=writeheader[2])
    writeheader[2] = False
    return True

def tag_parse(filepath, outpath):
    """ Parses the data on tag files ONLY.
        Inputs: path of tag file, output path of processed file
        Outputs: True if everything works
    """
    tag_df = pd.read_csv(filepath, sep='\t', encoding='iso8859-1', quoting=csv.QUOTE_NONE)
    # Does the easy processing: columns to keep as-is or simply rename
    proc_cols = ['tag', 'version', 'abstract', 'datatype', 
                 'iord', 'crdr', 'doc']
    tag_proc_df = pd.concat([tag_df[col] for col in proc_cols], axis=1)
    col_dict = {'tag': 'tag_name', 'version': 'tag_version', 
                'iord':'point_or_duration', 'crdr':'debit_or_credit'}
    tag_proc_df = tag_proc_df.rename(columns=col_dict)
    # Transforms abstract into is_numeric by swapping values
    lambda_swap = lambda x: int(not x)
    tag_proc_df['abstract'] = tag_proc_df['abstract'].apply(lambda_swap)
    tag_proc_df = tag_proc_df.rename(columns={'abstract':'is_numeric'})
    write_as_append(tag_proc_df, outpath, header=writeheader[3])
    writeheader[3] = False
    return True

def parse_in_directory(folderpath):
    """ Parses the data on all files in a directory.
        Inputs: path of target directory
        Outputs: True if everything works
    """
    for cur_path, directories, files in os.walk(folderpath, topdown=True):
        for file in files:
            path = os.path.join(cur_path,file)
            memory_check(path)
            logger.debug("Processing {}".format(path))
            if "sub" in file:
                submission_parse(path, folderpath + "SUB_INTERMEDIATE.txt")
            elif "num" in file:
                number_parse(path, folderpath + "NUM_INTERMEDIATE.txt")
            elif "pre" in file:
                presentation_parse(path, folderpath + "PRE_INTERMEDIATE.txt")
            elif "tag" in file:
                tag_parse(path, folderpath + "TAG_INTERMEDIATE.txt")
    return True

# Move to separate file?
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
            

def post_proc(folderpath, stock_folderpath):
    """ Post-processing on data of interest.
        Inputs: path of tag file, path of stock data folder
        Outputs: True if everything works
    """
    ## Loads all stock data downloaded to given folder
    symbols = get_current_symbols(stock_folderpath)
    #########################################################
    ## Loads SUB_INTERMEDIATE from its location            ##
    #########################################################
    logger.debug("Reading %s file from local drive...", "SUB")
    sub_inter_df = pd.read_csv(folderpath + "SUB_INTERMEDIATE.txt", sep='\t', encoding='iso8859-1')
    # Drop non-unique CIK values
    sub_inter_df.drop_duplicates(subset=['accession_num'], inplace=True)
    # Drop rows with symbols not in the symbol list
    sub_inter_df = sub_inter_df[sub_inter_df.symbol.isin(symbols)]
    # Saves the accession number column for later use
    accession_list = list(sub_inter_df.accession_num.values)
    # Frees up some memory and writes SUB FINAL to file
    sub_inter_df = sub_inter_df.to_csv(folderpath + "SUB_FINAL.txt", sep='\t', index=False)
    #########################################################
    ## Loads TAG_INTERMEDIATE from its location            ##
    #########################################################
    logger.debug("Reading %s file from local drive...", "TAG")
    tag_inter_df = pd.read_csv(folderpath + "TAG_INTERMEDIATE.txt", sep='\t', encoding='iso8859-1')
    # Drops non-unique values based on tag name AND tag version
    tag_inter_df.drop_duplicates(subset=['tag_name', 'tag_version'], inplace=True)
    # Frees up memory and writes TAG FINAL to file
    tag_inter_df = tag_inter_df.to_csv(folderpath + "TAG_FINAL.txt", sep='\t', index=False)
    #########################################################
    ## Loads NUM_INTERMEDIATE from its location in chunks  ##
    #########################################################
    logger.debug("Reading %s file from local drive...", "NUM")
    num_chunks = pd.read_csv(folderpath + "NUM_INTERMEDIATE.txt", sep='\t', chunksize=csize, encoding='iso8859-1')
    writeHeader = True
    with open(folderpath + "NUM_FINAL.txt", 'w') as numfinalfile:
        for chunk in num_chunks:
            logger.debug("Accession #%s being read...", chunk.accession_num[chunk.index[0]])
            chunk_filter = chunk[chunk.accession_num.isin(accession_list)]
            chunk_filter.to_csv(numfinalfile, sep='\t', index=False, header=writeHeader)
            writeHeader = False
    numfinalfile.close()
    #########################################################
    ## Loads PRE_INTERMEDIATE from its location in chunks  ##
    #########################################################
    logger.debug("Reading %s file from local drive...", "PRE")
    pre_chunks = pd.read_csv(folderpath + "PRE_INTERMEDIATE.txt", sep='\t', chunksize=csize, encoding='iso8859-1')
    writeHeader = True
    with open(folderpath + "PRE_FINAL.txt", 'w') as prefinalfile:
        for chunk in pre_chunks:
            logger.debug("Accession #%s being read...", chunk.accession_num[chunk.index[0]])
            chunk_filter = chunk[chunk.accession_num.isin(accession_list)]
            chunk_filter.to_csv(prefinalfile, sep='\t', index=False, header=writeHeader)
            writeHeader = False
    prefinalfile.close()
    return True

def json_build(folderpath, outpath):
    # Loads the four FINAL files from their location
    sub_final_df = pd.read_csv(folderpath + "SUB_FINAL.txt", sep='\t', encoding='iso8859-1')
    # num_final_df = pd.read_csv(folderpath + "NUM_FINAL.txt", sep='\t', encoding='iso8859-1')
    # pre_final_df = pd.read_csv(folderpath + "PRE_FINAL.txt", sep='\t', encoding='iso8859-1')
    # tag_final_df = pd.read_csv(folderpath + "TAG_FINAL.txt", sep='\t', encoding='iso8859-1')
    # Gets all the columns of interest for json metadata
    json_meta = pd.concat([sub_final_df.symbol, sub_final_df.company_name, 
                           sub_final_df.central_index_key, sub_final_df.industry_name, 
                           sub_final_df.former_name, sub_final_df.date_of_name_change, 
                           sub_final_df.is_well_known_seasoned_issuer, sub_final_df.data_source], axis=1)
    # The metadata entries are one-to-one with symbol
    json_meta.drop_duplicates(subset=['symbol'], inplace=True)
    # For each symbol in json_meta, processes into a different JSON file
    for symbol in json_meta.symbol:
        # Gets the current symbol
        logger.debug("Processing %s financal statements...", symbol)
        # Gets all accession numbers for this symbol
        symbol_sub = sub_final_df[sub_final_df.symbol == symbol]
        # Isolates the metadata for this symbol
        json_meta_one = json_meta[json_meta.symbol == symbol].to_json(orient='records')
        # Indicates that this info is metadata
        json_meta_one = json_meta_one[:1] + "\"metadata\":" + json_meta_one[1:]
        # Cleans up the JSON metadata
        json_meta_one = json_meta_one.replace('[', '')
        json_meta_one = json_meta_one.replace(']', '')
        json_meta_one = "{" + json_meta_one + ","
        # For given symbol, merge symbol_sub with NUM on accession_num
        # and merge with PRE on accession_num
        # and merge with TAG on tag_name and tag_version
        # Write each row of dataframe as JSON file
        # Writes each line of JSON to file with symbol in name
        filename = outpath + "{}_Financials.json".format(symbol)
        with open(filename, 'w') as jsonfile:
            jsonfile.write(json_meta_one + '\n')
        jsonfile.close()
        break

folder_path = "C:/Users/Miguel/Desktop/EDGAR/"
stock_folder_path = "C:/Users/Miguel/Documents/EQUITIES/stockDaily"
outpath = "C:/Users/Miguel/Desktop/"
# download_unzip(folder_path)
# parse_in_directory(folder_path)
# post_proc(folder_path, stock_folder_path)
json_build(folder_path, outpath)