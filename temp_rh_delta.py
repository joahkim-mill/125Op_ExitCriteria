"""
This script reads in csv files of all the variables and inspects the differences between 
intake and exhaust SHT40s, and the RH values. 
"""
import pandas as pd 
from plotly import graph_objects as go
import streamlit as st
import os

def saturation_vapor_pressure(temperature_air):
    # Resource: https://unidata.github.io/MetPy/latest/api/generated/metpy.calc.saturation_vapor_pressure.html
    # Temperature in Celcius
    return 6.112 * (2.718281828459 ** ((17.67 * temperature_air) / (temperature_air + 243.5)))

def saturation_mixing_ratio(temperature_air, total_pressure=1013.25, molecular_weight_ratio=0.6219569100577033):
    # https://unidata.github.io/MetPy/latest/api/generated/metpy.calc.saturation_mixing_ratio.html#metpy.calc.saturation_mixing_ratio
    # molecular_weight_ratio = epsilon
    # Temperature in Celcius
    # pressure in hPa
    # total pressure assumes standard atmospheric pressure = 1,013.25 hPa
    saturation_pressure = saturation_vapor_pressure(temperature_air)
    mr_s = molecular_weight_ratio * (saturation_pressure / (total_pressure - saturation_pressure))
    return mr_s

def mixing_ratio_from_rh(relative_humidity, temperature_air, total_pressure=1013.25):
    # https://unidata.github.io/MetPy/latest/api/generated/metpy.calc.mixing_ratio_from_relative_humidity.html
    # Temperature in Celcius
    # pressure in hPa
    # total pressure assumes standard atmospheric pressure = 1,013.25 hPa
    # TODO: 1. Use atmospheric pressure more indicative of California
    mr_s = saturation_mixing_ratio(temperature_air, total_pressure)
    mr = relative_humidity * mr_s
    return mr

# '''
# desc: plots ONE dataset
# input: dataname - name of the dataset to be analyzed
#        csv - csv of the dataset to be analyzed --> already processed and contains runtime data only
# '''
def plot_dgo(dataname, csv, rh_threshold, sht40_threshold):

    t = csv["time"] /60 # time in minutes
    t_end = t[t.last_valid_index()] 
    rh_delta = csv["Exhaust RH"] - csv["Intake Air RH"]
    # rh_delta = csv["Exhaust RH"] 
    sht40_delta = csv["Exhaust SHT40"] - csv["Intake SHT40"]


    # initialize dataframe to hold all of the info --> to be displayed in table(s)
    rh_stats = pd.DataFrame({"Name":[],
                          "Runtime End":[],
                          "Time @ RH Threshold":[],
                          "Diff. in Time (RH)":[],
                          "MR @ RH Threshold":[]
                          })
    sht40_stats = pd.DataFrame({"Name":[],
                          "Runtime End":[],
                          "Time @ SHT40 Threshold":[],
                          "Diff. in Time (SHT40)":[],
                          "MR @ SHT40 Threshold":[]
                          })
    # plot the delta data as is
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=rh_delta, name=f"RH_Delta_{dataname}"))
    fig.add_trace(go.Scatter(x=t, y=sht40_delta, name=f"SHT40_Delta_{dataname}"))


    t_rh_threshold = None
    val_rh_threshold = None 
    dt_rh = None
    mr_rh = None
    
    t_sht40_threshold = None
    val_sht40_threshold = None
    dt_sht40 = None
    mr_sht40 = None

    if rh_threshold is not None:
        # determine where the thresholds are met  ** may have to change the 0.025 if this is too fine !! **
        rh_filt = rh_delta.where(abs(rh_delta - rh_threshold) < 0.025)
        rh_threshold_index = rh_filt.first_valid_index()  # first crossing of the threshold
        
        if not(rh_threshold_index == None):
            t_rh_threshold = t[rh_threshold_index] # minutes
            val_rh_threshold = rh_delta[rh_threshold_index] # value of the dataset when the rh threshold is crossed
            dt_rh = t_end - t_rh_threshold # minutes
            mr_rh = mixing_ratio_from_rh(csv["Exhaust RH"][rh_threshold_index], csv["Exhaust SHT40"][rh_threshold_index])
            # fig.add_trace(go.Scatter(mode='markers', x=[t_rh_threshold], y=[val_rh_threshold], name=f"RH Threshold_{dataname}"))

    if sht40_threshold is not None: 
        sht40_filt = sht40_delta.where(abs(sht40_delta - sht40_threshold) < 0.025)
        sht40_threshold_index = sht40_filt.first_valid_index()
    
        if not (sht40_threshold_index == None):
            t_sht40_threshold = t[sht40_threshold_index]
            val_sht40_threshold = sht40_delta[sht40_threshold_index]
            dt_sht40 = t_end - t_sht40_threshold 
            mr_sht40 = mixing_ratio_from_rh(csv["Exhaust RH"][sht40_threshold_index], csv["Exhaust SHT40"][sht40_threshold_index])
            # fig.add_trace(go.Scatter(mode='markers', x=[t_sht40_threshold], y=[val_sht40_threshold], name=f"SHT40 Threshold_{dataname}"))

    rh_stats.loc[len(rh_stats.index)] = [dataname,  # name
                                    t_end,  # runtime end [minutes]
                                    t_rh_threshold,  # time @ rh threshold
                                    dt_rh,  # diff in time (rh)
                                    mr_rh
                                    ] 
    sht40_stats.loc[len(sht40_stats.index)] = [dataname,  # name
                                    t_end,  # runtime end [minutes]
                                    t_sht40_threshold,  # time @ sht40 threshold
                                    dt_sht40,  # diff in time (sht40)
                                    mr_sht40
                                    ] 

 
    fig.update_layout(title=f"RH and SHT40 Differentials for {dataname}",
                  xaxis_title="Time [min]", 
                  yaxis_title="Delta Data",
                  height=800,
                  width=1000,
                  )
    fig.update_xaxes(color="black", title_font_color="black")
    fig.update_yaxes(color="black", title_font_color="black")

    return fig, rh_stats, sht40_stats, [t_rh_threshold, val_rh_threshold], [t_sht40_threshold, val_sht40_threshold]



