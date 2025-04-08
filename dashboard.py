from dash import Dash, dcc, html, Input, Output, State, ctx, DiskcacheManager
import dash_bootstrap_components as dbc
import os
import pandas as pd
import utils
import overtopping_graphs_components as ogc
import feature_components as fc
import core_components as cc
from datetime import datetime, timedelta
import diskcache
import multiprocessing
import aiohttp
import asyncio

utils.loadConfigFile()

DAWLISH_API_ROOT_ENDPOINT = os.environ.get("DAWLISH_API_ROOT_ENDPOINT")
PENZANCE_API_ROOT_ENDPOINT = os.environ.get("PENZANCE_API_ROOT_ENDPOINT")
dawlish_lat_seawall = os.environ.get("DAWLISH_LAT_SEAWALL")
dawlish_lon_seawall = os.environ.get("DAWLISH_LON_SEAWALL")
penzance_lat_seawall = os.environ.get("PENZANCE_LAT_SEAWALL")
penzance_lon_seawall = os.environ.get("PENZANCE_LON_SEAWALL")
DEBUG = eval(os.environ.get("DEBUG").capitalize()) #DEBUG must by True or False with first letter in caps and rest in lower case

PERCENTAGE_MIN_VAL_SLIDER = -100
PERCENTAGE_MAX_VAL_SLIDER = 100
PERCENTAGE_DEFAULT_VALUE = 0
DEGREE_MIN_VAL_SLIDER = -180
DEGREE_MAX_VAL_SLIDER = 180
DEGREE_DEFAULT_VALUE = 0
PERCENTAGE_CHAR = "%"
DEGREE_CHAR = "°"

DASHBOARD_NAME = "SPLASH"
DASHBOARD_BRIEF_DESCRIPTION = "DIGITAL APPROACHES TO PREDICT WAVE OVERTOPPING HAZARDS"
CPRG_LINK = "https://www.plymouth.ac.uk/research/coastal-processes"
WIREWALL_LINK = "https://coastalmonitoring.org/ccoresources/wirewall/"
AI_MODELS_LINK = "https://www.sciencedirect.com/science/article/pii/S1463500325000137"
NOC_LINK = "https://noc.ac.uk/"
DASHBOARD_SUBTITLE = "Advancing current understanding on wave-related coastal hazards"
DASHBOARD_FULL_DESC_P1 = "With sea level rise accelerating and weather extremes becoming increasingly stronger, tools to help climate adaptation of coastal communities are of paramount importance. SPLASH provides an overtopping tool that will act as forecast model directly helping to mitigate effects of this coastal hazard, and ultimately, guiding new climate adaptation strategies."
DASHBOARD_FULL_DESC_P2_1 = "The model has been developed at the University of Plymouth Coastal Processes Research Group ("
DASHBOARD_FULL_DESC_P2_2 = ") with the support of the National Oceanography Centre ("
DASHBOARD_FULL_DESC_P2_3 = ") as part of the SPLASH project. The project was part of the Twinning Capability for the Natural Environment (TWINE) programme, designed to harness the potential of digital twinning technology to transform environmental science. "
DASHBOARD_FULL_DESC_P3_1 = "SPLASH digital twin is a demonstrator based on "
DASHBOARD_FULL_DESC_P3_2 = " trained "
DASHBOARD_FULL_DESC_P3_3 = ". The model is updated once a day and uses Met Office wave and wind data as input, as well as predicted water level. This tool provides overtopping forecast 5 days ahead for Dawlish and Penzance, and allows the user to modify wind and wave input variables to test the sensitivity of wave overtopping."


multiprocessing.set_start_method("forkserver")

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)


external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,100..900;1,100..900&family=Viga&display=swap",
    "./assets/css/dashboard.css",
]
app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    background_callback_manager=background_callback_manager,
)


