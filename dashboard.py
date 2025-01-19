import dash
import dash.dcc as dcc
from dash import html
import plotly.express as px
import pandas as pd
import dawlish_final_digital_twin_script_upgraded as ddt
import penzance_final_digital_twin_script_upgraded as pdt
import dash_bootstrap_components as dbc


def get_dawlish_wave_overtopping():
    final_DawlishTwin_dataset = ddt.get_digital_twin_dataset()
    df_adjusted = ddt.adjust_features(final_DawlishTwin_dataset)
    data_rf1_rf2_tmp, data_rf3_rf4_tmp = ddt.process_wave_overtopping(df_adjusted)
    return data_rf1_rf2_tmp, data_rf3_rf4_tmp

data_rf1_rf2, data_rf3_rf4 = get_dawlish_wave_overtopping()

# Sample data for the line plots
df_line = pd.DataFrame({
    "Date": pd.to_datetime(
        ["10-12-2024", "11-12-2024", "12-12-2024", "13-12-2024", "14-12-2024", "15-12-2024"], dayfirst=True
    ),
    "Value": [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
})

external_stylesheets = ['./assets/css/dashboard.css']
app = dash.Dash(external_stylesheets=external_stylesheets)

# Rendering Dawlish plot
def render_overtopping_plot(plot_title, plot_logo, overtopping_data):

    fig_rf1_rf2_tmp = px.scatter(
        overtopping_data,
        x='Time',
        y='Overtopping Count',
        color_continuous_scale=['aqua', 'skyblue', 'blue'],
        labels={
            'Time': 'Time',
            'Overtopping Count': 'No. of Overtopping Occurrences (Per 10 Mins)',
            'Confidence': 'Confidence Level'
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
                for c, o in zip(overtopping_data['Confidence'], overtopping_data['Overtopping Count'])
            ],
            color=[
                'black' if o == 0 else
                '#FF0004' if c > 0.80 and o > 0 else
                '#2A5485' if c >= 0.50 and c <= 0.8 and o > 0 else
                '#AAD3E3' if c < 0.50 and o > 0 else
                '#AAD3E3' 
                for c, o in zip(overtopping_data['Confidence'], overtopping_data['Overtopping Count'])
            ],
            line_color=[
                'black' if o == 0 else
                'red' if c > 0.80 and o > 0 else
                '#2A5485' if c >= 0.50 and c <= 0.80 and o > 0 else
                '#AAD3E3' if c < 0.50 and o > 0 else
                '#AAD3E3' 
                for c, o in zip(overtopping_data['Confidence'], overtopping_data['Overtopping Count']) # Corrected order
            ]
        )
    )

    fig_rf1_rf2_tmp.add_hline(y=6, line_dash='dash', line_color='#8A8D90', annotation_text='25% IQR (6)')
    fig_rf1_rf2_tmp.add_hline(y=54, line_dash='dash', line_color='#8A8D90', annotation_text='75% IQR (54)')

    return fig_rf1_rf2_tmp

# Plot for RF1 & RF2 - Dawlish Seawall Crest
fig_rf1_rf2 = render_overtopping_plot('Dawlish Seawall Crest', 'dawlish_seawall_crest.png', data_rf1_rf2)
# Plot for RF3 & RF4 - Dawlish Railway Line
fig_rf3_rf4 = render_overtopping_plot('Dawlish Railway Line', 'dawlish_railway_line.png', data_rf3_rf4)

# Create the line plots
fig_line1 = px.line(
    df_line,
    x="Date",
    y="Value",
    title="Dawlish - Significant wave height",
    width=800,
    height=600,
)

fig_line2 = px.line(
    df_line,
    x="Date",
    y="Value",
    title="Dawlish - Freeboard",
    width=800,
    height=600,
)

fig_line3 = px.line(
    df_line,
    x="Date",
    y="Value",
    title="Dawlish - Wind speed",
    width=800,
    height=600,
)

# Create the app
app = dash.Dash(__name__)


