import numpy as np
from .VectorClass import Vector2d


class Waves(Vector2d):
    
    """
    Waves takes the phase speed as self.i and direction as 
    self.j, or i,j = u,v components of the bulk phase speed. Angles 
    are assumed to be the clockwise displacement from the positive 
    y-axis in degrees.                          
    ATTRIBUTES:
        -self.i = Cartesian u or polar r component of phase speed.
        -self.j = Cartesian v or polar theta component of phase speed.
        -self.swh = Significant wave height.
        -self.Tm = Mean Wave period.
        -self.Tp = Peak wave period.
        -self.h = water depth.
    IMPROVEMENTS:
    Add support for the full wave spectrum and include more solutions to the 
    Stokes-Drift.
    -Tim Hesford"""

    def __init__(self,i=None,j=None,swh=None, k=None,depth=None,Tm=None,Tp=None,spec=None,fbins=None):
        super().__init__(i,j)
        self.swh,self.Tp,self.Tm,self.h,self.spec,self.fbins = swh,Tp,Tm,depth,spec,fbins

    def new_coordsys(self,y_displacement,cart=False):
        """
        This function applies a clockwise rotation 
        y_displacement degrees from the current 
        positive y axis using Vector2d.rot_angles(theta,cart=False).
        INPUTS:
            -self in polar coordinates.
        REASSIGNS:
            -self.j = self.j - y_displacement."""

        self.rot_angles(y_displacement,cart=cart)

    def getk(self):
        """See docstring in wavenumber.py"""
        from wavenumber import getk
        
        return getk(self.Tp,self.h)

   

    def bottom_velocity(self,h):
        """See docstring in madsen94.py"""
        from madsen94 import bed_velocity
        
        return bed_velocity(self.spec,self.fbins,self.h)
     
        return friction
    
    def bottom_stress(self,K_N,C_mu=1,rho=1025):
        """See docstring in madsen94.py"""
        
        from .madsen94 import seafloor_stress
        
        return seafloor_stress(self.spec,self.fbins,self.h,K_N,C_mu=1,rho=1025)

    