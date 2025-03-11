from dash import Dash, dcc, html, Input, Output, State, ctx
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import seaborn as sns
import numpy as np
import os
import requests
import pandas as pd
from matplotlib.colors import Normalize
import utils
import overtopping_graphs_component as ogc
from datetime import datetime, timedelta

utils.loadConfigFile()

# Create the app
DAWLISH_API_ENDPOINT = os.environ.get('DAWLISH_API_ENDPOINT')
PENZANCE_API_ENDPOINT = os.environ.get('PENZANCE_API_ENDPOINT')
dawlish_lat_seawall = os.environ.get('DAWLISH_LAT_SEAWALL')
dawlish_lon_seawall = os.environ.get('DAWLISH_LON_SEAWALL')
penzance_lat_seawall = os.environ.get('PENZANCE_LAT_SEAWALL')
penzance_lon_seawall = os.environ.get('PENZANCE_LON_SEAWALL')

PERCENTAGE_MIN_VAL_SLIDER = -100
PERCENTAGE_MAX_VAL_SLIDER = 100
PERCENTAGE_DEFAULT_VALUE = 0
DEGREE_MIN_VAL_SLIDER = -180
DEGREE_MAX_VAL_SLIDER = 180
DEGREE_DEFAULT_VALUE = 0
PERCENTAGE_CHAR = '%'
DEGREE_CHAR = '°'

DASHBOARD_NAME = 'SPLASH'
DASHBOARD_BRIEF_DESCRIPTION = 'DIGITAL APPROACHES TO PREDICT WAVE OVERTOPPING HAZARDS'
DASHBOARD_SUBTITLE = 'Advancing current understanding on wave-related coastal hazards'
DASHBOARD_FULL_DESC_P1 = 'With sea level rise accelerating and weather extremes becoming increasingly stronger, tools to help climate adaptation of coastal communities are of paramount importance. SPLASH provides an overtopping tool that will act as forecast model directly helping coastal communities mitigate effects of this coastal hazard, and ultimately, guiding new climate adaptation strategies.'
DASHBOARD_FULL_DESC_P2 = 'The model has been developed at the University of Plymouth Coastal Processes Research Group (CPRG) as part of the SPLASH project. The project was part of the Twinning Capability for the Natural Environment (TWINE) programme, designed to harness the potential of digital twinning technology to transform environmental science. '
DASHBOARD_FULL_DESC_P3 = 'SPLASH digital twin is based on AI models trained using field measurements of wave overtopping. The model is updated once a day and uses Met Office wave and wind data as input, as well as predicted water level. This tool provides overtopping forecast 5 days ahead for Dawlish and Penzance, and allows the user to modify wind and wave input variables to test the sensitivity of wave overtopping.'