async def fetch_data(api_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                response.raise_for_status()
                data = await response.json()
                return data
    except aiohttp.ClientError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Unexpected Error: {e}"


def get_dawlish_wave_overtopping(api_url):
    """Get overtopping counts of Dawlish

    Args:
        api_url (string): Query url to send a request to backend API

    Returns:
        Tuple: Forecast overtopping data of seawall crest and railway line, forecast start date and end date
    """

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    overtopping_data = loop.run_until_complete(fetch_data(api_url))
    loop.close()

    seawall_crest_overtopping_df = utils.convert_overtopping_data_to_df(
        overtopping_data["seawall_crest_overtopping"]
    )
    railway_line_overtopping_df = utils.convert_overtopping_data_to_df(
        overtopping_data["railway_line_overtopping"]
    )
    start_date = utils.format_range_date(seawall_crest_overtopping_df["time"].min())
    end_date = utils.format_range_date(seawall_crest_overtopping_df["time"].max())
    return (
        seawall_crest_overtopping_df,
        railway_line_overtopping_df,
        start_date,
        end_date,
    )


def get_penzance_wave_overtopping(api_url):
    """Get overtopping counts of Penzance

    Args:
        api_url (string): Query url to send a request to backend API

    Returns:
        Tuple: Forecast overtopping data of seawall crest and seawall crest sheltered, forecast start date and end date
    """

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    overtopping_data = loop.run_until_complete(fetch_data(api_url))
    loop.close()
    seawall_crest_overtopping_df = utils.convert_overtopping_data_to_df(
        overtopping_data["seawall_crest_overtopping"]
    )
    seawall_crest_sheltered_overtopping_df = utils.convert_overtopping_data_to_df(
        overtopping_data["seawall_crest_sheltered_overtopping"]
    )
    start_date = utils.format_range_date(seawall_crest_overtopping_df["time"].min())
    end_date = utils.format_range_date(seawall_crest_overtopping_df["time"].max())

    return (
        seawall_crest_overtopping_df,
        seawall_crest_sheltered_overtopping_df,
        start_date,
        end_date,
    )


def get_features_data(
    root_endpoint, resource_name, params, feature_list_name, feature_name
):
    """Get features data and overtopping events times

    Args:
        root_endpoint (string): Root of query url of backend API
        resource_name (string): Wave or atmospheric variable name
        params (string): Wave or atmospheric parameters
        feature_list_name (string): Feature list name in json data
        feature_name (string): Feature name for each record in feature list

    Returns:
        Dataframes: Feature dataframe and forecast overtopping events dataframe
    """

    resource_url = utils.add_resource(root_endpoint, resource_name)
    full_url = utils.add_query_params(resource_url, params)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    feature_overtopping_data = loop.run_until_complete(fetch_data(full_url))
    loop.close()
    feature_df = utils.convert_feature_list_to_df(
        feature_overtopping_data[feature_list_name], feature_name
    )
    overtopping_times_df = utils.convert_feature_list_to_df(
        feature_overtopping_data["overtopping_times"], feature_name
    )
    return feature_df, overtopping_times_df


def get_all_features_data(root_endpoint, params):
    """Get all features data

    Args:
        root_endpoint (string): Base query endpoint to get features data
        params (string): Wave or atmospheric parameters

    Returns:
        Tuple: Features and overtopping events times dataframes
    """

    significant_wave_height_df, swh_overtopping_times_df = get_features_data(
        root_endpoint,
        "significant-wave-height",
        params,
        "significant_wave_heights",
        "significant_wave_height",
    )
    tidal_level_df, tl_overtopping_times_df = get_features_data(
        root_endpoint, "tidal-level", params, "tidal_levels", "tidal_level"
    )
    wind_speed_df, ws_overtopping_times_df = get_features_data(
        root_endpoint, "wind-speed", params, "wind_speeds", "wind_speed"
    )
    return (
        significant_wave_height_df,
        swh_overtopping_times_df,
        tidal_level_df,
        tl_overtopping_times_df,
        wind_speed_df,
        ws_overtopping_times_df,
    )


def get_default_forecast_dates():
    """Get default forecast dates

    Returns:
        Dates: Forecast start date and end date
    """

    str_start_date = utils.format_date_to_str(datetime.now().date(), "%m-%d-%Y")
    end_date = datetime.now().date() + timedelta(days=5)
    str_end_date = utils.format_date_to_str(end_date, "%m-%d-%Y")
    return str_start_date, str_end_date


def render_dashboard():
    """Render Splash dashboard"""

    header_panel = cc.get_header_components()

    dropdown_panel = ogc.get_dropdown_panel()

    start_date, end_date = get_default_forecast_dates()

    forecast_range = ogc.get_date_picker_range(start_date, end_date)

    info_button = ogc.get_date_picker_range_button()

    date_picker_range_popover = ogc.get_date_picker_range_popover()

    full_legend = ogc.get_full_legend(False)

    wave_variables_panels = ogc.get_wave_variables_panels()

    atmospheric_variables_panels = ogc.get_atmospheric_variables_panels()

    buttons_panel = ogc.get_buttons_panel()

    footer_panel = cc.get_footer_components()

    app.layout = dbc.Container(
        [
            dcc.Store(id="previous-dataframe-1"),
            dcc.Store(id="previous-dataframe-2"),
            dcc.Store(id="current-dataframe-1"),
            dcc.Store(id="current-dataframe-2"),
            dcc.Store(id="previous-swh"),
            dcc.Store(id="current-swh"),
            dcc.Store(id="previous-swh-ot"),
            dcc.Store(id="current-swh-ot"),
            dcc.Store(id="previous-tidal-level"),
            dcc.Store(id="current-tidal-level"),
            dcc.Store(id="previous-tidal-level-ot"),
            dcc.Store(id="current-tidal-level-ot"),
            dcc.Store(id="previous-wind-speed"),
            dcc.Store(id="current-wind-speed"),
            dcc.Store(id="previous-wind-speed-ot"),
            dcc.Store(id="current-wind-speed-ot"),
            dbc.Row(
                header_panel, style={"paddingLeft": "72px", "paddingRight": "62px"}
            ),
            dbc.Row(
                html.Div(DASHBOARD_SUBTITLE, className="dashboard-description"),
                style={
                    "paddingLeft": "72px",
                    "paddingTop": "51px",
                    "paddingBottom": "5px",
                },
            ),
            dbc.Row(
                dbc.Col(
                    [
                        html.P(DASHBOARD_FULL_DESC_P1, className="dashboard-summary"),
                        html.P(
                            [
                                DASHBOARD_FULL_DESC_P2_1,
                                html.A("CPRG", href=CPRG_LINK, className="info-link"),
                                DASHBOARD_FULL_DESC_P2_2,
                                html.A("NOC", href=NOC_LINK, className="info-link"),
                                DASHBOARD_FULL_DESC_P2_3,
                            ],
                            className="dashboard-summary",
                        ),
                        html.P(
                            [
                                DASHBOARD_FULL_DESC_P3_1,
                                html.A(
                                    "AI models",
                                    href=AI_MODELS_LINK,
                                    className="info-link",
                                ),
                                DASHBOARD_FULL_DESC_P3_2,
                                html.A(
                                    "using field measurements of wave overtopping",
                                    href=WIREWALL_LINK,
                                    className="info-link",
                                ),
                                DASHBOARD_FULL_DESC_P3_3,
                            ],
                            className="dashboard-summary",
                        ),
                    ],
                    md=9,
                    style={"paddingLeft": "0", "paddingRight": "0"},
                ),
                style={"paddingLeft": "72px", "paddingRight": "72px"},
            ),
            dbc.Row(
                dbc.Col(
                    html.Hr(id="horizontal-separator", className="horizontal-line"),
                    md=12,
                    style={"paddingLeft": "0", "paddingRight": "0"},
                ),
                style={"paddingLeft": "72px", "paddingRight": "72px"},
            ),
            dbc.Row(
                [
                    dbc.Col(dropdown_panel, md="8", style={"padding": "0px"}),
                    dbc.Col(
                        [forecast_range, date_picker_range_popover],
                        md="3",
                        style={"paddingLeft": "80px"},
                    ),
                    dbc.Col(info_button, md=1, style={"paddingTop": "27px"}),
                ],
                style={
                    "paddingTop": "19px",
                    "paddingLeft": "72px",
                    "paddingRight": "72px",
                },
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    html.Div(
                                        "Wave variables",
                                        className="wave-variables-panel",
                                    ),
                                    wave_variables_panels,
                                    html.Div(
                                        "Atmospheric variables",
                                        className="atmospheric-variables-panel",
                                    ),
                                    atmospheric_variables_panels,
                                    buttons_panel,
                                ],
                                title="Wave and atmospheric variables",
                                class_name="wave-atmospheric-variables-panel",
                            )
                        ],
                        start_collapsed=True,
                    ),
                    style={"padding": "0px"},
                ),
                style={
                    "paddingTop": "25px",
                    "paddingLeft": "72px",
                    "paddingRight": "72px",
                },
            ),
            html.Div(dcc.Loading(id="loading", children=[html.Div(id="output")])),
            html.Div(
                full_legend,
                id="overtopping-graph-legend",
                className="overtopping-legend",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id="scatter-plot-rig1",
                            style={"border": "1.011px solid #8A8D90"},
                        ),
                        md=6,
                        style={"padding": "0px"},
                    ),
                    dbc.Col(
                        dcc.Graph(
                            id="scatter-plot-rig2",
                            style={"border": "1.011px solid #8A8D90"},
                        ),
                        md=6,
                        style={"paddingLeft": "16px", "paddingRight": "0px"},
                    ),
                ],
                style={
                    "paddingTop": "22px",
                    "paddingLeft": "72px",
                    "paddingRight": "72px",
                },
            ),
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id="line-plot-swh", style={"border": "1.011px solid #8A8D90"}
                    ),
                    md=12,
                    style={"padding": "24px 72px"},
                )
            ),
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id="line-plot-tidal-level",
                        style={"border": "1.011px solid #8A8D90"},
                    ),
                    md=12,
                    style={"padding": "24px 72px"},
                )
            ),
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id="line-plot-wind-speed",
                        style={"border": "1.011px solid #8A8D90"},
                    ),
                    md=12,
                    style={"padding": "24px 72px"},
                )
            ),
            dbc.Row(
                footer_panel, style={"backgroundColor": "#2A5485", "height": "141px"}
            ),
        ],
        fluid=True,
        className="body-container",
    )


