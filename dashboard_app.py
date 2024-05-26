## Install necessary libraries
import streamlit as st
import pandas as pd
import altair as alt #Data vizualization library
import plotly.express as px #High-level API for creating figures
from dashboard_methods import *

#######################
## Setup configurations
st.set_page_config(
    page_title = "US Population Dashboard",
    page_icon='👪',
    layout = "wide",
    initial_sidebar_state= 'expanded'
)

alt.themes.enable("dark")

##########################
##Load data
df_reshaped = pd.read_csv('data/US_population_preprocessed.csv')

################################
#Add sidebar

#st.side bar is a context manager for the
with st.sidebar:
    st.title('👪US Population Dashboard')

    #get the unique year values in descending order
    year_list = list(df_reshaped.Year.unique())[::-1]
    
    #add a year less than 2010
    year_list.append(year_list[-1]-1)

    #years drop drown list and filtering of dataframe info
    selected_year = st.selectbox('Select a year', year_list,
                                  index = len(year_list)-4)
    df_selected_year = df_reshaped[df_reshaped.Year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by = "Population", ascending = False)

    #Color theme drop down list
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 
                        'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    color_theme = st.selectbox("Select color theme", color_theme_list)
    
    population_change = st.slider('Select the level of annual population change (in thoudsands)',
              min_value = 25.0, max_value = 100.0, value = 50.0, step = 1.0)
    population_change = population_change*1000
##########################
# App Layout

# 3 columns with the given ratios and "medium spacing"
col = st.columns((1.5,4.5,2), gap = 'medium')

#column 1
with col[0]:
    #Heading 3
    st.markdown('### Gains/Losses')

    #using custom dashmethods library calculate the population difference for selected year
    df_population_difference_sorted = calculate_population_difference(df_reshaped,selected_year)

    # this accounts for dates outside the scope of the data set
    if selected_year >  year_list[-1]:
        # details of state with greatest increase (or least decrease)
        first_state_name = df_population_difference_sorted.State.iloc[0]
        first_state_population = format_number(df_population_difference_sorted.Population.iloc[0])
        first_state_delta = format_number(df_population_difference_sorted.Population_difference.iloc[0])
    else:
        first_state_name = '-'
        first_state_population = '-'
        first_state_delta = ''
    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    if selected_year > year_list[-1]:
        # details of state with largest decrease (or least increase)
        last_state_name = df_population_difference_sorted.State.iloc[-1]
        last_state_population = format_number(df_population_difference_sorted.Population.iloc[-1])   
        last_state_delta = format_number(df_population_difference_sorted.Population_difference.iloc[-1])   
    else:
        last_state_name = '-'
        last_state_population = '-'
        last_state_delta = ''
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)
    
    # the states with population significant
    st.markdown('#### States Migration')

    
    if selected_year >  year_list[-1]:
        # filter states which had a significant population increase
        df_greater_75k = df_population_difference_sorted[df_population_difference_sorted.Population_difference > population_change]
        # filter states which had a significant population decrease
        df_less_75k = df_population_difference_sorted[df_population_difference_sorted.Population_difference < - population_change]

        # percent of states with significant population increase
        positive_state_migration = round((len(df_greater_75k)/len(df_population_difference_sorted))*100)
        # percent of states with significant population decrease
        negative_state_migration = round((len(df_less_75k)/len(df_population_difference_sorted))*100)

        #generate donut charts
        donut_chart_greater = make_donut(positive_state_migration,'Population growth','green')
        donut_chart_lesser = make_donut(negative_state_migration, 'Population shrinkage', 'red' )

    else:
        positve_state_migration = 0
        negative_state_migration = 0
        donut_chart_greater = make_donut(positve_state_migration, 'Population growth', 'orange')
        donut_chart_lesser = make_donut(negative_state_migration, 'Population shrinkage', 'orange')
    
    #create columns inside column one
    migration_columns = st.columns((0.2,1,0.2))
    with migration_columns[1]:
        st.write("Growth")
        st.altair_chart(donut_chart_greater)
        st.write("Shrinkage")
        st.altair_chart(donut_chart_lesser)

#Heatmap and choropleth
with col[1]:
    st.markdown('#### Total Population')
    
    #this will be for a specific year
    choropleth = make_choropleth(df_selected_year, 'State Code', 'Population', color_theme)
    st.plotly_chart(choropleth, use_container_width=True)

    #this will be for all years
    heatmap = make_heatmap(df_reshaped,'Year','State','Population',color_theme)
    st.altair_chart(heatmap, use_container_width=True)

#third column shows the top states and an About section
with col[2]:
    st.markdown('#### Top States')
    if selected_year > year_list[-1]:
        st.dataframe(df_selected_year_sorted,
                    column_order = ("State","Population"),
                    hide_index = True,
                    width = None,
                    column_config = {
                        "State": st.column_config.TextColumn("States"),
                        "Population": st.column_config.ProgressColumn(
                            "Population", format = "%f",
                            min_value = 0,
                            max_value = df_selected_year_sorted.Population.max()
                        )}
                    )
    else:
        st.dataframe(df_selected_year_sorted,
                    column_order = ("State","Population"),
                    hide_index = True,
                    width = None,
                    column_config = {
                        "State": st.column_config.TextColumn("States"),
                        "Population": st.column_config.ProgressColumn(
                            "Population", format = "%f",
                            min_value = 0,
                            max_value = 0
                        )}
                    )
    
    with st.expander('About', expanded = True):
        st.write('''
            - Data: [U.S. Census Bureau](<https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html>).
            - :orange[**Gains/Losses**]: states with high growth/ shrinkage migration for selected year
            - :orange[**States Migration**]: percentage of states with annual growth/ shrinkage migration > {population_change}]
            - Thanks to the [streamlit blog](<https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/>) for the tutorial!
                 ''')