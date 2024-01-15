import numpy as np
import pandas as pd
import requests 
from bs4 import BeautifulSoup
from .datetimearr import datetime_array
from .datearr import date_array
from .make_hr import make_hourly
from .ClassNDBC import NDBC


def get_git_txt(fil):    
    url = 'https://raw.githubusercontent.com/twhesford/DataChallenge/main/data/{}'.format(fil)
    response = requests.get(url)

    soup = BeautifulSoup(response.content,features='html.parser')

    with open('text.txt','w') as fil:
        fil.write(soup.contents[0])
        fil.close()
    try:
        dat = np.loadtxt('text.txt')
    except ValueError:
        dat= np.loadtxt('text.txt',dtype=str,delimiter=',')
    return dat

def get_meta():
    """
    This function reads buoy and event meta data from Github
    and returns the moorings, their depths, and the top 10
    events."""
    meta = np.array(get_git_txt('meta.txt'))

    idxs =np.linspace(0,44,5,dtype=int)

    names = meta[:,0]
    
    events = np.delete(meta,idxs[:-1],axis=0)

    ec = np.array(get_git_txt('east_coast.txt'))
                  

    mod_lat = get_git_txt('mod_lat.txt')
    mod_lon = get_git_txt('mod_lon.txt')
    mod_X = np.zeros((mod_lat.shape[0],mod_lat.shape[1],2))
    
    mod_X[:,:,0] = mod_lat
    mod_X[:,:,1] = mod_lon

    stations,depths,lat,lon = [[] for i in range(4)]

    for i in range(1,5):
        stations.append(int(float(meta[idxs[i-1]][0])))
        depths.append(float(meta[idxs[i-1]][1]))
        lat.append(float(meta[idxs[i-1]][2]))
        lon.append(float(meta[idxs[i-1]][3]))


    return stations,depths,events[:,:-1],names,mod_X,lat,lon,ec


