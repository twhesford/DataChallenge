import numpy as np


def bottom_velocity(spec,fbins,h)
    """
    docstring"""

    df_1d = np.zeros_like(fbins)
    df_1d[:-1] = fbins[1:] - fbins[:-1]
    df_1d[-1] = df_1d[-2]
    f_1d = fbins+df_1d
    k_1d = getk(1/f_1d)
    df,k,f = [np.zeros_like(spec) for i in range(3)]
    t_axis = list(spec.shape).index(max(spec.shape))

    for i in range(max(spec.shape)):

        if t_axis == 0:
            f[i,:]  = f_1d
            k[i,:]  = k_1d
            df[i,:] = df_1d
        else:
            f[:,i]  = f_1d
            k[:,i]  = k_1d
            df[:,i] = df_1d
        
    ax = list(spec.shape).index(min(spec.shape))

    u_br = np.sqrt(2)*np.sqrt(np.nansum(4*np.pi**2*spec*df/((1/f)**2*(np.sinh(k*h)**2)),
                                  axis=ax))
    u_br[u_br==0] = np.nan
    T_br = 1/(np.nansum(f*df*spec,axis=ax)/np.nansum(df*spec,axis=ax))
    return u_br,T_br

def bottom_friction(u_b,T_b,K_N,C_mu = 1):


    friction = np.zeros_like(u_b)
    xi=np.zeros_like(u_b)
    if type(C_mu) is int:
        C_mu = np.ones(len(u_b))
      

    for i in range(len(u_b)):

        xi_scale = C_mu[i]*(u_b[i]*T_b[i])/K_N
        xi[i] = xi_scale
        if .2 < xi_scale < 100:
            friction[i] = C_mu[i]*np.exp((7.02*xi_scale**-.078) - 8.82)
        elif 100 < xi_scale < 10000:
            friction[i] = C_mu[i]*np.exp((5.61*xi_scale**-.109) - 7.3)
        else:
            friction[i] = np.nan
     
    return friction