render_dashboard()


def render_feature_line_plots(location_name, variables_ot_dfs, show_dynamic_y_axis):
    """Render feature line plots

    Args:
        location_name (string): Location name e.g. Dawlish or Penzance
        variables_ot_dfs (dataframes): Forecast and adjusted forecast wave and atmospheric variables dataframes
        show_dynamic_y_axis (boolean): Flag to display y-axis dynamically when generating adjusted forecast overtopping data

    Returns:
        Figures: Significant wave height, tidal level and wind speed figures
    """

    (
        prev_swh_df,
        cur_swh_df,
        prev_swh_ot_df,
        cur_swh_overtopping_times_df,
        prev_tl_df,
        cur_tidal_level_df,
        prev_tl_ot_df,
        cur_tl_overtopping_times_df,
        prev_ws_df,
        cur_wind_speed_df,
        prev_ws_ot_df,
        cur_ws_overtopping_times_df,
    ) = variables_ot_dfs
    features_description = tuple(
        ["Significant wave height (Hm)", "Adjusted significant wave height (Hm)"]
    )
    overtopping_evts_desc = tuple(["Overtopping event", "Adjusted overtopping event"])
    swh_fig = fc.render_feature_plot(
        location_name + " - Significant wave height",
        prev_swh_df,
        cur_swh_df,
        "significant_wave_height",
        features_description,
        overtopping_evts_desc,
        0,
        5,
        prev_swh_ot_df,
        cur_swh_overtopping_times_df,
        show_dynamic_y_axis,
    )
    features_description = tuple(
        ["Tidal level (m, CD)", "Adjusted tidal level (m, CD)"]
    )
    tidal_level_fig = fc.render_feature_plot(
        location_name + " - Tidal Level ",
        prev_tl_df,
        cur_tidal_level_df,
        "tidal_level",
        features_description,
        overtopping_evts_desc,
        0,
        6,
        prev_tl_ot_df,
        cur_tl_overtopping_times_df,
        show_dynamic_y_axis,
    )
    features_description = tuple(["Wind speed (m/s)", "Adjusted wind speed (m/s)"])
    wind_speed_fig = fc.render_feature_plot(
        location_name + " - Wind Speed ",
        prev_ws_df,
        cur_wind_speed_df,
        "wind_speed",
        features_description,
        overtopping_evts_desc,
        0,
        25,
        prev_ws_ot_df,
        cur_ws_overtopping_times_df,
        show_dynamic_y_axis,
    )
    return swh_fig, tidal_level_fig, wind_speed_fig


