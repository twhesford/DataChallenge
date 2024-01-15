import numpy as np
from .BuoyClass import Buoy

def NDBC_stdmet(station,years,stamps,printlink=False):
    
    data = station.get_histdata(['stdmet'],years,printlink=printlink)
    datatime = list(map(station.make_timestamp,data[:,:4]))
    
    if stamps is None:
        
        hrly_data = station.make_hrly(data[:,[5,6,8,9,10,11,12,13,14]],datatime,years)
    else:
        
        start = datatime.index(stamps[0])
        end = datatime.index(stamps[-1])     
        hrly_data = station.make_hrly(data[start:end,[5,6,8,9,10,11,12,13,14]],datatime[start:end],years)
        hrly_start = list(hrly_data[:,0]).index(stamps[0])
        hrly_end   = list(hrly_data[:,0]).index(stamps[-1])
        
    buoy = Buoy()
    
    buoy.timestamps = hrly_data[:,0]
    buoy.wind.j = np.array(hrly_data[:,1],dtype=float)
    buoy.wind.i = np.array(hrly_data[:,2],dtype=float)
    buoy.waves.swh = np.array(hrly_data[:,3],dtype=float)
    buoy.waves.Tp = np.array(hrly_data[:,4],dtype=float)
    buoy.waves.Tm = np.array(hrly_data[:,5],dtype=float)
    buoy.waves.j  = np.array(hrly_data[:,6],dtype=float)
    buoy.climate.atm_pressure = np.array(hrly_data[:,7],dtype=float)
    buoy.climate.air_temp = np.array(hrly_data[:,8],dtype=float)
    buoy.climate.sst = np.array(hrly_data[:,9],dtype=float)
    
#     if stamps is None:
#         return buoy
#     else:
#         buoy.timeslice(stamps[0],stamps[-1])
    return buoy

def NDBC_swden(station,years,stamps,printlink=False):
    
    spec = station.get_histdata(['swden'],years,printlink=printlink)
    
    datatime = list(map(station.make_timestamp,spec[:,:4]))
    
    if stamps is None:
        hrly_spec = station.make_hrly(spec[:,5:],datatime,years)
    else:
        
        start = datatime.index(stamps[0])
        end = datatime.index(stamps[-1])
        
        hrly_spec = station.make_hrly(spec[start:end,5:],datatime[start:end],years)
    buoy = Buoy()
    
    buoy.waves.spec = np.array(hrly_spec[:,1:],dtype=float)
    buoy.timestamps = hrly_spec[:,0]
    
    if np.all(np.array(years,dtype=int)> 2005):
        buoy.waves.fbins =  np.array([.0200,.0325,.0375,.0425,.0475,
                                      .0525,.0575,.0625,.0675,.0725,
                                      .0775,.0825,.0875,.0925,.1000,
                                      .1100,.1200,.1300,.1400,.1500,
                                      .1600,.1700,.1800,.1900,.2000,
                                      .2100,.2200,.2300,.2400,.2500,
                                      .2600,.2700,.2800,.2900,.3000,
                                      .3100,.3200,.3300,.3400,.3500,
                                      .3650,.3850,.4050,.4250,.4450,
                                      .4650,.4850])

#     buoy.timeslice(stamps[0],stamps[-1])
    return buoy