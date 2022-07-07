import pandas as pd
from tqdm import tqdm

def get_postcode_candidates(
    entry_w_no_postcode : pd.Series, 
    all_info : pd.DataFrame) -> str:
    """
    Obtains a possible postcode match for properties based
    on other common attributes such as shared road names and
    city names, or region names.
    
    Parameters
    ----------
    entry_w_no_postcode : pd.Series
        Single row from historical property information
        with a missing postcode field.
    all_info : pd.DataFrame
        Contains all of the historical property information.
    
    Returns
    -------
    candidate_postcode : str
        Possible match for the property postcode (or None
        if no match could be found).
    """
    # Try to find candidates that share a road name and the same town 
    # (Assumption here is unique road names in every town)
    candidates = all_info.loc[
        (all_info.road_name == entry_w_no_postcode.road_name) &
        (all_info.town == entry_w_no_postcode.town)
    ]
    
    if not candidates.empty:
        return candidates.postcode.mode().values[0]
    
    # Failing this, try to find candidates that share a road name 
    # and the city (Assumption here is unique road names in every city)
    candidates = all_info.loc[
        (all_info.road_name == entry_w_no_postcode.road_name) &
        (all_info.city == entry_w_no_postcode.city)
    ]
    
    if not candidates.empty:
        return candidates.postcode.mode().values[0]
    
    # Otherwise try to find a match on a road name and a region, though
    # this is not ideal as road names will not necessarily be unique to 
    # a city
    candidates = all_info.loc[
        (all_info.road_name == entry_w_no_postcode.road_name) &
        (all_info.region == entry_w_no_postcode.region)
    ]
    
    if not candidates.empty:
        return candidates.postcode.mode().values[0]
    
    return None 


def impute_postcodes(all_sales_history : pd.DataFrame) -> pd.DataFrame:
    """
    imputes missing postcodes where possible by searching,
    in order, for the following:
    - Matching road names and towns
    - Matching road names and cities
    - Matching road names and regions
    
    This function is very slow and unoptimized, but works
    as a last resort.
    
    Parameters
    ----------
    all_sales_history : pandas.DataFrame
        Contains all historical house price sales.
        
    Returns
    -------
    all_sales_history : pandas.DataFrame
        All historical house price sales with missing postcodes
        imputed where possible.
    """
    # Split off entries with no postcodes
    no_postcodes = (
        all_sales_history.loc[
            all_sales_history.postcode.isna()
        ].copy()
    )
    
    entries_w_postcodes = (
        all_sales_history.loc[
            all_sales_history.postcode.notna()
        ].copy()
    )
    
    postcode_subset = entries_w_postcodes.loc[
        entries_w_postcodes.region.isin(no_postcodes.region.unique())
    ]
                                        
    # Loop through to repair missing postcodes - Note 
    # iterrows is very slow, but this only needs to be 
    # done once, and only on the 12k missing postcodes
    imputed_postcodes = []
    for row in tqdm(no_postcodes.itertuples()):
        best_postcode_match = (
            get_postcode_candidates(row, postcode_subset)
        )

        imputed_postcodes.append(best_postcode_match)
    
    no_postcodes.loc[:,'postcode'] = imputed_postcodes
    
    # Modify argument directly as dataframe will be very large
    all_sales_history = pd.concat([
        entries_w_postcodes, 
        no_postcodes.loc[no_postcodes.postcode.notna()]
    ], axis=0)
    
    return all_sales_history



def calculate_adjustment_ratio(
    price_adjustments : pd.DataFrame, 
    all_info : pd.DataFrame) -> pd.DataFrame:
    """
    Determines the fractional multiplier [0,1] that should be 
    applied to adjust for historical monthly fluctuations to
    house prices in the UK. Sets the most recent month with
    a recorded property sale as the reference index i.e. 1
    
    Parameters
    ----------
    price_adjustments : pd.DataFrame
        Contains the adjusted prices for the average
        house price, by month, for the UK.
    all_info : pd.DataFrame
        Contains all of the historical property information.
    
    Returns
    -------
    price_adjustments_w_index : pd.DataFrame
        Contains the adjusted prices for the average
        house price, by month, for the UK, with the adjustment
        reference index.
    """
    reference_price = (
        price_adjustments.loc[
            price_adjustments.date ==  all_info.sold_year_month.max(),
            'adjusted_avg_price'
        ].values[0]
    )

    price_adjustments_w_index = price_adjustments.loc[
        (price_adjustments.date <= all_info.sold_year_month.max()) &
        (price_adjustments.date >= all_info.sold_year_month.min())
    ].copy()
    
    
    price_adjustments_w_index.loc[:,'adjustment_ratio'] = (
        price_adjustments_w_index.loc[:,'adjusted_avg_price']
        .divide(reference_price)
    )
    
    return price_adjustments_w_index


def append_time_information(all_info : pd.DataFrame) -> pd.DataFrame:
    """
    Joins on month, yeay, and year-month information
    to the historical property sales.
    
    Parameters
    ----------
    all_info : pd.DataFrame
        Contains all of the historical property information.
        
    Returns
    -------
    all_info_w_time : pd.DataFrame
        Contains all of the historical property information
        with year, month and year month columns joined on.
    """
    all_info_w_time = all_info.copy()
    all_info_w_time.loc[:,'postcode_group'] = [
        x.split(' ')[0] for x in all_info_w_time.postcode
    ]
    all_info_w_time.loc[:,'sold_date'] = pd.to_datetime(all_info_w_time.sold_date)
    all_info_w_time.loc[:,'sold_year'] = all_info_w_time.sold_date.dt.year
    all_info_w_time.loc[:,'sold_month'] = all_info_w_time.sold_date.dt.month
    all_info_w_time.loc[:,'sold_year_month'] = pd.to_datetime(
        all_info_w_time['sold_year'].astype('str') + 
        '-' + all_info_w_time['sold_month'].astype('str')
    )
    
    return all_info_w_time


def apply_sold_price_adjustments(
    price_adjustments : pd.DataFrame, 
    all_info : pd.DataFrame) -> pd.DataFrame:
    """
    Adjusts the sold price for historical house sales to account
    for UK housing market index fluctuations.
    
    Parameters
    ----------
    price_adjustments : pd.DataFrame
        Contains the adjusted prices for the average
        house price, by month, for the UK.
    all_info : pd.DataFrame
        Contains all of the historical property information.
    
    Returns
    -------
    all_info_adjusted : pd.DataFrame
        Contains all historical property information
        with an adjusted price to account for historical
        national market fluctuations.
    """
    all_info_adjusted = (
        all_info.merge(
            price_adjustments[['date','adjustment_ratio']], 
            left_on='sold_year_month', 
            right_on='date', 
            how='left').drop('date',axis=1)
    )
    all_info_adjusted.loc[:, 'adjusted_sold_price'] = (
        all_info_adjusted.loc[:,'sold_price'] /
        all_info_adjusted.loc[:,'adjustment_ratio']
    )
    return all_info_adjusted