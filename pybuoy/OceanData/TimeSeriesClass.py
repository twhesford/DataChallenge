from .datetimearr import datetime_array
import numpy as np

class TimeSeries:
    """
    This class contains functions used to format time series
    data."""
    

    def make_hrly(self,data,datatime,years):
        
        from .make_hr import make_hourly

        return make_hourly(data,datatime,years)

    
#         def check(step):
#             try:
#                 return np.all(timestamp == datatime[idx+step])
#             except IndexError:
#                 return False 
            
#         out = datetime_array(years,data.shape[1]+1)
#         idx_map = np.array(range(len(out)))
        
#         data[data==99]= np.nan
#         data[data==999]=np.nan
#         data[data==9999]=np.nan
        
#         idx = 0
#         while idx < len(data)-1:
#             timestamp = datatime[idx]
#             try:
#                 out_idx = idx_map[out[:,0]==timestamp][0]
#                 step = 1
#                 same_hr = check(step)
#                 while same_hr == True:
#                     step += 1 
#                     same_hr = check(step)
#                 out[out_idx,1:] =  np.nanmean(data[idx:idx+step,:],axis=0)
#                 idx += step  
                
#             except IndexError:
#                 print(timestamp,'is not in years')
#                 idx +=1
#                 pass

#         return out