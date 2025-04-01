from dash import dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc


PERCENTAGE_MIN_VAL_SLIDER = -100
PERCENTAGE_MAX_VAL_SLIDER = 100
PERCENTAGE_DEFAULT_VALUE = 0
DEGREE_MIN_VAL_SLIDER = -180
DEGREE_MAX_VAL_SLIDER = 180
DEGREE_DEFAULT_VALUE = 0
PERCENTAGE_CHAR = "%"
DEGREE_CHAR = "°"


def render_overtopping_plot(plot_title, plot_logo, overtopping_data):
    """Render overtopping plot

    Args:
        plot_title (string): Plot's title
        plot_logo (string): Relative path to plot's log
        overtopping_data (Dataframe): Forecast overtopping events dataframe

    Returns:
        Figure: Forecast overtopping events figure
    """

    fig_rf1_rf2_tmp = px.scatter(
        overtopping_data,
        x="time",
        y="overtopping_count",
        color_continuous_scale=["aqua", "skyblue", "blue"],
        height=513,
        labels={
            "time": "Time",
            "overtopping_count": "No. of Overtopping Occurrences (Per 10 Mins)",
            "confidence": "Confidence Level",
        },
    )

    fig_rf1_rf2_tmp.add_layout_image(
        dict(
            source="./assets/imgs/" + plot_logo,
            xref="paper",
            yref="paper",
            x=0.30,
            y=1.03,
            sizex=0.06,
            sizey=0.06,
            xanchor="left",
            yanchor="bottom",
        )
    )

    fig_rf1_rf2_tmp.update_layout(
        title=dict(
            text=plot_title,
            font=dict(family="Helvetica Neue", size=22, color="#3279B7", weight=500),
            xref="container",
            yref="container",
            x=0.4,
            y=0.91,
            xanchor="left",
            yanchor="bottom",
        ),
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=True,
            gridcolor="#8A8D90",
            linecolor="#8A8D90",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#8A8D90",
            linecolor="#8A8D90",
        ),
        showlegend=False,
    )

    fig_rf1_rf2_tmp.update_traces(
        selector=dict(type="scatter", mode="markers"),
        marker=dict(
            line=dict(width=2),
            size=12,
            symbol=[
                (
                    "x-thin"
                    if o == 0
                    else (
                        "circle-open"
                        if c > 0.80 and o > 0
                        else (
                            "circle"
                            if c >= 0.50 and c <= 0.8 and o > 0
                            else "square" if c < 0.50 and o > 0 else "circle"
                        )
                    )
                )
                for c, o in zip(
                    overtopping_data["confidence"],
                    overtopping_data["overtopping_count"],
                )
            ],
            color=[
                (
                    "#2A5485"
                    if o == 0 and s == "forecast"
                    else (
                        "#000"
                        if c > 0.80 and o > 0 and s == "forecast"
                        else (
                            "#2A5485"
                            if c >= 0.50 and c <= 0.8 and o > 0 and s == "forecast"
                            else (
                                "#AAD3E3"
                                if c < 0.50 and o > 0 and s == "forecast"
                                else (
                                    "#C5C5C5"
                                    if o == 0 and s == "adjusted_forecast"
                                    else (
                                        "#808080"
                                        if c > 0.80
                                        and o > 0
                                        and s == "adjusted_forecast"
                                        else (
                                            "#C5C5C5"
                                            if c >= 0.50
                                            and c <= 0.8
                                            and o > 0
                                            and s == "adjusted_forecast"
                                            else (
                                                "#C7C7C7"
                                                if c < 0.50
                                                and o > 0
                                                and s == "adjusted_forecast"
                                                else "#AAD3E3"
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
                for c, o, s in zip(
                    overtopping_data["confidence"],
                    overtopping_data["overtopping_count"],
                    overtopping_data["stage"],
                )
            ],
            line_color=[
                (
                    "#2A5485"
                    if o == 0 and s == "forecast"
                    else (
                        "#000"
                        if c > 0.80 and o > 0 and s == "forecast"
                        else (
                            "#2A5485"
                            if c >= 0.50 and c <= 0.80 and o > 0 and s == "forecast"
                            else (
                                "#AAD3E3"
                                if c < 0.50 and o > 0 and s == "forecast"
                                else (
                                    "#C5C5C5"
                                    if o == 0 and s == "adjusted_forecast"
                                    else (
                                        "#808080"
                                        if c > 0.80
                                        and o > 0
                                        and s == "adjusted_forecast"
                                        else (
                                            "#000"
                                            if c >= 0.50
                                            and c <= 0.80
                                            and o > 0
                                            and s == "adjusted_forecast"
                                            else (
                                                "#C7C7C7"
                                                if c < 0.50
                                                and o > 0
                                                and s == "adjusted_forecast"
                                                else "#AAD3E3"
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
                for c, o, s in zip(
                    overtopping_data["confidence"],
                    overtopping_data["overtopping_count"],
                    overtopping_data["stage"],
                )
            ],
        ),
    )

    fig_rf1_rf2_tmp.add_hline(
        y=6, line_dash="dash", line_color="#8A8D90", annotation_text="25% IQR (6)"
    )
    fig_rf1_rf2_tmp.add_hline(
        y=54, line_dash="dash", line_color="#8A8D90", annotation_text="75% IQR (54)"
    )

    return fig_rf1_rf2_tmp


def render_dawlish_seawall_crest_graph(dawlish_seawall_crest_data):
    """Render Dawlish seawall crest graph

    Args:
        dawlish_seawall_crest_data (Dataframe): Forecast overtopping events dataframe

    Returns:
        Figure: Forecast overtopping events graph
    """

    fig_dawlish_seawall_crest = render_overtopping_plot(
        "Dawlish Seawall Crest", "dawlish_seawall_crest.png", dawlish_seawall_crest_data
    )

    return fig_dawlish_seawall_crest


def render_dawlish_railway_line_graph(data_dawlish_railway_line):
    """Render Dawlish railway line graph

    Args:
        data_dawlish_railway_line (_type_): Forecast overtopping events dataframe

    Returns:
       Figure: Forecast overtopping events graph
    """
    
    fig_dawlish_railway_line = render_overtopping_plot(
        "Dawlish Railway Line", "dawlish_railway_line.png", data_dawlish_railway_line
    )

    return fig_dawlish_railway_line


def render_penzance_seawall_crest_graph(penzance_seawall_crest_data):
    """Render Penzance seawall crest graph

    Args:
        penzance_seawall_crest_data (Dataframe): Forecast overtopping events dataframe

    Returns:
        Figure: Forecast overtopping events graph
    """

    fig_penzance_seawall_crest = render_overtopping_plot(
        "Penzance Seawall Crest",
        "dawlish_seawall_crest.png",
        penzance_seawall_crest_data,
    )

    return fig_penzance_seawall_crest


def render_penzance_seawall_crest_sheltered_graph(
    data_penzance_seawall_crest_sheltered,
):
    """Render Penzance seawall crest sheltered graph

    Args:
        data_penzance_seawall_crest_sheltered (Dataframe): Forecast overtopping events dataframe

    Returns:
        Figure: Forecast overtopping events graph
    """

    fig_penzance_seawall_crest_sheltered = render_overtopping_plot(
        "Penzance, Seawall Crest (sheltered) ",
        "dawlish_seawall_crest.png",
        data_penzance_seawall_crest_sheltered,
    )

    return fig_penzance_seawall_crest_sheltered


def get_variable_slider(
    identifier,
    min_value,
    max_value,
    default_value,
    template_symbol,
    decrease_btn_id,
    increase_btn_id,
):
    """Get variable slider

    Args:
        identifier (string): Slider's id
        min_value (integer): Slider's minimum value
        max_value (integer): Slider's maximum value
        default_value (integer): Slider's default value
        template_symbol (string): Slider's template symbol
        decrease_btn_id (string): Decrease button's id
        increase_btn_id (string): Increase button's id

    Returns:
        Div: Slider's panel component
    """

    variable_slider = html.Div(
        children=[
            html.Div(
                html.Button(
                    id=decrease_btn_id,
                    children=[
                        html.Img(
                            src="./assets/imgs/minus-icon.svg",
                            className="action-button-img",
                        ),
                    ],
                    className="action-button",
                ),
                className="slider-button-panel",
            ),
            html.Div(
                dcc.Slider(
                    id=identifier,
                    min=min_value,
                    max=max_value,
                    step=1,
                    value=default_value,
                    marks=None,
                    tooltip={
                        "always_visible": True,
                        "template": "{value}" + template_symbol,
                        "placement": "top",
                        "style": {
                            "color": "#2A5485",
                            "fontFamly": "Helvetica Neue",
                            "fontSize": "18px",
                            "fontStyle": "normal",
                            "fontWeight": "400",
                            "lineHeight": "160%",
                        },
                    },
                ),
                style={"padding": "25px 25px 0px", "width": "508px"},
            ),
            html.Div(
                html.Button(
                    id=increase_btn_id,
                    children=[
                        html.Img(
                            src="./assets/imgs/plus-icon.svg",
                            className="action-button-img",
                        ),
                    ],
                    className="action-button",
                ),
                className="slider-button-panel",
            ),
        ],
        className="slider-panel",
    )
    return variable_slider


def get_wave_variables_panels():
    """Get wave variables and mean wave direction panels

    Returns:
        Container: Container of wave variables and mean wave direction panels
    """

    wave_variables_panels = dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div(
                                    dbc.Button(
                                        "Reset",
                                        id="wad-reset-button",
                                        color="link",
                                        class_name="button-link",
                                    ),
                                    className="reset-var-button",
                                ),
                                html.Div(
                                    "Adjusted data", className="adjusted-data-panel"
                                ),

                                html.Div(
                                    children=[
                                        html.Div(
                                            "Significant wave height",
                                            className="variable-full-title",
                                        ),
                                        html.Div(
                                            "Hs [metres]",
                                            className="variable-short-title",
                                        ),
                                    ],
                                    className="variable-section",
                                    style={"paddingTop": "32px"},
                                ),
                                get_variable_slider(
                                    "sig-wave-height",
                                    PERCENTAGE_MIN_VAL_SLIDER,
                                    PERCENTAGE_MAX_VAL_SLIDER,
                                    PERCENTAGE_DEFAULT_VALUE,
                                    PERCENTAGE_CHAR,
                                    "swh-decrease-btn",
                                    "swh-increase-btn",
                                ),

                                html.Div(
                                    children=[
                                        html.Div(
                                            "Tidal level",
                                            className="variable-full-title",
                                        ),
                                        html.Div(
                                            "Rc [metres]",
                                            className="variable-short-title",
                                        ),
                                    ],
                                    className="variable-section",
                                ),
                                get_variable_slider(
                                    "freeboard",
                                    PERCENTAGE_MIN_VAL_SLIDER,
                                    PERCENTAGE_MAX_VAL_SLIDER,
                                    PERCENTAGE_DEFAULT_VALUE,
                                    PERCENTAGE_CHAR,
                                    "fb-decrease-btn",
                                    "fb-increase-btn",
                                ),

                                html.Div(
                                    children=[
                                        html.Div(
                                            "Mean wave period",
                                            className="variable-full-title",
                                        ),
                                        html.Div(
                                            "Tz [seconds]",
                                            className="variable-short-title",
                                        ),
                                    ],
                                    className="variable-section",
                                ),
                                get_variable_slider(
                                    "mean-wave-period",
                                    PERCENTAGE_MIN_VAL_SLIDER,
                                    PERCENTAGE_MAX_VAL_SLIDER,
                                    PERCENTAGE_DEFAULT_VALUE,
                                    PERCENTAGE_CHAR,
                                    "mwp-decrease-btn",
                                    "mwp-increase-btn",
                                ),
                            ]
                        ),
                        style={"borderStyle": "None", "borderRadius": "15px"},
                    ),
                    md=7,
                    style={"padding": "38px 0px 0px 87px"},
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [

                                html.Div(
                                    dbc.Button(
                                        "Reset",
                                        id="mwd-reset-button",
                                        color="link",
                                        class_name="button-link",
                                    ),
                                    className="reset-var-button",
                                ),
                                html.Div(
                                    children=[
                                        html.Div(
                                            "Mean wave direction",
                                            className="variable-full-title",
                                        ),
                                        html.Div(
                                            "Dir [degrees]",
                                            className="variable-short-title",
                                        ),
                                    ],
                                    className="variable-section",
                                ),
                                get_variable_slider(
                                    "mean-wave-direction",
                                    DEGREE_MIN_VAL_SLIDER,
                                    DEGREE_MAX_VAL_SLIDER,
                                    DEGREE_DEFAULT_VALUE,
                                    DEGREE_CHAR,
                                    "mwd-decrease-btn",
                                    "mwd-increase-btn",
                                ),
                            ]
                        ),
                        style={"borderStyle": "None", "borderRadius": "15px"},
                    ),
                    md=5,
                    style={"padding": "38px 67px 0px 16px"},
                ),
            ]
        ),
        fluid=True,
    )
    return wave_variables_panels


def get_atmospheric_variables_panels():
    """Get atmospheric variables panels

    Returns:
        Container: Container of atmospheric variables panels
    """

    atmospheric_variables_panels = dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div(
                                    dbc.Button(
                                        "Reset",
                                        id="aad-reset-button",
                                        color="link",
                                        class_name="button-link",
                                    ),
                                    className="reset-var-button",
                                ),
                                html.Div(
                                    "Adjusted data", className="adjusted-data-panel"
                                ),

                                html.Div(
                                    children=[
                                        html.Div(
                                            "Wind speed",
                                            className="variable-full-title",
                                        ),
                                        html.Div(
                                            "U10 [metres per second]",
                                            className="variable-short-title",
                                        ),
                                    ],
                                    className="variable-section",
                                    style={"paddingTop": "32px"},
                                ),
                                get_variable_slider(
                                    "wind-speed",
                                    PERCENTAGE_MIN_VAL_SLIDER,
                                    PERCENTAGE_MAX_VAL_SLIDER,
                                    PERCENTAGE_DEFAULT_VALUE,
                                    PERCENTAGE_CHAR,
                                    "ws-decrease-btn",
                                    "ws-increase-btn",
                                ),
                            ]
                        ),
                        style={"borderStyle": "None", "borderRadius": "15px"},
                    ),
                    md=7,
                    style={"padding": "39px 0px 0px 87px"},
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div(
                                    dbc.Button(
                                        "Reset",
                                        id="wd-reset-button",
                                        color="link",
                                        class_name="button-link",
                                    ),
                                    className="reset-var-button",
                                ),
                                html.Div(
                                    children=[
                                        html.Div(
                                            "Wind direction",
                                            className="variable-full-title",
                                        ),
                                        html.Div(
                                            "U10 Dir [degrees]",
                                            className="variable-short-title",
                                        ),
                                    ],
                                    className="variable-section",
                                ),
                                get_variable_slider(
                                    "wind-direction",
                                    DEGREE_MIN_VAL_SLIDER,
                                    DEGREE_MAX_VAL_SLIDER,
                                    DEGREE_DEFAULT_VALUE,
                                    DEGREE_CHAR,
                                    "wd-decrease-btn",
                                    "wd-increase-btn",
                                ),
                            ]
                        ),
                        style={"borderStyle": "None", "borderRadius": "15px"},
                    ),
                    md=5,
                    style={"padding": "39px 67px 0px 16px"},
                ),
            ]
        ),
        fluid=True,
    )
    return atmospheric_variables_panels


