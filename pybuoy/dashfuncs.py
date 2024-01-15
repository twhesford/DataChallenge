import numpy as np
import matplotlib.pyplot as plt
import panel as pn
from .webfuncs import get_git_txt
from .ClassNDBC import NDBC


def phi2mm(phi_units):
    """
    This function converts grain diameter
    from phi units to mm."""
    return 10**(-phi_units/3.322)

def get_field(buoy,field):
    """
    This function selects the buoy data field corresponding 
    to input field and calls the seafloor stress function from
    Madsen94.py"""
    
    # calculate seafloor roughess for D_50 = 1.7 phi (0.31mm)
    rgh = 2.5*.001*phi2mm(1.7)

    var_dict = {'Seafloor Stress (pa)':buoy.waves.bottom_stress(rgh)[0],
                'Wind Dir. (deg)':buoy.wind.j,
                'Wind Speed (m/s)':buoy.wind.i,
                'Sig. Wave Height (m)':buoy.waves.swh,
                'Peak Period (s)':buoy.waves.Tp,
                'Mean Period (s)':buoy.waves.Tm,
                'Mean Wave Dir. (deg)':buoy.waves.j,
                'Atm. Pressure (hPa)':buoy.climate.atm_pressure,
                'Air Temp (c)':buoy.climate.air_temp,
                'SST (c)':buoy.climate.sst}
    
    return var_dict[field]

def get_time_idx(event_dur,percent):
    """
    This function maps a % of the storm duration 
    to a time index."""
    
    return int(np.round(event_dur*(percent/100)))

def plot_map(ax,coast,stations,blat,blon):
    """
    This function plots the moorings and coast 
    on the model panel."""
    
    ax.plot(coast[:,0],coast[:,1],'k.',markersize=.05)

    for i in range(len(stations)):
        
        ax.plot(blon[i],blat[i],'o',label=stations[i])
                
    ax.legend()#fontsize=10,loc = 'lower right')
    
def reshape_loaded_3darr(loaded_arr):
    """
    This function inputs model outputs flattened into 
    a 2d array for storage on GitHub and reshapes them into 
    a 3d array."""
    load_original_arr = loaded_arr.reshape( 
    loaded_arr.shape[0], loaded_arr.shape[1] // 166, 166)
    return load_original_arr

def fetch_mod_data(event):
    """
    This funciton reads model outputs stored on 
    GitHub."""
    cur_arr2d = get_git_txt(event + 'cur.txt')
    sst_arr2d = get_git_txt(event + 'sst.txt')
    curr = reshape_loaded_3darr(cur_arr2d)
    sst = reshape_loaded_3darr(sst_arr2d)
    
    return curr,sst

def fmt_stamp(stamp):
    """
    This function formats NDBC time stamps 
    to display as x tick labels on the dashboard"""
    
    stamp = str(stamp)
    return stamp[5:7] + '/' + stamp[8:10] + ' ' + stamp[11:] + ':00'

def plot(event,dtype,mdtype,time,meta):
    """
    This is the main function """
    
    # unpack meta data
    stations,depths,events,names,mod_coords,blat,blon,ec = meta
    
    
    
    event_stamps= events[:,1:][events[:,0]==event][0]

    mooring_idx = list(map(lambda x : x in event,['a.','b.','c.','d.']))

    mooring = np.array(stations)[mooring_idx][0]
    event_yr = event_stamps[0][:4]


    station = NDBC(str(mooring))
    
    buoy = station.NDBC_to_Buoy(years=[int(event_yr)],stamps=event_stamps)
    buoy.waves.h = np.array(depths)[mooring_idx]
    mod_cur,mod_sst = fetch_mod_data(event)
    
    # initialize figure
    fig,ax = plt.subplots(1,2)
    for a in ax:
        a.grid(ls='--',lw=1)
    Nticks = 5 # number of x ticks
    tfs = 10 # panel title fontsize
    tkfs= 8  # tick and axis label fontsize
    suptitle = event[event.index(' ')+1:] + ' ' + '{}'.format(event_yr) # subplot title 
    fig.suptitle(suptitle)
    # select buoy data field to plot    
    met_dat = get_field(buoy,dtype)
    
    # time indicies from from time slider %
    mod_tidx = get_time_idx(mod_cur.shape[0],time)
    tidx = get_time_idx(len(met_dat),time)

    # set x ticks and x tick labels for buoy data  
    ticks = np.linspace(0,len(met_dat)-1,Nticks,dtype=int)
    stamps = buoy.timestamps[ticks]
    
    # plot buoy data
    ax[0].plot(met_dat)
    ax[0].plot(tidx,met_dat[tidx],'o')
    
    # format buoy subplot
    ax[0].set_xticks(ticks)
    ax[0].set_xticklabels(list(map(fmt_stamp,stamps)),rotation = 30,fontsize=tkfs)
    ax[0].set_title(str(mooring) + ' ' +dtype,fontsize=tfs)
    
    
    # plot model data
    if mdtype == 'Seafloor Current Spd. (m/s)':
        ax[1].pcolormesh(mod_coords[:,:,1],mod_coords[:,:,0],mod_cur[mod_tidx,:,:])
    else:
        ax[1].pcolormesh(mod_coords[:,:,1],mod_coords[:,:,0],mod_sst[mod_tidx,:,:])
        
    # format model subplot
    ax[1].set_title(mdtype,fontsize=tfs)
    ax[1].set_ylim(np.nanmin(mod_coords[:,:,0]),np.nanmax(mod_coords[:,:,0]))
    ax[1].set_xlim(np.nanmin(mod_coords[:,:,1]),np.nanmax(mod_coords[:,:,1]))
  
    ax[1].set_ylabel('Lat.',fontsize=tkfs)
    ax[1].set_xlabel('Lon.',fontsize=tkfs)
    
    #  plot shoreline and buoy locations
    plot_map(ax[1],ec,stations,blat,blon)
    
    
    plt.tight_layout()
    
    
    return pn.pane.Matplotlib(fig)
    