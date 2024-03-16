import matplotlib.pyplot as plt
import numpy as np

x=np.linspace(-5,5,5)
y=x**3
print(y)

plt.plot(x,y)
plt.xlabel('x')
plt.ylabel("xcube")
plt.show()