rh_threshold = st.number_input("RH Delta Threshold: ")
sht40_threshold = st.number_input("SHT40 Delta Threshold: ")

# colors = []
#region units 1&2 plotting
for unit in range(1,3):
    rh_thresh_met = [[],[]]  # list of [times],[values]
    sht40_thresh_met = [[],[]]
    for day in range(1,8):
        filepath = f"./O2_DGO_DATA/O2-DVT-DGO-{unit}_D{day}.csv"
        data = pd.read_csv(filepath)
        dataname = f"DGO-{unit}_D{day}"

        fig, rh_stats, sht40_stats, rh, sht40 = plot_dgo(dataname, data, rh_threshold, sht40_threshold)
        if (unit==1) and (day == 1):
            d = fig.data
            r = rh_stats
            s = sht40_stats
        elif (day == 1):
            d = fig.data
        else:
            d += fig.data
            r = pd.concat([r, rh_stats])
            s = pd.concat([s, sht40_stats])
        
        rh_thresh_met[0].append(rh[0])
        rh_thresh_met[1].append(rh[1])
        sht40_thresh_met[0].append(sht40[0])
        sht40_thresh_met[1].append(sht40[1])

    fig_total = go.Figure(data = d)
    fig_total.add_trace(go.Scatter(x=rh_thresh_met[0], 
                                   y=rh_thresh_met[1],
                                   mode='markers', 
                                   name="RH Threshold",
                                   marker=dict(color="red", symbol="diamond")))  # add the threshold markers here
    fig_total.add_trace(go.Scatter(x=sht40_thresh_met[0], 
                                   y=sht40_thresh_met[1],
                                   mode='markers',
                                   name="SHT40 Threshold",
                                   marker=dict(color="blue", symbol="diamond")))
    fig_total.update_layout(title=f"RH and SHT40 Differentials for O2-DVT-DGO-{unit}",
                    xaxis_title="Time [min]", 
                    yaxis_title="Delta Data",
                    height=900,
                    width=1000,
                    )
    fig_total.update_xaxes(color="black", title_font_color="black")
    fig_total.update_yaxes(color="black", title_font_color="black")
    st.plotly_chart(fig_total)
#endregion units 1&2 plotting
    
#region unit3 plotting
## for unit 3, since not all 7 days had usable data
unit=3
days = [3, 6, 7]
rh_thresh_met = [[],[]]  # list of [times],[values]
sht40_thresh_met = [[],[]]
for day in days:
    filepath = f"./O2_DGO_DATA/O2-DVT-DGO-{unit}_D{day}.csv"
    data = pd.read_csv(filepath)
    dataname = f"DGO-{unit}_D{day}"

    fig, rh_stats, sht40_stats, rh, sht40 = plot_dgo(dataname, data, rh_threshold, sht40_threshold)
    if (day == 3):
        d = fig.data
        # r = rh_stats
        # s = sht40_stats
        
    else:
        d += fig.data
        r = pd.concat([r, rh_stats])
        s = pd.concat([s, sht40_stats])
    
    rh_thresh_met[0].append(rh[0])
    rh_thresh_met[1].append(rh[1])
    sht40_thresh_met[0].append(sht40[0])
    sht40_thresh_met[1].append(sht40[1])

fig_total = go.Figure(data = d)
fig_total.add_trace(go.Scatter(x=rh_thresh_met[0], 
                                y=rh_thresh_met[1],
                                mode='markers', 
                                name="RH Threshold",
                                marker=dict(color="red", symbol="diamond")))  # add the threshold markers here
fig_total.add_trace(go.Scatter(x=sht40_thresh_met[0], 
                                y=sht40_thresh_met[1],
                                mode='markers',
                                name="SHT40 Threshold", 
                                marker=dict(color="blue", symbol="diamond")))
fig_total.update_layout(title=f"RH and SHT40 Differentials for O2-DVT-DGO-{unit}",
                xaxis_title="Time [min]", 
                yaxis_title="Delta Data",
                height=900,
                width=1000,
                )
fig_total.update_xaxes(color="black", title_font_color="black")
fig_total.update_yaxes(color="black", title_font_color="black")
st.plotly_chart(fig_total)
#endregion unit3 plotting

st.header("DGO Stats")
st.write("Times are in minutes. A positive difference in time indicates how much *shorter* the runtime would be if DGO is stopped at the threshold.")

# # display stats
# col = st.columns(2)
# with col[0]:
#     f'''
#     RH stats when RH threshold = {rh_threshold}
#     '''
#     st.dataframe(r, width=900)
# with col[1]:
#     f'''
#     SHT40 stats when SHT40 threshold = {sht40_threshold}
#     '''
#     st.dataframe(s, width=900)


# display stats
"""
TODO : refine the RH threshold met value and only start looking after ~20min 
"""
f'''
RH stats when RH threshold = {rh_threshold}
'''
st.dataframe(r, width=900)

f'''
SHT40 stats when SHT40 threshold = {sht40_threshold}
'''
st.dataframe(s, width=900)
