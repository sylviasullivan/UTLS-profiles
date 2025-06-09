# Extract <n> random indices along each dimension (time, alt, lat, lon) of variable <var>
def randIndx(var):
    import numpy as np
    n = 10
    dim_rand = np.empty((n, 4), dtype='int')
    t_size, alt_size, lat_size, lon_size = var.shape
    dim_rand[:, 0] = np.random.randint(low=0, high=t_size, size=n)
    dim_rand[:, 1] = np.random.randint(low=0, high=alt_size, size=n)
    dim_rand[:, 2] = np.random.randint(low=0, high=lat_size, size=n)
    dim_rand[:, 3] = np.random.randint(low=0, high=lon_size, size=n)
    return dim_rand
