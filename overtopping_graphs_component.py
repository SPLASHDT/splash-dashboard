from dash import dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc


PERCENTAGE_MIN_VAL_SLIDER = -100
PERCENTAGE_MAX_VAL_SLIDER = 100
DEGREE_MIN_VAL_SLIDER = -180
DEGREE_MAX_VAL_SLIDER = 180
PERCENTAGE_CHAR = '%'
DEGREE_CHAR = '°'


# Render overtopping plot
def render_overtopping_plot(plot_title, plot_logo, overtopping_data):

    fig_rf1_rf2_tmp = px.scatter(
        overtopping_data,
        x='time',
        y='overtopping_count',
        color_continuous_scale=['aqua', 'skyblue', 'blue'],
        height=513,
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
            x=0.25, y=1,  # Adjust position as needed
            sizex=0.06, sizey=0.06,  # Adjust size as needed
            xanchor="left", yanchor="bottom"
        )
    )

    fig_rf1_rf2_tmp.update_layout(
        title=dict(
            text=plot_title,  # Just the text title
            font=dict(
                family='Helvetica Neue',
                size=22,
                color='#3279B7',
                weight=500
            ),
            xref="paper", yref="paper",
            x=0.3, y=1,  # Adjust title position if necessary
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
            size=12,
            symbol=[
                'x-thin' if o == 0 else
                'circle-open' if c > 0.80 and o > 0 else
                'circle' if c >= 0.50 and c <= 0.8 and o > 0 else
                'square' if c < 0.50 and o > 0 else
                'circle' 
                for c, o in zip(overtopping_data['confidence'], overtopping_data['overtopping_count'])
            ],
            color=[
                '#000' if o == 0 and s == 'previous' else
                '#808080' if c > 0.80 and o > 0 and s == 'previous' else
                '#585858' if c >= 0.50 and c <= 0.8 and o > 0 and s == 'previous' else
                '#C7C7C7' if c < 0.50 and o > 0 and s == 'previous' else
                '#FF00CC' if o == 0 and s == 'current' else
                '#FF0004' if c > 0.80 and o > 0 and s == 'current' else
                '#2A5485' if c >= 0.50 and c <= 0.8 and o > 0 and s == 'current' else
                '#AAD3E3' if c < 0.50 and o > 0 and s == 'current' else
                '#AAD3E3' 
                for c, o, s in zip(overtopping_data['confidence'], overtopping_data['overtopping_count'], overtopping_data['stage'])
            ],
            line_color=[
                '#000' if o == 0 and s == 'previous' else
                '#808080' if c > 0.80 and o > 0 and s == 'previous' else
                '#585858' if c >= 0.50 and c <= 0.80 and o > 0 and s == 'previous' else
                '#C7C7C7' if c < 0.50 and o > 0 and s == 'previous' else                          
                '#FF00CC' if o == 0 and s == 'current' else
                '#FF0004' if c > 0.80 and o > 0 and s == 'current' else
                '#2A5485' if c >= 0.50 and c <= 0.80 and o > 0 and s == 'current' else
                '#AAD3E3' if c < 0.50 and o > 0 and s == 'current' else
                '#AAD3E3' 
                for c, o, s in zip(overtopping_data['confidence'], overtopping_data['overtopping_count'], overtopping_data['stage']) # Corrected order
            ]
        )
    )

    fig_rf1_rf2_tmp.add_hline(y=6, line_dash='dash', line_color='#8A8D90', annotation_text='25% IQR (6)')
    fig_rf1_rf2_tmp.add_hline(y=54, line_dash='dash', line_color='#8A8D90', annotation_text='75% IQR (54)')

    return fig_rf1_rf2_tmp


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


def get_variable_slider(identifier, min_value, max_value, template_symbol, decrease_btn_id, increase_btn_id):
    variable_slider =  html.Div(
        children = [
            html.Div(
                html.Button(
                    id=decrease_btn_id,
                    children = [
                        html.Img(src='./assets/imgs/minus-icon.png', className='action-button-img'),
                    ],
                    className='action-button'
                ),
                className='slider-button-panel'
            ),         
            html.Div(
                dcc.Slider(id=identifier, min=min_value, max=max_value, step=1, value=min_value, marks=None, 
                        tooltip={
                            'always_visible': True,
                            'template': '{value}' + template_symbol,
                            'placement': 'top', 
                            'style': {'color': '#2A5485', 'fontFamly': 'Helvetica Neue', 'fontSize': '18px', 'fontStyle': 'normal', 'fontWeight': '400', 'lineHeight': '160%'},
                        },
                ),
                style={'padding': '25px 25px 0px', 'width': '508px'}
            ),
            html.Div(
                html.Button(
                    id=increase_btn_id,
                    children = [
                        html.Img(src='./assets/imgs/plus-icon.png', className='action-button-img'),
                    ],
                    className='action-button'
                ),
                    className='slider-button-panel'
            ),
        ],
        className='slider-panel'
    )
    return variable_slider


