# Pulling from
# https://towardsdatascience.com/kl-divergence-python-example-b87069e4b810
import numpy as np
from scipy.stats import norm
from matplotlib import pyplot as plt
import seaborn as sns
sns.set()

def kl_divergence(p,q):
    return np.sum(np.where(p != 0, p*np.log(p / q),0))
