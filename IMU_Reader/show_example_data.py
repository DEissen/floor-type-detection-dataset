import numpy as np
from matplotlib import pyplot as plt

if __name__ == "__main__":
    y = np.genfromtxt('logged_data/footForce.csv', delimiter=';')
    #y = y[2000:2500]
    x = np.arange(0, np.shape(y)[0])
    plt.title("Matplotlib demo") 
    plt.plot(x,y) 
    plt.show()