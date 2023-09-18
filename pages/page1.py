# pages/page1.py
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


layout = html.Div([
    html.H1('Page 1'),
    # ... other components specific to Page 1
])

# Add any callbacks specific to this page here
