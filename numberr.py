import matplotlib.pyplot as plt

time = [1, 2, 3, 4 ,5 ,6, 7]
spotnr = 2000
area = 3136/1000000
nrs = []
for i in range (0, 7):
    nrs.append(area * time[i] * spotnr)

plt.plot(time, nrs)
plt.show()