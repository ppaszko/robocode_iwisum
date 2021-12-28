#! /usr/bin/python
#-*- coding: utf-8 -*-
import math
import joblib
import random
import numpy as np
from robot import Robot #Import a base Robot


class Scout(Robot): #Create a Robot
    
    def init(self):# NECESARY FOR THE GAME   To initialyse your robot
        
        
        #Set the bot color in RGB
        self.setColor(0, 200, 100)
        self.setGunColor(200, 200, 0)
        self.setRadarColor(255, 60, 0)
        self.setBulletsColor(0, 200, 100)
        
        #get the map size
        size = self.getMapSize() #get the map size
        self.radarVisible(True) # show the radarField
        
    
    def run(self): #NECESARY FOR THE GAME  main loop to command the bot
        
        
        self.move(4) # for moving (negative values go back)
        self.turn(360) #for turning (negative values turn counter-clockwise)
        self.stop()
        """
        the stop command is used to make moving sequences: here the robot will move 90steps and turn 360° at the same time
        and next, fire
        """
        
        
        # self.fire(3) # To Fire (power between 1 and 10)
        
        self.move(4)
        self.turn(50)
        self.stop()
        # bulletId = self.fire(2) #to let you you manage if the bullet hit or fail
        self.move(4)
        self.turn(180)
        self.gunTurn(90) #to turn the gun (negative values turn counter-clockwise)
        self.stop()
        # self.fire(1) # To Fire (power between 1 and 10)
        self.radarTurn(180) #to turn the radar (negative values turn counter-clockwise)
        self.stop()
        
    def sensors(self):  #NECESARY FOR THE GAME
        """Tick each frame to have datas about the game"""
        
        pos = self.getPosition() #return the center of the bot
        x = pos.x() #get the x coordinate
        y = pos.y() #get the y coordinate
        
        angle = self.getGunHeading() #Returns the direction that the robot's gun is facing
        angle = self.getHeading() #Returns the direction that the robot is facing
        angle = self.getRadarHeading() #Returns the direction that the robot's radar is facing
        list = self.getEnemiesLeft() #return a list of the enemies alive in the battle
        for robot in list:
            id = robot["id"]
            name = robot["name"]
            # each element of the list is a dictionnary with the bot's id and the bot's name
        
    def onHitByRobot(self, robotId, robotName):
        self.rPrint("damn a bot collided me!")

    def onHitWall(self):
        self.reset() #To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event) 
        self.pause(100)
        self.move(-100)
        self.rPrint('ouch! a wall !')
        self.setRadarField("large") #Change the radar field form
    
    def onRobotHit(self, robotId, robotName): # when My bot hit another
        self.rPrint('collision with:' + str(robotName)) #Print information in the robotMenu (click on the righ panel to see it)
       
    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower): #NECESARY FOR THE GAME
        """ When i'm hit by a bullet"""
        self.reset()#To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event)
        self.move(4)


        self.rPrint ("hit by " + str(bulletBotName) + "with power:" +str( bulletPower))
        
    def onBulletHit(self, botId, bulletId):#NECESARY FOR THE GAME
        """when my bullet hit a bot"""
        self.rPrint ("fire done on " +str( botId))

        
    def onBulletMiss(self, bulletId):#NECESARY FOR THE GAME
        """when my bullet hit a wall"""
        self.rPrint ("the bullet "+ str(bulletId) + " fail")
        self.pause(10) #wait 10 frames
        
    def onRobotDeath(self):#NECESARY FOR THE GAME
        """When my bot die"""
        self.rPrint ("damn I'm Dead")
    
    def onTargetSpotted(self, botId, botName, botPos,bot_color=None):#NECESARY FOR THE GAME
        "when the bot see another one"
        pos = self.getPosition()
        dx = botPos.x() - pos.x()
        dy = botPos.y() - pos.y()
        dist = math.sqrt(dx ** 2 + dy ** 2)
        # self.fire(5)
        if dist>200:
            dist=200
        elif dist<20:
            dist=20
        dist_calc=int(dist/4)
        c1 = bot_color[0] + random.randrange(-dist_calc, dist_calc)
        c2 = bot_color[1] + random.randrange(-dist_calc, dist_calc)
        c3 = bot_color[2] + random.randrange(-dist_calc, dist_calc)
        clf=joblib.load('./model.sav')
        predicted_bot=clf.predict(np.asarray((c1, c2, c3)).reshape(1, -1))


        self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(botPos.x()) + " , y:" + str(botPos.y()))
    
