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
from app import app, lookup_table,token
from pages import page1, page2, AllActiveJobs,EDR_Report,GAS_Report,GWA_Report,Lookup_Page,Singlejob_Report,RAE_Report,UpdateToken
from components import navbar





def update_lookup():
    global token
    if token is None:
        try:
            # Get the token
            token_response = requests.get(
                "https://data.welldata.net/api/v1/tokens/token",
                headers={"accept": "application/json", "ApplicationID": "00258061-5290-41AA-A63D-0B84E00FDA11"},
                params={},
                auth=HTTPBasicAuth(username="EDR_RestAPI", password="59ee#NK0sxtB"))

            token_response.raise_for_status()  # raise exception if the request failed

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting token: {err}")

        # Extract the token from the response
        token = token_response.json().get('token')  # replace 'token' with the correct field if different
        emoji_check = u'\u2705'  # ✅

        # Now that we have the token, we need to update the Lookup Table
        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']
            data_response.raise_for_status()  # raise exception if the request failed

            for w in values:
                # jobs.append([w['id'], w['assetInfoList'][0]['owner'], w['assetInfoList'][0]['name']])
                key = f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}"
                # key = w['siteInfoList'][0]['owner']
                value = w['id']
                lookup_table[key] = value
        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting token: {err}")

        return lookup_table
    else:
        # Now that we have the token, we need to update the Lookup Table
        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']
            data_response.raise_for_status()  # raise exception if the request failed

            for w in values:
                # jobs.append([w['id'], w['assetInfoList'][0]['owner'], w['assetInfoList'][0]['name']])
                key = f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}"
                # key = w['siteInfoList'][0]['owner']
                value = w['id']
                lookup_table[key] = value
        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting token: {err}")

        return lookup_table

    return ''

# setting lookup table
lookup_table = update_lookup()


@app.callback(Output('lookup-container', 'children'), [Input('lookup-table-button', 'n_clicks')])
def lookup_data(n):
    lookup_table = lookup_table
    total = 0
    tmpJobs = []
    if n and n > 0:
        if token is None and lookup_table is None:
            lookup_table = update_lookup()
            return html.Div("No token available. Please generate a token first.")

        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']
            data_response.raise_for_status()  # raise exception if the request failed

            for w in values:
                # jobs.append([w['id'], w['assetInfoList'][0]['owner'], w['assetInfoList'][0]['name']])
                key = f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}"
                # key = w['siteInfoList'][0]['owner']
                value = w['id']
                lookup_table[key] = value

            # app.layout = html.Div([
            #     html.H1('Lookup Table'),
            #     html.Div([
            #         html.Div([html.Span(f"{key}: "), html.Span(value)])
            #         for key, value in sorted(lookup_table.items())
            #     ])
            # ])

            # app.layout = html.Div([
            #     html.H1('Lookup Table'),
            #     html.Div([
            #         html.Div(id='value-display', style={'marginRight': '20px'}),
            #         html.Div([
            #             html.Button(key, id={'type': 'dynamic-button', 'index': key},
            #                         style={'border': 'thin lightgrey solid',
            #                                'padding': '10px',
            #                                'margin': '10px',
            #                                'maxWidth': '100px',
            #                                'textOverflow': 'ellipsis',
            #                                'overflow': 'hidden',
            #                                'whiteSpace': 'nowrap'})
            #             for key in sorted(lookup_table.keys())
            #         ], style={'display': 'flex',
            #                   'grid-template-columns': 'repeat(minmax(200px, 1fr), minmax(200px, 1fr))',
            #                   'grid-gap': '10px',
            #                   'overflow': 'auto',
            #                   'maxHeight': '80vh'
            #                   })
            #     ], style={'display': 'flex','grid-template-columns': 'repeat(minmax(200px, 1fr), minmax(200px, 1fr))'}),
            # ])
            app.layout = html.Div([
                html.H1('Lookup Table'),
                html.Div([
                    html.Div(id='value-display', style={'paddingLeft': '40px', 'width': '500px', }),
                    dcc.Dropdown(
                        id='dropdown',
                        options=[{'label': key, 'value': key} for key in sorted(lookup_table.keys())],
                        placeholder='Select a key',
                        style={'width': '500px'}
                    ),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'row-reverse',
                    'justifyContent': 'center',
                    'alignItems': 'center'

                }),
            ])




        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

        return app.layout

    return ''

@app.callback(
    Output('value-display', 'children'),
    [Input('dropdown', 'value')]
)
def display_value(value):
    if value is None:
        return ''
    return html.Div(f"{value}: {lookup_table[value]}")
