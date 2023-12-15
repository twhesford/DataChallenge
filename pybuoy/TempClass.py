import numpy as np

class Temps:
    
    def __init__(self,sst=None,bot_temp=None,air_temp=None):
        
        self.sst = np.array(sst)
        self.air_temp = np.array(air_temp)
        self.bot_temp = np.array(bot_temp)
        
        