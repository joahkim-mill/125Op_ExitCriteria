import streamlit as st 
import plotly.figure_factory as ff 
import numpy as np
import pandas as pd 
import plotly.graph_objects as go

st.set_page_config(layout="wide")

### 
st.title("125C Operation Investigation of Exit Criteria")
st.header("Inspect the differential between SHT40 and RH sensors to determine if this is a valid DGO exit criteria")
st.write("D1: 3/6/24, D2: 3/7/24, D3:3/8, D4: 3/11, D5: 3/14, D6: 3/15, D7: 3/18")
###


sht_threshold = st.number_input('SHT40 Delta Threshold')
rh_threshold = st.number_input('RH Delta Threshold')

fig_sht = go.Figure()
fig_rh = go.Figure() 

met_sht = [[],[]] # times, vals
met_rh = [[],[]] # times, vals

rh_stats = pd.DataFrame({"Name":[],
                            "Runtime End":[],
                            "Time @ RH Threshold":[],
                            "Diff. in Time (RH)":[],
                        })
sht_stats = pd.DataFrame({"Name":[],
                            "Runtime End":[],
                            "Time @ SHT40 Threshold":[],
                            "Diff. in Time (SHT40)":[],
                        })

# read in the csv's of the data --> already extrapolated to runtime
for unit in range(1,3): # units 1 and 2 for now
    for day in range(1,8):
        dataname = f"O2-DVT-DGO-{unit}_D{day}"
        dgo_data = pd.read_csv(f"./125C_DATA/O2_DGO_DATA/{dataname}.csv")
        t_min = dgo_data["time"] / 60
        t_end = t_min[t_min.last_valid_index()]
        delta_SHT = dgo_data["Exhaust SHT40"] - dgo_data["Intake SHT40"]
        delta_RH = dgo_data["Exhaust RH"] - dgo_data["Intake Air RH"] 

        t_sht_threshold = None
        val_sht_threshold = None
        dt_sht = None 

        t_rh_threshold = None
        val_rh_threshold = None
        dt_rh = None 

        # determine the threshold met
        if sht_threshold is not None:
            sht_filt = delta_SHT.where(abs(delta_SHT - sht_threshold) < 0.025) # may need to increase 0.025 if it's too fine
            sht_threshold_index = sht_filt.first_valid_index() 

            if (sht_threshold_index is not None):
                t_sht_threshold = t_min[sht_threshold_index]
                val_sht_threshold = delta_SHT[sht_threshold_index]
                dt_sht = t_end - t_sht_threshold 
                met_sht[0].append(t_sht_threshold)
                met_sht[1].append(val_sht_threshold)
        
        if rh_threshold is not None:
            rh_filt = delta_RH.where(abs(delta_RH - rh_threshold) < 0.025) # may need to increase 0.025 if it's too fine
            rh_threshold_index = rh_filt.first_valid_index()

            if (rh_threshold_index is not None):
                t_rh_threshold = t_min[rh_threshold_index]
                val_rh_threshold = delta_RH[rh_threshold_index]
                dt_rh = t_end - t_rh_threshold
                met_rh[0].append(t_rh_threshold)
                met_rh[1].append(val_rh_threshold)

        sht_stats.loc[len(sht_stats.index)] = [dataname, # name
                                               t_end, # runtime end [minutes] 
                                               t_sht_threshold, # time @ sht threshold
                                               dt_sht # diff in time (sht)
                                            ]
        rh_stats.loc[len(rh_stats.index)] = [dataname,  # name
                                               t_end, # runtime end [minutes]
                                               t_rh_threshold, # time @ rh threshold
                                               dt_rh # diff in time (rh)
                                            ]

        # add data to plots 
        fig_sht.add_trace(go.Scatter(x=t_min, y=delta_SHT, name=dataname))
        fig_rh.add_trace(go.Scatter(x=t_min, y=delta_RH, name=dataname))

        
