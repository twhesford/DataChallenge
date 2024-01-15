from .ScrapeClass import DataScrape
from .datetimearr import datetime_array
import numpy as np

class NDBC:
    
    def __init__(self,station):
        
        self.baselink   = 'https://www.ndbc.noaa.gov//'
        self.exts = {
            'history' : 'station_history.php?station={}'.format(station),
            'realtimemet':'data//realtime2//{}.txt'.format(station),
            'realtimeswden':'data//realtime2//{}.data_spec'.format(station)
                    }
  
    
    def make_timestamp(self,datehr,sep='-'):
        out = ''
        for i in range(len(datehr)):
            out += str(int(datehr[i])) if int(datehr[i]) >=10 else '0' + str(int(datehr[i]))
            out += sep
        return out[:-1]
    
    def make_hrly(self,data,datatime,years):
        
        from .make_hr import make_hourly

        return make_hourly(data,datatime,years)          
            
    def get_histdata(self,datatypes,years,printlink=False):
        """
        docstring  
        
        """
        
        def check_header(data,header):
            if header == False: # if the header is commented out in the NDBC archive
                return data
            else:
                return np.array(data[1:,:],dtype=float)
            
        def check_timestamp(data,minutes):
            if minutes == True: # if data has minutes in timestamp
                return data
            else:
                out_data = np.zeros((len(data),data.shape[1]+1))
                out_data[:,:4] = data[:,:4]
                out_data[:,5:] = data[:,4:]
                return out_data
            
        def fmt_data(raw_data,year):
            
            if int(year) < 2007:
                header = True
            else:
                header = False
                        
            if int(year) < 2005:
                minutes = False
            else:
                minutes = True
                
            data = check_header(raw_data,header)
            data = check_timestamp(data,minutes)
            
            return data
            
        self.fields = datatypes
        self.years  = years
        
        fields = {}
        for data in datatypes:
            fields[data] = list(map(str,years))

        scraper = DataScrape(self.baselink,fields=fields)
        goodhrefs = scraper.layer1_and_search(ext=self.exts['history'])
        output = np.zeros(len(goodhrefs),dtype=object)
        histfilt = lambda goodhrefs : filter(lambda href : 'histor' in href,
                                             goodhrefs)
        extensions = map(histfilt,
                         goodhrefs)
        field_idx = 0
        for field in extensions:
                i = 0
                has_data = False # avoids copies in output when theres no availible data.
                
                for ext in field:
                    has_data = True
                        
                    if i == 0:                        
                        href = scraper.layer1_search(fields=['view_text'],ext=ext)[0][0]
                        response = scraper.make_request(self.baselink,href)

                        data = fmt_data(scraper.read_txtarry(response),years[i]) 
                                        
                        if printlink == True:    
                            print(self.baselink+href)             
                    else:                        
                        href = scraper.layer1_search(fields=['view_text'],ext=ext)[0][0]
                        response = scraper.make_request(self.baselink,href) 
                        try:
                            yr_data = fmt_data(scraper.read_txtarry(response),years[i]) 
                            data = np.concatenate((data,yr_data))

                                
                        except ValueError:
                            print('Inconsistent Array Size in the link below')
                            pass
                        if printlink == True:    
                            print(self.baselink+href)                        
                    i += 1     
                    
                output[field_idx] = data if has_data == True else []
                field_idx += 1
        if len(output) == 1:
            return output[0]
        else:
            return output
                
            
    def NDBC_to_Buoy(self,years,stamps,printlink=False):
        
        from .NDBCHelp import NDBC_stdmet,NDBC_swden
    

        wvbuoy = NDBC_swden(self,years,stamps,printlink=printlink)
        metbuoy =  NDBC_stdmet(self,years,stamps,printlink=printlink)
        metbuoy.waves.spec = wvbuoy.waves.spec
        metbuoy.waves.fbins = wvbuoy.waves.fbins
        
        metbuoy.timeslice(stamps[0],stamps[1])
        return metbuoy        