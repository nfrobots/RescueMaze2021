from matplotlib import pyplot as plt

START_VALUE = 100000
X_MAX = 20
f = lambda x: x * 0.01 + 200
#    f(x-1) = x+2

x = [i for i in range(X_MAX)]
y = [START_VALUE]
for i in range(X_MAX - 1):
    y.append(f(y[-1]))

plt.plot(x, y, 'or')
plt.show()