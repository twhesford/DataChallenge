import numpy as np
from .ScrapeClass import DataScrape
import ast

def NDBC_stdmet(station,Buoy,years,printlink=False):
    
    data = station.get_histdata(['stdmet'],years,printlink=printlink)
    
    datatime = list(map(station.make_timestamp,data[:,:4]))
    
    hrly_data = station.make_hrly(data[:,[5,6,8,9,10,11,12,13,14]],datatime,years)
    
    Buoy.timestamps = hrly_data[:,0]
    Buoy.wind.j = np.array(hrly_data[:,1],dtype=float)
    Buoy.wind.i = np.array(hrly_data[:,2],dtype=float)
    Buoy.waves.swh = np.array(hrly_data[:,3],dtype=float)
    Buoy.waves.Tp = np.array(hrly_data[:,4],dtype=float)
    Buoy.waves.Tm = np.array(hrly_data[:,5],dtype=float)
    Buoy.waves.j  = np.array(hrly_data[:,6],dtype=float)
    Buoy.climate.atm_pressure = np.array(hrly_data[:,7],dtype=float)
    Buoy.climate.air_temp = np.array(hrly_data[:,8],dtype=float)
    Buoy.climate.sst = np.array(hrly_data[:,9],dtype=float)
                           
    return Buoy

def NDBC_swden(station,Buoy,years,printlink=False):
    
    spec = station.get_histdata(['swden'],years,printlink=printlink)
    
    datatime = list(map(station.make_timestamp,spec[:,:4]))
    hrly_spec = station.make_hrly(spec[:,5:],datatime,years)
    
    Buoy.waves.spec = np.array(hrly_spec[:,1:],dtype=float)
    return Buoy

def NDBC_rtmet(station,Buoy):
    
    scraper = DataScrape(station.baselink)
    response = scraper.make_request(scraper.baselink,ext=station.exts['realtimemet'])
    met_data = scraper.read_txtarry(response)[::-1]
    met_data[met_data=='MM'] = np.nan
    met_data = np.array(met_data,dtype=float)    
    
    datatime = list(map(station.make_timestamp,met_data[:,:4]))
    years = np.array(list(set([met_data[0,0],met_data[-1,0]])),dtype=int)
    hrly_data = station.make_hrly(met_data[:,[5,6,8,9,10,11,12,13,14]],datatime,years)
    
    start_idx = list(np.isnan(np.array(hrly_data[:,-1],dtype=float))).index(False)
    end_idx = -list(np.isnan(np.array(hrly_data[:,-1],dtype=float)[::-1])).index(False)
    
    Buoy.timestamps = hrly_data[start_idx:end_idx,0]
    Buoy.wind.j = np.array(hrly_data[start_idx:end_idx,1],dtype=float)
    Buoy.wind.i = np.array(hrly_data[start_idx:end_idx,2],dtype=float)
    Buoy.waves.swh = np.array(hrly_data[start_idx:end_idx,3],dtype=float)
    Buoy.waves.Tp = np.array(hrly_data[start_idx:end_idx,4],dtype=float)
    Buoy.waves.Tm = np.array(hrly_data[start_idx:end_idx,5],dtype=float)
    Buoy.waves.j  = np.array(hrly_data[start_idx:end_idx,6],dtype=float)
    Buoy.climate.atm_pressure = np.array(hrly_data[start_idx:end_idx,7],dtype=float)
    Buoy.climate.air_temp = np.array(hrly_data[start_idx:end_idx,8],dtype=float)
    Buoy.climate.sst = np.array(hrly_data[start_idx:end_idx,9],dtype=float)
                           
    return Buoy

def NDBC_rtswden(station,Buoy):
    
    scraper = DataScrape(station.baselink)
    response = scraper.make_request(scraper.baselink,ext=station.exts['realtimeswden'])
    data = scraper.read_txtarry(response)[::-1]
    
    out = np.zeros_like(data,dtype=float)

    i=0
    for row in data:
        try:
            out[i,:] = np.fromiter((ast.literal_eval(val) for val in row),dtype=float)
        except SyntaxError:
            out[i,:5] = np.fromiter((int(val) for val in row[:5]),dtype=int)
            out[i,5:] = np.fromiter((ast.literal_eval(val) for val in row[5:]),dtype=float)

        i+=1

    fbins = out[0,7:][range(0,out.shape[1]-6,2)]
    spec = out[:,6:][:,range(0,out.shape[1]-6,2)]
    
    years = np.array(list(set([data[0,0],data[-1,0]])),dtype=int)
    datatime = list(map(station.make_timestamp,data[:,:4]))
    hrly_spec = station.make_hrly(spec,datatime,years)
    
    start_idx = list(np.isnan(np.array(hrly_spec[:,-1],dtype=float))).index(False)
    end_idx = -list(np.isnan(np.array(hrly_spec[:,-1],dtype=float)[::-1])).index(False)
    Buoy.waves.fbins = fbins
    Buoy.waves.spec  = np.array(hrly_spec[start_idx:end_idx,1:],dtype=float)
    
    return Buoy
    
    