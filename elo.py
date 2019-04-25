import math


def get_winrate(delta, alpha):
    return 1/(1+math.e**(-alpha*delta))