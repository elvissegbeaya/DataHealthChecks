# pages/AllActiveJobs.py
import time
import timeit
from datetime import date
import dash
import pandas as pd
import requests
from cachetools import LFUCache, cached
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth
from tenacity import retry, stop_after_attempt, wait_fixed
# from cachetools import cached, TTLCache, Cache, LFUCache, LRU Cache
from functools import lru_cache
import json
import sqlite3
import threading
import configparser
import dash_core_components as dcc
import dash_html_components as html
import queue
import plotly.express as px
import concurrent.futures
from app import app
from app import app
from pages import page1, page2, AllActiveJobs,EDR_Report,GAS_Report,GWA_Report,Lookup_Page,Singlejob_Report,RAE_Report,UpdateToken
from components import navbar

@app.callback(Output('data-container', 'children'), [Input('get-data-button', 'n_clicks')])
def get_data(n):
    total = 0
    tmpJobs = []
    well_operator = ''
    well_contractor = ''
    if n and n > 0:
        if app.token is None:
            return html.Div("No token available. Please generate a token first.")

        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"

            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']
            data_response.raise_for_status()  # raise exception if the request failed
            for w in values:
                tmpJobs.append(
                    [w['id'], f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}", w['assetInfoList'][0]['owner'], w['siteInfoList'][0]['owner'], w['startDate'],
                     w['firstDataDate'], w['lastDataDate']])

                # tmpJobs.append(w['id'])
                # tmpJobs.append(f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}")  # Rig Name
                # # set operator and contractor
                # tmpJobs.append(w['assetInfoList'][0]['owner'])  # Contractor
                # tmpJobs.append(w['siteInfoList'][0]['owner'])  # Operator
                # tmpJobs.append(w['startDate'])
                # tmpJobs.append(w['firstDataDate'])
                # tmpJobs.append(w['lastDataDate'])

            for w in values:
                key = f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}"
                value = w['id']
                lookup_table[key] = value

            header = ['Job Id', 'Rig', 'Contractor', 'Operator', 'Start Date', 'First Data Date', 'Last Data Date']
            df = pd.DataFrame(tmpJobs, columns=header)
            print(df.shape)
            # df.columns = header
            results = html.Div([
                html.H1(f"--Quick Look: All Active Job--", style={'text-align': 'center'}),
                dash_table.DataTable(
                    data=df.to_dict('records'),  # convert the DataFrame to a dictionary
                    columns=[{'name': i, 'id': i} for i in df.columns],  # create a list of dictionaries for each column
                    sort_action='native',
                    page_current=0,
                    page_size=10,
                    page_action='native',
                    style_cell={'whiteSpace': 'normal', 'height': 'auto', 'width': '70%', 'text-align': 'left'},
                )
            ])

            return html.Div(results)

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

        # Return an empty Div if n is None or 0
        return html.Div()

layout = html.Div([
    html.H1('UpdateToken'),
    # ... other components specific to UpdateToken
])

# Add any callbacks specific to this page here
