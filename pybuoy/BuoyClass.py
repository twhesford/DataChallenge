import numpy as np
from .WindClass    import Wind 
from .WaveClass    import Waves
from .CurrentClass import Currents
from .ClimateClass import Climate


class Buoy:
    """
    Buoy class assembles ocean, wave, and met
    data objects for working with sources like 
    buoys and met stations.
    Attributes:
        wind : WindClass object
        waves : WaveClass object
        currents : CurrentClass object
        climate : ClimateClass object
        h : water depth
        timestamps : use if all objects have
        the same timestamps.
    """

    def __init__(self):
        self.initialize()

    def initialize(self):

        self.wind = Wind(None,None)
        self.waves = Waves(None,None)
        self.currents = Currents(None,None)
        self.climate  = Climate()
        self.h = None
        self.lat = None
        self.lon = None
        self.timestamps = None
        
        return self

    def rotate_buoy(self,y_displacement):
        """
        This function rotates the coordinate system 
        of the buoy y_displacement degrees clockwise 
        from the current y-axis. Wind and Wave angles 
        are adjusted to stay in [0,360], currents are 
        kept in Cartesian coordinates.
        INPUTS:
            -y_displacement = angle of rotation clockwise 
            -                 from the current positive y-axis
            -                 in degrees.
        REASSIGNS:
            -self.wind.j,self.waves.j = (self.wind.j,self.waves.j) - theta
            -self.currents.i,self.currents.j = u,v Cartesian coordinates in new 
            -                                  coordinate system."""

        self.wind.new_coordsys(y_displacement,cart=False)
        self.waves.new_coordsys(y_displacement,cart=False)
        self.currents.new_coordsys(y_displacement,cart=True)

        
    def savebuoy(self,buoy_id,path=''):
        """
        docstring."""
        
   
        if len(self.wind.i.shape) == 0 or len(self.wind.j.shape) == 0:
            print('no wind data')
        else:
            wind = np.zeros((2,len(self.wind.i)))
            wind[range(2),:] = self.wind.i,self.wind.j
            np.save(path+buoy_id+'wind.npy',wind)
            
        cli_data = self.climate.cat_data()
        if np.all(cli_data == 0):
            print('no climate data')
        else:
            np.save(path+buoy_id+'climate.npy',cli_data) 

        if self.waves.Tp is None or self.waves.j is None or self.waves.swh is None:
            print('no wave data')
        else:
            bulk_waves = np.zeros((4,len(self.waves.j)))
            bulk_waves[range(4),:] = self.waves.swh,self.waves.Tp,self.waves.Tm,self.waves.j
            np.save(path+buoy_id+'waves.npy',bulk_waves)
        
        if self.waves.spec is None:
            print('no wave spectrum data')
        else:
            np.save(path+buoy_id+'wvspec.npy',self.waves.spec)
            np.save(path+buoy_id+'fbins.npy',self.waves.fbins) 
        
        if len(self.currents.i.shape) == 0 or len(self.currents.j.shape) == 0:
            print('no current data')
        else:
            currents = np.zeros((self.currents.i.shape[0],self.currents.i.shape[1],2))
            currents[:,:,0] = self.currents.i
            currents[:,:,1] = self.currents.j
            np.save(path+buoy_id+'currents.npy',currents)
        if type(self.timestamps)==None:
            print('no timestamps')
        else:
            np.save(path+buoy_id+'times.npy',self.timestamps)
            
    def readbuoy(self,buoy_id,path=''):
        """
        docstring"""
        def read_meta(buoy,data):
            buoy.timestamps = data
        def read_wind(buoy,data):
            buoy.wind.i = data[0,:]
            buoy.wind.j = data[1,:]
        def read_bulk_waves(buoy,data):
            data[data<0] = np.nan
            try:
                buoy.waves.swh = data[0,:]
                buoy.waves.Tp   = data[1,:]
                buoy.waves.Tm   = data[2,:]
                buoy.waves.j   = data[3,:]
            except IndexError: # put in place 12/17 to deal with lazieness in reformatting data
                buoy.waves.swh = data[0,:]
                buoy.waves.Tp   = data[1,:]
                buoy.waves.j   = data[2,:]            
        def read_spec(buoy,spec,fbins):
            buoy.waves.spec = spec
            buoy.waves.fbins= fbins
            
        def read_currents(buoy,data):
            buoy.currents.i = data[:,:,0]
            buoy.currents.j = data[:,:,1]
            
        def read_climate(buoy,data):          
            buoy.climate.sst         = data[:,0]
            buoy.climate.bottom_temp = data[:,1]
            buoy.climate.atm_pressure= data[:,2]
            buoy.climate.air_temp    = data[:,3]
            

        try:
            read_climate(self,np.load(path+buoy_id+'climate.npy',allow_pickle=True))
        except FileNotFoundError:
            print('no climate data')    
        try:
            read_wind(self,np.load(path + buoy_id + 'wind.npy',allow_pickle= True))
        except FileNotFoundError:
            print('no wind data')
        try:
            read_bulk_waves(self,np.load(path+buoy_id+'waves.npy',allow_pickle=True))
        except FileNotFoundError:
            print('no bulk waves data')
        try:
            read_spec(self,np.load(path+buoy_id+'wvspec.npy',allow_pickle=True),np.load(path + buoy_id+'fbins.npy',allow_pickle=True))
        except FileNotFoundError:
            print('no wave spectrum data')
        try:
            read_currents(self,np.load(path + buoy_id+'currents.npy',allow_pickle=True))
        except FileNotFoundError:
            print('no currents data')
        try:
            read_meta(self,np.load(path+buoy_id+'times.npy',allow_pickle=True))
        except FileNotFoundError:
            print('no time stamps') 
           
        
    def timeslice(self,start,end):
        """
        This function slices all data arrays to the 
        period within start and end.
        Inputs-
            start : timestamp of the start in the same 
                    format as self.timestamps.
            end   : timestamp of the end.
        Rassigns-
            all objects with data arrays.
        -Tim Hesford"""
        
        idx_map = np.array(range(len(self.timestamps)))
        start_idx = idx_map[self.timestamps==start][0]
        end_idx = idx_map[self.timestamps==end][0] +1

        try:
            self.wind.i = self.wind.i[start_idx:end_idx]
            self.wind.j = self.wind.j[start_idx:end_idx]
        except IndexError:
            pass
        try:
            self.waves.j = self.waves.j[start_idx:end_idx]
            self.waves.swh = self.waves.swh[start_idx:end_idx]
            self.waves.Tm = self.waves.Tm[start_idx:end_idx]
            self.waves.Tp = self.waves.Tp[start_idx:end_idx]
            self.waves.spec = self.waves.spec[start_idx:end_idx,:]
#             try:
#                 t_ax = list(self.waves.spec.shape).index(max(self.waves.spec.shape))
#                 if t_ax==0:
#                     self.waves.spec = self.waves.spec[start_idx:end_idx,:]
#                 else:
#                     self.waves.spec = self.waves.spec[:,start_idx:end_idx]
#             except AttributeError:
#                 pass
        except IndexError:
            pass
        try:
            self.timestamps = self.timestamps[start_idx:end_idx]
        except AttributeError:
            pass
        try:
            self.climate.sst = self.climate.sst[start_idx:end_idx]
            self.climate.air_temp = self.climate.air_temp[start_idx:end_idx]
            self.climate.atm_pressure = self.climate.atm_pressure[start_idx:end_idx]
        except IndexError:
            pass

