import tkinter as tk
from tkinter import messagebox
import random
import math
import numpy as np
import time
import sys

class Brain():

    def __init__(self,botp):
        self.bot = botp
        self.turningCount = 0 # number of turns bot gets for turning 
        self.movingCount = random.randrange(50,100) # number of turns the bot gets before starting to turn
        self.currentlyTurning = False
        self.map = np.zeros((10,10), dtype=int) # dividing x and y into 10x10 maps. Start with an array of 0s

    # modify this to change the robot's behaviour
    def thinkAndAct(self, lightL, lightR, chargerL, chargerR, x, y, sl, sr, battery,wanderingBehaviour):
        newX = None
        newY = None
        
        if(wanderingBehaviour):
            # wandering behaviour
            # bot turns around for a bit
            if self.currentlyTurning==True:
                speedLeft = -2.0
                speedRight = 2.0
                self.turningCount -= 1 # decrease turn until it reaches 0
            else:
                # make these depend on either getting to dirt or attracted to light
                speedLeft = 5.0
                speedRight = 5.0
                self.movingCount -= 1 # decreasing moving count so the bot starts to turn at some point
            if self.movingCount==0 and not self.currentlyTurning:
                self.turningCount = random.randrange(20,40) 
                self.currentlyTurning = True
            if self.turningCount==0 and self.currentlyTurning:
                self.movingCount = random.randrange(50,100)
                self.currentlyTurning = False

        #will go to unexplored parts of the map
            



        #battery - these are later so they have priority
        if battery<600:
            if chargerR>chargerL: # goes directly towards the battery
                speedLeft = 2.0
                speedRight = -2.0
            elif chargerR<chargerL:
                speedLeft = -2.0
                speedRight = 2.0
            if abs(chargerR-chargerL)<chargerL*0.1: #approximately the same
                speedLeft = 5.0
                speedRight = 5.0
        if chargerL+chargerR>200 and battery<1000: # bot now stops to make sure it recharges to at least 1000
            speedLeft = 0.0
            speedRight = 0.0

        #toroidal geometry
        if x>1000:
            newX = 0
        if x<0:
            newX = 1000
        if y>1000:
            newY = 0
        if y<0:
            newY = 1000

        return speedLeft, speedRight, newX, newY

    def updateMap(self):
        # calculating the current square the robot is in

        xMapPosition = int(math.floor(self.bot.x/100)) # get the current 10x10 x map index
        yMapPosition = int(math.floor(self.bot.y/100)) # same for y

        #safe guard for indices as at 1000 it will be 10, but we want range of 0-9
        if xMapPosition == 10:
            xMapPosition = 9
        if yMapPosition == 10:
            yMapPosition = 9

        
        self.map[xMapPosition,yMapPosition] = 1 # we have now visited the position