# read in the csv's of the data --> already extrapolated to runtime
for unit in range(3,4): # include unit 3
    for day in range(2,5):
        dataname = f"O2-DVT-DGO-{unit}_D{day}"
        dgo_data = pd.read_csv(f"./125C_DATA/O2_DGO_DATA/{dataname}.csv")
        t_min = dgo_data["time"] / 60
        t_end = t_min[t_min.last_valid_index()]
        delta_SHT = dgo_data["Exhaust SHT40"] - dgo_data["Intake SHT40"]
        delta_RH = dgo_data["Exhaust RH"] - dgo_data["Intake Air RH"] 

        t_sht_threshold = None
        val_sht_threshold = None
        dt_sht = None 

        t_rh_threshold = None
        val_rh_threshold = None
        dt_rh = None 

        # determine the threshold met
        if sht_threshold is not None:
            sht_filt = delta_SHT.where(abs(delta_SHT - sht_threshold) < 0.025) # may need to increase 0.025 if it's too fine
            sht_threshold_index = sht_filt.first_valid_index() 

            if (sht_threshold_index is not None):
                t_sht_threshold = t_min[sht_threshold_index]
                val_sht_threshold = delta_SHT[sht_threshold_index]
                dt_sht = t_end - t_sht_threshold 
                met_sht[0].append(t_sht_threshold)
                met_sht[1].append(val_sht_threshold)
        
        if rh_threshold is not None:
            rh_filt = delta_RH.where(abs(delta_RH - rh_threshold) < 0.025) # may need to increase 0.025 if it's too fine
            rh_threshold_index = rh_filt.first_valid_index()

            if (rh_threshold_index is not None):
                t_rh_threshold = t_min[rh_threshold_index]
                val_rh_threshold = delta_RH[rh_threshold_index]
                dt_rh = t_end - t_rh_threshold
                met_rh[0].append(t_rh_threshold)
                met_rh[1].append(val_rh_threshold)

        sht_stats.loc[len(sht_stats.index)] = [dataname, # name
                                               t_end, # runtime end [minutes] 
                                               t_sht_threshold, # time @ sht threshold
                                               dt_sht # diff in time (sht)
                                            ]
        rh_stats.loc[len(rh_stats.index)] = [dataname,  # name
                                               t_end, # runtime end [minutes]
                                               t_rh_threshold, # time @ rh threshold
                                               dt_rh # diff in time (rh)
                                            ]

        # add data to plots 
        fig_sht.add_trace(go.Scatter(x=t_min, y=delta_SHT, name=dataname))
        fig_rh.add_trace(go.Scatter(x=t_min, y=delta_RH, name=dataname))        

# display plots
fig_sht.add_trace(go.Scatter(x=[0, 500], y=[sht_threshold, sht_threshold], name=' ', line=dict(dash='dash', color='#d3d3d3')))
fig_sht.add_trace(go.Scatter(x=met_sht[0], y=met_sht[1], name="SHT40 Delta Crossings", mode='markers', line=dict(color='black')))
fig_sht.update_layout(title="SHT40 Differential", xaxis_title="Time [min]", yaxis_title="Exhaust - Intake [degC]",
                      height=500, width=800)

fig_rh.add_trace(go.Scatter(x=[0, 500], y=[rh_threshold, rh_threshold], name=' ', line=dict(dash='dash', color='#d3d3d3')))
fig_rh.add_trace(go.Scatter(x=met_rh[0], y=met_rh[1], name="RH Delta Crossings", mode='markers', line=dict(color='black')))
fig_rh.update_layout(title="RH Differential", xaxis_title="Time [min]", yaxis_title="Exhaust - Intake",
                     height=500, width=800)

cols = st.columns([5,2])
with cols[0]:
    st.plotly_chart(fig_sht)
with cols[1]:
    st.dataframe(sht_stats)

cols2 = st.columns([3,1])
with cols2[0]:
    st.plotly_chart(fig_rh)
with cols2[1]:
    st.dataframe(rh_stats)
# display data
# stats = st.columns(2)
# with stats[0]:
#     st.dataframe(sht_stats)
# with stats[1]:
#     st.dataframe(rh_stats)