def get_overtopping_data_stage(trigger_id):
    """Get overtopping data's stage

    Args:
        trigger_id (string): Element's id which has triggered an event

    Returns:
        string: Value that defines if it's either forecast or adjusted forecast data
    """

    return (
        "forecast"
        if trigger_id is None or trigger_id == "dd_site_location"
        else "adjusted_forecast"
    )


def get_final_overtopping_dfs(
    first_location_data,
    current_df_1,
    second_location_data,
    current_df_2,
    trigger_id,
    submit_n_clicks,
):
    """Get final overtopping dataframes

    Args:
        first_location_data (Dataframe): First location dataframe e.g. Dawlish seawall crest data
        current_df_1 (Dataframe): Adjusted first location dataframe
        second_location_data (Dataframe): Second location dataframe e.g. Dawlish railway line data
        current_df_2 (Dataframe): Adjusted second location dataframe
        trigger_id (integer): Element's id which has triggered an event
        submit_n_clicks (integer): Number of clicks of submit button

    Returns:
        Dataframes: Joined dataframes, forecast and adjusted forecast overtopping events dataframes
    """
    first_location_data["stage"] = get_overtopping_data_stage(trigger_id)
    second_location_data["stage"] = get_overtopping_data_stage(trigger_id)

    dfs_to_store = [
        first_location_data,
        current_df_1,
        second_location_data,
        current_df_2,
    ]
    tmp_previous_df_1, tmp_current_df_1, tmp_previous_df_2, tmp_current_df_2 = (
        utils.get_dataframes_to_save(submit_n_clicks, trigger_id, dfs_to_store)
    )
    joined_dsc = pd.concat([tmp_previous_df_1, tmp_current_df_1], ignore_index=True)
    joined_drl = pd.concat([tmp_previous_df_2, tmp_current_df_2], ignore_index=True)
    return (
        joined_dsc,
        joined_drl,
        tmp_previous_df_1,
        tmp_current_df_1,
        tmp_previous_df_2,
        tmp_current_df_2,
    )


def get_final_variables_dfs(
    swh_df,
    current_swh_df,
    swh_overtopping_times_df,
    current_swh_ot_df,
    tidal_level_df,
    curren_tl_df,
    tl_overtopping_times_df,
    current_tl_ot_df,
    wind_speed_df,
    current_ws_df,
    ws_overtopping_times_df,
    current_ws_ot_df,
    trigger_id,
    submit_n_clicks,
):
    """Get final wave and atmospheric variables dataframes

    Args:
        swh_df (Dataframe): Significant wave height dataframe
        current_swh_df (Dataframe): Adjusted significant wave height dataframe
        swh_overtopping_times_df (Dataframe): Forecast overtopping event times dataframe for significant wave height data
        current_swh_ot_df (Dataframe): Adjusted forecast overtopping event times dataframe for significant wave height data
        tidal_level_df (Dataframe): Tidal level dataframe
        curren_tl_df (Dataframe): Adjusted tidal level dataframe
        tl_overtopping_times_df (Dataframe): Forecast overtopping event times dataframe for tidal level data
        current_tl_ot_df (Dataframe): Adjusted forecast overtopping event times dataframe for tidal level data
        wind_speed_df (Dataframe): Wind speed dataframe
        current_ws_df (Dataframe): Adjusted wind speed dataframe
        ws_overtopping_times_df (Dataframe): Forecast overtopping event times dataframe for wind speed data
        current_ws_ot_df (Dataframe): Adjusted forecast overtopping event times dataframe for wind speed data
        trigger_id (Dataframe): Element's id which has triggered an event
        submit_n_clicks (Dataframe): Number of clicks of submit button

    Returns:
        Tuple: Dataframes to store, and final forecast and adjust forecast significant-wave-height, tidal-level and wind-speed dataframes
    """

    swh_df["stage"] = get_overtopping_data_stage(trigger_id)
    tidal_level_df["stage"] = get_overtopping_data_stage(trigger_id)
    wind_speed_df["stage"] = get_overtopping_data_stage(trigger_id)

    dfs_to_store = [
        swh_df,
        current_swh_df,
        swh_overtopping_times_df,
        current_swh_ot_df,
        tidal_level_df,
        curren_tl_df,
        tl_overtopping_times_df,
        current_tl_ot_df,
        wind_speed_df,
        current_ws_df,
        ws_overtopping_times_df,
        current_ws_ot_df,
    ]
    (
        final_prev_swh_df,
        final_cur_swh_df,
        final_prev_swh_ot_df,
        final_cur_swh_ot_df,
        final_prev_tl_df,
        final_cur_tl_df,
        final_prev_tl_ot_df,
        final_cur_tl_ot_df,
        final_prev_ws_df,
        final_cur_ws_df,
        final_prev_ws_ot_df,
        final_cur_ws_ot_df,
    ) = utils.get_dataframes_to_save(submit_n_clicks, trigger_id, dfs_to_store)

    dfs_to_store = tuple(
        [
            final_prev_swh_df,
            final_cur_swh_df,
            final_prev_swh_ot_df,
            final_cur_swh_ot_df,
            final_prev_tl_df,
            final_cur_tl_df,
            final_prev_tl_ot_df,
            final_cur_tl_ot_df,
            final_prev_ws_df,
            final_cur_ws_df,
            final_prev_ws_ot_df,
            final_cur_ws_ot_df,
        ]
    )
    return (
        dfs_to_store,
        final_prev_swh_df,
        final_cur_swh_df,
        final_prev_swh_ot_df,
        final_cur_swh_ot_df,
        final_prev_tl_df,
        final_cur_tl_df,
        final_prev_tl_ot_df,
        final_cur_tl_ot_df,
        final_prev_ws_df,
        final_cur_ws_df,
        final_prev_ws_ot_df,
        final_cur_ws_ot_df,
    )


