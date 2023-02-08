from audioop import tostereo
from email.mime import audio
from operator import is_
from tkinter import Widget
from turtle import width
import pygame
import math
import numpy
import matplotlib
import matplotlib.pyplot as plt
pygame.init()

WHITE=(255, 255, 255)
GREEN = (0, 128, 0)
RED = (188, 39, 50)
BLUE = (0, 40, 180)
PINK = (255, 182, 193)

font = pygame.font.SysFont("Helvetica", 16)

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Debris Simulation")


apg_x, apg_y, apg_z = 0, 0, 0
prg_x, prg_y, prg_z= 0, 0, 0

apg_angles = []
apgangle = 0#-3.15 + 0.00287
prg_angles = []
prgangle = -0.3952# + 0.02 - 0.006 - 0.0142
apgpseudo = 0
prgpseudo = 0

apg0 = 0
prg0 = 0

apg0_x, apg0_y, apg0_z, prg0_x, prg0_y, prg0_z = 0, 0, 0, 0, 0, 0

anode = (0, 0)
dnode = (0, 0)
xn , yn = 0, 0 

top = int(input("1 for side view \n0 for top view\n"))
def dist(xa, ya, za, xb, yb, zb):
    dx = xa-xb
    dy = ya-yb
    dz = za-zb
    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    return distance
