# index.py
from dash import html
from dash.dependencies import Input, Output

from app import app
from pages import page1, page2, AllActiveJobs, EDR_Report, GAS_Report, GWA_Report, Lookup_Page, Singlejob_Report, RAE_Report, UpdateToken, AllActiveJobsStatus_Report
from components import navbar

app.layout = html.Div([
    navbar.layout,
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/UpdateToken':
        return UpdateToken.layout
    elif pathname == '/AllActiveJobs':
        return AllActiveJobs.layout
    elif pathname == '/EDR_Report':
        return EDR_Report.layout
    elif pathname == '/RAE_Report':
        return RAE_Report.layout
    elif pathname == '/GAS_Report':
        return GAS_Report.layout
    elif pathname == '/GWA_Report':
        return GWA_Report.layout
    elif pathname == '/SingleJob_Report':
        return Singlejob_Report.layout
    elif pathname == '/AllActiveJobsStatus_Report':
        return AllActiveJobsStatus_Report.layout
    else:
        return '404 - Page not found'