@app.callback(
    [
        Output("scatter-plot-rig1", "figure"),
        Output("scatter-plot-rig2", "figure"),
        Output("previous-dataframe-1", "data"),
        Output("previous-dataframe-2", "data"),
        Output("current-dataframe-1", "data"),
        Output("current-dataframe-2", "data"),
        Output("forecast-range", "start_date"),
        Output("forecast-range", "end_date"),
        Output("overtopping-graph-legend", "children"),
        Output("line-plot-swh", "figure"),
        Output("line-plot-tidal-level", "figure"),
        Output("line-plot-wind-speed", "figure"),
        Output("previous-swh", "data"),
        Output("current-swh", "data"),
        Output("previous-swh-ot", "data"),
        Output("current-swh-ot", "data"),
        Output("previous-tidal-level", "data"),
        Output("current-tidal-level", "data"),
        Output("previous-tidal-level-ot", "data"),
        Output("current-tidal-level-ot", "data"),
        Output("previous-wind-speed", "data"),
        Output("current-wind-speed", "data"),
        Output("previous-wind-speed-ot", "data"),
        Output("current-wind-speed-ot", "data"),
        Output("output", "children"),
    ],
    Input("submit-button", "n_clicks"),
    Input("dd_site_location", "value"),
    State("sig-wave-height", "value"),
    State("freeboard", "value"),
    State("mean-wave-period", "value"),
    State("mean-wave-direction", "value"),
    State("wind-speed", "value"),
    State("wind-direction", "value"),
    State("current-dataframe-1", "data"),
    State("current-dataframe-2", "data"),
    State("current-swh", "data"),
    State("current-swh-ot", "data"),
    State("current-tidal-level", "data"),
    State("current-tidal-level-ot", "data"),
    State("current-wind-speed", "data"),
    State("current-wind-speed-ot", "data"),
    background=True,
    running=[
        (Output("submit-button", "disabled"), True, False),
        (Output("output", "children"), "Loading...", None),
    ],
)
def submit_slider_values(
    submit_n_clicks,
    site_location_val,
    sig_wave_height_val,
    freeboard_val,
    mean_wave_period_val,
    mean_wave_dir_val,
    wind_speed_val,
    wind_dir_val,
    current_df_1,
    current_df_2,
    current_swh_df,
    current_swh_ot_df,
    curren_tl_df,
    current_tl_ot_df,
    current_ws_df,
    current_ws_ot_df,
):
    """Callback to render overtopping graphs when picking a location or submitting any variable

    Args:
        submit_n_clicks (integer): Number of clicks of submit button
        site_location_val (string): Site location value of dropdown box
        sig_wave_height_val (integer): Significant wave height value
        freeboard_val (integer): Freeboard value
        mean_wave_period_val (integer): Mean wave period value
        mean_wave_dir_val (integer): Mean wave direction value
        wind_speed_val (integer): Wind speed value
        wind_dir_val (integer): Wind direction value
        current_df_1 (Dataframe): Adjusted forecast overtopping data of first location
        current_df_2 (Dataframe): Adjusted forecast overtopping data of second location
        current_swh_df (Dataframe): Significant wave height dataframe
        current_swh_ot_df (Dataframe): Forecast overtopping events times dataframe of significant wave height data
        curren_tl_df (Dataframe): Tidal level dataframe
        current_tl_ot_df (Dataframe): Forecast overtopping events times dataframe of tidal level data
        current_ws_df (Dataframe): Wind speed dataframe
        current_ws_ot_df (Dataframe): Forecast overtopping events times dataframe of wind speed data

    Returns:
        Figures, data, div's children, Figure, data, div's children : Overtopping events scatter plots, overtopping events data to store,
        legend's components; significant wave height, tidal level and wind speed line plot figures; significant wave height, tidal level and wind speed data to store
    """

    trigger_id = ctx.triggered_id
    dfs_to_store = []
    if (
        submit_n_clicks is None
        or submit_n_clicks == 0
        or trigger_id is not None
        and trigger_id != "submit-button"
    ):
        option, start_date = utils.get_dataset_params(site_location_val)
        params = {"start_date": start_date, "option": option}
    else:
        option, start_date = utils.get_dataset_params(site_location_val)
        params = {
            "sig_wave_height": sig_wave_height_val,
            "freeboard": freeboard_val,
            "mean_wave_period": mean_wave_period_val,
            "mean_wave_dir": mean_wave_dir_val,
            "wind_speed": wind_speed_val,
            "wind_direction": wind_dir_val,
        }
        params["start_date"] = start_date
        params["option"] = option

    show_full_legend = (
        False if trigger_id is None or trigger_id == "dd_site_location" else True
    )
    full_legend = ogc.get_full_legend(show_full_legend)
    show_dynamic_y_axis = trigger_id == "submit-button"

    if utils.find_words_with_suffix(site_location_val, "Dawlish"):
        api_url = utils.add_resource(DAWLISH_API_ROOT_ENDPOINT, "wave-overtopping")
        api_url = utils.add_query_params(api_url, params)
        (
            dawlish_seawall_crest_data,
            dawlish_railway_line_data,
            forecast_start_date,
            forecast_end_date,
        ) = get_dawlish_wave_overtopping(api_url)
        (
            swh_df,
            swh_overtopping_times_df,
            tidal_level_df,
            tl_overtopping_times_df,
            wind_speed_df,
            ws_overtopping_times_df,
        ) = get_all_features_data(DAWLISH_API_ROOT_ENDPOINT, params)

        (
            joined_dsc,
            joined_drl,
            tmp_previous_df_1,
            tmp_current_df_1,
            tmp_previous_df_2,
            tmp_current_df_2,
        ) = get_final_overtopping_dfs(
            dawlish_seawall_crest_data,
            current_df_1,
            dawlish_railway_line_data,
            current_df_2,
            trigger_id,
            submit_n_clicks,
        )
        fig_dawlish_seawall_crest = ogc.render_dawlish_seawall_crest_graph(joined_dsc)
        fig_dawlish_railway_line = ogc.render_dawlish_railway_line_graph(joined_drl)

        (
            dfs_to_store,
            final_prev_swh_df,
            final_cur_swh_df,
            final_prev_swh_ot_df,
            final_cur_swh_ot_df,
            final_prev_tl_df,
            final_cur_tl_df,
            final_prev_tl_ot_df,
            final_cur_tl_ot_df,
            final_prev_ws_df,
            final_cur_ws_df,
            final_prev_ws_ot_df,
            final_cur_ws_ot_df,
        ) = get_final_variables_dfs(
            swh_df,
            current_swh_df,
            swh_overtopping_times_df,
            current_swh_ot_df,
            tidal_level_df,
            curren_tl_df,
            tl_overtopping_times_df,
            current_tl_ot_df,
            wind_speed_df,
            current_ws_df,
            ws_overtopping_times_df,
            current_ws_ot_df,
            trigger_id,
            submit_n_clicks,
        )
        swh_fig, tidal_level_fig, wind_speed_fig = render_feature_line_plots(
            "Dawlish", dfs_to_store, show_dynamic_y_axis
        )

    else:
        api_url = utils.add_resource(PENZANCE_API_ROOT_ENDPOINT, "wave-overtopping")
        api_url = utils.add_query_params(api_url, params)
        (
            data_penzance_seawall_crest,
            data_penzance_seawall_crest_sheltered,
            forecast_start_date,
            forecast_end_date,
        ) = get_penzance_wave_overtopping(api_url)

        (
            swh_df,
            swh_overtopping_times_df,
            tidal_level_df,
            tl_overtopping_times_df,
            wind_speed_df,
            ws_overtopping_times_df,
        ) = get_all_features_data(PENZANCE_API_ROOT_ENDPOINT, params)

        (
            joined_psc,
            joined_pscs,
            tmp_previous_df_1,
            tmp_current_df_1,
            tmp_previous_df_2,
            tmp_current_df_2,
        ) = get_final_overtopping_dfs(
            data_penzance_seawall_crest,
            current_df_1,
            data_penzance_seawall_crest_sheltered,
            current_df_2,
            trigger_id,
            submit_n_clicks,
        )
        fig_penzance_seawall_crest = ogc.render_penzance_seawall_crest_graph(joined_psc)
        fig_penzance_seawall_crest_sheltered = (
            ogc.render_penzance_seawall_crest_sheltered_graph(joined_pscs)
        )

        (
            dfs_to_store,
            final_prev_swh_df,
            final_cur_swh_df,
            final_prev_swh_ot_df,
            final_cur_swh_ot_df,
            final_prev_tl_df,
            final_cur_tl_df,
            final_prev_tl_ot_df,
            final_cur_tl_ot_df,
            final_prev_ws_df,
            final_cur_ws_df,
            final_prev_ws_ot_df,
            final_cur_ws_ot_df,
        ) = get_final_variables_dfs(
            swh_df,
            current_swh_df,
            swh_overtopping_times_df,
            current_swh_ot_df,
            tidal_level_df,
            curren_tl_df,
            tl_overtopping_times_df,
            current_tl_ot_df,
            wind_speed_df,
            current_ws_df,
            ws_overtopping_times_df,
            current_ws_ot_df,
            trigger_id,
            submit_n_clicks,
        )
        swh_fig, tidal_level_fig, wind_speed_fig = render_feature_line_plots(
            "Penzance", dfs_to_store, show_dynamic_y_axis
        )

    fig1 = (
        fig_dawlish_seawall_crest
        if utils.find_words_with_suffix(site_location_val, "Dawlish")
        else fig_penzance_seawall_crest
    )
    fig2 = (
        fig_penzance_seawall_crest_sheltered
        if utils.find_words_with_suffix(site_location_val, "Penzance")
        else fig_dawlish_railway_line
    )

    return (
        fig1,
        fig2,
        tmp_previous_df_1.to_dict("records"),
        tmp_previous_df_2.to_dict("records"),
        tmp_current_df_1.to_dict("records"),
        tmp_current_df_2.to_dict("records"),
        forecast_start_date,
        forecast_end_date,
        full_legend,
        swh_fig,
        tidal_level_fig,
        wind_speed_fig,
        final_prev_swh_df.to_dict("records"),
        final_cur_swh_df.to_dict("records"),
        final_prev_swh_ot_df.to_dict("records"),
        final_cur_swh_ot_df.to_dict("records"),
        final_prev_tl_df.to_dict("records"),
        final_cur_tl_df.to_dict("records"),
        final_prev_tl_ot_df.to_dict("records"),
        final_cur_tl_ot_df.to_dict("records"),
        final_prev_ws_df.to_dict("records"),
        final_cur_ws_df.to_dict("records"),
        final_prev_ws_ot_df.to_dict("records"),
        final_cur_ws_ot_df.to_dict("records"),
        "",
    )


