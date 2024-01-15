import numpy as np

def getk(T,h):
    """
    Uses the Newton-Raphson method to calculate the wavenumber
    k with an inital guess k0 being for shallow water waves where
    k0 = omega/sqrt(gh) and omega is the angular frequency 
    omega = 2pi/T. The function f is the dispersion relation for 
    surface gravity waves 0 = -omega + sqrt(gk*tanh(kh))
    Inputs-
        T : peak period in seconds
        h : water depth in meters
    Outputs-
        k : wavenumber in meters
    This method is outlined in: 
    "A close approximation of wave dispersion relation for direct 
    calculation of wavelength in any coastal water depth" """
       
        
    omega = (np.pi*2)/np.array(T)
        
    k = omega/np.sqrt(9.81*h) # make sure depth is set if error is thrown here 
    # create initial values using k0
    f = (9.81 * k * np.tanh(k*h)) - omega**2 
    dfdk = 9.81*h*k*( 1/(np.cosh(k*h)**2) ) + (9.81*np.tanh(k*h))
    ii = np.any(abs(f) > 1e-10)
        
    while ii: # while ii == True
                                                                
        k = k - (f/dfdk)
        f = (9.81*k*np.tanh(k*h)) - omega**2
        dfdk = 9.81*h*k*( 1/(np.cosh(k*h)**2) ) + (9.81 * np.tanh(k*h))
        ii = np.any(abs(f) > 1e-6)
        
    return k