def get_wave_variables_panels():
    # Wave variables and mean wave direction panels
    wave_variables_panels = dbc.Container(
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(
                            'Adjusted data', className='adjusted-data-panel'
                        ),
                        # Significant wave height
                        html.Div(
                            children=[
                                html.Div(
                                    'Significant wave height',
                                    className='variable-full-title'
                                ),
                                html.Div(
                                    'Hs [metres]',
                                    className='variable-short-title'
                                )
                            ],
                            className='variable-section',
                            style={'paddingTop': '32px'}
                        ),
                        get_variable_slider('sig-wave-height', PERCENTAGE_MIN_VAL_SLIDER, PERCENTAGE_MAX_VAL_SLIDER, PERCENTAGE_CHAR, 'swh-decrease-btn', 'swh-increase-btn'),
                        # Freeboard
                        html.Div(
                            children=[
                                html.Div(
                                    'Tidal level',
                                    className='variable-full-title'
                                ),
                                html.Div(
                                    'Rc [metres]',
                                    className='variable-short-title'
                                )
                            ],
                            className='variable-section'
                        ),
                        get_variable_slider('freeboard', PERCENTAGE_MIN_VAL_SLIDER, PERCENTAGE_MAX_VAL_SLIDER, PERCENTAGE_CHAR, 'fb-decrease-btn', 'fb-increase-btn'),
                        # Mean Wave Period
                        html.Div(
                            children=[
                                html.Div(
                                    'Mean wave period',
                                    className='variable-full-title'
                                ),
                                html.Div(
                                    'Tz [seconds]',
                                    className='variable-short-title'
                                )
                            ],
                            className='variable-section'
                        ),
                        get_variable_slider('mean-wave-period', PERCENTAGE_MIN_VAL_SLIDER, PERCENTAGE_MAX_VAL_SLIDER, PERCENTAGE_CHAR, 'mwp-decrease-btn', 'mwp-increase-btn'),
                    ])

                ),
                md=7,
                style={'padding': '38px 0px 0px 87px'}
            ),
            dbc.Col(
                dbc.Card(
                dbc.CardBody(
                    [
                        # Mean wave direction
                        html.Div(
                            children=[
                                html.Div(
                                    'Mean wave direction',
                                    className='variable-full-title'
                                ),
                                html.Div(
                                    'Dir [degrees]',
                                    className='variable-short-title'
                                )
                            ],
                            className='variable-section'
                        ),
                        get_variable_slider('mean-wave-direction', DEGREE_MIN_VAL_SLIDER, DEGREE_MAX_VAL_SLIDER, DEGREE_CHAR, 'mwd-decrease-btn', 'mwd-increase-btn'),
                    ]
                )
                ),
                md=5,
                style={'padding': '38px 67px 0px 16px'}
            )
        ]), 
        fluid=True
    )
    return wave_variables_panels


def get_atmospheric_variables_panels():
    atmospheric_variables_panels = dbc.Container(
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(
                            'Adjusted data', className='adjusted-data-panel'
                        ),
                        # Wind speed
                        html.Div(
                            children=[
                                html.Div(
                                    'Wind speed',
                                    className='variable-full-title'
                                ),
                                html.Div(
                                    'U10 [metres per second]',
                                    className='variable-short-title'
                                )
                            ],
                            className='variable-section'
                        ),
                        get_variable_slider('wind-speed', PERCENTAGE_MIN_VAL_SLIDER, PERCENTAGE_MAX_VAL_SLIDER, PERCENTAGE_CHAR, 'ws-decrease-btn', 'ws-increase-btn'),
                    ])

                ),
                md=7,
                style={'padding': '39px 0px 0px 87px'}
            ),
            dbc.Col(
                dbc.Card(
                dbc.CardBody(
                    [
                        # Wind direction
                        html.Div(
                            children=[
                                html.Div(
                                    'Wind direction',
                                    className='variable-full-title'
                                ),
                                html.Div(
                                    'U10 Dir [degrees]',
                                    className='variable-short-title'
                                )
                            ],
                            className='variable-section'
                        ),
                        get_variable_slider('wind-direction', DEGREE_MIN_VAL_SLIDER, DEGREE_MAX_VAL_SLIDER, DEGREE_CHAR, 'wd-decrease-btn', 'wd-increase-btn'),
                    ]
                )
                ),
                md=5,
                style={'padding': '39px 67px 0px 16px'}
            )
        ]), 
        fluid=True
    )
    return atmospheric_variables_panels


