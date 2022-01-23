#! /usr/bin/python
#-*- coding: utf-8 -*-
import math
import joblib
import random
import numpy as np
from robot import Robot #Import a base Robot
from enum import Enum
from math import cos, sin, radians

class Modes(Enum):
    T800 = 't800'
    CHARLIER = 'charlier'
    WALL_RUNNER = 'wall_runner'
    COIN = 'coin'
    INITIAL = 'initial'



MOVE_LIMIT = 0  # never get closer than this from the walls (hitting wall loose health)
MOVE_PRECISION = 20

class Scout(Robot): #Create a Robot
    
    def init(self):# NECESARY FOR THE GAME   To initialyse your robot
        
        
        #Set the bot color in RGB
        self.setColor(0, 200, 100)
        self.setGunColor(200, 200, 0)
        self.setRadarColor(255, 60, 0)
        self.setBulletsColor(0, 200, 100)
        
        # get game informations
        self.MapX = self.getMapSize().width()
        self.MapY = self.getMapSize().height()
        
        #get the map size
        size = self.getMapSize() #get the map size
        self.radarVisible(True) # show the radarField
        self.setRadarField("normal")
        self.lockRadar("gun")
        self.a = 10
        self.f = 1
        self.mode = Modes.INITIAL
        self.clf=joblib.load('./model.sav')
        
        self.radarGoingAngle = 5
        self.lookingForBot = 0
        self.angleMinBot = 0
        self.angleMaxBot = 0
        self.enemies = {}
        self.runcounter = 0     #used to record time based on game turns for our bot
        self.noSpotCounter = 0
        self.last_time = 0      #used to measure delays in "game turns"
        self.angles = {}

        self.clf=joblib.load('./model.sav')

    def run(self): #NECESARY FOR THE GAME  main loop to command the bot
        self.runcounter += 1
        self.noSpotCounter += 1
        self.MyComputeBotSearch(0)
        if self.mode == Modes.T800:
            self.setRadarField('thin')
            self.move(10)
            self.turn(self.radarGoingAngle)
            self.gunTurn(self.radarGoingAngle)
        elif self.mode == Modes.WALL_RUNNER:
            self.setRadarField('thin')
            self.move(10)
            self.turn(self.radarGoingAngle)
            self.gunTurn(self.radarGoingAngle)
        elif self.mode == Modes.CHARLIER:
            self.setRadarField('thin')
            self.move(5)
            self.turn(self.radarGoingAngle)
            self.gunTurn(self.radarGoingAngle)
        elif self.mode == Modes.COIN:
            self.setRadarField('thin')
            self.move(1)
            if self.noSpotCounter > 10:
                self.radarGoingAngle += 10
            self.turn(self.radarGoingAngle)
            self.gunTurn(self.radarGoingAngle)
        else:
            self.setRadarField('normal')
            self.move(3)
            self.turn(self.radarGoingAngle)
            self.gunTurn(self.radarGoingAngle)
        
    def sensors(self):  #NECESARY FOR THE GAME
        # get rid of dead oppponents in our tracking list
        list = self.getEnemiesLeft()  # return a list of the enemies alive in the battle
        alive = []
        for robot in list:
            alive.append(robot["id"])
        missing = []
        for robot in self.enemies:
            if robot not in alive:
                missing.append(robot)
        for robot in missing:
            del self.enemies[robot]
        
    def onHitByRobot(self, robotId, robotName):
        self.rPrint("damn a bot collided me!")

    def onHitWall(self):
        self.reset() #To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event) 
        self.pause(1)
        self.move(-50)
        self.rPrint('ouch! a wall !')
        self.changeMode(Modes.INITIAL)
        self.turn(30)
        self.gunTurn(30)
    
    def onRobotHit(self, robotId, robotName): # when My bot hit another
        self.rPrint('collision with:' + str(robotName)) #Print information in the robotMenu (click on the righ panel to see it)
       
    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower): #NECESARY FOR THE GAME
        """ When i'm hit by a bullet"""
        self.reset()#To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event)
        # self.move(4)

        self.rPrint ("hit by " + str(bulletBotName) + "with power:" +str( bulletPower))

    def changeMode(self, new_mode):
        old_mode = self.mode
        self.mode = new_mode
        if self.mode == Modes.CHARLIER and old_mode != Modes.CHARLIER:
            self.turn(90)
        if self.mode != Modes.CHARLIER and old_mode == Modes.CHARLIER:
            self.turn(-90)

        
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
    
    def onTargetSpotted(self, botId, botName, botPos, bot_color=None):#NECESARY FOR THE GAME
        "when the bot see another one"
        self.noSpotCounter = 0
        pos = self.getPosition()
        dx = botPos.x() - pos.x()
        dy = botPos.y() - pos.y()
        
        dist=math.sqrt(dx**2+dy**2)
        self.changeMode(Modes(self.predictOpponent(dist, bot_color)))
        
        if botId not in self.enemies:
            self.enemies[botId] = {}
            self.enemies[botId]["x"] = botPos.x()
            self.enemies[botId]["y"] = botPos.y()
            self.enemies[botId]["move"] = self.runcounter
        else:
            if self.enemies[botId]["x"] != botPos.x() or self.enemies[botId]["y"] != botPos.y():
                self.enemies[botId]["x"] = botPos.x()
                self.enemies[botId]["y"] = botPos.y()
                self.enemies[botId]["move"] = self.runcounter



        self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(botPos.x()) + " , y:" + str(botPos.y()))

        self.MyComputeBotSearch(botId)

    def predictOpponent(self, dist, bot_color):
        dist_calc=int(dist/4)
        c1 = bot_color[0] # + random.randrange(-dist_calc, dist_calc)
        c2 = bot_color[1] # + random.randrange(-dist_calc, dist_calc)
        c3 = bot_color[2] # + random.randrange(-dist_calc, dist_calc)
        return self.clf.predict(np.asarray((c1, c2, c3)).reshape(1, -1))

    
    def MyComputeBotSearch(self, botSpotted):
        # when we know all enemies positions, we compute radar seeking range
        # based on known enemy positions to avoid scanning empty space.

        #angles will store all enemies position for us
        angles = {}

        if self.noSpotCounter > 50:
            self.changeMode(Modes.INITIAL)
            self.noSpotCounter = 0
        e1 = len(self.getEnemiesLeft()) - 1  # we are counted in enemiesLeft !!
        e2 = len(self.enemies)
        if e1 == e2:
            # we know all enemies position, optimise radar moves
            pos = self.getPosition()

            my_radar_angle = self.getRadarHeading() % 360

            for botId in self.enemies:
                dx = self.enemies[botId]["x"] - pos.x()
                dy = self.enemies[botId]["y"] - pos.y()
                enemy_angle = math.degrees(math.atan2(dy, dx)) - 90
                a = enemy_angle - my_radar_angle
                if a < -180:
                    a += 360
                elif 180 < a:
                    a -= 360
                angles[a] = botId

            amin = min(angles.keys())
            amax = max(angles.keys())
            self.angleMinBot = angles[amin]
            self.angleMaxBot = angles[amax]

            if amin > 0:
                self.radarGoingAngle = min([5, amin])
            elif amin < 0:
                self.radarGoingAngle = -min([5, -amin])
            else:
                self.radarGoingAngle = 1
                
                
                #called with some bot spotted ! try to shoot ...
            if botSpotted!=0 and abs(self.radarGoingAngle)<1 and self.runcounter>self.last_time:
                enemyX = self.enemies[angles[amin]]["x"]
                enemyY = self.enemies[angles[amin]]["y"]
                dx= enemyX - pos.x()
                dy= enemyY - pos.y()
                
                dist=math.sqrt(dx**2+dy**2)
                if not self.mode == Modes.WALL_RUNNER or dist < 150:
                    self.fire(int(1000/dist)+1)
                #slow down fire rate with distance
                self.last_time=self.runcounter+int(dist/150)

            if self.lookingForBot == botSpotted:
                #bot spotted is the one we were looking for.
                #there are multiple enemies, go back and forth between enemies

                if self.lookingForBot == self.angleMinBot:
                    self.lookingForBot = self.angleMaxBot
                    if (self.radarGoingAngle<0):
                        self.radarGoingAngle = -self.radarGoingAngle
                else:
                    self.lookingForBot = self.angleMinBot
                    if (self.radarGoingAngle>0):
                        self.radarGoingAngle = -self.radarGoingAngle

            elif self.lookingForBot not in self.enemies:
                # lookingForBot not defined or lookingForBot is dead now
                # start seeking another one
                if self.radarGoingAngle > 0:
                    self.lookingForBot = self.angleMaxBot
#                    self.radarGoingAngle = (amax / abs(amax)) * min([5, abs(amax)])
                else:
                    self.lookingForBot = self.angleMinBot
#                   self.radarGoingAngle = (amin / abs(amin)) * min([5, abs(amin)])