@app.callback(
    Output("sig-wave-height", "value"),
    Input("sig-wave-height", "value"),
    Input("swh-increase-btn", "n_clicks"),
    Input("swh-decrease-btn", "n_clicks"),
    Input("reset-button", "n_clicks"),
    Input("wad-reset-button", "n_clicks"),
    Input("dd_site_location", "value"),
    State("sig-wave-height", "step"),
)
def update_slider(
    slider_value,
    n_clicks_inc,
    n_clicks_dec,
    n_clicks_reset,
    n_clicks_reset_wad,
    site_location_value,
    current_step,
):
    """Callback for significant wave height slider

    Args:
        slider_value (integer): Significant wave height slider's value
        n_clicks_inc (integer): Number of clicks of increase button
        n_clicks_dec (integer): Number of clicks of decrease button
        n_clicks_reset (integer): Number of clicks of reset button
        n_clicks_reset_wad (integer): Number of clicks of reset button for wave variables sliders
        site_location_value (string): Dropdown box's value
        current_step (integer): Current slider's value

    Returns:
        integer: Adjusted slider's value
    """

    if (
        n_clicks_inc == 0
        or n_clicks_dec == 0
        or n_clicks_reset == 0
        or n_clicks_reset_wad == 0
    ):
        return PERCENTAGE_DEFAULT_VALUE

    trigger_id = ctx.triggered_id

    if trigger_id == "swh-increase-btn":
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == "swh-decrease-btn":
        new_value = slider_value - current_step
        return new_value
    elif (
        trigger_id == "reset-button"
        or trigger_id == "wad-reset-button"
        or trigger_id == "dd_site_location"
    ):
        return PERCENTAGE_DEFAULT_VALUE
    else:
        return slider_value


