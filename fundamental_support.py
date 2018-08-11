## Supporting parser code for each file in the EDGAR dataset.
## Link: https://www.sec.gov/dera/data/financial-statement-data-sets.html
## Author: Miguel Opeña
## Version: 1.1.1

import csv
import pandas as pd

import io_support

lambda_reg_case = lambda x: " ".join([w.lower().capitalize() for w in x.split(" ")])
writeheader = [True, True, True, True]

def json_clean(json_as_string, newline=False):
    json_as_string = json_as_string.replace('\\/', '/')
    json_as_string = json_as_string.replace('\"nciks\":1,', '')
    json_as_string = json_as_string.replace('\"aciks\":null,', '')
    json_as_string = json_as_string.replace(',\"debit_or_credit\":null', '')
    json_as_string = json_as_string.replace(',\"point_or_duration\":null', '')
    json_as_string = json_as_string.replace(',\"datatype\":null', '')
    if newline:
        json_as_string = json_as_string.replace('},', '},\n')
    return json_as_string

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

def edgar_sub(filepath, outpath):
    """ Parses the data on submission files ONLY.
        Inputs: path of submission file, output path of processed file
        Outputs: True if everything works
    """
    sub_df = pd.read_csv(filepath, sep='\t', encoding='iso8859-1', quoting=csv.QUOTE_NONE)
    # Does the easy processing: columns to keep as-is or simply rename
    proc_cols = ['adsh', 'cik', 'name', 'sic', 'former', 'changed', 'wksi', 
                 'form', 'instance', 'nciks', 'aciks']
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
    io_support.write_as_append(sub_proc_df, outpath, header=writeheader[0])
    writeheader[0] = False
    return True

def edgar_num(filepath, outpath):
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
    io_support.write_as_append(num_proc_df, outpath, header=writeheader[1])
    writeheader[1] = False
    return True

def edgar_pre(filepath, outpath):
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
    io_support.write_as_append(pre_proc_df, outpath, header=writeheader[2])
    writeheader[2] = False
    return True

def edgar_tag(filepath, outpath):
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
    io_support.write_as_append(tag_proc_df, outpath, header=writeheader[3])
    writeheader[3] = False
    return True
