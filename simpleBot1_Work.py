import tkinter as tk
import random
import math
import numpy as np

class Brain():

    def __init__(self,botp):
        self.bot = botp
        self.lightAfraid = False

    # modify this to change the robot's behaviour, right now all it does is stay in same place
    # lightL and lightR are total amount of light on each of the sensors in the bot
    # x and y are coordinates, sl and sr are speed of left and right wheel
    def thinkAndAct(self, lightL, lightR, x, y, sl, sr):
        # wheels not moving - no movement - no response to light
        
        #making robot move towards the light

        lightSum = (lightL + lightR) * 0.1

        speedLeft = 0
        speedRight = 0
        

        if(self.lightAfraid):
            #make robot move away from light
            speedLeft = 10 - (lightR -lightL)*0.8 # this code is more relative in light difference than dividing by 2 if they are different
            # this also makes the bot slow around the light and fast away from it, can make the LOVE variant as in Vehicle 3

            speedRight = 10 - (lightL - lightR) * 0.8 # if lightR > lightL, the speed of right is bigger as 10 - (negative number)

            '''
            if(lightL > lightR):
                ##speed is halfed for right wheel to make a right move away from light
                speedLeft = max(-10,min(scaledValue,10))
                speedRight = speedLeft / 2
            elif(lightR >= lightL):
                ##speed is halfed for left wheel to make left turn away from light
                # if they are equal it will just make a turn to get away from light source, as if they are equal it is facing the light source
                speedRight = max(-10,min(scaledValue,10))
                speedLeft = speedRight / 2
            '''
        else:


            #make robot move towards light
            
            # if lightR is bigger -> make speedLeft larger
            # if lightL is bigger -> make speedRight larger

            speedLeft = (100 - (lightL - lightR) * 0.8)
            speedRight = (100 - (lightR - lightL) * 0.8)

            if speedLeft > 100:
                speedLeft = 100
            elif speedLeft < 0:
                speedLeft = 0

            if speedRight > 100:
                speedRight = 100
            elif speedRight < 0:
                speedRight = 0

            speedRight = max(10,speedRight / lightSum)
            speedLeft = max(10,speedLeft / lightSum)

            #if self.bot.batteryLevel % 20 == 0:
             #   print("got here")

            '''
            if(lightL > lightR):
                ##speed is halfed for left wheel to make a left move
                speedRight = max(-10,min(scaledValue,10))
                speedLeft = speedRight / 2
            elif(lightR > lightL):
                ##speed is halfed for right wheel to make right turn
                speedLeft = max(-10,min(scaledValue,10))
                speedRight = speedLeft / 2
            else:
                #same speed
                speedLeft = max(-10,min(scaledValue,10)) # make sure the speed is between -10 and 10
                speedRight = max(-10,min(scaledValue,10))
            '''
        newX = None
        newY = None
        return speedLeft, speedRight, newX, newY # return new speed and position