def get_buttons_panel():
    """Get buttons panel

    Returns:
        Container: Container of buttons panel
    """

    buttons_panel = dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Submit",
                        id="submit-button",
                        style={
                            "backgroundColor": "#2A5485",
                            "borderColor": "#2A5485",
                            "width": "180px",
                            "height": "48px",
                        },
                    ),
                    md=4,
                ),
                dbc.Col(
                    dbc.Button(
                        "Reset all",
                        id="reset-button",
                        color="link",
                        class_name="button-link",
                    ),
                    md=4,
                ),
            ],
            style={"padding": "38px 0px 0px 87px"},
        ),
        fluid=True,
    )

    return buttons_panel


def get_forecast_legend():
    """Get forecast legend

    Returns:
        Row: Row of forecast legend
    """

    forecast_legend = dbc.Row(
        [
            dbc.Col(html.Div("Key"), md=1, class_name="key-subtitle-legend"),
            dbc.Col(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div("Forecast", className="stage-subtitle-legend"),
                            md=1,
                        ),
                        dbc.Col(
                            html.Div(
                                children=[
                                    html.Div(className="high-confidence-marker"),
                                    html.Div(
                                        "High confidence > 80%",
                                        className="high-confidence-subtitle",
                                    ),
                                ],
                                style={"display": "flex", "marginLeft": "11px"},
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            html.Div(
                                children=[
                                    html.Div(className="medium-confidence-marker"),
                                    html.Div(
                                        "Medium confidence 50-80%",
                                        className="medium-confidence-subtitle",
                                    ),
                                ],
                                style={"display": "flex", "marginLeft": "11px"},
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            html.Div(
                                children=[
                                    html.Div(className="low-confidence-marker"),
                                    html.Div(
                                        "Low confidence < 50%",
                                        className="low-confidence-subtitle",
                                    ),
                                ],
                                style={"display": "flex", "marginLeft": "11px"},
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            html.Div(
                                children=[
                                    html.Img(
                                        src="./assets/imgs/no_overtopping_marker.png",
                                        className="no-overtopping-marker",
                                    ),
                                    html.Div(
                                        "No overtopping",
                                        className="no-overtopping-subtitle",
                                    ),
                                ],
                                style={"display": "flex", "marginLeft": "11px"},
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            html.Div(
                                children=[
                                    html.Div(className="interquartile-range-marker"),
                                    html.Div(
                                        "Interquartile range (25th and 75th)",
                                        className="interquartile-range-subtitle",
                                    ),
                                ],
                                style={"display": "flex", "marginLeft": "11px"},
                            ),
                            md=3,
                        ),
                    ],
                    class_name="forecast-sub-legend",
                ),
                md=11,
            ),
        ]
    )
    return forecast_legend


def get_adjusted_forecast_legend():
    """Get adjusted forecast legend

    Returns:
        Row: Row of adjusted forecast legend
    """

    adjusted_forecast_legend = dbc.Row(
        [
            dbc.Col(md=1, class_name="key-subtitle-legend"),
            dbc.Col(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                "Adjusted Forecast", className="stage-subtitle-legend"
                            ),
                            md=1,
                        ),
                        dbc.Col(
                            html.Div(
                                children=[
                                    html.Div(
                                        className="high-confidence-marker",
                                        style={"borderColor": "#808080"},
                                    ),
                                    html.Div(
                                        "High confidence > 80%",
                                        className="high-confidence-subtitle",
                                    ),
                                ],
                                style={"display": "flex", "marginLeft": "11px"},
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            html.Div(
                                children=[
                                    html.Div(
                                        className="medium-confidence-marker",
                                        style={
                                            "background": "#C5C5C5",
                                            "border": "1px solid #000",
                                        },
                                    ),
                                    html.Div(
                                        "Medium confidence 50-80%",
                                        className="medium-confidence-subtitle",
                                    ),
                                ],
                                style={"display": "flex", "marginLeft": "11px"},
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            html.Div(
                                children=[
                                    html.Div(
                                        className="low-confidence-marker",
                                        style={"background": "#C7C7C7"},
                                    ),
                                    html.Div(
                                        "Low confidence < 50%",
                                        className="low-confidence-subtitle",
                                    ),
                                ],
                                style={"display": "flex", "marginLeft": "11px"},
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            html.Div(
                                children=[
                                    html.Img(
                                        src="./assets/imgs/adj_no_overtopping_marker.png",
                                        className="no-overtopping-marker",
                                    ),
                                    html.Div(
                                        "No overtopping",
                                        className="no-overtopping-subtitle",
                                    ),
                                ],
                                style={"display": "flex", "marginLeft": "11px"},
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            html.Div(
                                children=[
                                    html.Div(className="interquartile-range-marker"),
                                    html.Div(
                                        "Interquartile range (25th and 75th)",
                                        className="interquartile-range-subtitle",
                                    ),
                                ],
                                style={"display": "flex", "marginLeft": "11px"},
                            ),
                            md=3,
                        ),
                    ],
                    class_name="adjusted-forecast-sub-legend",
                ),
                md=11,
            ),
        ],
        style={"paddingTop": "7px"},
    )
    return adjusted_forecast_legend


def get_full_legend(show_full_legend):
    """Get full legend

    Args:
        show_full_legend (bool): Flag to display forecast and adjusted forecast legends

    Returns:
        Tuple: Forecast and adjusted forecast legends when show_full_legend is True. Forecast legend when show_full_legend is False.
    """

    forecast_legend = get_forecast_legend()
    adjusted_forecast_legend = get_adjusted_forecast_legend()
    full_legend = (
        [forecast_legend, adjusted_forecast_legend]
        if show_full_legend
        else forecast_legend
    )

    return full_legend


def get_dropdown_panel():
    """Get dropdown panel

    Returns:
        Div: Div container of dropdown box
    """

    dropdown_panel = html.Div(
        [
            "Site location",
            dcc.Dropdown(
                id="dd_site_location",
                options=[
                    "Dawlish",
                    "Penzance",
                    "Dawlish Storm Bert - overtopping",
                    "Penzance Storm Bert - overtopping",
                    "Dawlish - no overtopping",
                    "Penzance - no overtopping",
                ],
                value="Dawlish",
                clearable=False,
                className="site-dropdown",
                optionHeight=44.39,
            ),
        ],
        className="label-dropdown",
    )

    return dropdown_panel


def get_date_picker_range(f_start_date, f_end_date):
    """Get date picker range

    Args:
        f_start_date (string): Forecast start date
        f_end_date (string): Forecast end date

    Returns:
        Div: Div container of datepicker range
    """

    date_picker_range_panel = html.Div(
        [
            "Forecast start date + 5 days",
            dcc.DatePickerRange(
                id="forecast-range",
                display_format="DD/MM/YYYY",
                start_date=f_start_date,
                end_date=f_end_date,
                disabled=True,
            ),
        ],
        className="forecast-range",
    )

    return date_picker_range_panel


def get_date_picker_range_button():
    """Get date picker range button

    Returns:
        Button: Button to display information about forecast date range
    """

    info_button = dbc.Button(
        "i",
        id="forecast-range-date-info-btn",
        color="primary",
        className="mb-3 info-button",
        n_clicks=0,
    )
    return info_button


def get_date_picker_range_popover():
    """Get date picker range popover

    Returns:
        Popover: Popover to display information about forecast date range
    """
    
    info_popover = dbc.Popover(
        [
            dbc.PopoverHeader("Why can I only see data for today and five days ahead?"),
            dbc.PopoverBody(
                "SPLASH provides forecast of wave overtopping up to 5 days ahead. This model uses Met Office wave and wind data as input that is limited to a 5-day forecast. The model is updated once a day using Met Office wave and wind data as input, as well as predicted water level."
            ),
        ],
        id="forecast-range-date-info",
        target="forecast-range-date-info-btn",
        trigger="legacy",
        hide_arrow=True,
    )
    return info_popover
