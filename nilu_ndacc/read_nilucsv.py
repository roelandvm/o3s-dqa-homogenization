import pandas as pd
import glob
from datetime import datetime

from nilu_ndacc.read_nilu_functions import organize_df, o3tocurrent

K = 273.15

filepath = '/home/poyraden/Analysis/Homogenization_Analysis/Files/Nilu/Sodankyl/version2/'

##read datafiles
allFiles = sorted(glob.glob(filepath + "/*.hdf"))

list_metadata = []

f = 0
sensortype = [''] * len(allFiles)

for filename in (allFiles):

    name = filename.split(".")[-2].split("/")[-1][2:8]
    fname = filename.split(".")[-2].split("/")[-1]
    # to not to read metada files with _md extension that has a length of more than 8
    if len(fname) > 8: continue
    print(fname)

    metafile = filepath + fname + "_md.csv"

    # extract the date from file name
    date = datetime.strptime(name, '%y%m%d')
    datef = date.strftime('%Y%m%d')

    dfd = pd.read_hdf(filename)
    # dfd = pd.read_csv(filename)
    dfd = dfd[1:]

    for i in list(dfd):
        dfd[i] = dfd[i].astype('float')

    if (len(dfd) < 500): continue
    if len(dfd.columns) < 8: continue

    # read the metadata file
    try:
        dfm = pd.read_csv(metafile, index_col=0, names=['Parameter', 'Value'])
        if (len(dfm)) < 15:
            print('skip this dataset')
            continue
    except FileNotFoundError:
        continue

    dfm = dfm.T
    dfm['Date'] = datef

    dfl = pd.DataFrame()
    # using the data and metadata make a new dataframe from them
    dfl = organize_df(dfd, dfm)

    if (len(dfl) < 300): continue

    # for some files that the value were written wrong
    try:
        sensortype[f] = dfl.at[dfl.first_valid_index(), 'SensorType']
    except KeyError:
        sensortype[f] = sensortype[f - 2]
        dfl['SensorType'] = sensortype[f - 2]
    f = f + 1
    #

    # convert the partial pressure to current
    dfl = o3tocurrent(dfl)
    # set the date
    dfl['Date'] = datef

    rawname = filename.split(".")[-2].split("/")[-1] + "_rawcurrent.hdf"
    metaname = filename.split(".")[-2].split("/")[-1] + "_metadata.csv"
    #
    dfl.to_hdf(filepath + '/Current/' + rawname, key = 'df')
    dfm.to_csv(filepath + '/Metadata/' + metaname)

    list_metadata.append(dfm)

# save all the metada in one file, either in hdf format or csv format
dff = pd.concat(list_metadata, ignore_index=True)
hdfall = filepath + "All_metadata.hdf"
csvall = filepath + "All_metadata.csv"

dff.to_hdf(hdfall, key = 'df')
dff.to_csv(csvall)

