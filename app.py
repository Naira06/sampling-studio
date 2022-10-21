
from io import BytesIO
from re import X
from tkinter import Button
import numpy as np
import scipy
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
import scipy as sc
from scipy.interpolate import interp1d, interp2d,splev


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


ColorMinMax = st.markdown(''' <style> div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {
    background: rgb(1 1 1 / 0%); } </style>''', unsafe_allow_html = True)


Slider_Cursor = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{
    background-color: rgb(14, 38, 74); box-shadow: rgb(14 38 74 / 20%) 0px 0px 0px 0.2rem;} </style>''', unsafe_allow_html = True)

    
Slider_Number = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div > div
                                { color: rgb(14, 38, 74); } </style>''', unsafe_allow_html = True)
    

col = f''' <style> div.stSlider > div[data-baseweb = "slider"] > div > div {{
    background: linear-gradient(to right,rgba(151, 166, 195, 0.25)  0%, 
                                 rgba(151, 166, 195, 0.25) , 
                                rgb(1, 183, 158), 
                                rgb(1, 183, 158) 100%); }} </style>'''

ColorSlider = st.markdown(col, unsafe_allow_html = True)

Fs = 1000    #Sampling Freqyency    
t = np.arange(0, 1 + 1 / Fs, 1 / Fs)    # Time
d=[]


def draw(x_axis,y_axis):
    st.plotly_chart(fig, use_container_width=True)
def demo():
    y_demo=np.sin(2 * np.pi * t)
    fig3=px.line(y_demo,x=t,y=y_demo)
    st.plotly_chart(fig3, use_container_width=True)


 
#Adding noise to signal
def Noise(Data, number):
    snr = 10.0**(number/10.0)
    p1 = Data.var()   #power signal
    Noise = p1/snr
    w = sc.sqrt(Noise)*sc.randn(1001)    #Noise Signal
        
    return w


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
    Add_F= st.sidebar.slider("F(max)")
    Add_Am = st.sidebar.slider("Amp.")        
    Include_signal= Add_Am * np.sin( 2 * np.pi * Add_F* t)
    return Include_signal



# horizontal menu
selected2 = option_menu(None, ["Home", "Upload", 'History'], 
    icons=['house', 'folder', "save", '💀'], 
    menu_icon="cast", default_index=0, orientation="horizontal" ,
    styles={
        "container": {"padding": "0 px"},
        "icon": {"color": "black", "font-size": "15px"}, 
        "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "grey"},
    }

    )



if selected2=="Upload":
    upload_file= st.file_uploader("Browse")
    if upload_file:
        signal_upload=pd.read_excel(upload_file)
        signal_figure= px.line(signal_upload, x=signal_upload.columns[0], y=signal_upload.columns[1], title="The normal signal")
        y_signal= signal_upload.columns[1]
        addSignal = st.checkbox('Add Signal')
        sumSignal = st.checkbox('Sum Signal')
        if addSignal:
            signal_figure.add_scatter(x=t, y=add_signal(), mode="lines")
        st.plotly_chart(signal_figure,use_container_width=True)

elif selected2=="Home":

    #drawing normal sine
    frequency = st.sidebar.slider("Fmax", min_value=0)
    amplitude = st.sidebar.slider("Amplitude", min_value=0)
    sampleRate = st.sidebar.slider("sample rate", min_value=0,max_value=10)
    signal = amplitude * np.sin(2 * np.pi * frequency * t)
    frequency_sample= sampleRate*frequency
    noise = st.sidebar.checkbox('Add noise')
    if noise:
        number = st.sidebar.slider('Insert SNR')
        new_signal = Noise(signal, number)
        signal = amplitude * np.sin(2 * np.pi * frequency * t) + new_signal
    
    addSignal = st.sidebar.checkbox('Add Signal')
    

    fig = px.line(signal, x=t, y=signal)

    
    if addSignal:
        added= add_signal()
        sumSignal = st.sidebar.button('Sum Signals')
        fig.add_scatter(x=t, y=added, mode="lines")
        if sumSignal:
                s2= sum_signal(signal,added)  
                fig = px.line(s2, x=t, y=s2)
    sum = st.sidebar.checkbox('Sum Signal')
    if sum:
            freq_sum = st.sidebar.slider("Add frequency")
            amp_sum = st.sidebar.slider("Add amplitude")
            new= amp_sum * np.sin( 2 * np.pi * freq_sum* t)
            signal= sum_signal(signal,new)
            fig = px.line(signal, x=t, y=signal)
            
    
    
    st.plotly_chart(fig, use_container_width=True)
    
    #sampling func
    if frequency_sample!=0:
        T=1/frequency_sample
        n_Sample=np.arange(0,1/T)
        t_sample = n_Sample * T
        signal_sample = amplitude * np.sin(2 * np.pi * frequency * t_sample)
        fig2=px.scatter(x=t_sample, y=signal_sample)
        
        Inter=st.checkbox("interpolation")
        if Inter:
            sum=0
            for i in n_Sample:
                s_sample = amplitude * np.sin(2 * np.pi * frequency *i* T)
                sum+= np.dot(s_sample,np.sinc((t-i*T)/T))
            fig2.add_scatter(x=t, y=sum, mode="lines")
        
        st.plotly_chart(fig2, use_container_width=True)
        
    d1= st.sidebar.button("Demo")  #demo sin with amp. 1
    if d1:
      demo()      

    download(t,signal)
    













