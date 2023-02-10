import matplotlib.pyplot as plt
import numpy as np
import pygame
pygame.init()
WHITE=(255, 255, 255)
GREEN = (0, 128, 0)
RED = (188, 39, 50)
BLUE = (0, 40, 180)
PINK = (255, 182, 193)

font = pygame.font.SysFont("Helvetica", 16)

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("prob calc")

angles = 0
deltav = 0
distrn = 0
vsum = 0

disties = []
spds = []
angie = []

time = [1, 2, 3, 4 ,5 ,6, 7]
spotnr = 2000
area = 3136/1000000
nrs = []
class simbod:
    G = 6.67 * 10**(-11)
    M = 5.97 * 10**24
    STEP = 0.05
    def __init__(self, apg, prg):
        self.apg = apg
        self.prg = prg
        self.a = (apg + prg)/2
        self.e = self.apg/self.a - 1
        self.truan = 0
        self.period = 131958
        self.ac = 3.136 * 10**(-3)
    
    def update(self):
        global distrn, deltav
        self.truan = self.truan + self.STEP
        distrn =(self.a *(1-self.e**2) / (1 + self.e * np.cos(self.truan)))
        param = (self.a/distrn) * np.sqrt(((1-self.e**2)*distrn)/(2*self.a - distrn))

        beta = np.pi - np.arcsin(param)
        #ang = abs(beta - np.pi/2)
        ang = 3*np.pi/4 - beta
        vrn = np.sqrt(self.G * self.M * ((2/distrn)- (1/self.a)))

        vd = np.sqrt(self.G*self.M / distrn)

        deltav = np.sqrt(vrn**2 + vd**2 - 2*vrn*vd*np.cos(ang))

body = simbod(1600000, 600000)

def simulate():
    run = True
    global angles
    global vsum
    
    clock = pygame.time.Clock()

    while run:
            
        clock.tick(60)
        millis = clock.get_time()
        angles = body.truan
        if angles >= np.pi:
            run = False
        WIN.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        body.update()
        angie.append(angles)
        disties.append(distrn)
        vsum += deltav
        spds.append(deltav)
        progr = font.render("Tinkering... Progress so far: ", 1, WHITE)
        WIN.blit(progr , (10, 10))
        actualprogr = font.render(str(int(np.pi - angles)), 1, WHITE)
        WIN.blit(actualprogr, (30, 30))
        
        pygame.display.update()
    pygame.quit()
simulate()

plt.plot(angie, spds)
#plt.plot(disties, spds)
#plt.legend()
plt.xlabel("True anomaly (rad)")
#plt.ylabel("Relative velocity (m/s)")
#plt.xlabel("Distance to Earth's center (m)")
plt.ylabel("Relative velocity (m/s)")
plt.show()
numar = (body.period * body.ac * 3 * vsum)/(8 * np.pi * (body.apg)**3 - (body.prg)**3)
print(numar)