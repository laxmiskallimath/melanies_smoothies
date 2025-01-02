# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie:cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

#option = st.selectbox(
    #'What is your favorite fruit?',
   # ('Banana', 'Strawberries', 'Peaches')
#)

#st.write('Your favorite fruit is:', option)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    ,my_dataframe
    ,max_selections = 5
)

if ingredients_list:
    # Combine the selected ingredients into a single string and display
    ingredients_string = ' '.join(ingredients_list)
    #st.write('Ingredients selected:', ingredients_string)
    
    # Place the button in the correct location
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        st.success('Your Smoothie is ordered!', icon="✅")

# New section to display smoothiefroot nutrition information
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json(),use_container_width=True)


 