# so far it looks for chargers and lights
class Bot():

    def __init__(self,namep):
        self.name = namep
        self.x = random.randint(100,900)
        self.y = random.randint(100,900)
        self.theta = random.uniform(0.0,2.0*math.pi)
        #self.theta = 0
        self.ll = 60 #axle width
        self.sl = 0.0
        self.sr = 0.0
        self.battery = 1000

    def thinkAndAct(self, agents, passiveObjects):
        lightL, lightR = self.senseLight(passiveObjects)
        chargerL, chargerR = self.senseChargers(passiveObjects)
        self.sl, self.sr, xx, yy = self.brain.thinkAndAct\
            (lightL, lightR, chargerL, chargerR, self.x, self.y, self.sl, self.sr, self.battery,True)
        if xx != None:
            self.x = xx
        if yy != None:
            self.y = yy
        
    def setBrain(self,brainp):
        self.brain = brainp

    #returns the output from polling the light sensors
    def senseLight(self, passiveObjects):
        lightL = 0.0
        lightR = 0.0
        for pp in passiveObjects:
            if isinstance(pp,Lamp):
                lx,ly = pp.getLocation()
                distanceL = math.sqrt( (lx-self.sensorPositions[0])*(lx-self.sensorPositions[0]) + \
                                       (ly-self.sensorPositions[1])*(ly-self.sensorPositions[1]) )
                distanceR = math.sqrt( (lx-self.sensorPositions[2])*(lx-self.sensorPositions[2]) + \
                                       (ly-self.sensorPositions[3])*(ly-self.sensorPositions[3]) )
                lightL += 200000/(distanceL*distanceL)
                lightR += 200000/(distanceR*distanceR)
        return lightL, lightR

    #returns sensors values that detect chargers
    def senseChargers(self, passiveObjects):
        chargerL = 0.0
        chargerR = 0.0
        for pp in passiveObjects:
            if isinstance(pp,Charger):
                lx,ly = pp.getLocation()
                distanceL = math.sqrt( (lx-self.sensorPositions[0])*(lx-self.sensorPositions[0]) + \
                                       (ly-self.sensorPositions[1])*(ly-self.sensorPositions[1]) )
                distanceR = math.sqrt( (lx-self.sensorPositions[2])*(lx-self.sensorPositions[2]) + \
                                       (ly-self.sensorPositions[3])*(ly-self.sensorPositions[3]) )
                chargerL += 200000/(distanceL*distanceL)
                chargerR += 200000/(distanceR*distanceR)
        return chargerL, chargerR

    def distanceTo(self,obj):
        xx,yy = obj.getLocation()
        return math.sqrt( math.pow(self.x-xx,2) + math.pow(self.y-yy,2) )

    # what happens at each timestep
    # will need to make Dirt objects be collected here if robot is close to them
    def update(self,canvas,passiveObjects,dt):
        # for now, the only thing that changes is that the robot moves
        #   (using the current settings of self.sl and self.sr)
        self.battery -= 1 # battery goes down for now
        for rr in passiveObjects:
            if isinstance(rr,Charger) and self.distanceTo(rr)<80:
                self.battery += 10 # recharges if it is near a charger
        if self.battery<=0:
            self.battery = 0
        self.move(canvas,dt)

    # draws the robot at its current position
    def draw(self,canvas):
        points = [ (self.x + 30*math.sin(self.theta)) - 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y - 30*math.cos(self.theta)) - 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x - 30*math.sin(self.theta)) - 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y + 30*math.cos(self.theta)) - 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x - 30*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y + 30*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x + 30*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y - 30*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta)  \
                ]
        canvas.create_polygon(points, fill="blue", tags=self.name)

        self.sensorPositions = [ (self.x + 20*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                                 (self.y - 20*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta), \
                                 (self.x - 20*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                                 (self.y + 20*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta)  \
                            ]
    
        centre1PosX = self.x 
        centre1PosY = self.y
        canvas.create_oval(centre1PosX-16,centre1PosY-16,\
                           centre1PosX+16,centre1PosY+16,\
                           fill="gold",tags=self.name)
        canvas.create_text(self.x,self.y,text=str(self.battery),tags=self.name)

        wheel1PosX = self.x - 30*math.sin(self.theta)
        wheel1PosY = self.y + 30*math.cos(self.theta)
        canvas.create_oval(wheel1PosX-3,wheel1PosY-3,\
                                         wheel1PosX+3,wheel1PosY+3,\
                                         fill="red",tags=self.name)

        wheel2PosX = self.x + 30*math.sin(self.theta)
        wheel2PosY = self.y - 30*math.cos(self.theta)
        canvas.create_oval(wheel2PosX-3,wheel2PosY-3,\
                                         wheel2PosX+3,wheel2PosY+3,\
                                         fill="green",tags=self.name)

        sensor1PosX = self.sensorPositions[0]
        sensor1PosY = self.sensorPositions[1]
        sensor2PosX = self.sensorPositions[2]
        sensor2PosY = self.sensorPositions[3]
        canvas.create_oval(sensor1PosX-3,sensor1PosY-3, \
                           sensor1PosX+3,sensor1PosY+3, \
                           fill="yellow",tags=self.name)
        canvas.create_oval(sensor2PosX-3,sensor2PosY-3, \
                           sensor2PosX+3,sensor2PosY+3, \
                           fill="yellow",tags=self.name)
        self.drawMap(canvas)
        
    def drawMap(self,canvas):
        map = self.brain.map
        for i in range(map.shape[0]):
            for j in range(map.shape[1]):
                element = map[i,j]
                if(element == 1):
                    canvas.create_rectangle(100*i,100*j,100*i+100,100*j+100
                                                 ,fill="pink",width=0,tags="map")
                    canvas.tag_lower("map") 
        

    # handles the physics of the movement
    # cf. Dudek and Jenkin, Computational Principles of Mobile Robotics
    def move(self,canvas,dt):
        print("Current Battery = " + str(self.battery))
        if self.battery==0:
            self.sl = 0
            self.sl = 0
        if self.sl==self.sr:
            R = 0
        else:
            R = (self.ll/2.0)*((self.sr+self.sl)/(self.sl-self.sr))
        omega = (self.sl-self.sr)/self.ll
        ICCx = self.x-R*math.sin(self.theta) #instantaneous centre of curvature
        ICCy = self.y+R*math.cos(self.theta)
        m = np.matrix( [ [math.cos(omega*dt), -math.sin(omega*dt), 0], \
                        [math.sin(omega*dt), math.cos(omega*dt), 0],  \
                        [0,0,1] ] )
        v1 = np.matrix([[self.x-ICCx],[self.y-ICCy],[self.theta]])
        v2 = np.matrix([[ICCx],[ICCy],[omega*dt]])
        newv = np.add(np.dot(m,v1),v2)
        newX = newv.item(0)
        newY = newv.item(1)
        newTheta = newv.item(2)
        newTheta = newTheta%(2.0*math.pi) #make sure angle doesn't go outside [0.0,2*pi)
        self.x = newX
        self.y = newY
        self.theta = newTheta        
        if self.sl==self.sr: # straight line movement
            self.x += self.sr*math.cos(self.theta) #sr wlog
            self.y += self.sr*math.sin(self.theta)
        canvas.delete(self.name)
        self.brain.updateMap()
        self.draw(canvas)

    # checks if dirt is near the bot and then deletes it from canvas
    def collectDirt(self, canvas, passiveObjects, count):
        toDelete = []
        for idx,rr in enumerate(passiveObjects):
            if isinstance(rr,Dirt):
                if self.distanceTo(rr)<30: # if bot is closer than 30 eat dirt
                    canvas.delete(rr.name)
                    toDelete.append(idx)
                    count.itemCollected(canvas) # update the counter
                    print("Dirt collected = " + str(count.dirtCollected))
        for ii in sorted(toDelete,reverse=True):
            del passiveObjects[ii]
        return passiveObjects
        
# bot may be attracted to light
class Lamp():
    def __init__(self,namep):
        self.centreX = random.randint(100,900)
        self.centreY = random.randint(100,900)
        self.name = namep
        
    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-10,self.centreY-10, \
                                  self.centreX+10,self.centreY+10, \
                                  fill="yellow",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY

# robot recharges from this
class Charger():
    def __init__(self,namep):
        self.centreX = random.randint(100,900)
        self.centreY = random.randint(100,900)
        self.name = namep
        
    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-10,self.centreY-10, \
                                  self.centreX+10,self.centreY+10, \
                                  fill="red",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY

# figure out what this does
class WiFiHub:
    def __init__(self,namep,xp,yp):
        self.centreX = xp
        self.centreY = yp
        self.name = namep
        
    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-10,self.centreY-10, \
                                  self.centreX+10,self.centreY+10, \
                                  fill="purple",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY

# simple dot on screen
class Dirt:
    def __init__(self,namep):
        self.centreX = random.randint(100,900)
        self.centreY = random.randint(100,900)
        self.name = namep

    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-1,self.centreY-1, \
                                  self.centreX+1,self.centreY+1, \
                                  fill="grey",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY

# counts number of dirt collected BY ALL BOTS 
class Counter:
    dirtCollected = 0

    def itemCollected(self,canvas):
        Counter.dirtCollected += 1
        canvas.delete("dirtCount")
        canvas.create_text(50,50,anchor="w",\
                           text="Dirt collected: "+str(Counter.dirtCollected),\
                           tags="dirtCount")


def initialise(window):
    window.resizable(False,False)
    canvas = tk.Canvas(window,width=1000,height=1000)
    canvas.pack()
    
    return canvas

def buttonClicked(x,y,agents):
    for rr in agents:
        if isinstance(rr,Bot):
            rr.x = x
            rr.y = y

# same as lab1, but have dirt and charger + wifi hub
def createObjects(canvas,noOfBots=2,noOfLights=2,amountOfDirt=300):
    agents = []
    passiveObjects = []
    for i in range(0,noOfBots):
        bot = Bot("Bot"+str(i))
        brain = Brain(bot)
        bot.setBrain(brain)
        agents.append(bot)
        bot.draw(canvas)

    for i in range(0,noOfLights):
        lamp = Lamp("Lamp"+str(i))
        passiveObjects.append(lamp)
        lamp.draw(canvas)

    charger = Charger("Charger"+str(i))
    passiveObjects.append(charger)
    charger.draw(canvas)
    
    hub1 = WiFiHub("Hub1",750,50)
    passiveObjects.append(hub1)
    hub1.draw(canvas)
    hub2 = WiFiHub("Hub2",50,500)
    passiveObjects.append(hub2)
    hub2.draw(canvas)
    hub3 = WiFiHub("Hub3",800,800)
    passiveObjects.append(hub3)
    hub3.draw(canvas)

    for i in range(0,amountOfDirt):
        dirt = Dirt("Dirt"+str(i))
        passiveObjects.append(dirt)
        dirt.draw(canvas)

    count = Counter()
    
    canvas.bind( "<Button-1>", lambda event: buttonClicked(event.x,event.y,agents) )
    
    return agents, passiveObjects, count

# same as lab1
def moveIt(canvas,agents,passiveObjects,count,moves,noOfBots):
    for rr in agents:
        rr.thinkAndAct(agents,passiveObjects)
        rr.update(canvas,passiveObjects,1.0)
        passiveObjects = rr.collectDirt(canvas,passiveObjects,count)
        moves +=1
        if moves==2000:
            time.sleep(3)
            # this will be useful for evaluating how much dirt was collected based on the number of bots.
            messagebox.showinfo("Number of dirt collected", "Number of bots = "+ str(noOfBots) + 
                                ", Dirt collected = " + str(Counter.dirtCollected))
            sys.exit()
            # here need to print/ display the number of dirt collected
    canvas.after(50,moveIt,canvas,agents,passiveObjects,count,moves,noOfBots)

# same as lab 1
def main():
    window = tk.Tk()
    canvas = initialise(window)
    numberOfBots = 2
    agents, passiveObjects, count = createObjects(canvas,numberOfBots,noOfLights=0,amountOfDirt=300)
    moveIt(canvas,agents,passiveObjects,count,0,numberOfBots)
    window.mainloop()

main()
