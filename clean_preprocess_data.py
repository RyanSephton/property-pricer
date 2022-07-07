import pandas as pd


if __name__ == "__main__":
    
    ## If postcodes need imputing 
    # all_df = (
    #     ingest_join_properties(
    #         ['data/raw_data/' + x 
    #          for x in os.listdir('data/raw_data')[1:]]
    #     )
    # )
    # all_df = impute_postcodes(all_df) # WARNING - very very slow
    # all_df.to_csv('data/cleaned_data/joined_imputed_data.csv')


    # If postcodes have been imputed before, start from here
    all_df = pd.read_csv('data/cleaned_data/joined_imputed_data.csv',index_col=0)
    all_df = append_time_information(all_df)

    # Load in postcode info
    postcodes = pd.read_csv('data/raw_data/Postcode districts.csv')

    # Load in historical price index adjustments
    price_adjs = ingest_price_adjustments(
        'data/raw_data/Average-price-seasonally-adjusted.csv'
    )

    # Calculate adjusted price
    price_adjs = calculate_adjustment_ratio(price_adjs, all_df)

    # Free up memory
    df = all_df[[
        'sold_price','sold_date','sold_year',
        'sold_month', 'sold_year_month','postcode',
        'postcode_group','property_type'
    ]]
    del all_df

    df_adjusted = (
        apply_sold_price_adjustments(
            price_adjs, 
            df
        )
    )

    # Convert to JSON format for consumption in the web app
    property_info_json = convert_property_info_to_json(postcodes, df_adjusted)
    save_json(
        'data/cleaned_data/clean_property_info_test.json', 
        property_info_json
    )