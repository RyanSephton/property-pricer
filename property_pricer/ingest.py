import pandas as pd
from typing import List


def ingest_join_properties(file_list : List) -> pd.DataFrame:
    """
    Load in the files containing historical property sales by year
    and join them into a continuous dataframe.
    
    Parameters
    ----------
    file_list : list
        Contains the filenames with property transaction information,
        to be joined.
        
    Returns
    -------
    df_joined : pd.DataFrame
        Contains the joined historical property information.
    """
    # Specify field names for property dataset
    col_names = [
        'sold_price', 'sold_date','postcode','property_type',
        'unknown','freehold','door_number','apartment_number',
        'road_name','area','city','town','region'
    ]
    
    # Initialise container to store joined data
    df_joined = None
    
    for file in file_list:
        # Should exception handle here, to check valid csv 
        # (will skip for exercise)
        df = pd.read_csv(
            file, usecols = [x for x in range(1,14)], names = col_names
        )
        
        if df_joined is None:
            df_joined = df.copy()
        else:
            df_joined = pd.concat([df_joined, df], axis=0)
            
    return df_joined


def ingest_price_adjustments(filepath : str) -> pd.DataFrame:
    """
    Ingest historical, seasonally adjusted average
    house prices in the UK. Sourced from:
    http://publicdata.landregistry.gov.uk/
    market-trend-data/house-price-index-data/
    
    Parameters
    ----------
    filepath : str
        Filepath specifying the local directory
        where seasonally adjusted prices are stored
    
    Returns
    -------
    price_adjustments : pd.DataFrame
        Contains the adjusted prices for the average
        house price, by month, for the UK.
    """
    price_adjustments = (
        pd.read_csv(filepath)
    )
    price_adjustments['date'] = pd.to_datetime(price_adjustments['date'])
    
    return price_adjustments
