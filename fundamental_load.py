## This code gets company data from the SEC's Financial Statement Datasets.
## Link: https://www.sec.gov/dera/data/financial-statement-data-sets.html
## Author: Miguel Opeña
## Version: 2.0.10

import logging
import os
import pandas as pd
import sys
import time
import urllib.request
import urllib.error
import zipfile

import command_parser
import edgar_parse
import io_support

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

csize = 1000000

def edgar_extract(folderpath, startyear=2013, endyear=2018):
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
            logger.info("Downloading {} from SEC website...".format(file_name))
            # Tries to download data
            try:
                urllib.request.urlretrieve(base_url + file_name, folderpath + file_name)
            # Gracefully handles errors
            except urllib.error.URLError as e:
                logger.error("URLError encountered with {}. Continuing to next file...".format(file_name))
                continue
            # Extracts file as ZIP
            logger.info("Extracting {} from ZIP file...".format(file_name.split('.')[0]))
            zip_ref = zipfile.ZipFile(folderpath + file_name, 'r')
            zip_ref.extractall(folderpath + file_name.split('.')[0])
            zip_ref.close()
            # Deletes the ZIP
            logger.info("Deleting {} ZIP file...".format(file_name.split('.')[0]))
            os.remove(folderpath + file_name)
    return

def proc_in_directory(folderpath, stock_folderpath):
    """ Parses the data on all files in a directory. Also does post-processing. 
        Inputs: path of target directory, path of folder on stock data
        Outputs: True if everything works
    """
    for cur_path, directories, files in os.walk(folderpath, topdown=True):
        for file in files:
            path = os.path.join(cur_path,file)
            io_support.memory_check(path)
            logger.info("Processing {}".format(path))
            if "sub" in file:
                edgar_parse.edgar_sub(path, folderpath + "SUB_INTERMEDIATE.txt")
            elif "num" in file:
                edgar_parse.edgar_num(path, folderpath + "NUM_INTERMEDIATE.txt")
            elif "pre" in file:
                edgar_parse.edgar_pre(path, folderpath + "PRE_INTERMEDIATE.txt")
            elif "tag" in file:
                edgar_parse.edgar_tag(path, folderpath + "TAG_INTERMEDIATE.txt")
    ## Loads all stock data downloaded to given folder
    symbols = io_support.get_current_symbols(stock_folderpath)
    #########################################################
    ## Loads SUB_INTERMEDIATE from its location            ##
    #########################################################
    logger.info("Reading %s file from local drive...", "SUB")
    sub_inter_df = pd.read_csv(folderpath + "SUB_INTERMEDIATE.txt", sep='\t', encoding='iso8859-1')
    # Drop non-unique accession numbers
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
    logger.info("Reading %s file from local drive...", "TAG")
    tag_inter_df = pd.read_csv(folderpath + "TAG_INTERMEDIATE.txt", sep='\t', encoding='iso8859-1')
    # Drops non-unique values based on tag name AND tag version
    tag_inter_df.drop_duplicates(subset=['tag_name', 'tag_version'], inplace=True)
    # Frees up memory and writes TAG FINAL to file
    tag_inter_df = tag_inter_df.to_csv(folderpath + "TAG_FINAL.txt", sep='\t', index=False)
    #########################################################
    ## Loads NUM_INTERMEDIATE from its location in chunks  ##
    #########################################################
    logger.info("Reading %s file from local drive...", "NUM")
    num_chunks = pd.read_csv(folderpath + "NUM_INTERMEDIATE.txt", sep='\t', chunksize=csize, encoding='iso8859-1')
    writeHeader = True
    with open(folderpath + "NUM_FINAL.txt", 'w') as numfinalfile:
        for chunk in num_chunks:
            logger.info("Accession #%s being read...", chunk.accession_num[chunk.index[0]])
            chunk_filter = chunk[chunk.accession_num.isin(accession_list)]
            chunk_filter.to_csv(numfinalfile, sep='\t', index=False, header=writeHeader)
            writeHeader = False
    numfinalfile.close()
    #########################################################
    ## Loads PRE_INTERMEDIATE from its location in chunks  ##
    #########################################################
    logger.info("Reading %s file from local drive...", "PRE")
    pre_chunks = pd.read_csv(folderpath + "PRE_INTERMEDIATE.txt", sep='\t', chunksize=csize, encoding='iso8859-1')
    writeHeader = True
    with open(folderpath + "PRE_FINAL.txt", 'w') as prefinalfile:
        for chunk in pre_chunks:
            logger.info("Accession #%s being read...", chunk.accession_num[chunk.index[0]])
            chunk_filter = chunk[chunk.accession_num.isin(accession_list)]
            chunk_filter.to_csv(prefinalfile, sep='\t', index=False, header=writeHeader)
            writeHeader = False
    prefinalfile.close()
    return True

