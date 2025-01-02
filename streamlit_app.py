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

# Convert the Snowpark DataFrame to a Pandas DataFrame so we can use the LOC function
pd_df = my_dataframe.to_pandas()

# Display the dataframe for debugging purposes
st.dataframe(pd_df)

# Create a multiselect dropdown to choose fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Pass only the fruit names from the dataframe
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Fetch the search value for the selected fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')
        
        # Display the fruit name first
        st.subheader(f"{fruit_chosen} Nutrition Information")
        
        # Fetch data from the Fruityvice API using the search term
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        
        if fruityvice_response.status_code == 200:
            # Assuming the API returns nutrition information in a structured format
            nutrition_data = fruityvice_response.json()
            
            # Convert the JSON data into a pandas DataFrame for better display
            if isinstance(nutrition_data, dict):
                nutrition_df = pd.DataFrame([nutrition_data])
                st.dataframe(nutrition_df)  # Display as a DataFrame
            else:
                st.error("Nutrition data is not in the expected format.")
        else:
            st.error(f"Error fetching nutrition data for {fruit_chosen}")
    
    # Display the selected ingredients
    st.write(f"You've selected the following ingredients: {ingredients_string.strip()}")
    
    # Place the button in the correct location
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        st.success('Your Smoothie is ordered!', icon="✅")
