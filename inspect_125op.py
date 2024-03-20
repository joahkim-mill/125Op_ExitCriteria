import pandas as pd 
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import os
from extrapolate_dgo import compile_dgos
"""
EXIT CRITERIA EXPLORATION -- 125degC operation 

This script reads in csv files of all the variables and inspects the differences between 
intake and exhaust SHT40s, and the RH values. 
"""

# compile_dgos()  # takes all of the raw data csv's and extrapolates the runtime data

'''
desc: 
input: 
output:
'''
# 1. input csv and parse through for start and end of dgo run
# 2. determine at what point the threshold is met --> maybe also take in as input the specific variable name to be inspected 
# 3. keep track of time the threshold is met, how much shorter the runtime would be


fig_sht40 = go.Figure()
fig_rh = go.Figure()

for dvt in range(1,4):
    for day in range(1,8):
        filepath = f"./125C_DATA/O2_DGO_DATA/O2-DVT-DGO-{dvt}_D{day}.csv"

        if os.path.isfile(filepath):
            data = pd.read_csv(filepath)
            t = data["time"] / 60 # convert from seconds to minutes
            in_SHT40 = data["Intake SHT40"]
            ex_SHT40 = data["Exhaust SHT40"]
            delta_SHT40 = ex_SHT40 - in_SHT40 

            in_RH = data["Intake Air RH"]
            ex_RH = data["Exhaust RH"]
            delta_RH = ex_RH - in_RH 

            fig_sht40.add_trace(go.Scatter(x=t, y=delta_SHT40, name=f"O2-DGO-{dvt}_D{day}"))
            fig_rh.add_trace(go.Scatter(x=t, y=delta_RH, name=f"O2-DGO-{dvt}_D{day}"))
fig_sht40.update_layout(title="SHT 40",xaxis_title="Time [min]", yaxis_title="SHT40 Diff. [degC]",
                         height=500, width=1000)
fig_rh.update_layout(title="RH", xaxis_title="Time [min]", yaxis_title="RH Diff.",
                         height=500, width=1000)
st.title("125C Operation - Runtime Comparison")
st.plotly_chart(fig_sht40)
st.plotly_chart(fig_rh)



#region -- using subplots (better for plotly fig.show())
# fig = make_subplots(rows=2, cols=1,
#                     subplot_titles=("Exhaust SHT40 - Intake SHT40", "Exhaust RH - Intake RH"))

# for dvt in range(1,4):
#     for day in range(1,8):
#         filepath = f"./125C_DATA/O2_DGO_DATA/O2-DVT-DGO-{dvt}_D{day}.csv"

#         if os.path.isfile(filepath):
#             data = pd.read_csv(filepath)
#             t = data["time"] / 60 # convert from seconds to minutes
#             in_SHT40 = data["Intake SHT40"]
#             ex_SHT40 = data["Exhaust SHT40"]
#             delta_SHT40 = ex_SHT40 - in_SHT40 

#             in_RH = data["Intake Air RH"]
#             ex_RH = data["Exhaust RH"]
#             delta_RH = ex_RH - in_RH 

#             fig.add_trace(go.Scatter(x=t, y=delta_SHT40, name=f"SHT40_DGO-{dvt}_D{day}"), row=1, col=1)
#             fig.add_trace(go.Scatter(x=t, y=delta_RH, name=f"RH_DGO-{dvt}_D{day}"), row=2, col=1)
# fig.update_layout(title="125C Operation - Runtime Comparison", height=1000, width=1000)
# fig['layout']['xaxis']['title']='Time [min]'
# fig['layout']['xaxis2']['title']='Time [min]'
# fig['layout']['yaxis']['title']='SHT40 Diff. [degC]'
# fig['layout']['yaxis2']['title']='RH Diff.'
# # fig.show()
# st.plotly_chart(fig)
#endregion -- using subplots (better for plotly fig.show())