@app.callback(
    Output("freeboard", "value"),
    Input("freeboard", "value"),
    Input("fb-increase-btn", "n_clicks"),
    Input("fb-decrease-btn", "n_clicks"),
    Input("reset-button", "n_clicks"),
    Input("wad-reset-button", "n_clicks"),
    Input("dd_site_location", "value"),
    State("freeboard", "step"),
)
def update_slider(
    slider_value,
    n_clicks_inc,
    n_clicks_dec,
    n_clicks_reset,
    n_clicks_reset_wad,
    site_location_value,
    current_step,
):
    """Callback for freeboard slider

    Args:
        slider_value (integer): Freeboard slider's value
        n_clicks_inc (integer): Number of clicks of increase button
        n_clicks_dec (integer): Number of clicks of decrease button
        n_clicks_reset (integer): Number of clicks of reset button
        n_clicks_reset_wad (integer): Number of clicks of reset button for wave variables sliders
        site_location_value (string): Dropdown box's value
        current_step (integer): Current slider's value

    Returns:
        integer: Adjusted slider's value
    """

    if (
        n_clicks_inc == 0
        or n_clicks_dec == 0
        or n_clicks_reset == 0
        or n_clicks_reset_wad == 0
    ):
        return PERCENTAGE_DEFAULT_VALUE

    trigger_id = ctx.triggered_id

    if trigger_id == "fb-increase-btn":
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == "fb-decrease-btn":
        new_value = slider_value - current_step
        return new_value
    elif (
        trigger_id == "reset-button"
        or trigger_id == "wad-reset-button"
        or trigger_id == "dd_site_location"
    ):
        return PERCENTAGE_DEFAULT_VALUE
    else:
        return slider_value


@app.callback(
    Output("mean-wave-period", "value"),
    Input("mean-wave-period", "value"),
    Input("mwp-increase-btn", "n_clicks"),
    Input("mwp-decrease-btn", "n_clicks"),
    Input("reset-button", "n_clicks"),
    Input("wad-reset-button", "n_clicks"),
    Input("dd_site_location", "value"),
    State("mean-wave-period", "step"),
)
def update_slider(
    slider_value,
    n_clicks_inc,
    n_clicks_dec,
    n_clicks_reset,
    n_clicks_reset_wad,
    site_location_value,
    current_step,
):
    """Callback for mean wave period slider

    Args:
        slider_value (integer): Mean wave period slider's value
        n_clicks_inc (integer):  Number of clicks of increase button
        n_clicks_dec (integer): Number of clicks of decrease button
        n_clicks_reset (integer): Number of clicks of reset button
        n_clicks_reset_wad (integer): Number of clicks of reset button for wave variables sliders
        site_location_value (string): Dropdown box's value
        current_step (integer):  Current slider's value

    Returns:
        integer: Adjusted slider's value
    """

    if (
        n_clicks_inc == 0
        or n_clicks_dec == 0
        or n_clicks_reset == 0
        or n_clicks_reset_wad == 0
    ):
        return PERCENTAGE_DEFAULT_VALUE

    trigger_id = ctx.triggered_id

    if trigger_id == "mwp-increase-btn":
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == "mwp-decrease-btn":
        new_value = slider_value - current_step
        return new_value
    elif (
        trigger_id == "reset-button"
        or trigger_id == "wad-reset-button"
        or trigger_id == "dd_site_location"
    ):
        return PERCENTAGE_DEFAULT_VALUE
    else:
        return slider_value


