## This code gets company data from the SEC's Financial Statement Datasets.
## Link: https://www.sec.gov/dera/data/financial-statement-data-sets.html
## Author: Miguel Opeña
## Version: 1.7.10

import logging
import os
import pandas as pd
import urllib.request
import urllib.error
import zipfile

import edgar_parse
import io_support

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

csize = 1000000

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

def proc_in_directory(folderpath):
    """ Parses the data on all files in a directory.
        Inputs: path of target directory
        Outputs: True if everything works
    """
    for cur_path, directories, files in os.walk(folderpath, topdown=True):
        for file in files:
            path = os.path.join(cur_path,file)
            io_support.memory_check(path)
            logger.debug("Processing {}".format(path))
            if "sub" in file:
                edgar_parse.submission_parse(path, folderpath + "SUB_INTERMEDIATE.txt")
            elif "num" in file:
                edgar_parse.number_parse(path, folderpath + "NUM_INTERMEDIATE.txt")
            elif "pre" in file:
                edgar_parse.presentation_parse(path, folderpath + "PRE_INTERMEDIATE.txt")
            elif "tag" in file:
                edgar_parse.tag_parse(path, folderpath + "TAG_INTERMEDIATE.txt")
    return True

def post_proc(folderpath, stock_folderpath):
    """ Post-processing on data of interest.
        Inputs: path of tag file, path of stock data folder
        Outputs: True if everything works
    """
    ## Loads all stock data downloaded to given folder
    symbols = io_support.get_current_symbols(stock_folderpath)
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
    pre_final_df = pd.read_csv(folderpath + "PRE_FINAL.txt", sep='\t', encoding='iso8859-1')
    tag_final_df = pd.read_csv(folderpath + "TAG_FINAL.txt", sep='\t', encoding='iso8859-1')
    # Gets all the columns of interest for json metadata
    json_meta = pd.concat([sub_final_df.symbol, sub_final_df.company_name, 
                           sub_final_df.central_index_key, sub_final_df.industry_name, 
                           sub_final_df.former_name, sub_final_df.date_of_name_change, 
                           sub_final_df.is_well_known_seasoned_issuer, sub_final_df.data_source], axis=1)
    # The metadata entries are one-to-one with symbol
    json_meta.drop_duplicates(subset=['symbol'], inplace=True)
    # For each symbol in json_meta, processes into a different JSON file
    for symbol in json_meta.symbol:
        ## Logs the current symbol
        logger.debug("Processing %s financial statements...", symbol)
        ## Isolates the metadata for this symbol
        json_meta_one = json_meta[json_meta.symbol == symbol].to_json(orient='records')
        # Indicates that this info is metadata
        json_meta_one = json_meta_one[:1] + "\"metadata\":" + json_meta_one[1:]
        # Cleans up the JSON metadata
        json_meta_one = json_meta_one.replace('[', '')
        json_meta_one = json_meta_one.replace(']', '')
        json_meta_one = "{" + json_meta_one + ","
        ## Gets all data for current symbol
        symbol_sub = sub_final_df[sub_final_df.symbol == symbol]
        # Drops irrelevant records (already in metadata):
        symbol_sub.drop(labels=['central_index_key', 'company_name',
                                'former_name', 'date_of_name_change',
                                'is_well_known_seasoned_issuer', 'detail', 
                                'data_source', 'symbol', 'industry_name'], axis=1, inplace=True) 
        # For given symbol, merge symbol_sub with PRE on accession_num (in chunks)
        symbol_sub_pre = symbol_sub.merge(pre_final_df, how='inner')
        # Merge with TAG on tag_name and tag_version
        symbol_sub_pre_tag = symbol_sub_pre.merge(tag_final_df, how='inner')
        symbol_sub_pre_tag.drop(labels=['doc'], axis=1, inplace=True)
        # Merge with NUM on accession_num
        symbol_all = io_support.merge_chunked(folderpath + "NUM_FINAL.txt", symbol_sub_pre_tag)
        # Drops irrelevant records (already in metadata):
        # Sort the dataframe
        symbol_all.sort_values(by=['accession_num','tag_name','tag_version'], inplace=True)
        # Write each row of dataframe as JSON file
        # Writes each line of JSON to file with symbol in name
        filename = outpath + "{}_Financials.json".format(symbol)
        with open(filename, 'w') as jsonfile:
            json_rows = symbol_all.to_json(orient='records')
            # Cleans up the JSON rows
            json_rows = json_rows.replace('[', '')
            json_rows = json_rows.replace(']', '')
            json_rows = json_rows.replace('\\/', '/')
            json_rows = json_rows.replace('},', '},\n')
            # Removes unnecessary data
            json_rows = json_rows.replace('\"nciks\":1,', '')
            json_rows = json_rows.replace('\"aciks\":null,', '')
            json_rows = json_rows.replace(',\"debit_or_credit\":null', '')
            # Writes metadata and rows to file
            jsonfile.write(json_meta_one + '\n')
            jsonfile.write(json_rows + "}")
        jsonfile.close()
        break

folder_path = "C:/Users/Miguel/Desktop/EDGAR/"
stock_folder_path = "C:/Users/Miguel/Documents/EQUITIES/stockDaily"
outpath = "C:/Users/Miguel/Desktop/"
# download_unzip(folder_path)
# proc_in_directory(folder_path)
# post_proc(folder_path, stock_folder_path)
json_build(folder_path, outpath)