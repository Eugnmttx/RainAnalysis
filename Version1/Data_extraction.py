import numpy as np
import pandas as pd

def Get_data(Station, Places_sst, Normalized):
    """
    Args: 
        Station = (str) Swiss Stations name
        Places_sst = (str array) Name of the places for Sea Surface Temperature
    Return:
        Dataset = (2D array) Withn Rows per day and with columns: rain, nao, oni, [sst]
    """

    # Handle Rain Data
    dfprec = pd.read_csv("../Database/Precipitations/Data"+Station+"Minutes/Data"+Station+"M8095.txt", sep=";", low_memory=False)
    dfprec_temp = pd.read_csv("../Database/Precipitations/Data"+Station+"Minutes/Data"+Station+"M9524.txt", sep=";", low_memory=False)

    last_time = dfprec['time'].iloc[-1]
    df_temp_no_overlap= dfprec_temp[dfprec_temp['time'] > last_time]
    dfprec = pd.concat([dfprec, df_temp_no_overlap], ignore_index=True)

    del dfprec['stn']
    dfprec.time = pd.to_datetime(dfprec['time'], yearfirst=True, utc=False, format='%Y%m%d%H%M')
    dfprec.replace('-', 0, inplace=True)
    dfprec = dfprec[~dfprec.time.dt.year.isin([2025, 1980])]
    dfprec['rre150z0'] = pd.to_numeric(dfprec['rre150z0'])

    n=6*24
    rows_to_keep = len(dfprec) - (len(dfprec) % n)
    dfprec = dfprec.iloc[:rows_to_keep]
    dfprec['group'] = np.floor(dfprec.index / n)
    dfprecsummed = dfprec.groupby('group')['rre150z0'].sum()

    # Select the bounds of the dataset
    yearmin = dfprec.time.dt.year.iloc[0]
    yearmax = dfprec.time.dt.year.iloc[-1]+1

    # Handle Oni index
    dfoni = pd.read_csv("../Database/ONI/oni_index.csv", sep=";")
    dfoni = dfoni[~dfoni.Year.isin(np.arange(0,yearmin))]
    

    # Handle NAO index
    dfnao = pd.read_csv("../Database/NAO/nao.csv", sep=";")

    for i in range(len(dfnao)):
            if np.isnan(dfnao['aao_index_cdas'].iloc[i]):
                idx = i
                dfnao.loc[dfnao.index[i], 'aao_index_cdas'] = dfnao.loc[dfnao.index[i-1], 'aao_index_cdas']
                print(idx)

    dfnao = dfnao[~dfnao.year.isin(np.arange(0,yearmin))]
    dfnao = dfnao[~dfnao.year.isin([yearmax])]
    dfnao['time'] = pd.to_datetime(dfnao[['year','month','day']])
    dfnao = dfnao.reset_index()

    # Handle SST
    dfsst = pd.DataFrame()
    for i, p in enumerate(Places_sst):
        dfsst_temp = pd.read_csv("../Database/SST/SST_"+p+".csv", sep=",")
        if i == 0:
            dfsst['time'] = pd.to_datetime(dfsst_temp['time'], format='%Y-%m-%d')
        dfsst["sst_"+p] = dfsst_temp['sst']
    dfsst = dfsst[~dfsst.time.dt.year.isin(np.arange(0,yearmin))]
    dfsst = dfsst[~dfsst.time.dt.year.isin([yearmax])]

    # Combining the Data Frames into the nao one
    dfnao['ONI'] = [dfoni['ONI'].iloc[i] for i in dfnao['time'].dt.to_period('M').factorize()[0]]
    for j, p in enumerate(Places_sst):
        dfnao['sst_'+p] = [dfsst["sst_"+p].iloc[i] for i in dfnao['time'].dt.to_period('M').factorize()[0]]
    labels = np.array(dfprecsummed)
    labels = np.delete(labels, -1)

    # Converting into one large 2D numpy array and Normalizing
    samples = dfnao[['aao_index_cdas','ONI']+['sst_'+p for p in Places_sst]].to_numpy()
    print('Returns 2D-numpy array with rows per day and with columns: nao, oni, [sst] and Returns 1D-numpy array with the monthly rain sum as labels')

    if Normalized == True:
        norms = np.linalg.norm(samples, axis=1, keepdims=True)
        norms[norms == 0] = 1
        samples = samples / norms

    return samples, labels




