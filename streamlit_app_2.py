# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched
# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")



cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED")==False).collect()

st.text('Orders that need to filled')
if my_dataframe:
    editable_df = st.data_editor(my_dataframe)
    submitted = st.button('Submit') 

    if submitted:

        try:
            og_dataset = session.table("smoothies.public.orders")
            edited_dataset = session.create_dataframe(editable_df)
            og_dataset.merge(edited_dataset
                     , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                     , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                    )
            st.success('Someone clicked the button', icon = '👍')
        except:
            st.write('Something went wrong.')

else:
    st.success('There are no pending orders right now',icon = '👍' )
