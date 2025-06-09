from thermodynamic_functions import satVapP_ice, satMR_ice
import numpy as np
Na = 6.02214*10**23       # Avogadro's number [molecules mol-1]
Mw = 18.015/1000          # molar moass of water [kg mol-1]
kb = 1.380649*10**(-23)   # Stefan-Boltzmann constant [J K-1]
rhoa = 1.5                # air density assuming -30 C [kg m-3]
                          # This is not correct. Density should be solved for with continuity

# Diffusivity of water vapor in air as a function of temperature [K] and pressure [Pa]
# Eq 31 of Spichtinger and Gierens taken from Pruppacher and Klett 1997
# Dv [=] m2 s-1
def diffusivity_clams( T, p ):
    T0 = 273.15
    p0 = 101325
    Dv = 2.11*10**(-5)*(T / T0)**1.94*(p0 / p)
    return Dv

# Diffusivity of water vapor in air as a function of temperature [K] and pressure [Pa]
# atm_phy_schemes/mo_2mom_processes.f90 ELEMENTAL FUNCTION line 684
# Dv [=] m2 s-1
def diffusivity_icon( T, p ):
    Dv = 8.7602*10**(-5)*T**1.81/p
    return Dv

# Ice crystal length as a function of mass as in Spichtinger and Gierens 2009 (Tab 1),
# taken from Heymsfield and Iaquinta 2000, input mass [=] kg, length [=] m
def length( mass ):
    mass_threshold = 2.146*10**(-13) # [=] kg
    if(mass < mass_threshold):
        alpha = 1/526.1  # [=] m-1
        beta = 1/3
        L = alpha*mass**beta
    else:
        alpha = 1/0.04142
        beta = 1/2.2
        L = alpha*mass**beta
    return L

# Ice crystal aspect ratio as a function of mass as in Spichtinger and Gierens 2009 (Eq 17),
# derived from Heymsfield and Iaquinta 2000 and hexagonal column volume, input mass [=] kg
def aspectRatio( mass ):
    mass_threshold = 2.146*10**(-13) # [=] kg
    if(mass < mass_threshold):
        ra = 1
    else:
        rho_ice = 0.81*10**3 # [=] kg m-3
        alpha = 1/0.04142
        beta = 1/2.2
        prefactor = np.sqrt(27)*rho_ice/(8*alpha**(3/beta))
        ra = np.sqrt(prefactor)*mass**(3-beta)/(2*beta)
    return ra


# Snow particle terminal velocity as a function of mass as in SB06 (Eq 5.93),
def terminalVelocity_icon2m( mass, rho ):
    alpha = 317 # [m s-1 kg**(-beta)]
    beta = 0.363
    rho0 = 1.225 # [kg m-3] air density at surface conditions
    gamma = 0.5
    vt_ice = alpha*mass**beta*(rho0 / rho)**gamma

    alpha = 27.7 # [m s-1 kg**(-beta)]
    beta = 0.216
    vt_snow = alpha*mass**beta*(rho0 / rho)**gamma
    return vt_ice, vt_snow


# Snow particle terminal velocity as a function of mass as in Doms 2005 (Eq 5.93),
def terminalVelocity_icon1m( mass ):
    a = 0.038 # [kg m-2]
    Ds = (mass / a)**0.5
    v0_snow = 4.9   # [m^0.75 s-1]
    vt = v0_snow*Ds**0.25
    return vt


# Ice crystal terminal velocity as a function of mass, temperature, and pressure as in Spichtinger and Gierens 2009 (Eq 18),
# derived from Heymsfield and Iaquinta 2000, input mass [=] kg, T [=] K, p [=] Pa
def terminalVelocity_clams( mass, T, p ):
    m1_threshold = 2.146*10**(-13) # [=] kg
    m2_threshold = 2.166*10**(-9)
    m3_threshold = 4.264*10**(-8)

    if( mass <= m1_threshold ):
        gamma = 735.4
        delta = 0.42
    elif( (mass > m1_threshold) & (mass <= m2_threshold) ):
        gamma = 63292.4
        delta = 0.57
    elif( (mass > m2_threshold) & (mass <= m3_threshold) ):
        gamma = 329.8
        delta = 0.31
    else:
        gamma = 8.8
        delta = 0.096
    T0 = 233
    p0 = 30000
    c = (p / p0)**(-0.178)*(T / T0)**(-0.394)
    vt = gamma*c*mass**delta
    return vt

# Cloud ice mass over time via depositional growth in the kinetic regime as a function of
# ice crystal number (ni), specific humidity (qv), temperature (T), and pressure (Pa)
# as in Koehler and Seifert 2015 (Eq 62)
def kineticGrowth_icon( ni, qv, T, p ):
    alpha = 0.5  # deposition coefficient
    mw = Mw / Na # mass per molecule of water
    vth = np.sqrt( 2*kb*T/(np.pi*mw) ) # thermal velocity
    psati = satVapP_ice( T ) # saturation vapor pressure wrt ice
    qvsati = satMR_ice( T )  # saturation vapor mixing ratio wrt ice
    Dv = diffusivity_icon( T, p ) # diffusion coefficient

    num = np.pi*ni*ri**2*mw*alpha*vth*psati
    factor = 1 + alpha*vth*ri/(4*Dv)
    den = qvsati*rhoa*kb*T*factor
    dqdt = (num / den)*(qv - qvsati)
    return dqdt

# Function to calculate crystal capacitance for CLaMS
def capacitance(lengthscale, aspectratio):
    b = lengthscale
    a = aspectratio*b
    eps = np.sqrt(1 - (b/a)**2)
    C = 2*a*eps/np.log((1+eps)/(1-eps))
    return C
