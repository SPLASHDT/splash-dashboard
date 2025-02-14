from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import seaborn as sns
import numpy as np
import os
import requests
import pandas as pd
from datetime import datetime
from matplotlib.colors import Normalize
import utils

utils.loadConfigFile()

# Create the app
SPLASH_DT_Dawlish_models_folder = os.environ.get("SPLASH_DT_DAWLISH_MODELS_FOLDER")
SPLASH_DT_Penzance_models_folder = os.environ.get("SPLASH_DT_PENZANCE_MODELS_FOLDER")
DAWLISH_API_ENDPOINT = os.environ.get("DAWLISH_API_ENDPOINT")
PENZANCE_API_ENDPOINT = os.environ.get("PENZANCE_API_ENDPOINT")
dawlish_lat_seawall = os.environ.get("DAWLISH_LAT_SEAWALL")
dawlish_lon_seawall = os.environ.get("DAWLISH_LON_SEAWALL")
penzance_lat_seawall = os.environ.get("PENZANCE_LAT_SEAWALL")
penzance_lon_seawall = os.environ.get("PENZANCE_LON_SEAWALL")

external_stylesheets = ['./assets/css/dashboard.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Convert lit to dataframe object
def convert_list_to_dataframe(data_list):
    """Converts a list of dictionaries to a Pandas DataFrame with a numerical index.

    Args:
        data_list: A list of dictionaries.

    Returns:
        A Pandas DataFrame with a numerical index starting from 0, or None if the 
        input list is invalid. Handles potential errors in time string parsing.
    """

    if not isinstance(data_list, list):
        return None

    if not data_list:
        return pd.DataFrame(columns=["time", "overtopping_count", "confidence"])

    try:
        df_data = []
        for item in data_list:
            try:
                time_obj = datetime.strptime(item['time'], "%a, %d %b %Y %H:%M:%S GMT")
                time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"Warning: Invalid time format: {item['time']}")
                time_str = None

            df_data.append({
                "time": time_str,
                "overtopping_count": item['overtopping_count'],
                "confidence": item['confidence']
            })

        df = pd.DataFrame(df_data)

        # The key change: Reset the index to a numerical one starting from 0
        df = df.reset_index(drop=True)  # drop=True discards the old index

        return df
    except (KeyError, TypeError) as e:
        print(f"Error converting list to DataFrame: {e}")
        return None


# Get overtopping counts of Dawlish
def get_dawlish_wave_overtopping(start_date, option: str = "dawlish"):
    backend_api = DAWLISH_API_ENDPOINT + '?option='+ option + '&start_date='+ start_date if start_date != "" else DAWLISH_API_ENDPOINT + '?option='+ option
    response = requests.get(backend_api)
    response.raise_for_status()
    overtopping_data = response.json()
    seawall_crest_overtopping_df = convert_list_to_dataframe(overtopping_data["seawall_crest_overtopping"])
    railway_line_overtopping_df = convert_list_to_dataframe(overtopping_data["railway_line_overtopping"])
    return seawall_crest_overtopping_df, railway_line_overtopping_df


def get_penzance_wave_overtopping(option: str = "penzance"):        
    response = requests.get(PENZANCE_API_ENDPOINT+ '?option='+ option)
    response.raise_for_status()
    overtopping_data = response.json()
    seawall_crest_overtopping_df = convert_list_to_dataframe(overtopping_data["seawall_crest_overtopping"])
    seawall_crest_sheltered_overtopping_df = convert_list_to_dataframe(overtopping_data["seawall_crest_sheltered_overtopping"])
    return seawall_crest_overtopping_df, seawall_crest_sheltered_overtopping_df


# def get_significant_wave_height_data():
#     return ddt.plot_significant_wave_height()
    