def edgar_load(inpath, outpath):
    """ Processes data into one JSON file for each company.
        Inputs: path of input folder, path of output folder
        Outputs: True if everything works
    """
    # Retrieves already processed symbols
    previous_symbols = io_support.get_current_symbols(outpath, keyword='Financials', datatype='json')
    # Loads the four FINAL files from their location
    logger.info("Loading FINAL files...")
    sub_final_df = pd.read_csv(inpath + "SUB_FINAL.txt", sep='\t', encoding='iso8859-1')
    pre_final_df = pd.read_csv(inpath + "PRE_FINAL.txt", sep='\t', encoding='iso8859-1')
    tag_final_df = pd.read_csv(inpath + "TAG_FINAL.txt", sep='\t', encoding='iso8859-1')
    # Gets all the columns of interest for json metadata
    json_meta = pd.concat([sub_final_df.symbol, sub_final_df.company_name, 
                           sub_final_df.central_index_key, sub_final_df.industry_name, 
                           sub_final_df.former_name, sub_final_df.date_of_name_change, 
                           sub_final_df.is_well_known_seasoned_issuer, sub_final_df.data_source], axis=1)
    # The metadata entries are one-to-one with symbol
    json_meta.drop_duplicates(subset=['symbol'], inplace=True)   
    # For each symbol in json_meta, processes into a different JSON file
    for symbol in json_meta.symbol:
        # Skips symbols already in the folder
        if symbol in previous_symbols:
            logger.info("Symbol %s already processed, moving on.", symbol)
            continue
        # Starts timer for each symbol
        time0 = time.time() 
        ## Logs the current symbol
        logger.info("Processing %s financial statements...", symbol)
        ## Isolates the metadata for this symbol
        json_rows = json_meta[json_meta.symbol == symbol].to_json(orient='records')
        # Indicates that this info is metadata
        json_rows = json_rows[:1] + "\"metadata\":" + json_rows[1:]
        # Cleans up the JSON metadata
        json_rows = json_rows[1:-1]
        json_rows = "[{" + json_rows + ","
        #########################################################
        ## Loads SUB_FINAL for given symbol into JSON          ##
        #########################################################
        symbol_sub = sub_final_df[sub_final_df.symbol == symbol]
        # Drops irrelevant records (already in metadata):
        symbol_sub.drop(labels=['central_index_key', 'company_name',
                                'former_name', 'date_of_name_change',
                                'is_well_known_seasoned_issuer', 'detail', 
                                'data_source', 'symbol', 'industry_name'], axis=1, inplace=True, errors='ignore') 
        symbol_json = symbol_sub.drop_duplicates(subset=['accession_num'])[1:]
        # Harvests SUB records as JSON and cleans up file
        json_rows = json_rows + symbol_json.to_json(orient='records')
        json_rows = edgar_parse.json_clean(json_rows, newline=True)
        json_rows = json_rows.replace('xml\"},\n', 'xml\",\n')
        json_rows = json_rows.replace('[{\"accession', '{\"accession')
        # Saves JSON rows to split on newline
        json_split = json_rows.split('\n')
        #########################################################
        ## Merges PRE_FINAL using accession number             ##
        #########################################################
        symbol_sub_pre = symbol_sub.merge(pre_final_df, how='inner')
        for idx, row in enumerate(json_split):
            if "metadata" in row:
                continue
            # Harvests current accession number
            this_acc = row.split("\"")[3]
            logger.info("Processing accession number: %s", this_acc)
            # Retrives data from this accession number
            this_pre = symbol_sub_pre[symbol_sub_pre.accession_num == this_acc]
            this_pre.sort_values(by=['line'], inplace=True)
            this_pre.drop(labels=['accession_num', 'source', 'form'], axis=1, inplace=True)
            this_pre = pd.concat([this_pre.line, this_pre.tag_name, this_pre.tag_version, 
                                  this_pre.statement_report, this_pre.nciks, this_pre.aciks], axis=1)
            # Builds presentation data into JSON object
            pre_json = edgar_parse.json_clean(this_pre.to_json(orient='records'), newline=True)
            json_split[idx] = json_split[idx] + "\"presentation\":\n[[" + pre_json + "},"
        # Drops unnecessary columns
        symbol_sub_pre.drop(labels=['source', 'form', 'line', 'statement_report'], axis=1, inplace=True)
        # Resets the values in json_split
        json_rows = '\n'.join(json_split)
        json_split = json_rows.split('\n')
        #########################################################
        ## Merges TAG_FINAL and NUM_FINAL using tag info       ##
        #########################################################
        symbol_sub_pre_tag = symbol_sub_pre.merge(tag_final_df, how='inner')
        symbol_sub_pre_tag.drop(labels=['doc'], axis=1, inplace=True)
        symbol_all = io_support.merge_chunked(inpath + "NUM_FINAL.txt", symbol_sub_pre_tag)
        # Iterates through current lines of submission and presentation data
        for idx, row in enumerate(json_split):
            if "line" not in row:
                continue
            # Harvests current tag name and version
            this_tagname = row.split("\"")[5]
            this_tagver = row.split("\"")[9]
            logger.info("Processing tag name: %s", this_tagname)
            # Retrives data from the combined tag-num dataframe
            this_tag_num = symbol_all[symbol_all.tag_name == this_tagname]
            this_tag_num = this_tag_num[this_tag_num.tag_version == this_tagver]
            this_tag_num.drop(labels=['tag_name', 'tag_version', 'accession_num'], axis=1, inplace=True)
            # Converts date field to actual date
            lambda_date = lambda x: str(int(x))[:4] + "-" + str(int(x))[4:6] + "-" + str(int(x))[6:8] if not pd.isna(x) else x
            this_tag_num['end_date_rounded'] = this_tag_num['end_date_rounded'].apply(lambda_date)
            # Retrives data on TAG only
            tag_cols = ['is_numeric', 'datatype', 'point_or_duration', 'debit_or_credit']
            this_tag = pd.concat([this_tag_num[col] for col in tag_cols], axis=1)
            tag_json = edgar_parse.json_clean(this_tag.to_json(orient='records'))
            tag_json = '[ ]' if tag_json == '[]' else tag_json
            tag_json = tag_json.split('},')[0][2:].strip() if '},' in tag_json else tag_json[2:-2].strip()
            tag_json = tag_json + ',' if tag_json != '' else tag_json
            # Retrieves data on NUM only
            this_num = this_tag_num.drop(labels=[col for col in tag_cols], axis=1)
            num_json = edgar_parse.json_clean(this_num.to_json(orient='records'))
            # Removes entries with blank num (i.e. non-numerical rows)
            if num_json == "[]":
                json_split.pop(idx)
                continue
            num_json = "\"num\":" + num_json
            # Builds number and tag data into JSON object
            endcap = json_split[idx][json_split[idx].rfind("\"") + 1:]
            json_split[idx] = json_split[idx].replace(endcap, ',' + tag_json)
            json_split[idx] = json_split[idx] + num_json + endcap
        # Converts json_split into string and caps off the file
        json_rows = "\n".join(json_split) + "}"
        json_rows = json_rows.replace('\"},\n{\"acc', '\"}]},\n{\"acc')
        json_rows = json_rows.replace('\"SEC_EDGAR\"}]},', '\"SEC_EDGAR\"},')
        if json_rows[-2] == ',':
            json_rows = json_rows[:-2] + json_rows[-1]
        filename = outpath + "{}_Financials.json".format(symbol)
        # Writes final JSON file
        with open(filename, 'w') as jsonfile:
            jsonfile.write(json_rows)
        jsonfile.close()
        # Starts timer for each symbol
        time1 = time.time()
        time_tot = (time1 - time0)
        logger.info("Time elapsed for %s was %4.2f seconds", symbol, time_tot)
    return True

