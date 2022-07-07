import pandas as pd
from tqdm import tqdm

def convert_property_info_to_json(
    postcodes : pd.DataFrame, all_info_adjusted : pd.DataFrame
) -> dict:
    """
    Convert property and postcode information into a JSON format
    structured as follows:
        - Postcode:
            - Number of Sales [Adjusted, Unadjusted]
            - Detached House Sales [Adjusted, Unadjusted]
            - Semi Detached House Sales [Adjusted, Unadjusted]
            - Terraced House Sales [Adjusted, Unadjusted]
            - Flat Sales [Adjusted, Unadjusted]
            - Other Sales [Adjusted, Unadjusted]
            - Neighbour Postcodes
    
    Parameters
    ----------
    postcodes : pd.DataFrame
        Postcode information (containing neighbouring postcodes)
    all_info_adjusted : pd.DataFrame
        Contains all historical property information
        with an adjusted price to account for historical
        national market fluctuations.
    
    Returns
    -------
    postcode_info : dict
        The postcode information structured in JSON format (as
        outlined above).
    """
    postcode_info = {}
    
    for tup in tqdm(postcodes[['Postcode','Nearby districts']].itertuples()):
        
        # Set postcode as key
        postcode_info[tup.Postcode] = {}
        
        # Find all property sales in the postcode
        properties = all_info_adjusted.loc[
            all_info_adjusted.postcode_group == tup.Postcode
        ]
        
        # Store number of properties sold in the postcode
        postcode_info[tup.Postcode]['n'] = len(properties)


        for prop_type in {'D','S','T','F','O'}:
            
            # Store vector of historical property sales, adjusted
            # and not, for each of the property types
            postcode_info[tup.Postcode][prop_type] = {}
            postcode_info[tup.Postcode][prop_type]['adjusted'] = (
                list(
                    properties
                    .loc[properties.property_type == prop_type]
                    .adjusted_sold_price.values
                )
            )
            postcode_info[tup.Postcode][prop_type]['unadjusted'] = (
                list(
                    properties
                    .loc[properties.property_type == prop_type]
                    .sold_price.values
                )
            )
        
        # Store the neighbouring postcodes (or an empty list
        # if there aren't any)
        if type(tup._2) != str:
            postcode_info[tup.Postcode]['Neighbours'] = {}

        else:
            postcode_info[tup.Postcode]['Neighbours'] = {
                    x.replace(' ','') for x in tup._2.split(',')
                }
    return postcode_info