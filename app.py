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
    st.download_button(
        label="Download",
        data=output.getvalue(),
        file_name="signal.xlsx",
        mime="application/vnd.ms-excel"
    )


def sum_signal(data,y):
    newSignal = data + y
    return newSignal

def add_signal():
    Add_F= st.number_input("Fmax")
    Add_Am = st.number_input("Amplitude")        
    Include_signal= Add_Am * np.sin( 2 * np.pi * Add_F* t)
    return Include_signal
#sampling func





# horizontal menu
selected2 = option_menu(None, ["Home", "Upload", "Generate", 'History'], 
    icons=['house', 'folder', 'play', "save", '💀'], 
    menu_icon="cast", default_index=0, orientation="horizontal")



if selected2=="Upload":
    upload_file= st.file_uploader("Browse")
    if upload_file:
        signal_upload=pd.read_excel(upload_file)
        signal_figure= px.line(signal_upload, x=signal_upload.columns[0], y=signal_upload.columns[1], title="The normal signal")
        # noise = st.checkbox('Add noise')
        # if noise:
        #         number = st.number_input('Insert SNR')
        #         st.write('The current value is ', number)
        #         B_new_signal = Noise(signal_upload, number)
        #         signal_upload = signal_upload + B_new_signal
        # addSignal = st.checkbox('Add Signal')
        # if addSignal:
        #     signal_upload= add_signal(signal_upload)
        #fig = px.line(signal_upload, x=t, y=signal_upload)
        st.plotly_chart(signal_figure,use_container_width=True)    

elif selected2=="Generate":
    #drawing normal sine
    frequency = st.slider("Fmax", min_value=0)
    amplitude = st.slider("Amplitude", min_value=0)
    sampleRate = st.slider("sample rate", min_value=1,max_value=4)
    signal = amplitude * np.sin(2 * np.pi * frequency * t)
    frequency_sample= sampleRate*frequency
    if frequency_sample!=0:
        T=1/frequency_sample
        n_Sample=np.arange(0,1/T)
        t_sample = n_Sample * T
        signal_sample = amplitude * np.sin(2 * np.pi * frequency * t_sample)
        sampleFig=px.line(signal, x=t, y=signal)
        sampleFig.add_scatter(x=t_sample, y=signal_sample, mode='markers')
        st.plotly_chart(sampleFig, use_container_width=True)

    noise = st.checkbox('Add noise')
    if noise:
        number = st.number_input('Insert SNR')
        st.write('The current value is ', number)
        new_signal = Noise(signal, number)
        signal = amplitude * np.sin(2 * np.pi * frequency * t) + new_signal
    addSignal = st.checkbox('Add Signal')
    sumSignal = st.checkbox('Sum Signal')
       

    if addSignal:
        fig = px.line(signal, x=t, y=signal)
        fig.add_scatter(x=t, y=add_signal(), mode="lines")
        st.plotly_chart(fig, use_container_width=True)
   
    if sumSignal:
        freq_sum = st.slider("Add frequency")
        amp_sum = st.slider("Add amplitude")
        new= amp_sum * np.sin( 2 * np.pi * freq_sum* t)
        signal= sum_signal(signal,new)
        fig = px.line(signal, x=t, y=signal)
        st.plotly_chart(fig, use_container_width=True)
    #fig = px.line(signal, x=t, y=signal)
    #st.plotly_chart(fig, use_container_width=True)
      
    download(t,signal)
















