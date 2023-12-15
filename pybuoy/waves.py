def getk(T,h,thresh=1e-6):
    """
    Uses the Newton-Raphson method to calculate the wavenumber
    k with an inital guess k0 being for shallow water waves where
    k0 = omega/sqrt(gh) and omega is the angular frequency 
    omega = 2pi/T. The function f is the dispersion relation for 
    surface gravity waves 0 = -omega + sqrt(gk*tanh(kh))
    This method is outlined in: 
    "A close approximation of wave dispersion relation for direct 
    calculation of wavelength in any coastal water depth" -Zai-Jin You"""
        
    # create omega and the initial guess of k defined in the doc string        
    omega = (np.pi*2)/np.array(T)
    k = omega/np.sqrt(9.81*h)
    
    # create initial values using k0
    f = (9.81 * k * np.tanh(k*h)) - omega**2 
    dfdk = 9.81*h*k*( 1/(np.cosh(k*h)**2) ) + (9.81*np.tanh(k*h))
    ii = np.any(abs(f) > thresh)
        
    while ii:                                                       
        k = k - (f/dfdk)
        f = (9.81*k*np.tanh(k*h)) - omega**2
        dfdk = 9.81*h*k*( 1/(np.cosh(k*h)**2) ) + (9.81 * np.tanh(k*h))
        ii = np.any(abs(f) > thresh)
           
    return k
 
def bottom_period(spec,f,df):
    """
    This function calculates the representative bottom 
    period."""
    
    ax = list(spec.shape).index(min(spec.shape))
    
    t_br = 1/(np.nansum(f*df*spec,axis=ax)/np.nansum(df*spec,axis=ax))
        
    return t_br

def bottom_velocity(h,spec,f,df):
    """
    This function calculates bottom orbital velocities based off 
    Madsen 1994. spec,k,f,and df must be the same shape.
    INPUTS:
        -h    = depth in meters
        -spec = wave frequency spectrum in m^2/Hz
        -f    = frequency bin centers for the inputted spectrum
        -df   = frequency discritization
    OUTPUTS:
        -u_br = bottom orbital velocities in m/s
        -t_br = representative bottom period in s"""

    # find the frequency axis
    ax = list(spec.shape).index(min(spec.shape))
 
    k = getk(1/f,h)
    
    u_br = np.sqrt(2)*np.sqrt(np.nansum((4*np.pi**2)*spec*df/((1/f)**2*(np.sinh(k*h)**2)),axis=ax))
    u_br[u_br==0] = np.nan
    
    return u_br
    
def friction_factor(u_b,T_b,K_N,C_mu):
    """
    Calculates bottom friction factor for waves and 
    currents from Madsen 1994.
    INPUTS:
        -u_b  = bottom orbital velocities in m/s
        -t_b  = representative bottom period in s
        -K_N  = roughness scale in m
        -C_mu = in the absence of currents C_mu = 1
    OUTPUTS:
        -f_wc = wave/current friction factor"""
    
    f_wc = np.zeros_like(u_b)
    xi=np.zeros_like(u_b)

    for i in range(len(u_b)):

        xi_scale = C_mu[i]*(u_b[i]*T_b[i])/K_N
        xi[i] = xi_scale
        if .2 < xi_scale < 100:
            f_wc[i] = C_mu[i]*np.exp((7.02*xi_scale**-.078) - 8.82)
        elif 100 < xi_scale < 10000:
            f_wc[i] = C_mu[i]*np.exp((5.61*xi_scale**-.109) - 7.3)
        else:
            f_wc[i] = np.nan
 
    return f_wc

