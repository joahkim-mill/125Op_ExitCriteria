
import pandas as pd 
from plotly import graph_objects as go
import os
import numpy as np
'''
desc: determine the instance of the DGO cycle based on the intake SHT40 [clearer depiction of end] for a single dgo cycle
input: raw_data - csv file of the raw data for a single unit/day (taken ~2 min before and after visual beginning and end)
output: dgo_data - dataframe of the extrapolated data from the start of the runtime to the end containing all of the variables

'''
def extrapolate_dgo(raw_data, dataname):

    t = (raw_data["time"] - raw_data["time"][0]) / 1000  # convert from ms to seconds
    half_t = (int)(len(t) / 2) 
    in_RH = raw_data["Intake Air RH"]
    ex_RH = raw_data["Exhaust RH"]
    in_SHT40 = raw_data["Intake SHT40"]
    ex_SHT40 = raw_data["Exhaust SHT40"]

    delta_SHT40 = ex_SHT40 - in_SHT40 
    # delta_RH = ex_RH - in_RH 
    found_start = False 
    found_end = False
    
    start_index = 0
    end_index = 0

    last = in_SHT40.last_valid_index() - 10

    fig = go.Figure()

    # parse through max half of the time frame to look for each end
    for i in range(half_t):
        if ((abs(in_SHT40[i + 3] - in_SHT40[i])) > 0.25) and (not found_start):  # may need the absolute value
            # print("start: ", i)
            start_index = i
            found_start = True   
            # break
        if ((in_SHT40[last - i] - in_SHT40[last - i - 1]) > -0.0075) and (not found_end):  # may need the absolute value
            # print("end: ", i)
            end_index = last - i
            found_end = True 
        if (found_start and found_end):
            break

    fig.add_trace(go.Scatter(x=raw_data["time"], y=delta_SHT40, name="deltaSHT40"))
    fig.add_trace(go.Scatter(x=raw_data["time"], y=in_SHT40, name="in_SHT40"))
    fig.add_trace(go.Scatter(x=[raw_data["time"][start_index], raw_data["time"][end_index]], y=[in_SHT40[start_index], in_SHT40[end_index]],mode='markers' ))
    fig.update_layout(title=dataname)
    fig.show()
    runtime = end_index - start_index
    # print("runtime is: ", runtime)
    dgo_data = pd.DataFrame() 
    # dgo_data["time"] = (raw_data["time"][:runtime+1] - raw_data["time"][start_index])/1000  # only take data from beginning to end of dgo runtime
    # print("time: ", dgo_data["time"])
    dgo_data["time"] = (raw_data["time"][start_index:end_index+1] - raw_data["time"][start_index])/1000 # ms to seconds
    num_vars = len(raw_data.columns[2:]) # number of variables EXCLUDING TIME
    # iterate through the variables to extrapolate only relevant data
    for i in range(num_vars): 
        var_name = raw_data.columns[2+i] 
        extrapolated = raw_data[var_name][start_index:end_index+1]
        dgo_data.insert(i+1, column=var_name, value=extrapolated)
    new_index = np.arange(0,len(dgo_data["time"])+1, 1)
    dgo_data.reset_index(drop=True, inplace=True)
    # print(new_index)
    return dgo_data

'''
desc: iterate through each raw data file and extrapolate dgo cycle data using extrapolate_dgo(). each csv of the dgo data 
is saved to a folder O2_DGO_DATA
'''
def compile_dgos():
    for unit in range(1,4):
        for day in range(1,8):
            filepath = f"~/../../SHT40_delta/125C_DATA/O2_DGO_RAWDATA/O2-DVT-DGO-{unit}_D{day}_RAW.csv"
            savepath = f"~/../../SHT40_delta/125C_DATA/O2_DGO_DATA/O2-DVT-DGO-{unit}_D{day}.csv"
            if os.path.isfile(filepath):
                raw_data = pd.read_csv(filepath)
                dgo_data = extrapolate_dgo(raw_data, f"O2-DVT-DGO-{unit}_D{day}") 
                dgo_data.to_csv(savepath)
            

# rawdata = pd.read_csv("./125C_DATA/O2_DGO_RAWDATA/O2-DVT-DGO-2_D1_RAW.csv")              
# extrapolate_dgo(rawdata)