from tkinter import *
import random
from math import sqrt
import time

# A bunch of global variables
WIDTH = 800
HEIGHT = 600
boids = []
windBlown = False
windChoices = ['North','South','East','West']
windDir = 'East'
activePrey = False
activePredator = False
showCenter = False



tk = Tk()
canvas = Canvas(tk, width=WIDTH, height=HEIGHT)
tk.title("Boids")
canvas.pack()
font = font.Font(family='Times', size='20', weight='bold')
statusText = canvas.create_text(WIDTH / 2, 10, font=font, fill='blue', text='')



class Boid:

    def __init__(self):
        x0 = random.randrange(0, WIDTH - 10)
        y0 = random.randrange(0, HEIGHT - 10)
        self.body = canvas.create_oval(x0,y0, x0 + 10, y0 + 10, fill="cyan")
        self.xspeed = 2
        self.yspeed = 2
        self.avgList = []

    def calculateVelocity(self):

        speedLimit = 10

        pos = canvas.coords(self.body)
        if pos[3] >= HEIGHT - 10 or pos[1] <= 10:
            self.yspeed = -self.yspeed
        if pos[2] >= WIDTH -10 or pos[0] <= 10:
            self.xspeed = -self.xspeed
            
        # Rule 1 - Move towards flock center
        selfPos = self.getPos()
        selfX = selfPos[0]
        selfY = selfPos[1]

        center = flockCohesion(self)
        #canvas.create_oval(center[0], center[1], center[0] + 10, center[1] + 10, fill="red")
        self.xspeed += (center[0] - selfX) / 100
        self.yspeed += (center[1] - selfY) / 100
        
        # Rule 2 - Seperation
        for boid in boids:
            if not boid is self:
                closeness = tooClose(boid, self)
                if closeness[0]:
                    boidPos = boid.getPos()
                    self.xspeed -= (boidPos[0] - selfX)
                if closeness[1]:
                    boidPos = boid.getPos()
                    self.yspeed -= (boidPos[1] - selfY)
        
        # Rule 3 - Velocity Matching
        avgSpeed = velocityMatching(self)
        self.xspeed += avgSpeed[0] / 100
        self.yspeed += avgSpeed[1] / 100
    
        speed = sqrt((self.xspeed ** 2) + (self.yspeed ** 2))
        if speed > speedLimit:
            self.xspeed = (self.xspeed / speed) * speedLimit
            self.yspeed = (self.yspeed / speed) * speedLimit

        # Rule 4 (Extra) - Adding wind
        global windBlown
        global windDir
        if windBlown:
            if windDir == 'North':
                self.yspeed -= 0.5
            elif windDir == 'South':
                self.yspeed += 0.5
            elif windDir == 'East':
                self.xspeed -= -0.5
            else:
                self.xspeed += 0.5

        # Rule 5 (Extra) - Tracking Prey
        global activePrey
        if activePrey:
            mouseCoos = mouseCoords()
            self.xspeed += (mouseCoos[0] - selfX) / 100
            self.yspeed += (mouseCoos[1] - selfY) / 100

        # Rule 6 (Extra) - Avoiding Predator
        global activePredator
        if activePredator:
            mouseCoos = mouseCoords()
            if abs(selfX - mouseCoos[0]) < 50:
                self.xspeed -= (mouseCoos[0] - selfX) / 2
            if abs(selfY - mouseCoos[1]) < 50:
                self.yspeed -= (mouseCoos[1] - selfY) / 2
            
        
    # Because smoothly reversing speed doesnt always work to keep the
    # boids in the bounds
        if selfPos[0] < 0:
            canvas.delete(self.body)
            self.body = canvas.create_oval(10, pos[1], 20, pos[3], fill="cyan")
        if selfPos[0] > WIDTH:
            canvas.delete(self.body)
            self.body = canvas.create_oval(WIDTH - 20, pos[1], WIDTH - 10, pos[3], fill="cyan")
        if selfPos[1] < 0:
            canvas.delete(self.body)
            self.body = canvas.create_oval(pos[0], 10, pos[2], 20, fill="cyan")
        if selfPos[1] > HEIGHT:
            canvas.delete(self.body)
            self.body = canvas.create_oval(pos[0], HEIGHT - 20, pos[2], HEIGHT - 10, fill="cyan")
    def move(self):
        self.calculateVelocity()
        canvas.move(self.body, self.xspeed, self.yspeed)
        global showCenter
        if showCenter:
            center = flockCohesion(self)
            avgBoid = canvas.create_oval(center[0], center[1], center[0] + 10, center[1] + 10, fill="red")
            self.avgList.append(avgBoid)
            

    def getPos(self):
        selfPos = canvas.coords(self.body)
        xPos = (selfPos[0] + selfPos[2]) / 2
        yPos = (selfPos[1] + selfPos[3]) / 2
        return (xPos, yPos)

    def getSpeed(self):
        return (self.xspeed, self.yspeed)

    def getAvgList(self):
        return self.avgList