# Render overtopping plot
def render_overtopping_plot(plot_title, plot_logo, overtopping_data):

    fig_rf1_rf2_tmp = px.scatter(
        overtopping_data,
        x='time',
        y='overtopping_count',
        color_continuous_scale=['aqua', 'skyblue', 'blue'],
        labels={
            'time': 'Time',
            'overtopping_count': 'No. of Overtopping Occurrences (Per 10 Mins)',
            'confidence': 'Confidence Level'
        }
    )

    # Add the image as an annotation
    fig_rf1_rf2_tmp.add_layout_image(
        dict(
            source="./assets/imgs/" + plot_logo,
            xref="paper", yref="paper",
            x=0, y=1,  # Adjust position as needed
            sizex=0.15, sizey=0.15,  # Adjust size as needed
            xanchor="left", yanchor="bottom"
        )
    )

    fig_rf1_rf2_tmp.update_layout(
        title=dict(
            text=plot_title,  # Just the text title
            font=dict(
                family='Helvetica Neue',
                size=44.489,
                color='#3279B7',
                weight=500
            ),
            xref="paper", yref="paper",
            x=0.04, y=1,  # Adjust title position if necessary
            xanchor='left', yanchor='bottom'
        ),
        plot_bgcolor='white',  # Set the plot background color to white
        xaxis=dict(
            showgrid=True,  # Show x-axis gridlines
            gridcolor='#8A8D90',  # Set x-axis gridline color to light gray
            linecolor='#8A8D90'  # Set x-axis line color to gray
        ),
        yaxis=dict(
            showgrid=True,  # Show y-axis gridlines
            gridcolor='#8A8D90',  # Set y-axis gridline color to light gray
            linecolor='#8A8D90'  # Set y-axis line color to gray
        ),
        showlegend=False,
    )

    # Customize the symbols
    fig_rf1_rf2_tmp.update_traces(
        selector=dict(type='scatter', mode='markers'),
        marker=dict(
            line=dict(width=2),
            size=16,
            symbol=[
                'x-thin' if o == 0 else
                'circle-open' if c > 0.80 and o > 0 else
                'circle' if c >= 0.50 and c <= 0.8 and o > 0 else
                'square' if c < 0.50 and o > 0 else
                'circle' 
                for c, o in zip(overtopping_data['confidence'], overtopping_data['overtopping_count'])
            ],
            color=[
                'black' if o == 0 else
                '#FF0004' if c > 0.80 and o > 0 else
                '#2A5485' if c >= 0.50 and c <= 0.8 and o > 0 else
                '#AAD3E3' if c < 0.50 and o > 0 else
                '#AAD3E3' 
                for c, o in zip(overtopping_data['confidence'], overtopping_data['overtopping_count'])
            ],
            line_color=[
                'black' if o == 0 else
                'red' if c > 0.80 and o > 0 else
                '#2A5485' if c >= 0.50 and c <= 0.80 and o > 0 else
                '#AAD3E3' if c < 0.50 and o > 0 else
                '#AAD3E3' 
                for c, o in zip(overtopping_data['confidence'], overtopping_data['overtopping_count']) # Corrected order
            ]
        )
    )

    fig_rf1_rf2_tmp.add_hline(y=6, line_dash='dash', line_color='#8A8D90', annotation_text='25% IQR (6)')
    fig_rf1_rf2_tmp.add_hline(y=54, line_dash='dash', line_color='#8A8D90', annotation_text='75% IQR (54)')

    return fig_rf1_rf2_tmp


