import numpy as np
from .datetimearr import datetime_array

def make_hourly(data,datatime,years,print_=True):
        
       
    def check(step):
        try:
            return np.all(timestamp == datatime[idx+step])
        except IndexError:
            return False 
    try:
        out = datetime_array(years,data.shape[1]+1)
    except IndexError:
        out = datetime_array(years,2)
        new_data = np.zeros((len(data),1))
        new_data[:,0] = data
        data = new_data
    idx_map = np.array(range(len(out)))
        
    data[data==99]= np.nan
    data[data==999]=np.nan
    data[data==9999]=np.nan
       
    idx = 0
    while idx < len(data)-1:
        timestamp = datatime[idx]
        try:
            out_idx = idx_map[out[:,0]==timestamp][0]
            step = 1
            same_hr = check(step)
            while same_hr == True:
                step += 1 
                same_hr = check(step)
            out[out_idx,1:] =  np.nanmean(data[idx:idx+step,:],axis=0)
            idx += step  
                
        except IndexError:
            if print_ ==True:
                print(idx,timestamp,'is not in years')
            idx +=1
            pass
    return out