def flockCohesion(thisBoid): # Rule 1
    n = len(boids)
    avgX = 0
    avgY = 0
    for boid in boids:
        #if not boid is thisBoid: # Perceived center for thisBoid
        boidPos = boid.getPos()
        x = boidPos[0]
        y = boidPos[1]
        avgX += x
        avgY += y

    avgX = avgX / (n)
    avgY = avgY / (n)
    return (avgX, avgY)


def tooClose(otherBoid, thisBoid): # Rule 2
    closeX = False
    closeY = False
    
    thisBoidPos = thisBoid.getPos()
    thisX = thisBoidPos[0]
    thisY = thisBoidPos[1]
    
    
    boidPos = otherBoid.getPos()
    otherX = boidPos[0]
    otherY = boidPos[1]

    if abs(thisX - otherX) < 10:
        closeX = True
    if abs(thisY - otherY) < 10:
        closeY = True

    return (closeX, closeY)

def velocityMatching(thisBoid): # Rule 3
    n = len(boids)
    speedX = 0
    speedY = 0

    for boid in boids:
        if boid != thisBoid:
            boidSpeed = boid.getSpeed()
            speedX += boidSpeed[0]
            speedY += boidSpeed[1]

    avgSpeedX = speedX / (n - 1)
    avgSpeedY = speedY / (n - 1)

    return (avgSpeedX, avgSpeedY)


def genWind():
    global windBlown
    global windDir
    global statusText
    windDir = random.choice(windChoices)
    windString = "Wind blown in " + windDir + "ward direction"
    canvas.itemconfigure(statusText, text=windString)
    windBlown = True

def stopWind():
    global windBlown
    global statusText
    canvas.itemconfigure(statusText, text='')
    windBlown = False

def mouseCoords():
    x = tk.winfo_pointerx()
    y = tk.winfo_pointery()
    return (x,y)

def activatePrey():
    global activePrey
    global statusText
    deactivatePred()
    canvas.itemconfigure(statusText, text='Pursuing Prey')
    activePrey = True
    activatePreyButton["state"] = "disabled"
    activatePredButton["state"] = "normal"
    tk.config(cursor='heart red')

def deactivatePrey():
    global activePrey
    global statusText
    canvas.itemconfigure(statusText, text='')
    activePrey = False
    activatePreyButton["state"] = "normal"
    tk.config(cursor="")
    
def activatePred():
    global activePredator
    global statusText
    deactivatePrey()
    canvas.itemconfigure(statusText, text='Avoiding Predator')
    activePredator = True
    activatePredButton["state"] = "disabled"
    activatePreyButton["state"] = "normal"
    tk.config(cursor="pirate")
    
def deactivatePred():
    global activePredator
    global statusText
    canvas.itemconfigure(statusText, text='')
    activePredator = False
    activatePredButton["state"] = "normal"
    tk.config(cursor="")

def showAvg():
    global showCenter
    showCenter = True

def hideAvg():
    global showCenter
    showCenter = False
    for boid in boids:
        avgList = boid.getAvgList()
        for avgBoid in avgList:
            canvas.delete(avgBoid)
        avgList.clear()
    

windButton = Button(tk, text="Blow Wind", command=genWind)
windButton_window = canvas.create_window(10, 10, anchor=NW, window=windButton)
stopButton = Button(tk, text="Stop Wind", command=stopWind)
stopButton_window = canvas.create_window(10, 50, anchor=NW, window=stopButton)

activatePreyButton = Button(tk, text="Create Prey", command=activatePrey)
activatePreyButton_window = canvas.create_window(10, 90, anchor=NW, window=activatePreyButton)
deactivatePreyButton = Button(tk, text="Remove Prey", command=deactivatePrey)
deactivatePreyButton_window = canvas.create_window(10, 130, anchor=NW, window=deactivatePreyButton)

activatePredButton = Button(tk, text="Create Predator", command=activatePred)
activatePredButton_window = canvas.create_window(10, 170, anchor=NW, window=activatePredButton)
deactivatePredButton = Button(tk, text="Remove Predator", command=deactivatePred)
deactivatePredButton_window = canvas.create_window(10, 210, anchor=NW, window=deactivatePredButton)

showAvgButton = Button(tk, text="Show Center of Mass", command=showAvg)
showAvgButton_window = canvas.create_window(10, 250, anchor=NW, window=showAvgButton)

hideAvgButton = Button(tk, text="Hide Center of Mass", command=hideAvg)
hideAvgButton_window = canvas.create_window(10, 290, anchor=NW, window=hideAvgButton)


'''
spinbox = Spinbox(tk, from_=1, to=30)
spinbox_window = canvas.create_window(10, 250, anchor=NW, window=spinbox)
'''
# initialize boids
for i in range(0, 20):
    newBoid = Boid()
    boids.append(newBoid)


while True:
    for boid in boids:
        boid.move()
    tk.update()
    time.sleep(0.1)

tk.mainloop()
