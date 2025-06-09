# Input a np.datetime64 and round it to the nearest 10 minutes.
def timeround10(dt):
    import datetime
    #import pandas as pd
    #dt_not_np = pd.to_datetime(dt)
    b = round(dt.minute,-1) # round(dt_not_np.minute,-1)
    if b == 60:
        return_time = datetime.datetime(2017, 8, 8, dt.hour + 1, 0)
    else:
        return_time = datetime.datetime(2017, 8, 8, dt.hour, int(b))
    return return_time
