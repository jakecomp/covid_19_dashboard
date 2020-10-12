import pandas as pd
pd.options.plotting.backend = 'plotly'
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output
import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'firefox'
import json
import numpy as np

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CYBORG])

# Limited data set, doesnt provide active/recovered/hospitalized cases by HA
input_file = pd.read_csv('http://www.bccdc.ca/Health-Info-Site/Documents/BCCDC_COVID19_Dashboard_Case_Details.csv')

input_file = input_file.rename(columns={"Sex":"Daily_Cases"})

ha_total_cases = input_file.groupby('HA').count()["Daily_Cases"]

ha_dict = {}
bc_health_map = json.load(open('B.C._Health_Authority_Boundaries__with_Provincial_Health_Services_Boundary_.geojson','r'))

for feature in bc_health_map['features']:
    feature['id'] = feature['properties']['HA_ID']
    ha_dict[feature['properties']['HA_Name']] = feature['id']

ha_total_cases = ha_total_cases.to_frame('Daily_Cases')

ha_total_cases = ha_total_cases.reset_index()

ha_total_cases = ha_total_cases[ha_total_cases.HA != 'Out of Canada']

ha_total_cases['ha_id'] = ha_total_cases['HA'].apply(lambda x:ha_dict[x])
ha_total_cases['covid_density_scale'] = np.log(ha_total_cases['Daily_Cases'])

fig = px.choropleth_mapbox(ha_total_cases,
                           locations = 'ha_id',
                           geojson = bc_health_map,
                           color = 'covid_density_scale',
                           hover_name = 'HA',
                           hover_data = ['Daily_Cases'],
                           mapbox_style = 'carto-darkmatter',
                           center = {'lat':52.5,'lon':-128},
                           zoom = 4,
                           opacity = 0.6)

fig.update_layout(autosize = True,width = 700,height=500,paper_bgcolor = 'black')

Cases_by_date = input_file.groupby('Reported_Date')['Daily_Cases'].count()

fig2 = Cases_by_date.plot.bar(title = 'Reported Cases')

app.layout = html.Div([

    dbc.Row(dbc.Col(html.H1("Jakob's BC Covid-19 Dashboard"),
                    width={'size':'auto','offset':2}),),

    dbc.Row(dbc.Col(html.Br())),

    dbc.Row(
        [
            dbc.Col(dcc.Graph(id = 'bc_heat_map',figure = fig),
                width={'size':5,'offset':0,'order':11}),

            dbc.Col(dcc.Graph(id = 'total_cases',figure = fig2),
                width={'size':7,'offset':0,'order':'first'})
        ]
    )

    #html.H1("Jakob's BC Covid-19 Dashbaord",style={'text-align':'center'}),

    #html.Br(),


    #dcc.Graph(id='bc_heat_map',figure = fig),
    #dcc.Graph(id='total_cases',figure = fig2)
    #dcc.Graph(id='total_cases',figure = fig2)

])



if __name__ == '__main__':
    app.run_server(debug=True)
