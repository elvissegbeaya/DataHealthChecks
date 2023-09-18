# app.py
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



class UnitV1(BaseModel):
    id: str
    name: str
    abbreviation: str


class Attribute(BaseModel):
    id: str
    mode: str


@retry(stop=stop_after_attempt(4), wait=wait_fixed(2), retry_error_callback=lambda _: print("Retrying..."))
class HistoricalTimeRequest(BaseModel):
    attributes: list
    fromTime: str
    toTime: str
    interval: float
    isDifferential: bool = False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry_error_callback=lambda _: print("Retrying..."))
def historical_data_time(job_id: str, payload: HistoricalTimeRequest, token: any):
    """
    args
        job
        payload
    """
    uri = f'https://data.welldata.net/api/v1/jobs/{job_id}/data/time'
    header = {'token': token}
    r = requests.post(uri, data=payload, headers=header)
    # print(r.status_code)
    return r.json()


''' Database '''

# Creating a database using SQL Lite
# Create a connection to the SQLite database
conn = sqlite3.connect('cache.db')

# Create a cursor to execute SQL commands
c = conn.cursor()

# Create a table if it doesn't exist
c.execute("""
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY_KEY,
    value TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")


# Delete data that's a day old.
c.execute("""
DELETE FROM cache 
WHERE timestamp < datetime('now', '-1 day')
""")
conn.commit()

# Create a cursor object
cur = conn.cursor()

#Printing DB to console

# # Execute a query to fetch all data from the table
# cur.execute("SELECT * FROM cache")


# # Fetch all rows from the last executed statement using fetchall()
# rows = cur.fetchall()
#
# # Loop through the rows and print them to the console
# for row in rows:
#     print(row)


'''Caching Layer '''
'''Setting Cache size '''
cache = LFUCache(maxsize=1000000)  # Adjust the maxsize as needed


# Define a function to get a value from the cache
@cached(cache)
def get_from_cache(key):
    with sqlite3.connect('cache2.db') as conn:
        c = conn.cursor()
        c.execute("SELECT value FROM cache WHERE key=?", (key,))
        result = c.fetchone()
        if result:
            return json.loads(result[0])
        else:
            return None


def add_to_cache(key, value):
    # Add to in-memory LFU cache.
    cache[key] = value
    with sqlite3.connect('cache2.db') as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)", (key, json.dumps(value)))
        conn.commit()


''' Configuration calls '''

config = configparser.ConfigParser()

# Read the config file
config.read('DataChecks.cfg')

# Pulling sections from Config
# EDR_Rigs = [value for key, value in config['DEFAULT'].items()]
# RAE_Rigs = [value for key, value in config['RAERigs'].items()]
# OdessaRigs = [value for key, value in config['OdessaRigs'].items()]
# MidconRigs = [value for key, value in config['MidconRigs'].items()]
# GulfCoastRigs = [value for key, value in config['GulfCoastRigs'].items()]
# DuboisRigs = [value for key, value in config['DuboisRigs'].items()]
# WillistonRigs = [value for key, value in config['WillistonRigs'].items()]


app = Dash(__name__)

# # Initialize the Flask-Caching
# cache = Cache(app.server)

#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

# Add a global variable to store the token and input value
token = None
JobID = None
header = ['Contractor', 'Rig Number', 'Operator', 'Well name', 'IADC', 'IADC 2', 'IADC3', 'HookLoad', 'PumpPressure', 'BlockHeight', 'PumpSpm', 'PumpSpm2', 'PumpSpm3',
          'RotaryTorque', 'TopDrive RPM',
          'TopDrive Torque', 'WOB', 'ROP-F', 'T-HL', 'BitPosition', 'BitStatus', 'SlipStatus', 'Comments', 'Next 24 Hr Comments', 'Report Id', 'Report Date']
# Variables
tmpAllJobs = []
lookup_table = {}
data_frames ={}
JobsList = []
current_threads = {}
task_results = {"edrJobs": None, "activeJobs":None,"raeJobs": None}  # Used for LRU Cache

# Serialize the task_result dictionary into a JSON string
task_result_json = json.dumps(task_results)