class body:
    AU = 149597871000
    RL = 384000000 # radius of the Moon's orbit

    c= 3*(10**8)
    G = 6.67428e-11
    SIR = 1361 # Solar irradiance 
    MO = 25000000 # mean orbital radius of the debris
    px = 250
    SCALE = px/(MO)
    TIMESTEP = 10 # dt = 10s

    def __init__ (self, x, y, z, radius, color, mass, real_radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.real_radius = real_radius
        self.color = color
        self.mass = mass

        self.xvel = 0
        self.yvel = 0
        self.zvel = 0

        self.center = False
        self.is_debris = False
        self.colided = False
        self.distance_to_center = 0
        self.apg = 0
        self.prg = math.sqrt(self.x**2  + self.y**2 + self.z*2)*2
        self.orbit = []
        self.zs = [self.z]
        self.zi = 0

    def draw(self, win):
        x = self.x*self.SCALE + WIDTH/2
        y = self.y*self.SCALE + HEIGHT/2

        if len(self.orbit) > 2:
            updated_points = []

            for point in self.orbit:
                x, y = point
                x = x*self.SCALE+ WIDTH/2
                y = y*self.SCALE+ HEIGHT/2
                updated_points.append((x,HEIGHT - y))
               
            pygame.draw.lines(win, self.color, False, updated_points, 1)
        pygame.draw.circle(win, self.color, (x, HEIGHT-y), self.radius)
        
    
    def attraction(self, other):
        dist_x=(other.x- self.x)
        dist_y=(other.y -self.y)
        dist_z=(other.z - self.z)
        dist = math.sqrt(dist_x**2 + dist_y**2 + dist_z**2)

        if other.center:
            self.distance_to_center = dist
        force = self.G * self.mass * other.mass / dist**2
        psi = math.asin(dist_z/dist)
        theta = math.atan2(dist_y, dist_x)

        force_plane = force*math.cos(psi)
        force_z = force*math.sin(psi)
        force_y = force_plane*math.sin(theta)
        force_x = force_plane*math.cos(theta)

        return force_x, force_y, force_z
    def drag(self):
        t_kelv = 273.1 -131.21 + self.distance_to_center*0.00299
        pressure = 2.488 * (t_kelv/216.6)**(-11.388)
        rho = pressure/(0.2869 * t_kelv)

        vel = math.sqrt(self.xvel**2 + self.yvel**2 + self.zvel**2)
        area = math.pi * self.real_radius**2
        drag = -0.5 * 0.5 * area * (vel**2) * rho

        psi = math.asin(self.zvel/vel)
        theta = math.atan2(self.yvel, self.xvel)

        drag_plane = drag * math.cos(psi)
        drag_z = drag* math.sin(psi)
        drag_y = drag_plane * math.sin(theta)
        drag_x = drag_plane * math.cos(theta)

        return drag_x, drag_y, drag_z


    def update_position(self, bodies):
        total_fx = total_fy = total_fz = 0
        global anode, dnode
        for body in bodies:
            if self == body or self.center:
                continue

            fx, fy, fz = self.attraction(body)
            total_fx+= fx
            total_fy += fy
            total_fz += fz
            if self.is_debris == True:
                drx, dry, drz = self.drag() #applying drag!!
                total_fx+= drx
                total_fy+= dry
                total_fz+= drz
                #total_fx += self.G*self.mass*(1.9*(10**30))/(self.AU -self.x)**2 # applying the attraction from the Sun

        if self.is_debris:
            if math.sqrt(self.y**2 + self.z**2) > 6380000 or self.x > 0:
                total_fx -= self.SIR/self.c * math.pi *self.real_radius**2 # applying the force due to solar radiation pressure

        self.xvel += (total_fx/self.mass)*self.TIMESTEP
        self.yvel += (total_fy/self.mass)*self.TIMESTEP
        if self.is_debris: self.zvel += (total_fz/self.mass)*self.TIMESTEP

        self.x += self.xvel *self.TIMESTEP
        self.y += self.yvel * self.TIMESTEP
        if self.is_debris: 
            self.z += self.zvel * self.TIMESTEP
            self.zi += 1
            self.zs.append(self.z)
        
        if self.is_debris and (numpy.sign(self.zs[self.zi]) == -numpy.sign(self.zs[self.zi-1]) or self.z == 0) and self.zvel != 0:
            if self.zvel > 0:
                anode = (self.x, self.y)
            elif self.zvel < 0:
                dnode = (self.x, self.y)

        if self.is_debris and top == 1:
            self.orbit.append((self.x, self.z))
        else:
            self.orbit.append((self.x, self.y))
        if self.distance_to_center < 6380000:
            self.colided = True
    
    def energy(self, other):
        distx = self.x - other.x
        disty = self.y - other.y
        distz = self.z - other.z
        dist = math.sqrt(distx**2 + disty**2 + distz**2)
        erg = -(self.G*self.mass*other.mass)/dist 
        return erg
def toScale(x, y, body):
    x = x*body.SCALE + WIDTH/2
    y = HEIGHT/2 - y*body.SCALE 
    return x, y
apg_neg_ang = 0
prg_neg_ang = 0

def elements(self):
    global prgpseudo, apgpseudo, apg_neg_ang, prg_neg_ang, apg_x, prg_x, apg_y, prg_y, apg_z, prg_z, apg_selected, prg_selected, apg0, prg0, apg_angles, prg_angles, apg0_x, apg0_y, apg0_z, prg0_x, prg0_y, prg0_z
    
    apgang = 0
    apgsgn = 0
    prgsgn = 0
    if self.distance_to_center > self.apg:
        if ((self.yvel > 0 and self.y < apg0_y) or (self.yvel < 0 and self.y > apg0_y)) and apg_neg_ang == 0:
            apgsgn = -1
        else:
            apg0 = self.apg
            apg0_x = apg_x
            apg0_y = apg_y
            apg0_z = apg_z
            apgsgn = +1
        self.apg = self.distance_to_center
        apg_x = self.x
        apg_y = self.y
        apg_z = self.z
        apgdistanc = dist(apg_x, apg_y, apg_z, apg0_x, apg0_y, apg0_z)
        if self.apg != 0 and apg0 != 0: apgang = math.acos((apg0**2 + self.apg**2 - apgdistanc**2)/(2*apg0*self.apg))
        if ((self.yvel > 0 and self.y < apg0_y) or (self.yvel < 0 and self.y > apg0_y)) and apg_neg_ang == 0:
            apg_neg_ang = -1 * apgang
            apgang = 0
            print("aici intra")

    elif apg_neg_ang != 0:
        apgang = apgpseudo + apg_neg_ang
        apg_neg_ang = 0
        apgpseudo = 0
    prgang = 0
    if self.distance_to_center <= self.prg:
        if ((self.yvel > 0 and self.y < prg0_y) or (self.yvel < 0 and self.y > prg0_y)) and prg_neg_ang == 0:
            print("yep yep")
            prgsgn = -1
        else:
            prg0 = self.prg
            prg0_x = prg_x
            prg0_y = prg_y
            prg0_z = prg_z
            prgsgn = +1
        self.prg = self.distance_to_center
        prg_x = self.x
        prg_y = self.y
        prg_z = self.z
        prgdistanc = dist(prg_x, prg_y, prg_z, prg0_x, prg0_y, prg0_z)
        if prg0 != 0 and self.prg != 0: prgang = math.acos((prg0**2 + self.prg**2 - prgdistanc**2)/(2*prg0*self.prg))
        if ((self.yvel > 0 and self.y < prg0_y) or (self.yvel < 0 and self.y > prg0_y)) and prg_neg_ang == 0:
            prg_neg_ang = -1*prgang
            prgang = 0

    elif prg_neg_ang != 0:
        prgang = prgpseudo + prg_neg_ang
        prgpseudo = 0
        prg_neg_ang = 0
    a = (self.apg + self.prg)/2
    e = (self.apg/a) - 1
    return a , e ,apgang, prgang

def line(a, b):
    xa, ya = a
    xb, yb = b
    if xa != xb and ya!= yb:
        m = (ya-yb)/(xa-xb)
        
        y0 = ya- m*xa
        x0 = -y0/m

        return x0, y0
    elif xa == xb:
        return xa, float('inf')
    elif ya == yb:
        return float('inf'), ya
    
 

earth = body(0, 0, 0, 15, GREEN, 5.972*(10**24), 6371000)
earth.center = True

moon = body(-1 * body.RL, 0,0, 8, WHITE, 7.34767309*(10**22), 1737400 )
moon.yvel = 1027.778

debris = body(-1*body.MO, 0,10000000, 5, RED, 0.0113, 0.001)
debris.yvel = 3938.88

debris.is_debris = True
apg0 = prg0 = math.sqrt(debris.x**2 + debris.y**2 + debris.z**2)
apg0_x = prg0_x = debris.x
apg0_y = prg0_y = debris.y
apg0_z = prg0_z = debris.z



time_elapsed =0
bodies = [earth, moon, debris]
e_tot = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
tstamp_tot = []
def main():
    run = True
    clock = pygame.time.Clock()

    while run:
        global time_elapsed, xn, yn, apgangle, prgangle, apgpseudo, prgpseudo
        clock.tick(60)
        millis = clock.get_time()
        time_elapsed += debris.TIMESTEP/millis

        time_elapsed = round(time_elapsed, 2)
        WIN.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    body.px+=5
                elif event.button == 5:
                    body.px-=5
        en = 0
        for body in bodies:
            if body == debris:
                continue
            else:
                en += debris.energy(body)

        for body in bodies:
            if not body.colided: body.update_position(bodies)
            body.draw(WIN)
        a, e, apgng, prgng = elements(debris)
        a = round(a, 3)

        if apg_neg_ang == 0: 
            apgangle = apgangle+ apgng
        else:
            apgpseudo+= apgng
        if prg_neg_ang == 0:
            prgangle = prgangle+ prgng
        else:
            prgpseudo+= prgng
        apg_angles.append(apgangle)
        prg_angles.append(prgangle)

        e_tot[0].append(e)
        tstamp_tot.append(time_elapsed*20.16)
        e = round(e, 3)
        

        xan, yan = anode
        xdn, ydn = dnode
        xn, yn = line(anode, dnode)
        long = math.atan2(xn, yn)
        long2 = math.atan2(yn, xn)
        x_prime = (yn - debris.y) * math.tan(long)
        plane = math.cos(long) * (debris.x-x_prime)
        if plane!= 0:
            i_rn = math.atan(abs(debris.z)/ abs(plane))



        adisplay = font.render(str(a), 1, WHITE)
        edisplay = font.render(str(e), 1, WHITE)
        idisplay = font.render(str(i_rn), 1, WHITE)
        longdisplay = font.render(str(long2), 1, WHITE)
        endisplay = font.render(str(en), 1, WHITE)
        tdisplay = font.render(str(time_elapsed*20.16), 1, WHITE)

        aeq = font.render("a(m) = ", 1, WHITE)
        eeq = font.render("e = ", 1, WHITE)
        ieq = font.render("i(rad) = ", 1,  WHITE)
        leq = font.render('\u03A9' + "(rad) = ", 1, WHITE)
        eneq = font.render("E(J) = ", 1, WHITE)
        teq = font.render("t(s) = ", 1, WHITE)


        WIN.blit(aeq , (10, 10))
        WIN.blit(eeq, (10, 30))
        WIN.blit(ieq, (10, 50))
        WIN.blit(leq, (10, 70))
        #WIN.blit(eneq, (10, 90))
        WIN.blit(teq, (10, 90))
        WIN.blit(adisplay, (50, 10))
        WIN.blit(edisplay, (30, 30))
        WIN.blit(idisplay, (52, 50))
        WIN.blit(longdisplay, (60 ,70))
        #WIN.blit(endisplay, (50, 90))
        WIN.blit(tdisplay, (45, 90))
        
        if top == 0: 
            #print(anode)
            #print(dnode)
            #print()  
            pygame.draw.line(WIN, PINK, toScale(xan, yan, debris), toScale(xdn, ydn, debris), 1)
            pygame.draw.line(WIN, WHITE, (WIDTH/2, HEIGHT/2), toScale(apg_x, apg_y, debris) , 1)
            pygame.draw.line(WIN,BLUE, (WIDTH/2, HEIGHT/2), toScale(prg_x, prg_y, debris) , 1)
        elif top == 1:
            #print(anode)
            #print(dnode)
            #print()
            pygame.draw.line(WIN, PINK, toScale(xan, 0, debris), toScale(xdn, 0 ,debris), 1)
            pygame.draw.line(WIN, WHITE, (WIDTH/2, HEIGHT/2), toScale(apg_x, apg_z, debris) , 1)
            pygame.draw.line(WIN,BLUE, (WIDTH/2, HEIGHT/2), toScale(prg_x, prg_z, debris) , 1)
        #print(debris.z)
        #print(" ")
        pygame.display.update()
    pygame.quit()
main()

#sub = plt.subplot()
#fig, ax = plt.subplots()
plt.plot(tstamp_tot, apg_angles, label = "apogee")
plt.plot(tstamp_tot, prg_angles, label = "perigee")
plt.legend()
plt.xlabel("Timestamp (s)")
plt.ylabel("Shift angle (rad)")
plt.show()

delta_v = []
delta_e = [0]
def deltae():
    for i in range(20):
        run = True
        global time_elapsed, xn, yn
        time_elapsed = 0
        delta_v.append(100*(i))
        clock = pygame.time.Clock()

        while run:
            
            clock.tick(60)
            millis = clock.get_time()
            time_elapsed += debris.TIMESTEP/millis
            if time_elapsed * 20.16 > 30000:
                run = False
            WIN.fill((0,0,0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            for body in bodies:
                if not body.colided: body.update_position(bodies)
            a, e = elements(debris)
            a = round(a, 3)


            e_tot[i].append(e)
        
            e = round(e, 3)
            progr = font.render("Tinkering... Progress so far: ", 1, WHITE)
            WIN.blit(progr , (10, 10))
            actualprogr = font.render(str(int(30000 - time_elapsed*20.16)), 1, WHITE)
            WIN.blit(actualprogr, (30, 30))
            iteration = font.render(str(i), 1, WHITE)
            WIN.blit(iteration, (30, 50))
            pygame.display.update()
    for i in range(1, 20):
        delta_e.append(abs(max(e_tot[0]) - max(e_tot[i])))
#deltae()

#figure, ax2 = plt.subplots()

#ax2.plot(delta_v, delta_e)

#plt.show()