############################
# Import necessary libraries
import altair as alt
import plotly.express as px
import pandas as pd

###########################
# Heat map method

def make_heatmap(input_df,input_y,input_x,input_color,input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            # O means ordinal or categorical variables that are ordered
            y = alt.Y(f'{input_y}:O',
                    axis = alt.Axis(title = "Year", 
                                    titleFontSize = 18, titlePadding=15,
                                    titleFontWeight=900, labelAngle=0)),
            x = alt.X(f'{input_x}:O',
                    axis = alt.Axis(title = "", titleFontSize=18,
                                    titlePadding=15, titleFontWeight= 900)),
            #Q means quantitave
            color = alt.Color(f'max({input_color}):Q',
                                legend=None,
                                scale=alt.Scale(scheme=input_color_theme)),  
            #color of the markers borders 
            stroke=alt.value('black'), 
            strokeWidth=alt.value(0.25),
        ).properties(width = 900
        ).configure_axis(labelFontSize=12,titleFontSize=12)
    # heaight = 300

    return heatmap

#################################
# Choropleth Map method
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column,
                               locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, input_df[input_column].max()),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

#######################################
#donut chart for percent of states + territories with mass migration
#mass migraton is defined as > 50,000

#calculate the population difference between a given year and its previous year
#returns a data frame
def calculate_population_difference(input_df, input_year):
  df_selected_year = input_df[input_df['Year'] == input_year].reset_index()
  df_previous_year = input_df[input_df['Year'] == input_year - 1].reset_index()
  #take difference in populations and add it to the data frame
  df_selected_year['Population_difference'] = df_selected_year.Population.sub(df_previous_year.Population, fill_value=0)
  return df_selected_year.sort_values(by="Population_difference", ascending=False)

#The donut chart will then be created from the population difference
def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    if input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    if input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    if input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
    
    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100-input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })

    plot = alt.Chart(source).mark_arc(innerRadius = 45, cornerRadius=25).encode(
        theta = "% value",
        color = alt.Color("Topic:N",
                          scale = alt.Scale(domain = [input_text,''],
                                            range = chart_color),
                          legend = None)
    ).properties(width=130,height = 130)

    text = plot.mark_text(align = 'center',color="#29b5e8",
                           font="Lato", fontSize=32,
                           fontWeight=700, fontStyle="italic").encode(
                                            text=alt.value(f'{input_response} %'))
    
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode( 
            theta="% value",
            color= alt.Color("Topic:N",
                            scale=alt.Scale(
                                domain=[input_text, ''],
                                range=chart_color),
                            legend=None),
             ).properties(width=130, height=130)
    
    return plot_bg + plot + text

##################################################
#population text formating

def format_number(num):
    if num > 10e6: #greater than a million
        if not num % 10e6: #if it is divisible by a million
            return f'{num // 10e6} M'
        return f'{round(num /10e6,1)} M'
    return f'{num // 1000} K'


   