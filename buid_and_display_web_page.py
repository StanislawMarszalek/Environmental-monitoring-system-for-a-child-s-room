#!/usr/bin/env python3

import datetime
import sqlite3
import numpy as np
import streamlit as st
import pandas as pd

todays_date:datetime.date=datetime.date.today()

UNITS:dict[str,str]={"Temperature":"C",
                    "LPG":"ppm",
                    "CO":"ppm",
                    "Humidity":"%",
                    "IsTooLoud":"None Unit"}


def get_parameter_from_db(data_base_name:str,table_name:str,
                        parameter_name:str,date_of_start:datetime.date=todays_date,
                        date_of_end:datetime.date=todays_date,group_by_data:bool=False,
                        only_last_minute:bool=False,select_format:str='%Y-%m-%d %H',
                        group_format:str='%Y%m%d%H')->np.ndarray|None:
    try:
        with sqlite3.connect(data_base_name) as conn:
            cursor:sqlite3.Cursor=conn.cursor()
            if not group_by_data:
                cursor.execute(f"SELECT {parameter_name} from {table_name}")
            else:
                if only_last_minute:
                    cursor.execute(f"SELECT {parameter_name},strftime('{select_format}',time) \
                                   from {table_name} \
                                   WHERE time>=datetime(CURRENT_TIMESTAMP,'-1 minute') \
                                   group by strftime('{group_format}',time) ")
                else:
                    if parameter_name=="IsTooLoud":
                        cursor.execute(f"SELECT max({parameter_name}),strftime('{select_format}',time) \
                                        from {table_name} \
                                        WHERE date(time) BETWEEN '{date_of_start}' AND '{date_of_end}' \
                                        group by strftime('{group_format}',time) ")
                    else:
                        cursor.execute(f"SELECT ROUND(avg({parameter_name}),1),strftime('{select_format}',time)\
                                        from {table_name} \
                                        WHERE date(time) BETWEEN '{date_of_start}' AND '{date_of_end}'\
                                        group by strftime('{group_format}',time) ")

            colected_data=np.array(list(cursor))
            if len(colected_data)<1:
                return None

    except (sqlite3.OperationalError,sqlite3.InternalError) as e:
        print(e)
    return colected_data

page_title=st.header("Check on your child :child:",text_alignment="center")
type_of_data:str=st.selectbox("Select type of data",["Last minute","Chosen pieriod of time"])
parameter:str = st.selectbox("Select Parameter:",['Temperature', 'LPG','CO','IsTooLoud','Humidity'])

if type_of_data=="Chosen pieriod of time":
    start_date:datetime.date = st.date_input("Start date:")
    end_date:datetime.date = st.date_input("End date:")
    group_option:str=st.selectbox("Select grouping option:",["HOURS","HOURS AND MINUTES"])

    if start_date>end_date:
        start_date,end_date=end_date,start_date


    if group_option=="HOURS":
        GROUP_FORMAT:str='%Y%m%d%H'
        SELECT_FORMAT:str='%Y-%m-%d %H'
    else:
        GROUP_FORMAT='%Y%m%d%H%M'
        SELECT_FORMAT='%Y-%m-%d %H:%M'

    data:np.ndarray|None=get_parameter_from_db("/home/nullpointer/Desktop/app/ChildRoom.db",
                               "ENV_PARAMETERS",
                               parameter,
                               start_date,
                               end_date,
                               True,
                               False,
                               SELECT_FORMAT,
                               GROUP_FORMAT)


    if data is None:
        st.info(f"No data for range : {start_date} to {end_date}")
    else:
        data_to_data_frame:dict[str,np.ndarray]={f"{parameter}":data[:,0],"time":data[:,1]}
        df:pd.DataFrame=pd.DataFrame(data=data_to_data_frame)

        df[f"{parameter}"] = df[f"{parameter}"].astype(float)
        if parameter in ("CO", "LPG"):
            df[f"{parameter}"] = df[f"{parameter}"].apply(np.ceil)
            df[f"{parameter}"] = df[f"{parameter}"].astype(int)
        chart=st.line_chart(data=df,
                            x="time",
                            y=f"{parameter}",
                            y_label=f"{parameter} [{UNITS[parameter]}]")
else:
    GROUP_FORMAT='%Y%m%d%H%M%S'
    SELECT_FORMAT='%Y-%m-%d %H:%M:%S'
    data=get_parameter_from_db("/home/nullpointer/Desktop/app/ChildRoom.db",
                               "ENV_PARAMETERS",
                               parameter,
                               group_by_data=True,
                               only_last_minute=True,
                               select_format=SELECT_FORMAT,
                               group_format=GROUP_FORMAT)

    if data is None:
        st.info("No data was collected in last minute")
    else:
        data_to_data_frame={f"{parameter}":data[:,0],"time":data[:,1]}
        df=pd.DataFrame(data=data_to_data_frame)

        df[f"{parameter}"] = df[f"{parameter}"].astype(float)
        if parameter in ("CO", "LPG"):
            df[f"{parameter}"] = df[f"{parameter}"].apply(np.ceil)
            df[f"{parameter}"] = df[f"{parameter}"].astype(int)

        chart=st.line_chart(data=df,
                            x="time",
                            y=f"{parameter}",
                            y_label=f"{parameter} [{UNITS[parameter]}]")
