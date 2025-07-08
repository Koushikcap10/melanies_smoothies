# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(f" :cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie")
name_on_order=st.text_input("Name on Smoothie: ")
st.write("The name on the smoothie will be: ",name_on_order)

# Get connection and session
cnx=st.connection("snowflake")
session=cnx.session()

# Get fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'),col('SEARCH_ON'))

# Convert to pandas
pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)

# Use the fruit names for the multiselect
ingredients_list=st.multiselect('Choose upto 5 ingredients: ', pd_df['FRUIT_NAME'].tolist(), max_selections=5)

if ingredients_list:
    st.write(ingredients_list)
    st.text(ingredients_list)
    ingredients_string=''
    
    for fruit_chosen in ingredients_list:
        ingredients_string+=fruit_chosen+' '
        
        # Get the search value for the API call
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Use fruityvice API and fix variable name
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+search_on)
        
        if fruityvice_response.status_code == 200:
            fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.error(f"Could not retrieve nutrition information for {fruit_chosen}")
    
    # Fixed INSERT statement - let sequence handle ORDER_UID
    my_insert_stmt = f"""insert into smoothies.public.orders 
                        (ingredients, name_on_order, order_filled, order_ts)
                        values ('{ingredients_string.strip()}', '{name_on_order}', FALSE, CURRENT_TIMESTAMP())"""
    
    st.write(my_insert_stmt)
    
    time_to_insert=st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
