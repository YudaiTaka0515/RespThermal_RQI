from math import e, tanh, atan, pi


def sigmoid(x):
    y = 1/(1+e**(-x))
    return y


def arc_tan(x):
    y = atan(x)/pi + 1/2
    return y


def step(x):
    if x>=0:
        return 1
    else :
        return 0


def tanh_01(x):
    y = (tanh(x)+1)/2
    return y