# Render countour significant wave height
def render_contour_wave_height(longitudes, latitudes, z_data, U, V, lon_grid, lat_grid, skip,
                       current_block_Met_office_final, time_label, output_folder, zmin=0):
    """
    Generates a Plotly plot of wave height, direction, and location markers.

    Args:
        longitudes (array-like): Longitude values.
        latitudes (array-like): Latitude values.
        z_data (array-like): Wave height data.
        U (array-like): U component of wave direction.
        V (array-like): V component of wave direction.
        lon_grid (array-like): Grid of longitudes for quiver plot.
        lat_grid (array-like): Grid of latitudes for quiver plot.
        skip (int): Sampling interval for quiver plot.
        current_block_Met_office_final (str): Block identifier.
        time_label (str): Time label for the plot.
        output_folder (str): Directory to save the plot.
    """

    mako_cmap = sns.color_palette("mako", as_cmap=True)
    norm = Normalize(vmin=zmin, vmax=11)  # Use zmin in normalization

    # Generate colorscale from zmin (Corrected)
    colorscale = [[(i - zmin) / (11 - zmin), f'rgb({int(r*255)},{int(g*255)},{int(b*255)})'] 
                  for i in range(zmin, 12) 
                  for r, g, b, _ in [mako_cmap((i - zmin) / (11 - zmin))]] 


    # Create contour plot
    contour = go.Contour(
        z=z_data,
        x=latitudes,
        y=longitudes,
        colorscale='Picnic',
        contours=dict(
            start=0,
            end=11,
            size=0.5,
        ),
        colorbar=dict(
            title='Significant Wave Height (Hs) [m]',
            tickvals=np.linspace(0, 11, 12)
        )
    )

    # Create quiver plot
    quiver = go.Cone(
        x=lon_grid[skip],
        y=lat_grid[skip],
        u=U[skip],
        v=V[skip],
        anchor="tail",
        colorscale=[[0, 'white'], [1, 'white']],  # Set color to white
        showscale=False,
        sizeref=20,  # Adjust arrow size here
    )

    # Create scatter plot for markers
    # Create scatter plot for Dawlish marker
    scatter_dawlish = go.Scatter(
        x=[dawlish_lon_seawall],
        y=[dawlish_lat_seawall],
        mode='markers',
        marker=dict(
            color='red',
            size=10,
            symbol='circle'
        ),
        name='Dawlish',  # Separate name for Dawlish
        text=['Dawlish'],
        hoverinfo='text'
    )

    # Create scatter plot for Penzance marker
    scatter_penzance = go.Scatter(
        x=[penzance_lon_seawall],
        y=[penzance_lat_seawall],
        mode='markers',
        marker=dict(
            color='red',
            size=10,
            symbol='square'
        ),
        name='Penzance',  # Separate name for Penzance
        text=['Penzance'],
        hoverinfo='text'
    )

    # Create layout
    layout = go.Layout(
        title=f'Significant Wave Height (Hs)<br>Block: {current_block_Met_office_final}, Time: {time_label}',
        xaxis=dict(title='Longitude'),
        yaxis=dict(title='Latitude'),
        showlegend=True,  # Show the legend
        legend=dict(
            x=0,  # Set x-coordinate to 0 (left side)
            y=1,  # Set y-coordinate to 1 (top)
            xanchor='left',  # Anchor legend to the left
            yanchor='top'   # Anchor legend to the top
        )
    )

    # Create figure
    fig = go.Figure(data=[contour, quiver, scatter_dawlish, scatter_penzance], layout=layout)

    # Save the plot
    output_file = os.path.join(output_folder, f'hs_wave_direction_plot_block_{current_block_Met_office_final}_time_{time_label.replace(":", "_")}.html')
    fig.write_html(output_file)
    print(f"Saved plot for time {time_label} to {output_file}")


# Render all plots and graphs
def render_all_graphs():
    # Plot for RF1 & RF2 - Dawlish Seawall Crest
    fig_dawlish_seawall_crest = render_overtopping_plot('Dawlish Seawall Crest', 'dawlish_seawall_crest.png', data_dawlish_seawall_crest)
    # Plot for RF3 & RF4 - Dawlish Railway Line
    fig_dawlish_railway_line = render_overtopping_plot('Dawlish Railway Line', 'dawlish_railway_line.png', data_dawlish_railway_line)
    # Plot for RF1 & RF2 - Penzance Seawall Crest
    fig_penzance_seawall_crest = render_overtopping_plot('Penzance Seawall Crest', 'dawlish_seawall_crest.png', data_penzance_seawall_crest)
    # # Plot for RF2 & RF4 - Penzance, Seawall Crest (sheltered)
    fig_penzance_seawall_crest_sheltered = render_overtopping_plot('Penzance, Seawall Crest (sheltered) ', 'dawlish_seawall_crest.png', data_penzance_seawall_crest_sheltered)
    
    # render_contour_wave_height(longitudes, latitudes, z_data, U, V, lon_grid, lat_grid, skip, current_block_Met_office_final, time_label, output_folder, 0)
    
    return fig_dawlish_seawall_crest, fig_dawlish_railway_line, fig_penzance_seawall_crest, fig_penzance_seawall_crest_sheltered

def render_dawlish_seawall_crest_graph(data_dawlish_seawall_crest):
    # Plot for RF1 & RF2 - Dawlish Seawall Crest
    fig_dawlish_seawall_crest = render_overtopping_plot('Dawlish Seawall Crest', 'dawlish_seawall_crest.png', data_dawlish_seawall_crest)

    return fig_dawlish_seawall_crest

def render_dawlish_railway_line_graph(data_dawlish_railway_line):
    # Plot for RF3 & RF4 - Dawlish Railway Line
    fig_dawlish_railway_line = render_overtopping_plot('Dawlish Railway Line', 'dawlish_railway_line.png', data_dawlish_railway_line)

    return fig_dawlish_railway_line