# App layout
app.layout = dbc.Container([
    dbc.Row([
        html.Div(
        children=[
            html.Div(
                children=[
                    html.Img(src="./assets/imgs/splash_logo.png", style={'width': '120.77px', 'height': '102.19px', 'margin-top': '15.61px'}),  # Add image here
                    html.Div(
                        children=[
                            html.Div("SPLASH", style={'color': '#3279B7', 'font-size': '87.22px', 'font-family': 'Viga', 'font-weight': '400', 'line-height': '104.66px', 'letter-spacing': '2.62px'}),
                            html.Div("DIGITAL APPROACHES TO PREDICT WAVE OVERTOPPING HAZARDS", style={'color': '#2A5485', 'font-size': '20.87px', 'font-family': 'Urbanist', 'font-weight': '600', 'line-height': '31.31px', 'letter-spacing': '0.83px', 'margin-top': '10px'})
                        ],
                        style={'width': '784.23px', 'height': '121.31px', 'margin-left': '34.92px'}
                    )
                ],
                className="head-container"
            )
        ],
        style={'padding-left': '72px'}
    )]),
    dbc.Row(
        html.Div("Advancing current understanding on wave-related coastal hazards", className="dashboard-description"),
        style={'padding-left': '72px'}
    ),
    dbc.Row(
        html.Div("With sea level rise accelerating and weather extremes becoming increasingly stronger, tools to help climate adaptation of coastal communities are of paramount importance. SPLASH provides an overtopping tool that will act as forecast model directly helping coastal communities mitigate effects of this coastal hazard, and ultimately, guiding new climate adaptation strategies.", className="dashboard-summary"),
        style={'padding-left': '72px'}
    ),
    dbc.Row([
        dbc.Col([
            html.Div(
                children=[
                    html.Div("Key", style={'color': 'black', 'font-size': '14.40px', 'font-family': 'Helvetica Neue', 'font-weight': '700', 'line-height': '21.60px', 'margin-top': '5px', 'width': '65px'}),
                    html.Div(
                        children=[
                            html.Div(style={'width': '26px', 'height': '26px', 'border-radius': '9999px', 'border': '2px #FF0004 solid', 'margin-left': '18px', 'margin-top': '3px'}),
                            html.Div("High confidence > 80%", style={'color': 'black', 'font-size': '12px', 'font-family': 'Helvetica Neue', 'font-weight': '400', 'line-height': '16.80px', 'margin-left': '11px', 'width': '88px'})
                        ],
                        style={'display': 'flex', 'margin-left': '37px'}
                    ),
                    html.Div(
                        children=[
                            html.Div(style={'width': '26px', 'height': '26px', 'background': '#2A5485', 'border-radius': '9999px', 'margin-top': '3px'}),
                            html.Div("Medium confidence 50-80%", style={'color': 'black', 'font-size': '12px', 'font-family': 'Helvetica Neue', 'font-weight': '400', 'line-height': '16.80px', 'margin-left': '11px', 'width': '107px'}),
                        ],
                        style={'display': 'flex', 'margin-left': '37px'}
                    ), 
                    html.Div(
                        children=[
                            html.Div(style={'width': '24px', 'height': '24px', 'background': '#AAD3E3', 'margin-top': '4px'}),
                            html.Div("Low confidence < 50%", style={'color': 'black', 'font-size': '12px', 'font-family': 'Helvetica Neue', 'font-weight': '400', 'line-height': '16.80px', 'margin-left': '11px', 'width': '86px'})
                        ],
                        style={'display': 'flex', 'margin-left': '37px'}
                    ),
                    html.Div(
                        children=[
                            html.Img(src='./assets/imgs/no_overtopping_marker.png', style={'width': '20px', 'height': '20px', 'margin-top': '6px'}),  # Add the image here   
                            html.Div("No overtopping", style={'color': 'black', 'font-size': '12px', 'font-family': 'Helvetica Neue', 'font-weight': '400', 'line-height': '16.80px', 'margin-top': '8px', 'margin-left': '11px', 'width': '84px'})
                            ],
                        style={'display': 'flex', 'margin-left': '37px'}
                    ),
                    html.Div(
                        children=[
                            html.Div(style={'width': '46px', 'height': '0px', 'border': '1px #8A8D90 dashed', 'margin-top': '16px'}),
                            html.Div("Interquartile range (25th and 75th)", style={'color': 'black', 'font-size': '12px', 'font-family': 'Helvetica Neue', 'font-weight': '400', 'line-height': '16.80px', 'margin-left': '11px', 'width': '101px'}),
                        ],
                        style={'display': 'flex', 'margin-left': '37px'}
                    ),

                ],
                className="dawlish-legend"
            )
        ], width=10, style={"padding": "22px 72px"})
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="scatter-plot-dsc", figure=fig_rf1_rf2)
        ], width=12, style={'border': '1.011px solid #8A8D90'})    
    ], style={'padding': '0px 72px'}),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="scatter-plot-drl", figure=fig_rf3_rf4)
        ], width=12, style={'border': '1.011px solid #8A8D90'})    
    ], style={'padding': '24px 72px'}),

    # dbc.Row([
    #     dcc.Graph(id="line-plot1", figure=fig_line1),
    # ]),

    # dbc.Row([
    #     dcc.Graph(id="line-plot2", figure=fig_line2),
    # ]),

    # dbc.Row([
    #     dcc.Graph(id="line-plot3", figure=fig_line3),
    # ])
], fluid=True, className='body-container')

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)