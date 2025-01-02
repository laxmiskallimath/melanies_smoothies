# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie:cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the snowpark dataframe to a Pandas DataFrame so we can use the LOC function
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    [row['FRUIT_NAME'] for row in my_dataframe],  # Extract fruit names directly here
    max_selections=5
)

if ingredients_list:
    # Initialize the ingredients string
    ingredients_string = ""

    # Display the selected fruits' search values
    for fruit_chosen in ingredients_list:
        # Fetch the SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        ingredients_string += search_on + " "  # Append search value to ingredients string
        
        # Display the search value for the selected fruit
        st.write(f'The search value for {fruit_chosen} is "{search_on}".')
        
        st.subheader(f"{fruit_chosen} Nutrition Information")  # Display header for the fruit
        
        # Fetch data from the API using the SEARCH_ON value
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        smoothiefroot_response.raise_for_status()  # Ensure proper error handling

        # Display the nutrition information as a dataframe
        nutrition_data = smoothiefroot_response.json()  # Assuming API returns JSON data
        st.dataframe(data=nutrition_data, use_container_width=True)

    # Place the button in the correct location
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        st.success('Your Smoothie is ordered!', icon="✅")
