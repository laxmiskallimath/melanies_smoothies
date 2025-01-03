# Import python packages
import requests
import pandas as pd
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Smoothie Name Input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be: ', name_on_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch Fruit Options
my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'), col('SEARCH_ON')).order_by(col('FRUIT_ID'))
pd_df = my_dataframe.to_pandas()

# Ingredients Selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    # Fetch Nutrition Information for Selected Fruits
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Insert Order into Database with order_filled=False
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
        VALUES ('{ingredients_string}', '{name_on_order}', FALSE)
    """
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# Manage Orders Section
st.header("Manage Orders")
orders_df = session.table('smoothies.public.orders').to_pandas()

# Display Orders with Status
st.subheader("Pending Orders")
pending_orders_df = orders_df[orders_df['ORDER_FILLED'] == False]
st.dataframe(pending_orders_df)

st.subheader("Completed Orders")
completed_orders_df = orders_df[orders_df['ORDER_FILLED'] == True]
st.dataframe(completed_orders_df)

# Update Order Status
order_id = st.number_input('Enter Order ID to mark as filled:', min_value=1, step=1)
mark_filled = st.button('Mark as Filled')

if mark_filled:
    update_stmt = f"UPDATE smoothies.public.orders SET order_filled = TRUE WHERE id = {order_id}"
    session.sql(update_stmt).collect()
    st.success(f"Order {order_id} marked as filled!")
