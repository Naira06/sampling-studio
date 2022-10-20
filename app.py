from io import BytesIO
from re import X
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
from streamlit_option_menu import option_menu
from streamlit import button


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
with open("style.css") as source_des:
    st.markdown(f"""<style>{source_des.read()}</style>""", unsafe_allow_html=True)

Fs = 1000    #Sampling Freqyency
t = np.arange(0, 1 + 1 / Fs, 1 / Fs)    # Time

#Adding noise to signal
def Noise(Data, number):
    #Get signal power
    Signal_power = Data[:][1]**2
    SignalPowerAVG = np.mean(Signal_power)
    SignalPower_DB = 10*np.log10(SignalPowerAVG)
    #Noise
    SNR = number
    #getting noise
    Noise_DB = SignalPower_DB - SNR
    Noise_watts = 10**(Noise_DB/10)
    noise = np.random.normal(0,np.sqrt(Noise_watts), len(Data))
    return noise


#download a file as excel
def download(time , magnitude):
    output = BytesIO()
    # Write files to in-memory strings using BytesIO
    # See: https://xlsxwriter.readthedocs.io/workbook.html?highlight=BytesIO#constructor
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    worksheet.write_column(0,0,time)
    worksheet.write_column(0,1,magnitude)
    workbook.close()
    #Button of downloading
    st.sidebar.download_button(
        label="Download",
        data=output.getvalue(),
        file_name="signal.xlsx",
        mime="application/vnd.ms-excel"
    )


def sum_signal(data, y):
    newSignal = data + y
    return newSignal

def add_signal():
    Add_F= st.sidebar.number_input("Fmax")
    Add_Am = st.sidebar.number_input("Amplitude")        
    Include_signal= Add_Am * np.sin( 2 * np.pi * Add_F* t)
    return Include_signal




# horizontal menu
selected2 = option_menu(None, ["Home", "Upload", "Generate", 'History'], 
    icons=['house', 'folder', 'play', "save", '💀'], 
    menu_icon="cast", default_index=0, orientation="horizontal" ,
    styles={
        "container": {"padding": "0 px"},
        "icon": {"color": "black", "font-size": "15px"}, 
        "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "grey"},
    }

    )
# st.markdown(
#     f"""
#     <style>
#     .css-18e3th9{
#     Padding:0px;
# }
#     </style>
#     """,



# unsafe_allow_html=True)

# st.markdown(
#    f”””
#    <style>
#    p {
#    background-image: url(‘img_file.jpg’);
#    }
#    </style>
#    ”””,
#    unsafe_allow_html=True)


if selected2=="Upload":
    upload_file= st.file_uploader("Browse")
    if upload_file:
        signal_upload=pd.read_excel(upload_file)
        signal_figure= px.line(signal_upload, x=signal_upload.columns[0], y=signal_upload.columns[1], title="The normal signal")
        addSignal = st.checkbox('Add Signal')
        sumSignal = st.checkbox('Sum Signal')
        if addSignal:
            signal_figure.add_scatter(x=t, y=add_signal(), mode="lines")
        st.plotly_chart(signal_figure,use_container_width=True)

elif selected2=="Generate":
    #drawing normal sine
    frequency = st.sidebar.slider("Fmax", min_value=0)
    amplitude = st.sidebar.slider("Amplitude", min_value=0)
    sampleRate = st.sidebar.slider("sample rate", min_value=1,max_value=10)
    
    signal = amplitude * np.sin(2 * np.pi * frequency * t)
    
    frequency_sample= sampleRate*frequency
    noise = st.sidebar.checkbox('Add noise')
    if noise:
        number = st.sidebar.number_input('Insert SNR')
        new_signal = Noise(signal, number)
        signal = amplitude * np.sin(2 * np.pi * frequency * t) + new_signal
    
    
    sumSignal = st.sidebar.checkbox('Sum Signal')
    if sumSignal:
        
            freq_sum = st.sidebar.slider("Add frequency")
            amp_sum = st.sidebar.slider("Add amplitude")
            new= amp_sum * np.sin( 2 * np.pi * freq_sum* t)
            signal= sum_signal(signal,new)

    fig = px.line(signal, x=t, y=signal)
    #sampling func
    if frequency_sample!=0:
        T=1/frequency_sample
        n_Sample=np.arange(0,1/T)
        t_sample = n_Sample * T
        signal_sample = amplitude * np.sin(2 * np.pi * frequency * t_sample)
        fig.add_scatter(x=t_sample, y=signal_sample, mode='markers')

    addSignal = st.sidebar.checkbox('Add Signal')
    if addSignal:
        
        fig.add_scatter(x=t, y=add_signal(), mode="lines")
    
   

    st.plotly_chart(fig, use_container_width=True)
    download(t,signal)
