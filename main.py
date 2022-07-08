import pandas as pd
import os
import json
from property_pricer import calculate_property_prices
import argparse


if __name__ == "__main__":
    
    with open('data/cleaned_data/clean_property_info.json') as f:
        d = json.load(f)


    lower_bound, upper_bound, lower_bound_delta, upper_bound_delta, conf = calculate_property_prices(data, postcode,price_type,property_type, confidence)


    # Create the parser
    parser = argparse.ArgumentParser()
    # Add an argument
    parser.add_argument('--postcode', type=str, required=True)
    parser.add_argument('--price_type', type=str, required=True)
    parser.add_argument('--property_type', type=str, required=True)
    parser.add_argument('--confidence', type=float, required=True)
    
    args = parser.parse_args()

    lower_bound, upper_bound, lower_bound_delta, upper_bound_delta, conf = (
        calculate_property_prices(
            data, args.postcode,args.price_type,
            args.property_type, args.confidence
        )
    )
    
    property_types = {
        'T' : 'Terraced',
        'S' : 'Semi-Detached',
        'D' : 'Detached',
        'F' : 'Flat',
        'O' : 'Other'
    }

    print(f"""
    We Are {100*(1-(conf/2)):.2f}% Confident that {property_types[property_type]} 
    Properties in {postcode} have an {price_type} Price Starting From 
    [£{lower_bound - lower_bound_delta} - £{lower_bound + lower_bound_delta}] ranging up 
    to [£{upper_bound - upper_bound_delta} - £{upper_bound + upper_bound_delta}]
    """)