def bottom_stress(u_b,f_w,
    
def tb_wv(h,spec,f,df,K_N,rho=1025):
    """
    Calculates bottom stress
    INPUTS:
        -u_b = bottom orbital velocities in m/s
    OUTPUTS:
        -t_b = bottom stress in Pa"""
    
    u_b = bottom_velocity(h,spec,f,df)
    t_b = bottom_period(spec,f,df)
    
    C_mu = np.ones_like(u_b)
    f_w = friction_factor(u_b,t_b,K_N,C_mu)
    
    return rho*f_w*(u_b**2)
    
def tb_wvcur1(wv_dir,cur_dir,cur_shear,h,spec,f,df,K_N,rho=1025):
    """
    Calculates the representative bottom stress with waves + currents
    using the bottom current shear velocity.
    INPUTS:
        -wv_dir    = direction of wave propagation (MWD) in degrees
        -cur_dir   = direction of bottom currents in degrees
        -cur_shear = current shear velocity in m/s 
        -h         = water depth in meters 
        -K_N       = bottom roughness scale in meters (CHECK UNITS!!!)
        -rho       = seawater density (defult 1025 kg/m^3)
    OUTPUTS:
        -t_b       = bottom stress in Pa"""
    
    # angle between waves and currents 
    phi =  np.deg2rad(cur_dir - wv_dir)

    mu = 0
    C_mu = np.ones_like(cur_dir)
    
    wv_strs,f_w = bottom_stress(h,K_N,C_mu,rho=rho)
    wv_shear = np.sqrt(wv_strs/rho)
    check = False
    i=0
    while check == False:
        wv_shear = np.sqrt(wv_strs/rho)
        mu = (cur_shear/wv_shear)**2
        C_mu = np.sqrt(1 + 2*mu*np.abs(np.cos(phi)) + mu**2)
        wv_strs,new_f_w = bottom_stress(h,K_N,C_mu=C_mu,rho=rho)
        dif = np.abs(f_w-new_f_w)/new_f_w
        if np.all(dif[np.isnan(dif)==False] <=.03):
            break
        f_w = new_f_w.copy()
        i +=1
    return wv_strs,C_mu

def tb_wvcur2(self,cur_dir,cur_vel,z_r,h,K_N,rho=1025):
    """
    Calculates wave generated bottom stress with the 
    addition of observed currents z_r meters above the 
    sea-floor. Make sure cur_vel is in (m/s)."""

    def delta_wc(rep_shear,T_r,u_r,C_mu,K_N):  
        d_wc = np.zeros_like(rep_shear)
        if type(C_mu) is int:
            C_mu = np.ones(len(rep_shear))
        xi_scale = (C_mu*u_b*T_r)/K_N
        for i in range(len(rep_shear)):
            if xi_scale[i] < 8:
                d_wc[i] = K_N
            else:
                d_wc[i] = 2*0.4*rep_shear[i]*T_r[i]
        return d_wc

    def cur_shear(cur_vel,rep_shear,d_wc,z_r):
        coeff = .5*rep_shear*(np.log(z_r/d_wc)/np.log(d_wc/z_o))
        interior = ((4*.4)*np.log(d_wc/z_o)*cur_vel)/(np.log(z_r/d_wc)**2*rep_shear)
        return coeff * (-1 + np.sqrt(1 + interior))

    phi =  np.deg2rad(cur_dir - wv_dir)
    mu = 0
    C_mu = 1
    z_o = K_N/30
    u_b,t_b = bottom_velocity(h)
    f_w = bottom_friction(u_b,t_b,K_N,C_mu=C_mu)
    check = False
    while check == False:
        wv_shear = np.sqrt(.5*f_w*u_b**2)
        rep_shear = np.sqrt(C_mu*wv_shear**2)
        d_wc = delta_wc(rep_shear,t_b,u_b,C_mu,K_N)
        c_shear = cur_shear(cur_vel,rep_shear,d_wc,z_r)
        mu = (c_shear/wv_shear)**2
        C_mu = np.sqrt(1 + 2*mu*np.abs(np.cos(phi)) + mu**2)
        new_f_w = bottom_friction(u_b,t_b,K_N,C_mu=C_mu)
        dif = np.abs(f_w-new_f_w)/new_f_w
        if np.all(dif[np.isnan(dif)==False] <=.02):
            break 
        f_w = new_f_w.copy()
        
    return rho*f_w*u_b**2