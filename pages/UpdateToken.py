# pages/UpdateToken.py
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

def update_token(n):
    global token
    if n and n > 0:
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
        return html.Div(f"Token: {emoji_check}")

    return ''
layout = html.Div([
    html.H1('UpdateToken'),
    # ... other components specific to UpdateToken
])

# Add any callbacks specific to this page here