def render_penzance_seawall_crest_graph(data_penzance_seawall_crest):
    # Plot for RF1 & RF2 - Penzance Seawall Crest
    fig_penzance_seawall_crest = render_overtopping_plot('Penzance Seawall Crest', 'dawlish_seawall_crest.png', data_penzance_seawall_crest)

    return fig_penzance_seawall_crest

def render_penzance_seawall_crest_sheltered_graph(data_penzance_seawall_crest_sheltered):
    # # Plot for RF2 & RF4 - Penzance, Seawall Crest (sheltered)
    fig_penzance_seawall_crest_sheltered = render_overtopping_plot('Penzance, Seawall Crest (sheltered) ', 'dawlish_seawall_crest.png', data_penzance_seawall_crest_sheltered)

    return fig_penzance_seawall_crest_sheltered


# Render Splash dashboard
def render_dashboard():
    # Search components
    dropdown_container = html.Div([
        "Site location",
        dcc.Dropdown(
        id='dd_site_location',
        options=['Dawlish', 'Penzance', 'Dawlish Storm Bert - overtopping', 'Penzance Storm Bert - overtopping', 'Dawlish - no overtopping', 'Penzance - no overtopping'],
        value='Dawlish',
        clearable=False,
    )
    ])

    # App layout
    app.layout = dbc.Container([
        dbc.Row([
            html.Div(
            children=[
                html.Div(
                    children=[
                        html.Img(src="./assets/imgs/splash_logo.png", className="splash-logo"),  # Add image here
                        html.Div(
                            children=[
                                html.Div("SPLASH", className="dashboard-title"),
                                html.Div("DIGITAL APPROACHES TO PREDICT WAVE OVERTOPPING HAZARDS", className="dashboard-sub-title")
                            ],
                            className="title-sub-title-container"
                        )
                    ],
                    className="head-container"
                )
            ],
            style={'paddingLeft': '72px'}
        )]),
        dbc.Row(
            html.Div("Advancing current understanding on wave-related coastal hazards", className="dashboard-description"),
            style={'paddingLeft': '72px'}
        ),
        dbc.Row(
            html.Div("With sea level rise accelerating and weather extremes becoming increasingly stronger, tools to help climate adaptation of coastal communities are of paramount importance. SPLASH provides an overtopping tool that will act as forecast model directly helping coastal communities mitigate effects of this coastal hazard, and ultimately, guiding new climate adaptation strategies.", className="dashboard-summary"),
            style={'paddingLeft': '72px'}
        ),
        dbc.Row([
            dbc.Col([
                dropdown_container,
            ],
            width="3",
            className="site-dropdown",
            )
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    children=[
                        html.Div("Key", style={'color': 'black', 'fontSize': '14.40px', 'fontFamily': 'Helvetica Neue', 'fontWeight': '700', 'lineHeight': '21.60px', 'marginTop': '5px', 'width': '65px'}),
                        html.Div(
                            children=[
                                html.Div(style={'width': '26px', 'height': '26px', 'borderRadius': '9999px', 'border': '2px #FF0004 solid', 'marginLeft': '18px', 'marginTop': '3px'}),
                                html.Div("High confidence > 80%", style={'color': 'black', 'fontSize': '12px', 'fontFamily': 'Helvetica Neue', 'fontWeight': '400', 'lineHeight': '16.80px', 'marginLeft': '11px', 'width': '88px'})
                            ],
                            style={'display': 'flex', 'marginLeft': '37px'}
                        ),
                        html.Div(
                            children=[
                                html.Div(style={'width': '26px', 'height': '26px', 'background': '#2A5485', 'borderRadius': '9999px', 'marginTop': '3px'}),
                                html.Div("Medium confidence 50-80%", style={'color': 'black', 'fontSize': '12px', 'fontFamily': 'Helvetica Neue', 'fontWeight': '400', 'lineHeight': '16.80px', 'marginLeft': '11px', 'width': '107px'}),
                            ],
                            style={'display': 'flex', 'marginLeft': '37px'}
                        ), 
                        html.Div(
                            children=[
                                html.Div(style={'width': '24px', 'height': '24px', 'background': '#AAD3E3', 'marginTop': '4px'}),
                                html.Div("Low confidence < 50%", style={'color': 'black', 'fontSize': '12px', 'fontFamily': 'Helvetica Neue', 'fontWeight': '400', 'lineHeight': '16.80px', 'marginLeft': '11px', 'width': '86px'})
                            ],
                            style={'display': 'flex', 'marginLeft': '37px'}
                        ),
                        html.Div(
                            children=[
                                html.Img(src='./assets/imgs/no_overtopping_marker.png', style={'width': '20px', 'height': '20px', 'marginTop': '6px'}),  # Add the image here   
                                html.Div("No overtopping", style={'color': 'black', 'fontSize': '12px', 'fontFamily': 'Helvetica Neue', 'fontWeight': '400', 'lineHeight': '16.80px', 'marginTop': '8px', 'marginLeft': '11px', 'width': '84px'})
                                ],
                            style={'display': 'flex', 'marginLeft': '37px'}
                        ),
                        html.Div(
                            children=[
                                html.Div(style={'width': '46px', 'height': '0px', 'border': '1px #8A8D90 dashed', 'marginTop': '16px'}),
                                html.Div("Interquartile range (25th and 75th)", style={'color': 'black', 'fontSize': '12px', 'fontFamily': 'Helvetica Neue', 'fontWeight': '400', 'lineHeight': '16.80px', 'marginLeft': '11px', 'width': '101px'}),
                            ],
                            style={'display': 'flex', 'marginLeft': '37px'}
                        ),

                    ],
                    className="dawlish-legend"
                )
            ], width=10, style={"padding": "22px 72px"})
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="scatter-plot-rig1")
            ], width=12, style={'border': '1.011px solid #8A8D90'})    
        ], style={'padding': '0px 72px'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="scatter-plot-rig2")
            ], width=12, style={'border': '1.011px solid #8A8D90'})    
        ], style={'padding': '24px 72px'})
    ], fluid=True, className='body-container')