def get_buttons_panel():
    buttons_panel = dbc.Container(
        dbc.Row([
            dbc.Col(
                dbc.Button('Submit', id='submit-button', style={'backgroundColor':'#2A5485', 'borderColor': '#2A5485', 'width': '180px', 'height': '48px'}),
                md=4,
            ),
            dbc.Col(
                dbc.Button('Reset all', id='reset-button', color='link'),
                md=4

            )],
            style={'padding': '38px 0px 0px 87px'}
        ), 
        fluid=True
    )

    return buttons_panel


def get_legend_panel():
    legend_component = html.Div([
        dbc.Row([
            dbc.Col(html.Div('Key'), md=1, class_name='key-subtitle-legend'),
            dbc.Col(html.Div(
                'Previous', 
                className='stage-subtitle-legend'
                ), 
            md=1),
            dbc.Col(html.Div(
                        children=[
                            html.Div(className='high-confidence-marker', style={'borderColor': '#808080'}),
                            html.Div('High confidence > 80%', className='high-confidence-subtitle')
                        ],
                        style={'display': 'flex', 'marginLeft': '11px'}
            ),
            md=2),
            dbc.Col(html.Div(
                        children=[
                            html.Div(className='medium-confidence-marker', style={'background': '#585858'}),
                            html.Div('Medium confidence 50-80%', className='medium-confidence-subtitle'),
                        ],
                        style={'display': 'flex', 'marginLeft': '11px'}
            ),
            md=2),
            dbc.Col(html.Div(
                        children=[
                            html.Div(className='low-confidence-marker', style={'background': '#C7C7C7'}),
                            html.Div('Low confidence < 50%', className='low-confidence-subtitle')
                        ],
                        style={'display': 'flex', 'marginLeft': '11px'}
            ),
            md=2),
            dbc.Col(html.Div(
                        children=[
                            html.Img(src='./assets/imgs/prev_no_overtopping_marker.png', className='no-overtopping-marker'), 
                            html.Div('No overtopping', className='no-overtopping-subtitle')
                            ],
                        style={'display': 'flex', 'marginLeft': '11px'}
            ),
            md=2),
            dbc.Col(html.Div(
                        children=[
                            html.Div(className='interquartile-range-marker'),
                            html.Div('Interquartile range (25th and 75th)', className='interquartile-range-subtitle'),
                        ],
                        style={'display': 'flex', 'marginLeft': '11px'}
            ),
            md=2)
        ]),
        dbc.Row([
            dbc.Col(md=1, class_name='key-subtitle-legend'),
            dbc.Col(html.Div(
                'Updated', 
                className='stage-subtitle-legend'
                ), 
            md=1),
            dbc.Col(html.Div(
                        children=[
                            html.Div(className='high-confidence-marker'),
                            html.Div('High confidence > 80%', className='high-confidence-subtitle')
                        ],
                        style={'display': 'flex', 'marginLeft': '11px'}
            ),
            md=2),
            dbc.Col(html.Div(
                        children=[
                            html.Div(className='medium-confidence-marker'),
                            html.Div('Medium confidence 50-80%', className='medium-confidence-subtitle'),
                        ],
                        style={'display': 'flex', 'marginLeft': '11px'}
            ),
            md=2),
            dbc.Col(html.Div(
                        children=[
                            html.Div(className='low-confidence-marker'),
                            html.Div('Low confidence < 50%', className='low-confidence-subtitle')
                        ],
                        style={'display': 'flex', 'marginLeft': '11px'}
            ),
            md=2),
            dbc.Col(html.Div(
                        children=[
                            html.Img(src='./assets/imgs/no_overtopping_marker.png', className='no-overtopping-marker'), 
                            html.Div('No overtopping', className='no-overtopping-subtitle')
                            ],
                        style={'display': 'flex', 'marginLeft': '11px'}
            ),
            md=2),
            dbc.Col(html.Div(
                        children=[
                            html.Div(className='interquartile-range-marker'),
                            html.Div('Interquartile range (25th and 75th)', className='interquartile-range-subtitle'),
                        ],
                        style={'display': 'flex', 'marginLeft': '11px'}
            ),
            md=2)
        ],
        style={'paddingTop': '7px'})
    ],
    className='overtopping-legend')
    
    return legend_component


def get_dropdown_panel():
    dropdown_panel = html.Div([
            'Site location',
            dcc.Dropdown(
                id='dd_site_location',
                options=['Dawlish', 'Penzance', 'Dawlish Storm Bert - overtopping', 'Penzance Storm Bert - overtopping', 'Dawlish - no overtopping', 'Penzance - no overtopping'],
                value='Dawlish',
                clearable=False,
                className='site-dropdown'
            )
        ], 
        className='label-dropdown'
    )

    return dropdown_panel
