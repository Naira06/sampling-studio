from io import BytesIO
from tkinter import Button
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit.components.v1 as com
import time
import xlsxwriter
from collections import deque
import hydralit_components as hc




st.set_page_config(page_title="sampling studio", page_icon=":bar_chart:",layout="wide")


#hiding copyright things
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# specify the primary menu definition
menu_data = [
        {'icon': "fa fa-folder", 'label':"Brows"},
        {'id':'Copy','icon':"fas fa-play",'label':"Generate"},
        {'icon': "fa fa-save", 'label':"Save"},#no tooltip message
        {'icon': "fa fa-waveform", 'label':"Add noise"},
        {'id':' Crazy return value 💀','icon': "💀", 'label':"History"},
        
]
# we can override any part of the primary colors of the menu
over_theme = {'txc_inactive': '#FFFFFF','menu_background':'grey','txc_active':'Black','option_active':'white'}
#over_theme = {'txc_inactive': '#808080'}
menu_id = hc.nav_bar(menu_definition=menu_data,home_name='Home',override_theme=over_theme)

    
#get the id of the menu item clicked
st.info(f"{menu_id=}")


#uploading file from desktob
upload_file= st.file_uploader("Browse")
if upload_file:
    signal_upload=pd.read_excel(upload_file)
    st.write(signal_upload.describe())
    signal_figure= px.line(signal_upload, x=signal_upload.columns[0], y=signal_upload.columns[1], title="The normal signal")
    st.plotly_chart(signal_figure,use_container_width=True)


#drawing noramal sine
frequency = st.slider("Fmax", min_value=0)
amplitude = st.slider("Amplitude", min_value=0)
Fs = 1000    #Sampling Freqyency
t = np.arange(-1, 1 + 1 / Fs, 1 / Fs)    # Time
signal = amplitude * np.sin(2 * np.pi * frequency * t)
fig = px.line(signal, x=t, y=signal)
st.plotly_chart(fig, use_container_width=True)  


#download a file as excel
output = BytesIO()
# Write files to in-memory strings using BytesIO
# See: https://xlsxwriter.readthedocs.io/workbook.html?highlight=BytesIO#constructor
workbook = xlsxwriter.Workbook(output, {'in_memory': True})
worksheet = workbook.add_worksheet()
worksheet.write_column(0,0,signal)
workbook.close()

st.download_button(
    label="Download Excel workbook",
    data=output.getvalue(),
    file_name="workbook.xlsx",
    mime="application/vnd.ms-excel"
)


#Adding noise to signal
noise = st.checkbox('Add noise')
if noise:
    number = st.number_input('Insert SNR')
    st.write('The current value is ', number)
