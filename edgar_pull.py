## From the downloaded JSON files, this code pulls 
## Part of the fundamental analysis. 
## Author: Miguel Opeña
## Version: 1.0.1

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_unique_tags(filepath):
    """ Fetches a list of all unique tags in a given JSON file of EDGAR data. 
        Inputs: file path of JSON file
        Outputs: list of unique tags in said file
    """
    # Opens the EDGAR JSON at the given filepath
    jsonfile = open(filepath, 'r')
    # Stores unique tags
    tag_uniques = []
    # Reads line-by-line for tags
    for line in jsonfile.readlines():
        # Skips metadata and accession number lines
        if "line" not in line:
            continue
        # Hardcodes the tag location
        this_tag = line.split('\"')[5]
        if this_tag not in tag_uniques:
            tag_uniques.append(this_tag)
    return tag_uniques

def main():
    inpath = "C:/Users/Miguel/Documents/EQUITIES/stockDaily/Financials/AAPL_Financials.json"
    print(get_unique_tags(inpath))

if __name__ == "__main__":
    main()