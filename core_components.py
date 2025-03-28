from dash import html
import dash_bootstrap_components as dbc

DASHBOARD_NAME = 'SPLASH'
DASHBOARD_BRIEF_DESCRIPTION = 'DIGITAL APPROACHES TO PREDICT WAVE OVERTOPPING HAZARDS'
ABOUT_SPLASH_LINK = 'https://www.plymouth.ac.uk/research/coastal-processes/splash-project'
GITHUB_REPO_LINK = 'https://github.com/orgs/SPLASHDT/repositories'

def get_header_components():
    header_components = [ 
        dbc.Col(html.Div(html.Img(src='./assets/imgs/splash_logo.png', className='splash-logo'), className='splash-logo-panel'), md=1),
        dbc.Col(
                html.Div(
                    children=[
                        html.Div(DASHBOARD_NAME, className='dashboard-title'),
                        html.Div(DASHBOARD_BRIEF_DESCRIPTION, className='dashboard-sub-title')
                    ],
                    className='title-sub-title-container'
                ), md=7),
        dbc.Col(
            html.Div(
                children = [
                    dbc.Button('About SPLASH', id='about-splash', href=ABOUT_SPLASH_LINK, n_clicks=0, class_name='header-button'),
                    html.Div(dbc.Button('Github repository', id='github-repo', href=GITHUB_REPO_LINK, n_clicks=0, class_name='header-button'), style={'paddingTop': '14px'}),
                ], className='header-buttons-panel'
            ), md=4
        )
    ]
    return header_components


def get_footer_components():
    footer_components = [
        dbc.Col(html.Div(html.Img(src='./assets/imgs/uni_plymouth_logo.png', className='uni-plymouth-logo')), md=5, className='uni-plymouth-logo-panel'),
        dbc.Col(html.Div(html.Img(src='./assets/imgs/noc_logo.png', className='noc-logo')), md=1, className='noc-logo-panel'),
        dbc.Col(html.Div(html.Img(src='./assets/imgs/ukri_met_office_logos.png', className='ukri-met-office-logos')), md=4, className='ukri-met-office-logos-panel'),
    ]
    return footer_components