external_stylesheets = [dbc.themes.BOOTSTRAP, './assets/css/dashboard.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)


# Get overtopping counts of Dawlish
def get_dawlish_wave_overtopping(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    overtopping_data = response.json()
    seawall_crest_overtopping_df = utils.convert_list_to_dataframe(overtopping_data['seawall_crest_overtopping'])
    railway_line_overtopping_df = utils.convert_list_to_dataframe(overtopping_data['railway_line_overtopping'])
    start_date = utils.format_range_date(seawall_crest_overtopping_df['time'].min())
    end_date = utils.format_range_date(seawall_crest_overtopping_df['time'].max())
    return seawall_crest_overtopping_df, railway_line_overtopping_df, start_date, end_date


def get_penzance_wave_overtopping(api_url):        
    response = requests.get(api_url)
    response.raise_for_status()
    overtopping_data = response.json()
    seawall_crest_overtopping_df = utils.convert_list_to_dataframe(overtopping_data['seawall_crest_overtopping'])
    seawall_crest_sheltered_overtopping_df = utils.convert_list_to_dataframe(overtopping_data['seawall_crest_sheltered_overtopping'])
    start_date = utils.format_range_date(seawall_crest_overtopping_df['time'].min())
    end_date = utils.format_range_date(seawall_crest_overtopping_df['time'].max())

    return seawall_crest_overtopping_df, seawall_crest_sheltered_overtopping_df, start_date, end_date


# def get_significant_wave_height_data():
#     return ddt.plot_significant_wave_height()


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


def get_default_forecast_dates():
    str_start_date = utils.format_date_to_str(datetime.now().date(), '%m-%d-%Y')
    end_date = datetime.now().date() + timedelta(days=5) 
    str_end_date = utils.format_date_to_str(end_date, '%m-%d-%Y')
    return str_start_date, str_end_date



# Render Splash dashboard
def render_dashboard():

    # Search components
    dropdown_panel = ogc.get_dropdown_panel()

    start_date, end_date = get_default_forecast_dates()

    # Forecast range
    forecast_range = ogc.get_date_picker_range(start_date, end_date)

    # Legend
    legend_panel = ogc.get_legend_panel()

    # Wave variables and mean wave direction panels
    wave_variables_panels = ogc.get_wave_variables_panels()

    # Atmospheric variables and wind direction panels
    atmospheric_variables_panels = ogc.get_atmospheric_variables_panels()

    # Buttons panel
    buttons_panel = ogc.get_buttons_panel()

    # App layout
    app.layout = dbc.Container([
        dcc.Store(id='previous-dataframe-1'),
        dcc.Store(id='previous-dataframe-2'),
        dcc.Store(id='current-dataframe-1'),
        dcc.Store(id='current-dataframe-2'),
        dbc.Row([
            html.Div(
            children=[
                html.Div(
                    children=[
                        html.Img(src='./assets/imgs/splash_logo.png', className='splash-logo'),  # Add image here
                        html.Div(
                            children=[
                                html.Div(DASHBOARD_NAME, className='dashboard-title'),
                                html.Div(DASHBOARD_BRIEF_DESCRIPTION, className='dashboard-sub-title')
                            ],
                            className='title-sub-title-container'
                        )
                    ],
                    className='head-container'
                )
            ],
            style={'paddingLeft': '72px'}
        )]),
        dbc.Row(
            html.Div(DASHBOARD_SUBTITLE, className='dashboard-description'),
            style={'paddingLeft': '72px', 'paddingTop': '60px', 'paddingBottom': '5px'}
        ),
        dbc.Row(
            dbc.Col([
                html.P(DASHBOARD_FULL_DESC_P1, className='dashboard-summary'),
                html.P(DASHBOARD_FULL_DESC_P2, className='dashboard-summary'),
                html.P(DASHBOARD_FULL_DESC_P3, className='dashboard-summary'),
            ], md=9, style={'paddingLeft': '0', 'paddingRight': '0'}),
            style={'paddingLeft': '72px', 'paddingRight': '72px'}
        ),
        dbc.Row(
            dbc.Col(
                 html.Hr(id='horizontal-separator', className='horizontal-line'), md=12, style={'paddingLeft': '0', 'paddingRight': '0'}
            ),
            style={'paddingLeft': '72px', 'paddingRight': '72px'}
        ),
        dbc.Row([
                dbc.Col(dropdown_panel, md='9', style={'padding': '0px'}),
                dbc.Col(forecast_range, md='3')
            ], 
            style={'paddingTop': '19px', 'paddingLeft': '72px', 'paddingRight': '72px'}
            ),
        dbc.Row(
            dbc.Col(dbc.Accordion([
                        dbc.AccordionItem(
                            [
                                html.Div('Wave variables', className='wave-variables-panel'),
                                wave_variables_panels,
                                html.Div('Atmospheric variables', className='atmospheric-variables-panel'),
                                atmospheric_variables_panels,
                                buttons_panel
                            ],
                            title='Wave and atmospheric variables',
                            class_name='wave-atmospheric-variables-panel'
                        )
                ], 
                start_collapsed=True), 
                style={'padding': '0px'}
            )
        , style={'paddingTop': '25px', 'paddingLeft': '72px', 'paddingRight': '72px'}),
        legend_panel,
        dbc.Row([
            dbc.Col(dcc.Graph(id='scatter-plot-rig1', style={'border': '1.011px solid #8A8D90'}), md=6, style={'padding': '0px'}),
            dbc.Col(dcc.Graph(id='scatter-plot-rig2', style={'border': '1.011px solid #8A8D90'}), md=6, style={'paddingLeft': '16px', 'paddingRight': '0px'})
        ], style={'paddingTop': '22px', 'paddingLeft': '72px', 'paddingRight': '72px'}),
    ], fluid=True, className='body-container')


render_dashboard()


def get_dataframes_to_save(n_clicks, trigger_id, generated_df_1, generated_df_2, stored_current_df_1, stored_current_df_2):
    if n_clicks is None or n_clicks == 0 or trigger_id is not None and trigger_id != 'submit-button':
        tmp_previous_df_1 = pd.DataFrame()
        tmp_previous_df_2 = pd.DataFrame()
        tmp_current_df_1 = generated_df_1
        tmp_current_df_2 = generated_df_2
    else:
        saved_current_df_1 = pd.DataFrame(stored_current_df_1)
        saved_current_df_2 = pd.DataFrame(stored_current_df_2)
        saved_current_df_1['stage'] = 'forecast'
        saved_current_df_2['stage'] = 'forecast'
        tmp_previous_df_1 = saved_current_df_1
        tmp_previous_df_2 = saved_current_df_2
        tmp_current_df_1 = generated_df_1
        tmp_current_df_2 = generated_df_2
    return tmp_previous_df_1, tmp_previous_df_2, tmp_current_df_1, tmp_current_df_2


# Callback to render overtopping graphs when picking a location or submitting any variable
@app.callback(
    [Output('scatter-plot-rig1', 'figure'),
     Output('scatter-plot-rig2', 'figure'),
     Output('previous-dataframe-1', 'data'),
     Output('previous-dataframe-2', 'data'),
     Output('current-dataframe-1', 'data'),
     Output('current-dataframe-2', 'data'),
     Output('forecast-range', 'start_date'),
     Output('forecast-range', 'end_date'),
    ],
    Input('submit-button', 'n_clicks'),
    Input('dd_site_location', 'value'),
    State('sig-wave-height', 'value'),
    State('freeboard', 'value'),
    State('mean-wave-period', 'value'),
    State('mean-wave-direction', 'value'),
    State('wind-speed', 'value'),
    State('wind-direction', 'value'),
    State('previous-dataframe-1', 'data'),
    State('previous-dataframe-2', 'data'),
    State('current-dataframe-1', 'data'),
    State('current-dataframe-2', 'data'),
)
def submit_slider_values(submit_n_clicks, site_location_val, sig_wave_height_val, freeboard_val, mean_wave_period_val, mean_wave_dir_val, wind_speed_val, wind_dir_val, previous_df_1, previous_df_2, current_df_1, current_df_2):
    trigger_id =  ctx.triggered_id
    if submit_n_clicks is None or submit_n_clicks == 0 or trigger_id is not None and trigger_id != 'submit-button':
        option, start_date = utils.get_dataset_params(site_location_val)
        params = {'start_date': start_date, 'option': option}
    else:
        option, start_date = utils.get_dataset_params(site_location_val)
        params = {'sig_wave_height': sig_wave_height_val, 'freeboard': freeboard_val, 'mean_wave_period': mean_wave_period_val, 'mean_wave_dir': mean_wave_dir_val, 'wind_speed': wind_speed_val, 'wind_direction': wind_dir_val}
        params['start_date'] = start_date
        params['option'] = option

    if utils.find_words_with_suffix(site_location_val, 'Dawlish'):
        api_url = utils.add_query_params(DAWLISH_API_ENDPOINT, params)
        data_dawlish_seawall_crest, data_dawlish_railway_line, forecast_start_date, forecast_end_date = get_dawlish_wave_overtopping(api_url)
        data_dawlish_seawall_crest['stage'] = 'forecast' if submit_n_clicks is None or submit_n_clicks == 0 else 'adjusted_forecast'
        data_dawlish_railway_line['stage'] = 'forecast' if submit_n_clicks is None or submit_n_clicks == 0 else 'adjusted_forecast'
        tmp_previous_df_1, tmp_previous_df_2, tmp_current_df_1, tmp_current_df_2 = get_dataframes_to_save(submit_n_clicks, trigger_id, data_dawlish_seawall_crest, data_dawlish_railway_line, current_df_1, current_df_2)
        joined_dsc = pd.concat([tmp_previous_df_1, tmp_current_df_1], ignore_index=True)
        joined_drl = pd.concat([tmp_previous_df_2, tmp_current_df_2], ignore_index=True)
        fig_dawlish_seawall_crest = ogc.render_dawlish_seawall_crest_graph(joined_dsc)
        fig_dawlish_railway_line = ogc.render_dawlish_railway_line_graph(joined_drl)
    else:
        api_url = utils.add_query_params(PENZANCE_API_ENDPOINT, params)
        data_penzance_seawall_crest, data_penzance_seawall_crest_sheltered, forecast_start_date, forecast_end_date = get_penzance_wave_overtopping(api_url)
        data_penzance_seawall_crest['stage'] = 'forecast' if submit_n_clicks is None or submit_n_clicks == 0 else 'adjusted_forecast'
        data_penzance_seawall_crest_sheltered['stage'] = 'forecast' if submit_n_clicks is None or submit_n_clicks == 0 else 'adjusted_forecast'
        tmp_previous_df_1, tmp_previous_df_2, tmp_current_df_1, tmp_current_df_2 = get_dataframes_to_save(submit_n_clicks, trigger_id, data_penzance_seawall_crest, data_penzance_seawall_crest_sheltered, current_df_1, current_df_2)
        joined_psc = pd.concat([tmp_previous_df_1, tmp_current_df_1], ignore_index=True)
        joined_pscs = pd.concat([tmp_previous_df_2, tmp_current_df_2], ignore_index=True)
        fig_penzance_seawall_crest = ogc.render_penzance_seawall_crest_graph(joined_psc)
        fig_penzance_seawall_crest_sheltered = ogc.render_penzance_seawall_crest_sheltered_graph(joined_pscs)

    
    fig1 = fig_dawlish_seawall_crest if utils.find_words_with_suffix(site_location_val, 'Dawlish') else fig_penzance_seawall_crest
    fig2 = fig_penzance_seawall_crest_sheltered if utils.find_words_with_suffix(site_location_val, 'Penzance') else fig_dawlish_railway_line

    return fig1, fig2, tmp_previous_df_1.to_dict('records'), tmp_previous_df_2.to_dict('records'), tmp_current_df_1.to_dict('records'), tmp_current_df_2.to_dict('records'), forecast_start_date, forecast_end_date


# Callback for significant wave height slider
@app.callback(
    Output('sig-wave-height', 'value'),
    Input('sig-wave-height', 'value'),
    Input('swh-increase-btn', 'n_clicks'),
    Input('swh-decrease-btn', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    Input('wad-reset-button', 'n_clicks'),
    Input('dd_site_location', 'value'),
    State('sig-wave-height', 'step')
)
def update_slider(slider_value, n_clicks_inc, n_clicks_dec, n_clicks_reset, n_clicks_reset_wad, site_location_value, current_step):

    if n_clicks_inc == 0 or n_clicks_dec == 0 or n_clicks_reset == 0 or n_clicks_reset_wad == 0:
        return PERCENTAGE_DEFAULT_VALUE

    trigger_id =  ctx.triggered_id

    if trigger_id == 'swh-increase-btn':
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == 'swh-decrease-btn':
        new_value = slider_value - current_step
        return new_value
    elif trigger_id == 'reset-button' or trigger_id == 'wad-reset-button' or trigger_id == 'dd_site_location':
        return PERCENTAGE_DEFAULT_VALUE
    else:  # Slider moved
        return slider_value  


# Callback for freeboard slider
@app.callback(
    Output('freeboard', 'value'),
    Input('freeboard', 'value'),
    Input('fb-increase-btn', 'n_clicks'),
    Input('fb-decrease-btn', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    Input('wad-reset-button', 'n_clicks'),
    Input('dd_site_location', 'value'),
    State('freeboard', 'step')
)
def update_slider(slider_value, n_clicks_inc, n_clicks_dec, n_clicks_reset, n_clicks_reset_wad, site_location_value, current_step):

    if n_clicks_inc == 0 or n_clicks_dec == 0 or n_clicks_reset == 0 or n_clicks_reset_wad == 0:
        return PERCENTAGE_DEFAULT_VALUE

    trigger_id =  ctx.triggered_id

    if trigger_id == 'fb-increase-btn':
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == 'fb-decrease-btn':
        new_value = slider_value - current_step
        return new_value
    elif trigger_id == 'reset-button' or trigger_id == 'wad-reset-button' or trigger_id == 'dd_site_location':
        return PERCENTAGE_DEFAULT_VALUE
    else:  # Slider moved
        return slider_value      


# Callback for mean wave period slider
@app.callback(
    Output('mean-wave-period', 'value'),
    Input('mean-wave-period', 'value'),
    Input('mwp-increase-btn', 'n_clicks'),
    Input('mwp-decrease-btn', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    Input('wad-reset-button', 'n_clicks'),
    Input('dd_site_location', 'value'),
    State('mean-wave-period', 'step')
)
def update_slider(slider_value, n_clicks_inc, n_clicks_dec, n_clicks_reset, n_clicks_reset_wad, site_location_value, current_step):

    if n_clicks_inc == 0 or n_clicks_dec == 0 or n_clicks_reset == 0 or n_clicks_reset_wad ==0:
        return PERCENTAGE_DEFAULT_VALUE

    trigger_id =  ctx.triggered_id

    if trigger_id == 'mwp-increase-btn':
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == 'mwp-decrease-btn':
        new_value = slider_value - current_step
        return new_value
    elif trigger_id == 'reset-button' or trigger_id == 'wad-reset-button' or trigger_id == 'dd_site_location':
        return PERCENTAGE_DEFAULT_VALUE
    else:  # Slider moved
        return slider_value   


# Callback for mean wave direction slider
@app.callback(
    Output('mean-wave-direction', 'value'),
    Input('mean-wave-direction', 'value'),
    Input('mwd-increase-btn', 'n_clicks'),
    Input('mwd-decrease-btn', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    Input('mwd-reset-button', 'n_clicks'),
    Input('dd_site_location', 'value'),
    State('mean-wave-direction', 'step')
)
def update_slider(slider_value, n_clicks_inc, n_clicks_dec, n_clicks_reset, n_clicks_reset_mwd, site_location_value, current_step):
    
    if n_clicks_inc == 0 or n_clicks_dec == 0 or n_clicks_reset == 0 or n_clicks_reset_mwd == 0:
        return DEGREE_DEFAULT_VALUE

    trigger_id =  ctx.triggered_id
    
    if trigger_id == 'mwd-increase-btn':     
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == 'mwd-decrease-btn':
        new_value = slider_value - current_step
        return new_value
    elif trigger_id == 'reset-button' or trigger_id == 'mwd-reset-button' or trigger_id == 'dd_site_location':
        return DEGREE_DEFAULT_VALUE
    else:  # Slider moved
        return slider_value       


# Callback for wind speed slider
@app.callback(
    Output('wind-speed', 'value'),
    Input('wind-speed', 'value'),
    Input('ws-increase-btn', 'n_clicks'),
    Input('ws-decrease-btn', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    Input('aad-reset-button', 'n_clicks'),
    Input('dd_site_location', 'value'),
    State('wind-speed', 'step')
)
def update_slider(slider_value, n_clicks_inc, n_clicks_dec, n_clicks_reset, n_clicks_reset_aad, site_location_value, current_step):
    
    if n_clicks_inc == 0 or n_clicks_dec == 0 or n_clicks_reset == 0 or n_clicks_reset_aad == 0:
        return PERCENTAGE_DEFAULT_VALUE

    trigger_id =  ctx.triggered_id
    
    if trigger_id == 'ws-increase-btn':
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == 'ws-decrease-btn':
        new_value = slider_value - current_step
        return new_value
    elif trigger_id == 'reset-button' or trigger_id == 'aad-reset-button' or trigger_id == 'dd_site_location':
        return PERCENTAGE_DEFAULT_VALUE
    else:  # Slider moved
        return slider_value     


# Callback for wind direction slider
@app.callback(
    Output('wind-direction', 'value'),
    Input('wind-direction', 'value'),
    Input('wd-increase-btn', 'n_clicks'),
    Input('wd-decrease-btn', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    Input('wd-reset-button', 'n_clicks'),
    Input('dd_site_location', 'value'),
    State('wind-direction', 'step')
)
def update_slider(slider_value, n_clicks_inc, n_clicks_dec, n_clicks_reset, n_clicks_reset_wd, site_location_value, current_step):
    
    if n_clicks_inc == 0 or n_clicks_dec == 0 or n_clicks_reset == 0 or n_clicks_reset_wd == 0:
        return DEGREE_DEFAULT_VALUE

    trigger_id =  ctx.triggered_id
    
    if trigger_id == 'wd-increase-btn':
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == 'wd-decrease-btn':
        new_value = slider_value - current_step
        return new_value
    elif trigger_id == 'reset-button' or trigger_id == 'wd-reset-button' or trigger_id == 'dd_site_location':
        return DEGREE_DEFAULT_VALUE
    else:  # Slider moved
        return slider_value     


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)