import streamlit as st
import json
from property_pricer import calculate_property_prices

st.set_page_config(
    page_title="Property Pricing App", page_icon="📊", initial_sidebar_state="expanded"
)

st.write(
    """
# 📊 The Property Pricer

This is a quick demonstration of a property pricing app. Enter the postcode, property type,
and pricing type, as well as how confident you want us to be in our estimate, and we'll tell you the
price range you're looking at.

We support the following property types:
* Detached
* Semi-Detached
* Terrace
* Flat
* Other

We also offer two pricing options, to make the numbers as transparent as we can:
* **Adjusted** price - Don't care if your nan bought her house for £3000? This options for you. We adjust the house prices for what you'll pay today, so you see how much houses would have cost, if all of them were sold this month.
* **Unadjusted** price - Just tell me what it sold for, when it sold, nobody likes a clever clogs. 
"""
)

@st.cache
def load_data():
    with open('data/cleaned_data/clean_property_info.json') as f:
        data = json.load(f)
    return data


data = load_data()

property_types = {
    'Terraced' : 'T',
    'Semi-Detached' : 'S',
    'Detached' : 'D',
    'Flat' : 'F',
    'Other' : 'O'
}



with st.form("user_input"):
    st.write("Tell us what you're into")
    
    postcode = st.selectbox("Pick a postcode", options = data.keys(),index = 600)
    property_type = st.selectbox("Pick a property type", options = property_types.keys())
    price_type = st.selectbox("Select a price type", options = ['adjusted', 'unadjusted'])
    confidence = st.slider(label = 'How confident would you like to be', min_value = 0., max_value = 1., value = 0.95)
    st.write('Note: confidence may fluctuate downwards depending on data availability')
    submitted = st.form_submit_button("Lets Go!")
    
    if submitted:
        try:
            lower_bound, upper_bound, lower_bound_delta, upper_bound_delta, conf = (
                calculate_property_prices(
                    data, postcode,price_type,property_types[property_type], confidence
                )
            )
            
            st.write(f"""
                    ## We Are {100*(1-(2*conf)):.2f}% Confident that {property_type} 
                    ## Properties in {postcode} have an {price_type} Price in the range  
                    ## [£{lower_bound - lower_bound_delta} - £{upper_bound + upper_bound_delta}]
                """)
        except: 
            st.warning("We don't have enough information in that postcode or the neighbouring"
                      " postcodes to give you a reliable estimate, try picking a different postcode")
        