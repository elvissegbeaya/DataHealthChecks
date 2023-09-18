# components/navbar.py
from dash import html

layout = html.Div([
    html.A('Home', href='/'),
    html.A('UpdateToken', href='/UpdateToken'),
    html.A('Single Job Lookup', href='/SingleJob_Report'),
    html.A('All Active Jobs', href='/AllActiveJobs'),
    html.A('EDR Report', href='/EDR_Report'),
    html.A('RAE Report', href='/RAE_Report'),
    html.A('All Active Jobs Report Status', href='/AllActiveJobsStatus_Report'),
    html.A('GAS Report', href='/GAS_Report'),
    html.A('GWA Report', href='/GWA_Report'),
    # ... other navigation items
])
