# pages/RAE_Report.py
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
from app import app, token, historical_data_time, HistoricalTimeRequest, Attribute, add_to_cache, get_from_cache
from app import app
from pages import page1, page2, AllActiveJobs,EDR_Report,GAS_Report,GWA_Report,Lookup_Page,Singlejob_Report,RAE_Report,UpdateToken
from components import navbar
from pages.UpdateToken import update_token


@lru_cache(maxsize=128)
@app.callback(Output('comments4-container', 'children'), [Input('get-comments4-button', 'n_clicks')])
def get_comments4(n):
    # Start the timer
    start_time = time.time()
    global task_results, JobsList

    # Getting Attributes per job
    # Process Name, used for stateless process control

    # gets all active jobs data and Status
    today = date.today().strftime('%m-%d-%Y')
    today2 = date.today().strftime('%Y-%m-%d')
    datetime_string_from = today2 + 'T06:05:17'
    datetime_string_to = today2 + 'T06:06:17'

    attsLst = []
    jobsTimeBased = []
    attribute_mapping = {}
    holder = []
    timerecord_values = None
    # JobsList = get_from_cache('ActiveJobList_pandas')

    # Enter into list, the Rigs, you are looking for.
    active_jobList = []
    edr_rigs = [
        'AKITA Drilling 801',
        'AKITA Drilling 523',
        'AKITA Drilling 519',
        'AKITA Drilling 518',
        'AKITA Drilling 802',
        'Arabian Drlg 48',
        'Cactus 162',
        'Cactus 158',
        'Cactus 135',
        'Cactus 152',
        'Cactus 166',
        'Cactus 164',
        'Cactus 172',
        'Cactus 160',
        'Cactus 141',
        'Cactus 126',
        'Cactus 168',
        'Cactus 149',
        'Cactus 170',
        'Cactus 169',
        'Cactus 150',
        'Cactus 129',
        'Cactus 165',
        'Cactus 161',
        'Cactus 132',
        'Cactus 167',
        'Cactus 145',
        'Ensign T136',
        'Ensign 766',
        'Ensign 778',
        'Ensign 759',
        'ICD 322',
        'ICD 214',
        'ICD 206',
        'ICD 328',
        'ICD 302',
        'ICD 306',
        'ICD 323',
        'ICD 304',
        'ICD 307',
        'ICD 331',
        'ICD 212',
        'ICD 203',
        'Latshaw Drlg 42',
        'Latshaw Drlg 44',
        'Latshaw Drlg 18',
        'Latshaw Drlg 10',
        'Latshaw Drlg 20',
        'Latshaw Drlg 45',
        'Latshaw Drlg 9',
        'NOV RDTC 5',
        'Noram Drilling 29',
        'Power Rig 6',
        'Precision 548',
        'Scandrill 1425 - Texas',
        'Scandrill 1427 - Liberty',
        'True Drlg 41',
        'True Drlg 33',
        'Unit Drilling 403'
    ]


    if n and n > 0:
        if token is None:
            return update_token(n)

        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']

            for w in values:
                rigname = f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}"
                if rigname in edr_rigs:
                    active_jobList.append(w['id'])

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

        try:
            # if JobsList is None:
            JobsList = get_from_cache('RAEList_pandas')

            if active_jobList is not None or JobsList is None:
                # JobsList = get_from_cache('EDRList_pandas')
                JobsList = []
                for count, w in enumerate(active_jobList, start=1):
                    # check if record is already in database, if not update database with record
                    record = get_from_cache(w)
                    if record:
                        JobsList.append(record)
                        continue
                    elif record is None:
                        print(f"I'm working on job {w}, which is item {count} in the list of {len(active_jobList)}.")

                        # variables
                        # Define emojis as Unicode characters
                        emoji_check = u'\u2705'  # 3  # u'\u2705'  # ✅
                        emoji_exclamation = u'\u2757'  # 2  # u'\u2757'  # ❗
                        emoji_x = u'\u274C'  # 0  # u'\u274C'  # ❌

                        # Attribute Values
                        HookLoadbool = emoji_x
                        PumpPressurebool = emoji_x
                        BlockHeightbool = emoji_x
                        PumpSpmbool = emoji_x
                        PumpSpm2bool = emoji_x
                        PumpSpm3bool = emoji_x
                        RotaryTorquebool = emoji_x
                        BitPositionbool = emoji_x
                        BitStatusbool = emoji_x
                        SlipStatusbool = emoji_x
                        tpDriveRPM = emoji_x
                        comment = 'NA'
                        comment24 = 'NA'
                        reportDate = ''
                        reportID = ''
                        reportStatus = ''
                        realTime = emoji_x
                        tpDriveTorq = emoji_x
                        weightonBit = emoji_x
                        RP_Fast = emoji_x
                        tHookLoad = emoji_x

                        HookLoad_val = ''
                        PumpPressure_val = ''
                        BlockHeight_val = ''
                        PumpSpm_val = ''
                        PumpSpm2_val = ''
                        PumpSpm3_val = ''
                        RotaryTorque_val = ''
                        tpDriveRPM_val = ''
                        tpDriveTorq_val = ''
                        weightonBit_val = ''
                        BitPosition_val = ''
                        BitStatus_val = ''
                        RP_Fast_val = ''
                        SlipStatus_val = ''
                        tHookLoad_val = ''
                        Iadc_Rig_val = ''
                        Iadc2_Rig_val = ''
                        Iadc3_Rig_val = ''
                        reportDate = ''
                        comment = ''
                        comment24 = ''
                        reportID = ''
                        reportStatus = ''

                        # Get Job Info

                        url1 = f'https://data.welldata.net/api/v1/jobs/{w}'
                        data_response = requests.get(url1, headers={'Token': token})
                        values = data_response.json()

                        # #checking if results are in db, if not query and update db
                        # values = get_from_cache(url1)
                        # if values is None:
                        #     data_response = requests.get(url1, headers={'Token': token})
                        #     values = data_response.json()
                        #     add_to_cache(url1, values)

                        rig_name = f'{values["assetInfoList"][0]["owner"]} {values["assetInfoList"][0]["name"]}'
                        job_contractor = values["assetInfoList"][0]["owner"]
                        job_operator = values['siteInfoList'][0]['owner']
                        holder = []

                        # Getting Attributes
                        # Make the data request with the token
                        url = f"https://data.welldata.net/api/v1/jobs/{w}/attributes"
                        data_response = requests.get(url, headers={'Token': token})
                        data_response.raise_for_status()  # raise exception if the request failed
                        values = data_response.json()


                        mnemonics = ['HOOKLOAD_MAX', 'STP_PRS_1', 'BLOCK_POS', 'MP1_SPM', 'MP2_SPM', 'MP3_SPM', 'ROT_TORQUE', 'TD_SPEED', 'TD_TORQUE', 'WOB', 'BIT_DEPTH',
                                     'BIT_ON_BTM', 'FAST_ROP_FT_HR', 'SLIPS_STAT', 'Trigger Hkld', 'IADC_RIG_ACTIVITY', 'IADC_RIG_ACTIVITY2', 'IADC_RIG_ACTIVITY3']

                        for c in values['attributes']:
                            if c.get('hasData'):
                                if c.get('alias', {}).get('witsml_mnemonic') in mnemonics:
                                    attr = Attribute(id=c['id'], mode='Last')
                                    attsLst.append(attr)

                        hist_interval = 60
                        hist_payload = HistoricalTimeRequest(job_id=w, attributes=attsLst, toTime=datetime_string_to, fromTime=datetime_string_from, interval=hist_interval)
                        hist = historical_data_time(job_id=w, payload=hist_payload.model_dump_json(exclude_unset=True), token=token)

                        # Ensure that 'timeRecords' list contains at least one element before accessing it
                        if hist is None:
                            continue
                        if 'timeRecords' in hist and len(hist['timeRecords']) > 0:
                            # Extract 'values' from the first record in 'timeRecords'
                            timerecord_values = hist['timeRecords'][0]['values']
                        else:
                            # Handle the situation where 'timeRecords' is None or empty
                            print('No Time Records or empty timeRecords list')
                            # holder.extend([
                            #     w, rig_name, job_contractor, job_operator,
                            #     Iadc_Rig_val, Iadc2_Rig_val, Iadc3_Rig_val,
                            #     HookLoadbool, PumpPressurebool, BlockHeightbool, PumpSpmbool,
                            #     PumpSpm2bool, PumpSpm3bool, RotaryTorquebool,
                            #     tpDriveRPM, tpDriveTorq, weightonBit, RP_Fast,
                            #     tHookLoad, BitPositionbool, BitStatusbool,
                            #     SlipStatusbool, comment, comment24,
                            #     reportID, reportDate, reportStatus
                            # ])
                            #
                            # add_to_cache(w, holder)
                            # JobsList.append(holder)
                            # continue
                            continue

                        # Iterate over the 'attributes' list and map each attribute to its value from timestamp 0
                        for i, attribute in enumerate(hist['attributes']):
                            attribute_id = attribute['id']
                            # Ensure the index is within the 'timerecord_values' list bounds
                            attribute_value = timerecord_values[i][1] if i < len(timerecord_values) else ''
                            attribute_mapping[attribute_id] = attribute_value
                        # print(attribute_mapping)

                        attribute_results = {}
                        keys_to_check = ['HookLoad', 'PumpPressure', 'BlockHeight', 'PumpSpm', 'PumpSpm2', 'PumpSpm3', 'RotaryTorque', 'TopDrvRpm', 'TopDrvTorque',
                                         'BitWeightQualified', 'BitPosition', 'BitStatus', 'FastRopFtHr', 'SlipStatus', 'TrigHkld']

                        for key, value in attribute_mapping.items():
                            if key in keys_to_check:
                                value = float(value)
                                if isinstance(value, float) or isinstance(value, int):
                                    if value == 0.00:
                                        attribute_results[key] = emoji_exclamation
                                    elif value > 0.00:
                                        attribute_results[key] = emoji_check
                                    else:
                                        attribute_results[key] = emoji_x
                            elif key in ['IadcRigActivity', 'IadcRigActivity2', 'RigActivity']:
                                attribute_results[key] = value

                        url = f"https://data.welldata.net/api/v1/jobs/{w}/reports/daily/2"
                        data_response = requests.get(url, headers={'Token': token})
                        data_response.raise_for_status()  # raise exception if the request failed
                        values = data_response.json()

                        # values = get_from_cache(url)
                        # if values is None:
                        #     data_response = requests.get(url, headers={'Token': token})
                        #     data_response.raise_for_status()  # raise exception if the request failed
                        #     values = data_response.json()
                        #     add_to_cache(url, values)

                        # print(attribute_results)
                        # if no values, print out current channels without the reports
                        if len(values) == 0:
                            holder.extend([
                                w, rig_name, job_contractor, job_operator,
                                attribute_results.get('IadcRigActivity'), attribute_results.get('IadcRigActivity2'), attribute_results.get('RigActivity'),
                                attribute_results.get('HookLoad'), attribute_results.get('PumpPressure'), attribute_results.get('BlockHeight'), attribute_results.get('PumpSpm'),
                                attribute_results.get('PumpSpm2'), attribute_results.get('PumpSpm3'), attribute_results.get('RotaryTorque'),
                                attribute_results.get('TopDrvRpm'), attribute_results.get('TopDrvTorque'), attribute_results.get('BitWeightQualified'),
                                attribute_results.get('FastRopFtHr'),
                                attribute_results.get('TrigHkld'), attribute_results.get('BitPosition'), attribute_results.get('BitStatus'),
                                attribute_results.get('SlipStatus'), comment, comment24,
                                reportID, reportDate, reportStatus
                            ])

                            add_to_cache(w, holder)
                            JobsList.append(holder)

                            continue
                        wells = []
                        if 'availableReports' not in values:
                            return "There's no Report for this well"
                        reportIds = values['availableReports']
                        for rep in reportIds:
                            wells.append(rep)

                        reportId = wells[0]['id']

                        url2 = f"https://data.welldata.net/api/v1/jobs/{w}/reports/daily/2/JSON?reportIds.ids={reportId}"
                        data_response2 = requests.get(url2, headers={'Token': token})
                        data_response2.raise_for_status()  # raise exception if the request failed
                        # Sort Morning Reports based on Type
                        report = data_response2.json()

                        # report = get_from_cache(url2)
                        # if report is None:
                        #     data_response2 = requests.get(url2, headers={'Token': token})
                        #     data_response2.raise_for_status()  # raise exception if the request failed
                        #     # Sort Morning Reports based on Type
                        #     report = data_response2.json()
                        #     add_to_cache(url2, report)

                        # Rest of your code here

                        if 'GenericAmericanMorningReportDW' in str(report):
                            # continue
                            reportDate = report['Reports'][0]['GenericAmericanMorningReportDW']['Header']['Date']
                            if 'OpsAtReportTime' in str(report):
                                comment = report['Reports'][0]['GenericAmericanMorningReportDW']['Header']['OpsAtReportTime']
                            if 'OpsNext24' in str(report):
                                comment24 = report['Reports'][0]['GenericAmericanMorningReportDW']['Header']['OpsNext24']
                            reportID = report['Reports'][0]['GenericAmericanMorningReportDW']['ReportAttributes']['ReportID']
                            reportStatus = report['Reports'][0]['GenericAmericanMorningReportDW']['ReportAttributes']['ReportStatus']

                            # 'HandPMorningReport'
                        elif 'HandPMorningReport' in str(report):
                            reportDate = report['Reports'][0]['HandPMorningReport']['Header']['Date']
                            comment = report['Reports'][0]['HandPMorningReport']['Operations']['PresentOp']
                            comment24 = ''
                            reportID = report['Reports'][0]['HandPMorningReport']['ReportAttributes']['ReportID']
                            reportStatus = report['Reports'][0]['HandPMorningReport']['ReportAttributes']['ReportStatus']

                            # 'ScanMorningReport'
                        elif 'ScanMorningReport' in str(report):
                            reportDate = report['Reports'][0]['ScanMorningReport']['Header']['Date']
                            reportID = report['Reports'][0]['ScanMorningReport']['ReportAttributes']['ReportID']
                            reportStatus = report['Reports'][0]['ScanMorningReport']['ReportAttributes']['ReportStatus']
                            comment = report['Reports'][0]['ScanMorningReport']['Header']['PresentOp']

                            # 'RapadMorningReport'
                        elif 'RapadMorningReport' in str(report):
                            reportDate = report['Reports'][0]['RapadMorningReport']['Header']['ReportDate']
                            comment = report['Reports'][0]['RapadMorningReport']['Header']['OperationsActivityCurrent']
                            comment24 = report['Reports'][0]['RapadMorningReport']['Header']['OperationsActivityNext24Hours']
                            reportID = report['Reports'][0]['RapadMorningReport']['ReportAttributes']['ReportID']
                            reportStatus = report['Reports'][0]['RapadMorningReport']['ReportAttributes']['ReportStatus']

                            # 'PattersonMorningReportRevB'
                        elif 'PattersonMorningReportRevB' in str(report):
                            reportDate = report['Reports'][0]['PattersonMorningReportRevB']['Header']['ReportDate']
                            comment = report['Reports'][0]['PattersonMorningReportRevB']['OperationsCasingDetails']['operations_at_report_time']
                            if 'operations_next_24_hours' in report['Reports'][0]['PattersonMorningReportRevB']['OperationsCasingDetails']:
                                comment24 = report['Reports'][0]['PattersonMorningReportRevB']['OperationsCasingDetails']['operations_next_24_hours']
                            reportID = report['Reports'][0]['PattersonMorningReportRevB']['ReportAttributes']['ReportID']
                            reportStatus = report['Reports'][0]['PattersonMorningReportRevB']['ReportAttributes']['ReportStatus']

                        else:
                            reportDate = ''
                            comment = ''
                            comment24 = ''
                            reportID = ''
                            reportStatus = ''

                        holder.extend([
                            w, rig_name, job_contractor, job_operator,
                            attribute_results.get('IadcRigActivity'), attribute_results.get('IadcRigActivity2'), attribute_results.get('RigActivity'),
                            attribute_results.get('HookLoad'), attribute_results.get('PumpPressure'), attribute_results.get('BlockHeight'), attribute_results.get('PumpSpm'),
                            attribute_results.get('PumpSpm2'), attribute_results.get('PumpSpm3'), attribute_results.get('RotaryTorque'),
                            attribute_results.get('TopDrvRpm'), attribute_results.get('TopDrvTorque'), attribute_results.get('BitWeightQualified'),
                            attribute_results.get('FastRopFtHr'),
                            attribute_results.get('TrigHkld'), attribute_results.get('BitPosition'), attribute_results.get('BitStatus'),
                            attribute_results.get('SlipStatus'), comment, comment24,
                            reportID, reportDate, reportStatus
                        ])

                        add_to_cache(w, holder)
                        JobsList.append(holder)

                # saving JobList to DB
                add_to_cache('RAEList_pandas', JobsList)

            header = ['Job Id', 'Rig', 'Contractor', 'Operator', 'IADC', 'IADC 2', 'IADC3', 'HookLoad', 'PumpPressure', 'BlockHeight', 'PumpSpm', 'PumpSpm2', 'PumpSpm3',
                      'RotaryTorque', 'TopDrive RPM', 'TopDrive Torque', 'WOB', 'ROP-F', 'T-HL', 'BitPosition', 'BitStatus', 'SlipStatus', 'comment', 'comment24', 'reportID',
                      'reportDate', 'reportStatus']


            df = pd.DataFrame(JobsList)
            print(df.shape)
            df.columns = header
            # Stop the timer
            end_time = time.time()
            # Calculate the elapsed time
            elapsed_time = end_time - start_time
            print(f"The for loop took {elapsed_time:.6f} seconds.")

            task_results["raeJobs"] = html.Div([
                html.H1("RAE Dashboards", style={'text-align': 'center'}), dash_table.DataTable(
                    id='Attributes ID',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    sort_action='native',
                    page_current=0,
                    page_size=10,
                    page_action='native',
                    style_cell={'whiteSpace': 'normal', 'height': 'auto', 'width': '70%', 'text-align': 'left'},
                )])
            return task_results["raeJobs"]



        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

    # Return an empty Div if n is None or 0
    return html.Div()
layout = html.Div([
    html.H1('UpdateToken'),
    # ... other components specific to UpdateToken
])

# Add any callbacks specific to this page here