@app.callback(
    Output("mean-wave-direction", "value"),
    Input("mean-wave-direction", "value"),
    Input("mwd-increase-btn", "n_clicks"),
    Input("mwd-decrease-btn", "n_clicks"),
    Input("reset-button", "n_clicks"),
    Input("mwd-reset-button", "n_clicks"),
    Input("dd_site_location", "value"),
    State("mean-wave-direction", "step"),
)
def update_slider(
    slider_value,
    n_clicks_inc,
    n_clicks_dec,
    n_clicks_reset,
    n_clicks_reset_mwd,
    site_location_value,
    current_step,
):
    """Callback for mean wave direction slider

    Args:
        slider_value (integer): Mean wave direction slider's value
        n_clicks_inc (integer):  Number of clicks of increase button
        n_clicks_dec (integer): Number of clicks of decrease button
        n_clicks_reset (integer): Number of clicks of reset button
        n_clicks_reset_mwd (integer): Number of clicks of reset button for wind direction variable slider
        site_location_value (string): Dropdown box's value
        current_step (integer): Current slider's value

    Returns:
        integer: Adjusted slider's value
    """

    if (
        n_clicks_inc == 0
        or n_clicks_dec == 0
        or n_clicks_reset == 0
        or n_clicks_reset_mwd == 0
    ):
        return DEGREE_DEFAULT_VALUE

    trigger_id = ctx.triggered_id

    if trigger_id == "mwd-increase-btn":
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == "mwd-decrease-btn":
        new_value = slider_value - current_step
        return new_value
    elif (
        trigger_id == "reset-button"
        or trigger_id == "mwd-reset-button"
        or trigger_id == "dd_site_location"
    ):
        return DEGREE_DEFAULT_VALUE
    else:
        return slider_value


@app.callback(
    Output("wind-speed", "value"),
    Input("wind-speed", "value"),
    Input("ws-increase-btn", "n_clicks"),
    Input("ws-decrease-btn", "n_clicks"),
    Input("reset-button", "n_clicks"),
    Input("aad-reset-button", "n_clicks"),
    Input("dd_site_location", "value"),
    State("wind-speed", "step"),
)
def update_slider(
    slider_value,
    n_clicks_inc,
    n_clicks_dec,
    n_clicks_reset,
    n_clicks_reset_aad,
    site_location_value,
    current_step,
):
    """Callback for wind speed slider

    Args:
        slider_value (integer): Wind speed slider's value
        n_clicks_inc (integer):  Number of clicks of increase button
        n_clicks_dec (integer): Number of clicks of decrease button
        n_clicks_reset (integer): Number of clicks of reset button
        n_clicks_reset_aad (integer): Number of clicks of reset button for atmospheric variables sliders
        site_location_value (string): Dropdown box's value
        current_step (integer): Current slider's value

    Returns:
        integer: Adjusted slider's value
    """

    if (
        n_clicks_inc == 0
        or n_clicks_dec == 0
        or n_clicks_reset == 0
        or n_clicks_reset_aad == 0
    ):
        return PERCENTAGE_DEFAULT_VALUE

    trigger_id = ctx.triggered_id

    if trigger_id == "ws-increase-btn":
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == "ws-decrease-btn":
        new_value = slider_value - current_step
        return new_value
    elif (
        trigger_id == "reset-button"
        or trigger_id == "aad-reset-button"
        or trigger_id == "dd_site_location"
    ):
        return PERCENTAGE_DEFAULT_VALUE
    else:
        return slider_value


@app.callback(
    Output("wind-direction", "value"),
    Input("wind-direction", "value"),
    Input("wd-increase-btn", "n_clicks"),
    Input("wd-decrease-btn", "n_clicks"),
    Input("reset-button", "n_clicks"),
    Input("wd-reset-button", "n_clicks"),
    Input("dd_site_location", "value"),
    State("wind-direction", "step"),
)
def update_slider(
    slider_value,
    n_clicks_inc,
    n_clicks_dec,
    n_clicks_reset,
    n_clicks_reset_wd,
    site_location_value,
    current_step,
):
    """Callback for wind direction slider

    Args:
        slider_value (integer): Wind direction slider's value
        n_clicks_inc (integer):  Number of clicks of increase button
        n_clicks_dec (integer): Number of clicks of decrease button
        n_clicks_reset (integer): Number of clicks of reset button
        n_clicks_reset_wd (integer):  Number of clicks of reset button for wind direction variable slider
        site_location_value (string): Dropdown box's value
        current_step (integer): Current slider's value

    Returns:
        integer: Adjusted slider's value
    """

    if (
        n_clicks_inc == 0
        or n_clicks_dec == 0
        or n_clicks_reset == 0
        or n_clicks_reset_wd == 0
    ):
        return DEGREE_DEFAULT_VALUE

    trigger_id = ctx.triggered_id

    if trigger_id == "wd-increase-btn":
        new_value = slider_value + current_step
        return new_value
    elif trigger_id == "wd-decrease-btn":
        new_value = slider_value - current_step
        return new_value
    elif (
        trigger_id == "reset-button"
        or trigger_id == "wd-reset-button"
        or trigger_id == "dd_site_location"
    ):
        return DEGREE_DEFAULT_VALUE
    else:
        return slider_value


if __name__ == "__main__":
    environment = os.getenv("SPLASH_ENV")

    if DEBUG == True:
        print("DAWLISH_API_ENDPOINT=", DAWLISH_API_ROOT_ENDPOINT)
        print("PENZANCE_API_ENDPOINT=", PENZANCE_API_ROOT_ENDPOINT)

    if environment == "docker":
        #docker requests from outside the container don't come from 127.0.0.1, so we need to bind to 0.0.0.0 to receive them
        app.run_server(host='0.0.0.0', debug=DEBUG)
    else:
        app.run(debug=DEBUG)

