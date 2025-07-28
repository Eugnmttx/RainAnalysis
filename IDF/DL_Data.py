import pandas as pd 

def DL_Data(Path,Station,):

    df=pd.read_csv(Path+"/Data"+Station+"Minutes/Data"+Station+"M8095.txt", sep=";", low_memory=False)
    df_temp=pd.read_csv(Path+"/Data"+Station+"Minutes/Data"+Station+"M9524.txt", sep=";", low_memory=False)
    last_time = df['time'].iloc[-1]
    df_temp_no_overlap= df_temp[df_temp['time'] > last_time]
    df = pd.concat([df, df_temp_no_overlap], ignore_index=True) # Ici on fusionne les données de 80 à 95 avec 95 à 25

    del df['stn']
    df.time = pd.to_datetime(df['time'], yearfirst=True, utc=False, format='%Y%m%d%H%M')
    df.replace('-', 0, inplace=True)
    df = df[~df.time.dt.year.isin([2025, 1980])] # J'enlève les années incomplètes manuellement
    return df