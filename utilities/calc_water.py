# TEMP is temperature in K
# PRESS is pressure in Pa
# SH is specific humidity in kg kg-1
def calc_water( TEMP, PRESS, SH ):
    MH2O = 18.0153 # g mol-1 molar mass of water vapor
    MLuft = 28.97  # g mol-1 molar mass of dry air
    egas = SH * MLuft / MH2O * PRESS / (1 + SH * (MLuft / MH2O - 1.))
    ppmv = 1e6 * egas / (PRESS - egas)
    return ppmv