class Bot():
    # random canvas placement at the start
    def __init__(self,namep):
        self.name = namep
        # x and y are positions
        self.x = random.randint(100,700)
        self.y = random.randint(100,500)
        self.theta = random.uniform(0.0,2.0*math.pi)
        #self.theta = 0
        self.ll = 60 #axle width
        self.sl = 0.0
        self.sr = 0.0
        self.currentCount = 0
        self.turnCount = 15
        self.batteryLevel = 100

    # uses the senseLight to use its sensors and make a decision
    def thinkAndAct(self, agents, passiveObjects):
        lightL, lightR = self.senseLight(passiveObjects) # poll the light sensors for info
        self.sl, self.sr, xx, yy = self.brain.thinkAndAct(lightL, lightR, self.x, self.y, self.sl, self.sr) # use the brain function, given these lights to make decision
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
        for pp in passiveObjects: ## lamps 
            if isinstance(pp,Lamp):
                lx,ly = pp.getLocation()
                distanceL = math.sqrt( (lx-self.sensorPositions[0])*(lx-self.sensorPositions[0]) + \
                                       (ly-self.sensorPositions[1])*(ly-self.sensorPositions[1]) )
                distanceR = math.sqrt( (lx-self.sensorPositions[2])*(lx-self.sensorPositions[2]) + \
                                       (ly-self.sensorPositions[3])*(ly-self.sensorPositions[3]) )
                lightL += 200000/(distanceL*distanceL)
                lightR += 200000/(distanceR*distanceR)
        return lightL, lightR
    

    # what happens at each timestep
    def update(self,canvas,dt):
        # for now, the only thing that changes is that the robot moves
        #   (using the current settings of self.sl and self.sr)
        self.batteryLevel -= 0.5
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
        canvas.create_oval(centre1PosX-8,centre1PosY-8,\
                           centre1PosX+8,centre1PosY+8,\
                           fill="gold",tags=self.name)

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

    # handles the physics of the movement
    #
    # cf. Dudek and Jenkin, Computational Principles of Mobile Robotics
    def move(self,canvas,dt):

        #make bot stop moving if battery level is below or 0
        if self.batteryLevel <= 0:
            self.sl = 0
            self.sr = 0


        self.currentCount += 1
        if(self.currentCount >= self.turnCount):
            #make a random turn left or right
            self.makeRandomTurn()

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
        
        newX,newY = self.toroidal(newv.item(0),newv.item(1),canvas) # make sure that if bot goes outside of bounds it appears on the other side
        
        newTheta = newv.item(2)
        newTheta = newTheta%(2.0*math.pi) #make sure angle doesn't go outside [0.0,2*pi)
        self.x = newX
        self.y = newY
        self.theta = newTheta        
        if self.sl==self.sr: # straight line movement
            self.x += self.sr*math.cos(self.theta) #sr wlog
            self.y += self.sr*math.sin(self.theta)
        canvas.delete(self.name)
        self.draw(canvas) # redraws the robot
    
    def makeRandomTurn(self):
        self.currentCount = 0
        self.turnCount = random.randint(5,25)

        rightOrLeft = random.randint(0,1)

        if(rightOrLeft == 0):
            self.sr = 0.0* self.sl # make a right turn
        else:
            self.sl = 0.0 * self.sr # make a left turn


    def toroidal(self, oldX, oldY, canvas):

        # normalise the values around the canvas size dimenions
        newX = oldX % canvas.winfo_reqwidth()
        newY = oldY % canvas.winfo_reqheight()

        return newX, newY
        

class Lamp():
    #randomly placement on canvas
    def __init__(self,namep):
        self.centreX = random.randint(100,700)
        self.centreY = random.randint(100,500)
        self.name = namep
        
    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-10,self.centreY-10, \
                                  self.centreX+10,self.centreY+10, \
                                  fill="yellow",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY

#creates the window to display screen
def initialise(window):
    window.resizable(False,False)
    canvas = tk.Canvas(window,width=800,height=600)
    canvas.pack()
    return canvas

def buttonClicked(x,y,agents):
    for rr in agents:
        if isinstance(rr,Bot):
            rr.x = x
            rr.y = y

# creates bits abd lamps
def createObjects(canvas,noOfBots,noOfLights):
    agents = []
    passiveObjects = []
    for i in range(0,noOfBots):
        bot = Bot("Bot"+str(i))
        brain = Brain(bot) #each robot has a brain
        bot.setBrain(brain)
        agents.append(bot)
        bot.draw(canvas)
    for i in range(0,noOfLights):
        lamp = Lamp("Lamp"+str(i))
        passiveObjects.append(lamp)
        lamp.draw(canvas)
    canvas.bind( "<Button-1>", lambda event: buttonClicked(event.x,event.y,agents) )
    return agents, passiveObjects

# infinite loop: thinkAndAct lets bot make decisions and update updates the state of robot, updates canvas every 50ms
def moveIt(canvas,agents,passiveObjects):
    for rr in agents:
        rr.thinkAndAct(agents,passiveObjects)
        rr.update(canvas,1.0)
    canvas.after(50,moveIt,canvas,agents,passiveObjects)

def main():
    window = tk.Tk()
    canvas = initialise(window)
    agents, passiveObjects = createObjects(canvas,noOfBots=1,noOfLights=4) #creating the lights and robots, 
    #agents is a list of moving bots and passiveObjects is non moving
    moveIt(canvas,agents,passiveObjects) #loop that 
    # adjusts speed of robots based on their light sensors
    # update state of robot, update method(calls move)
    window.mainloop() #gets app ready to run

main()