render_dashboard()


# Define event for site location dropdown
@app.callback(
    Output("scatter-plot-rig1", "figure"), 
    Input("dd_site_location", "value"))
def display_graph(site_location):
    if site_location == "Dawlish":
        option = "dawlish"
        start_date = ""
    elif utils.find_words_with_suffix(site_location, "Storm Bert"):
        option = "storm_bert"
        start_date = "21-11-2024"
    elif utils.find_words_with_suffix(site_location, "no overtopping"):
        option = "no_overtopping"
        start_date = "10-12-2024"
    else: 
        option = "penzance"
        start_date = ""

    if utils.find_words_with_suffix(site_location, "Dawlish"):
        data_dawlish_seawall_crest, data_dawlish_railway_line = get_dawlish_wave_overtopping(start_date, option)
        fig_dawlish_seawall_crest = render_dawlish_seawall_crest_graph(data_dawlish_seawall_crest)
    else:
        data_penzance_seawall_crest, data_penzance_seawall_crest_sheltered = get_penzance_wave_overtopping(option)
        fig_penzance_seawall_crest = render_penzance_seawall_crest_graph(data_penzance_seawall_crest)

    fig = fig_dawlish_seawall_crest if utils.find_words_with_suffix(site_location, "Dawlish") else fig_penzance_seawall_crest
    return fig


@app.callback(
    Output("scatter-plot-rig2", "figure"), 
    Input("dd_site_location", "value"))
def display_graph(site_location):
    if site_location == "Penzance":
        option = "penzance"
        start_date = ""
    elif utils.find_words_with_suffix(site_location, "Storm Bert"):
        option = "storm_bert"
        start_date = "21-11-2024"
    elif utils.find_words_with_suffix(site_location, "no overtopping"):
        option = "no_overtopping"
        start_date = "10-12-2024"
    else: 
        option = "dawlish"
        start_date = ""

    if utils.find_words_with_suffix(site_location, "Dawlish"):
        data_dawlish_seawall_crest, data_dawlish_railway_line = get_dawlish_wave_overtopping(start_date, option)
        fig_dawlish_railway_line = render_dawlish_railway_line_graph(data_dawlish_railway_line)
    else:
        data_penzance_seawall_crest, data_penzance_seawall_crest_sheltered = get_penzance_wave_overtopping(option)
        fig_penzance_seawall_crest_sheltered = render_penzance_seawall_crest_sheltered_graph(data_penzance_seawall_crest_sheltered)

    fig = fig_penzance_seawall_crest_sheltered if utils.find_words_with_suffix(site_location, "Penzance") else fig_dawlish_railway_line
    return fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)