import matplotlib.pyplot as plt

x = [0, 1, 2, 3, 4, 5, 6]
y = [18, 7, 88, 0, 4, 33, 12]
print(x, y)
avg_y = sum(y)/len(y)
avgy = [avg_y for i in x]
starty = [y[0] for i in x]
plt.plot(x, y)
plt.plot(x, avgy)
plt.plot(x, starty)
plt.show()