def main():
    """ User interacts with interface through command prompt, which obtains several "input" data. 
        Here are some examples of how to run this program: 
        
        python edgar_load.py -startYear 2013 -endYear 2018 -folderPath C:/Users/Miguel/Desktop/EDGAR/ -stockFolderPath C:/Users/Miguel/Documents/EQUITIES/stockDaily -financialFolderPath C:/Users/Miguel/Desktop/Financials
        This will download data from 2013 to 2018 into folderPath, filter based on stocks at stockFolderPath, and store final output in financialFolderPath
        
        Inputs: implicit through command prompt
        Outputs: True if everything works
    """
    prompts = sys.argv
    ## Handles start and end year of download
    startyear = int(command_parser.get_generic_from_prompts(prompts, query="-startYear"))
    endyear = int(command_parser.get_generic_from_prompts(prompts, query="-endYear"))
    ## Handles where the user wants to download files. 
    # Default folder path is relevant to the author only. 
    folder_path = command_parser.get_generic_from_prompts(prompts, query="-folderPath", default="/Users/openamiguel/Desktop/EDGAR", req=False)
    folder_path = folder_path + "/" if folder_path[-1] != "/" else folder_path
    ## Handles where the user downloaded their stock data.  
    # Default folder path is relevant to the author only. 
    stock_folder_path = command_parser.get_generic_from_prompts(prompts, query="-stockFolderPath", default="/Users/openamiguel/Documents/EQUITIES/stockDaily", req=False)
    stock_folder_path = stock_folder_path + "/" if stock_folder_path[-1] != "/" else stock_folder_path
    ## Handles where the user wants to store their financial data.
    # Default folder path is relevant to the author only.
    financial_folder_path = command_parser.get_generic_from_prompts(prompts, query="-financialFolderPath", default="/Users/openamiguel/Documents/EQUITIES/stockDaily/Financials", req=False)
    financial_folder_path = financial_folder_path + "/" if financial_folder_path[-1] != "/" else financial_folder_path
    # Checks if user wants to suppress any functions
    suppress = ["-suppressDownload" in prompts, "-suppressProcess" in prompts]
    ## Does all the legwork
    if not suppress[0]:
        edgar_extract(folder_path, startyear=startyear, endyear=endyear)
    if not suppress[1]:
        proc_in_directory(folder_path, stock_folder_path)
    edgar_load(folder_path, financial_folder_path)
    logger.info("All tasks completed. Have a nice day!")
    return True

if __name__ == "__main__":
    main()
