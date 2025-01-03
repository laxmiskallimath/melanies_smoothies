# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("""Choose the fruits you want in your custom Smoothie!""")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on smoothie will be:", name_on_order)

# Set ORDER_FILLED based on name
if name_on_order == "Kevin":
    order_filled = False  # Kevin's order is not filled
elif name_on_order == "Divya" or name_on_order == "Xi":
    order_filled = True  # Divya's and Xi's orders are filled
else:
    order_filled = False  # Default status if no name matches

# Display the order filled status
st.write(f"Order Status for {name_on_order}: {'FILLED' if order_filled else 'NOT FILLED'}")

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark DataFrame to Pandas DataFrame to use the LOC function
pd_df = my_dataframe.to_pandas()

# Let the user select fruits from the options
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:"
    , my_dataframe['FRUIT_NAME'].tolist()  # Using only the FRUIT_NAME column
    , max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(fruit_chosen + " Nutrition Information")
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # Prepare the SQL insert statement (simulated here)
    my_insert_stmt = f""" insert into smoothies.public.orders(ingredients, name_on_order, ORDER_FILLED)
                          values ('{ingredients_string}', '{name_on_order}', {order_filled})"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
