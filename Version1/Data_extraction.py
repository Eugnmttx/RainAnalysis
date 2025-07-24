import numpy as np
import pandas as pd

def Get_data(Station, Places_sst, Normalized):
    """
    Args: 
        Station = (str) Swiss Stations name
        Places_sst = (str array) Name of the places for Sea Surface Temperature
    Return:
        Dataset = (2D array) Withn Rows per day and with columns: nao, oni, [sst]
        Labels = (1D array) With sum of rain per day
    """

    # Handle Wind Data
    dfwind = pd.read_csv("../Database/Vents/Data"+Station+"Jours/Data"+Station+"J_dir.txt", sep=";", low_memory=False)
    dfwind_int = pd.read_csv("../Database/Vents/Data"+Station+"Jours/Data"+Station+"J_int.txt", sep=";", low_memory=False)

    dfwind.time = pd.to_datetime(dfwind['time'], yearfirst=True, utc=False, format='%Y%m%d')
    dfwind_int.time = pd.to_datetime(dfwind_int['time'], yearfirst=True, utc=False, format='%Y%m%d')
    col_dir = dfwind.columns[-1]
    col_int = dfwind_int.columns[-1]
    dfwind_int.replace('-', 0, inplace=True)
    dfwind.replace('-', 0, inplace=True)
    dfwind[col_dir] = pd.to_numeric(dfwind[col_dir])
    dfwind_int[col_int] = pd.to_numeric(dfwind_int[col_int])

    yearmin = dfwind_int.time.dt.year.iloc[400]
    dfwind = dfwind[(dfwind.time.dt.year >= yearmin) & (dfwind.time.dt.year < 2025)]
    dfwind_int = dfwind_int[(dfwind_int.time.dt.year >= yearmin) & (dfwind_int.time.dt.year < 2025)]
    dfwind = dfwind.reset_index()
    dfwind_int = dfwind_int.reset_index()
    dfwind_int['dir'] = dfwind[col_dir]

    rad = np.deg2rad(dfwind_int['dir'])

    # Handle Rain Data
    dfprec = pd.read_csv("../Database/Precipitations/Data"+Station+"Minutes/Data"+Station+"M8095.txt", sep=";", low_memory=False)
    dfprec_temp = pd.read_csv("../Database/Precipitations/Data"+Station+"Minutes/Data"+Station+"M9524.txt", sep=";", low_memory=False)

    last_time = dfprec['time'].iloc[-1]
    df_temp_no_overlap= dfprec_temp[dfprec_temp['time'] > last_time]
    dfprec = pd.concat([dfprec, df_temp_no_overlap], ignore_index=True)

    del dfprec['stn']
    dfprec.time = pd.to_datetime(dfprec['time'], yearfirst=True, utc=False, format='%Y%m%d%H%M')
    dfprec.replace('-', 0, inplace=True)
    dfprec['rre150z0'] = pd.to_numeric(dfprec['rre150z0'])
    dfprec = dfprec[(dfprec.time.dt.year >= yearmin) & (dfprec.time.dt.year < 2025)]

    n=6*24
    rows_to_keep = len(dfprec) - (len(dfprec) % n)
    dfprec = dfprec.iloc[:rows_to_keep]
    dfprec['group'] = np.floor(dfprec.index / n)
    dfprecsummed = dfprec.groupby('group')['rre150z0'].sum()

    # Handle Oni index
    dfoni = pd.read_csv("../Database/ONI/oni_index.csv", sep=";")
    dfoni = dfoni[(dfoni.Year >= yearmin) & (dfoni.Year < 2025)]
    dfoni = dfoni.reset_index()
    
    # Handle NAO index
    dfnao = pd.read_csv("../Database/NAO/nao.csv", sep=";")

    for i in range(len(dfnao)):
            if np.isnan(dfnao['aao_index_cdas'].iloc[i]):
                idx = i
                dfnao.loc[dfnao.index[i], 'aao_index_cdas'] = dfnao.loc[dfnao.index[i-1], 'aao_index_cdas']
                print(idx)

    dfnao['time'] = pd.to_datetime(dfnao[['year','month','day']])
    dfnao = dfnao.reset_index()
    dfnao = dfnao[(dfnao.time.dt.year >= yearmin) & (dfnao.time.dt.year < 2025)]
    dfnao = dfnao.reset_index()

    # Handle SST
    dfsst = pd.DataFrame()
    for i, p in enumerate(Places_sst):
        dfsst_temp = pd.read_csv("../Database/SST/SST_"+p+".csv", sep=",")
        if i == 0:
            dfsst['time'] = pd.to_datetime(dfsst_temp['time'], format='%Y-%m-%d')
        dfsst["sst_"+p] = dfsst_temp['sst']

    dfsst = dfsst[(dfsst.time.dt.year >= yearmin) & (dfsst.time.dt.year < 2025)]  
    dfsst = dfsst.reset_index()

    # Combining the Data Frames into the nao one
    dfnao['ONI'] = [dfoni['ONI'].iloc[i] for i in dfnao['time'].dt.to_period('M').factorize()[0]]
    for j, p in enumerate(Places_sst):
        dfnao['sst_'+p] = [dfsst["sst_"+p].iloc[i] for i in dfnao['time'].dt.to_period('M').factorize()[0]]
    dfnao['dir_x'] = np.cos(rad)
    dfnao['dir_y'] = np.sin(rad)
    dfnao['int'] = dfwind_int[col_int]
    labels = np.array(dfprecsummed)
    labels = np.delete(labels, -1)

    # Converting into one large 2D numpy array and Normalizing
    samples = dfnao[['aao_index_cdas','ONI']+['sst_'+p for p in Places_sst]+['dir_x','dir_y','int']].to_numpy()
    print('Returns 2D-numpy array with rows per day and with columns: nao, oni, [sst] and Returns 1D-numpy array with the monthly rain sum as labels')

    if Normalized == True:
        norms = np.linalg.norm(samples, axis=1, keepdims=True)
        norms[norms == 0] = 1
        samples = samples / norms

    return samples, labels




