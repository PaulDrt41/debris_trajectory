import math

x, y = -50,-50
l = 235

def angle (x, y, l):
    tan = (math.degrees(math.atan(y/x)))

    ang = tan

    if tan < 0 and x < 0:
        ang+= 180    
    elif tan < 0 and x > 0:
        ang += 360
    elif tan > 0 and x < 0:
        ang += 180
    true = abs(l-ang)

    while true > 180:
        true = 360-true
    truerad = true*math.pi/180 #returns the angle between the projection of the position vector of the debris
    return truerad             #and the position vector of the Moon


x = 15
y = 0
print(math.atan2(y, x))