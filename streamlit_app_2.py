# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Pending Smoothies Orders!:cup_with_straw:")
st.write(
    """Orders that need to be filled."""
)

session = get_active_session()
my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED") == 0).to_pandas()

# Editable dataframe using pandas
editable_df = st.data_editor(my_dataframe)

submitted = st.button('Submit')

if submitted:
    # Convert the pandas DataFrame back to a Snowpark DataFrame
    edited_dataset = session.create_dataframe(editable_df)

    # The original dataset (you should avoid using collect() unless necessary)
    og_dataset = session.table("smoothies.public.orders")

    try:
        # Perform the merge operation correctly
        og_dataset.merge(
            edited_dataset,
            on=(og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID']),
            when_matched=when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})
        )
        st.success('Order(s) Updated', icon='👍')
    except Exception as e:
        st.write(f'Something went wrong: {e}')
else:
    st.success('There are no pending orders right now', icon="👍")
