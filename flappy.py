from itertools import cycle
import random
import sys
import numpy as np
import pygame
from pygame.locals import *#pygame中所有的常量的引入


class FlappyBird:#一个FlappBird类
    def __init__(self):#类内定义函数自带的self参数,这个函数就是在船舰一个类对象的时候默认调用的方法
        self.score=0
        self.FPS = 300 # 帧数，一秒对应帧数（4的倍数），相当于刷新频率
        self.SCREENWIDTH  = 288
        self.SCREENHEIGHT = 512#设置游戏界面的长宽
        self.PIPEGAPSIZE  = 150 #gap between upper and lower part of pipe（管道上下的间隙）
        '''
        if 10<=self.score and self.score<=200:
            self.PIPEGAPSIZE = self.PIPEGAPSIZE-self.score//4
        elif 200<self.score:
            self.PIPEGAPSIZE = 100
        '''
        self.BASEY= self.SCREENHEIGHT * 0.79# 游戏最下面有一个土地，这个就是土地的y,这里坐标系的原点是左上角
        # 类里的图像文件，声音文件，撞击文件等资源
        self.IMAGES, self.SOUNDS, self.HITMASKS = {}, {}, {}



        # 三种鸟的图片资源存于players_list中，里面包括的三种飞行姿势
        self.PLAYERS_LIST = (
            # red bird
            (
                'assets/sprites/redbird-upflap.png',
                'assets/sprites/redbird-midflap.png',
                'assets/sprites/redbird-downflap.png',
            ),
            # blue bird
            (
                'assets/sprites/bluebird-upflap.png',
                'assets/sprites/bluebird-midflap.png',
                'assets/sprites/bluebird-downflap.png',
            ),
            # yellow bird
            (
                'assets/sprites/yellowbird-upflap.png',
                'assets/sprites/yellowbird-midflap.png',
                'assets/sprites/yellowbird-downflap.png',
            ),
        )
    
        # 背景
        self.BACKGROUNDS_LIST = (
            'assets/sprites/background-day.png',
            'assets/sprites/background-night.png',
        )
    
        # 管子
        self.PIPES_LIST = (
            'assets/sprites/pipe-green.png',
            'assets/sprites/pipe-red.png',
        )
    


        self.main()#初始化函数完毕后调用main函数

    def main(self):
        global SCREEN, FPSCLOCK#全局变量，是pygame的默认常量
        pygame.init()#pygame库初始化
        FPSCLOCK = pygame.time.Clock()#一个定时器对象，用于设置游戏循环频率
        SCREEN = pygame.display.set_mode((self.SCREENWIDTH, self.SCREENHEIGHT))#创建游戏窗口
        pygame.display.set_caption('Flappy Bird')#游戏标题

        # numbers sprites for score display
        self.IMAGES['numbers'] = (#绘制得分数字图像
            pygame.image.load('assets/sprites/0.png').convert_alpha(),#load是用于加载图片，后面的就是将图片绘制出来的方法
            pygame.image.load('assets/sprites/1.png').convert_alpha(),
            pygame.image.load('assets/sprites/2.png').convert_alpha(),
            pygame.image.load('assets/sprites/3.png').convert_alpha(),
            pygame.image.load('assets/sprites/4.png').convert_alpha(),
            pygame.image.load('assets/sprites/5.png').convert_alpha(),
            pygame.image.load('assets/sprites/6.png').convert_alpha(),
            pygame.image.load('assets/sprites/7.png').convert_alpha(),
            pygame.image.load('assets/sprites/8.png').convert_alpha(),
            pygame.image.load('assets/sprites/9.png').convert_alpha()
        )

        # game over sprite
        self.IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
        # message sprite for welcome screen
        self.IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
        # base (ground) sprite
        self.IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

        # self.SOUNDS
        if 'win' in sys.platform:
            soundExt = '.wav'
        else:
            soundExt = '.ogg'

        #设置各个情况下的音效
        self.SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
        self.SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
        self.SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
        self.SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
        self.SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

        #while True:
        # 随机选一个背景
        randBg = random.randint(0, len(self.BACKGROUNDS_LIST) - 1)
        self.IMAGES['background'] = pygame.image.load(self.BACKGROUNDS_LIST[randBg]).convert()

        # 随机选一个颜色的小鸟
        randPlayer = random.randint(0, len(self.PLAYERS_LIST) - 1)
        self.IMAGES['player'] = (
            pygame.image.load(self.PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(self.PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(self.PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # 随机一个管道，有上有下
        pipeindex = random.randint(0, len(self.PIPES_LIST) - 1)
        self.IMAGES['pipe'] = (
            pygame.transform.flip(#代表将管道在垂直方向上旋转，也就是上下反转
                pygame.image.load(self.PIPES_LIST[pipeindex]).convert_alpha(), False, True),
            pygame.image.load(self.PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # 获得管道的hitmask(这个是图像的alpha通道---专用名词还不清楚具体作用)
        self.HITMASKS['pipe'] = (
            self.getHitmask(self.IMAGES['pipe'][0]),
            self.getHitmask(self.IMAGES['pipe'][1]),
        )

        # 获得鸟的hitmask，获得边界
        self.HITMASKS['player'] = (
            self.getHitmask(self.IMAGES['player'][0]),
            self.getHitmask(self.IMAGES['player'][1]),
            self.getHitmask(self.IMAGES['player'][2]),
        )


        self.num_statex = int((self.SCREENWIDTH + (200)) - 57+80)+1
        self.num_statey=(332+440)+1
        self.num_states=self.num_statex*self.num_statey#算出环境的状态数
        self.num_actions=2
        self.action=1 #0 move, 1 not move
        self.absorbing = np.zeros(self.num_states, dtype=bool)

        self.lookup()

        #movementInfo = self.showWelcomeAnimation()#需要参数action
        #crashInfo = self.mainGame(movementInfo)
        #self.showGameOverScreen(crashInfo)

    #显示开始的游戏画面
    def showWelcomeAnimation(self,action):
        """Shows welcome screen animation of flappy bird"""
        # index of player to blit on screen
        #鸟的编号
        playerIndex = 0
        playerIndexGen = cycle([0, 1, 2, 1])#飞行姿势
        # iterator used to change playerIndex after every 5th iteration
        loopIter = 0

        #鸟的坐标位置
        playerx = int(self.SCREENWIDTH * 0.2)
        playery = int((self.SCREENHEIGHT - self.IMAGES['player'][0].get_height()) / 2)

        #message图像的位置
        messagex = int((self.SCREENWIDTH - self.IMAGES['message'].get_width()) / 2)
        messagey = int(self.SCREENHEIGHT * 0.12)

        basex = 0
        # 最大可以向左移动的距离，所以到了末尾的地方就要停止了
        baseShift = self.IMAGES['base'].get_width() - self.IMAGES['background'].get_width()

        # 尿中欢迎界面上下移动
        playerShmVals = {'val': 0, 'dir': 1}

        while True:
            if action==1:
                #self.SOUNDS['wing'].play()#对应位行为1的话就播放这个音效
                return {#返回的是初始位置
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        # 调整playery, playerIndex, basex
            if (loopIter + 1) % 5 == 0:
                playerIndex = next(playerIndexGen)
            loopIter = (loopIter + 1) % 30
            basex = -((-basex + 4) % baseShift)
            self.playerShm(playerShmVals)

            # draw sprites绘制位图
            #第一个参数是图，第二个参数是图绘制的其实位置
            SCREEN.blit(self.IMAGES['background'], (0,0))#背景位图
            SCREEN.blit(self.IMAGES['player'][playerIndex],
                        (playerx, playery + playerShmVals['val']))#鸟的位图
            SCREEN.blit(self.IMAGES['message'], (messagex, messagey))#欢迎消息的位图
            SCREEN.blit(self.IMAGES['base'], (basex, self.BASEY))#

            pygame.display.update()
            FPSCLOCK.tick(self.FPS)#这个就是每秒多少画面的数据设置


    def mainGame(self,action):

        if action==1:#1是不动，0是动
            if self.playery > -2 * self.IMAGES['player'][0].get_height():
                self.playerVelY = self.playerFlapAcc
                self.playerFlapped = True
                #self.SOUNDS['wing'].play()

        # check for score
        playerMidPos = self.playerx + self.IMAGES['player'][0].get_width() / 2
        for pipe in self.upperPipes:
            pipeMidPos = pipe['x'] + self.IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:#得分规则：鸟的中心位置
                self.score += 1
                #self.SOUNDS['point'].play()

        # playerIndex basex change
        if (self.loopIter + 1) % 3 == 0:
            self.playerIndex = next(self.playerIndexGen)
        self.loopIter = (self.loopIter + 1) % 30
        basex = -((-self.basex + 100) % self.baseShift)

        # rotate the player
        if self.playerRot > -90:
            self.playerRot -= self.playerVelRot

        # player's movement
        if self.playerVelY < self.playerMaxVelY and not self.playerFlapped:
            self.playerVelY += self.playerAccY
        if self.playerFlapped:
            self.playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            self.playerRot = 45

        playerHeight = self.IMAGES['player'][self.playerIndex].get_height()
        self.playery += min(self.playerVelY, self.BASEY - self.playery - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            uPipe['x'] += self.pipeVelX
            lPipe['x'] += self.pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if len(self.upperPipes) > 0 and 0 < self.upperPipes[0]['x'] < 5:
            newPipe = self.getRandomPipe()
            self.upperPipes.append(newPipe[0])
            self.lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if len(self.upperPipes) > 0 and self.upperPipes[0]['x'] < -self.IMAGES['pipe'][0].get_width():
            self.upperPipes.pop(0)
            self.lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(self.IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            SCREEN.blit(self.IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(self.IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(self.IMAGES['base'], (basex, self.BASEY))
        # print score so player overlaps the score
        self.showScore(self.score)

        # Player rotation has a threshold
        visibleRot = self.playerRotThr
        if self.playerRot <= self.playerRotThr:
            visibleRot = self.playerRot

        # check for crash here

        self.crashTest = self.checkCrash({'x': self.playerx, 'y': self.playery, 'index': self.playerIndex},
                               self.upperPipes, self.lowerPipes)
        if self.crashTest[0]:
            self.deltax = (self.lowerPipes[-2]['x'] - self.playerx)
            self.deltay = (self.lowerPipes[-2]['y'] - int(self.playery))
            #print('deltax: ', self.deltax, 'deltay: ', self.deltay)
            #print('pipLx: ', self.lowerPipes)
            #print('pipUx: ', self.upperPipes)
            #print('x: ', self.playerx, 'y: ', self.playery)

            return {
                'y': self.playery,
                'groundCrash': self.crashTest[1],
                'basex': self.basex,
                'upperPipes': self.upperPipes,
                'lowerPipes': self.lowerPipes,
                'score': self.score,
                'playerVelY': self.playerVelY,
                'playerRot': self.playerRot
            }

        self.deltax=(self.lowerPipes[-2]['x']-self.playerx)
        self.deltay=(self.lowerPipes[-2]['y']-int(self.playery))

        # print('deltax: ',self.deltax,'deltay: ',self.deltay)
        # print('pipLx: ',self.lowerPipes)
        # print('pipUx: ', self.upperPipes)
        # print('x: ',self.playerx,'y: ',self.playery)

        playerSurface = pygame.transform.rotate(self.IMAGES['player'][self.playerIndex], visibleRot)
        SCREEN.blit(playerSurface, (self.playerx, self.playery))

        pygame.display.update()
        FPSCLOCK.tick(self.FPS)


    def showGameOverScreen(self,crashInfo):#显示gameover的界面，好像没用
        """crashes the player down ans shows gameover image"""
        self.score = crashInfo['score']

        playerx = self.SCREENWIDTH * 0.2
        playery = crashInfo['y']
        playerHeight = self.IMAGES['player'][0].get_height()
        playerVelY = crashInfo['playerVelY']
        playerAccY = 2
        playerRot = crashInfo['playerRot']
        playerVelRot = 7

        basex = crashInfo['basex']

        upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

        # play hit and die self.SOUNDS
        #self.SOUNDS['hit'].play()
        #if not crashInfo['groundCrash']:
            #self.SOUNDS['die'].play()

        while True:
            # player y shift
            if playery + playerHeight < self.BASEY - 1:
                playery += min(playerVelY, self.BASEY - playery - playerHeight)

            # player velocity change
            if playerVelY < 15:
                playerVelY += playerAccY

            # rotate only when it's a pipe crash
            if not crashInfo['groundCrash']:
                if self.playerRot > -90:
                    self.playerRot -= playerVelRot

            # draw sprites
            SCREEN.blit(self.IMAGES['background'], (0,0))

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(self.IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
                SCREEN.blit(self.IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

            SCREEN.blit(self.IMAGES['base'], (basex, self.BASEY))
            self.showScore(self.score)




            playerSurface = pygame.transform.rotate(self.IMAGES['player'][1], playerRot)
            SCREEN.blit(playerSurface, (playerx,playery))
            SCREEN.blit(self.IMAGES['gameover'], (50, 180))

            FPSCLOCK.tick(self.FPS)
            pygame.display.update()
            return


    def playerShm(self,playerShm):#浮动在8~-8之间的playerShm，好像没用
        """oscillates the value of playerShm['val'] between 8 and -8"""
        if abs(playerShm['val']) == 8:
            playerShm['dir'] *= -1

        if playerShm['dir'] == 1:
             playerShm['val'] += 1
        else:
            playerShm['val'] -= 1


    def getRandomPipe(self):#返回随机生成的高度的管道
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gapY = random.randrange(0, int(self.BASEY * 0.6 - self.PIPEGAPSIZE))
        gapY += int(self.BASEY * 0.2)
        pipeHeight = self.IMAGES['pipe'][0].get_height()
        pipeX = self.SCREENWIDTH + 10#在屏幕左侧的往右10处为管道的x坐标

        return [
            {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
            {'x': pipeX, 'y': gapY + self.PIPEGAPSIZE}, # lower pipe
        ]


    def showScore(self,score):
        """displays score in center of screen"""
        scoreDigits = [int(x) for x in list(str(score))]
        totalWidth = 0 # total width of all numbers to be printed

        for digit in scoreDigits:
            totalWidth += self.IMAGES['numbers'][digit].get_width()

        Xoffset = (self.SCREENWIDTH - totalWidth) / 2

        for digit in scoreDigits:
            SCREEN.blit(self.IMAGES['numbers'][digit], (Xoffset, self.SCREENHEIGHT * 0.1))
            Xoffset += self.IMAGES['numbers'][digit].get_width()


    def checkCrash(self,player, upperPipes, lowerPipes):
        """returns True if player collders with base or pipes."""
        pi = player['index']
        player['w'] = self.IMAGES['player'][0].get_width()
        player['h'] = self.IMAGES['player'][0].get_height()

        # if player crashes into ground
        if player['y'] + player['h'] >= self.BASEY - 1:
            return [True, True]
        else:

            playerRect = pygame.Rect(player['x'], player['y'],
                          player['w'], player['h'])
            pipeW = self.IMAGES['pipe'][0].get_width()
            pipeH = self.IMAGES['pipe'][0].get_height()

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                # upper and lower pipe rects
                uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
                lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

                # player and upper/lower pipe self.HITMASKS
                pHitMask = self.HITMASKS['player'][pi]
                uHitmask = self.HITMASKS['pipe'][0]
                lHitmask = self.HITMASKS['pipe'][1]

                # if bird collided with upipe or lpipe
                uCollide = self.pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
                lCollide = self.pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

                if uCollide or lCollide:
                    return [True, False]

        return [False, False]

    def pixelCollision(self,rect1, rect2, hitmask1, hitmask2):
        """Checks if two objects collide and not just their rects"""
        rect = rect1.clip(rect2)

        if rect.width == 0 or rect.height == 0:
            return False

        x1, y1 = rect.x - rect1.x, rect.y - rect1.y
        x2, y2 = rect.x - rect2.x, rect.y - rect2.y

        for x in range(rect.width):
            for y in range(rect.height):
                if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                    return True
        return False

    def getHitmask(self,image):
        """returns a hitmask using an image's alpha."""
        mask = []
        for x in range(image.get_width()):
            mask.append([])
            for y in range(image.get_height()):
                mask[x].append(bool(image.get_at((x,y))[3]))
        return mask

    def reset(self):
        action = 1
        movementInfo = self.showWelcomeAnimation(action)
        self.init(movementInfo)
        self.mainGame(1)

        return self.state_lookup[(self.deltax,self.deltay)]

    def is_terminal(self):
        if self.crashTest[0]==True:
            return True
        else:
            return False

    def next(self,a):#传入动作
        crashInfo=self.mainGame(a)
        if crashInfo==None:
            reward=1
        else:
            reward=-1000

        state=self.state_lookup[(self.deltax,self.deltay)]
        #print(state,reward)
        return state,reward

    def lookup(self):  # 建立一个state的list和字典，这样当输入一对statex statey时可以返回一个对应的index
        self.state_lookup = {}  # 构建字典，每个(statex, statey)对应一个状态i
        state_names = []  # state_names是list，元素是(x,y)
        x = int(self.SCREENWIDTH * 0.2)  # x=57
        # 从-57遍历到431(含)
        for x in range(0 - x, int((self.SCREENWIDTH + (200)) - x) + 1):  # 左边x是下面遍历的x，右边x是上一行的x，不相同，这里属于是将固定的鸟的位置和最左最右做差
            for y in range(-322, 440 + 1):
                state_names.append((x, y))  # 一个个接入list

        for i, (statex, statey) in enumerate(
                state_names):  # enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标
            self.state_lookup[(statex, statey)] = i  # 构建字典，每个(statex, statey)对应一个状态i

    def init(self,movementInfo):
        self.score = self.playerIndex = self.loopIter = 0
        self.playerIndexGen = movementInfo['playerIndexGen']
        self.playerx, self.playery = int(self.SCREENWIDTH * 0.2), movementInfo['playery']

        self.basex = movementInfo['basex']
        self.baseShift = self.IMAGES['base'].get_width() - self.IMAGES['background'].get_width()

        # get 2 new pipes to add to upperPipes lowerPipes list
        self.newPipe1 = self.getRandomPipe()
        self.newPipe2 = self.getRandomPipe()

        # list of upper pipes
        self.upperPipes = [
            {'x': self.SCREENWIDTH + (200), 'y': self.newPipe1[0]['y']},
            {'x': self.SCREENWIDTH + (200) + (self.SCREENWIDTH / 2), 'y': self.newPipe2[0]['y']},
        ]

        # list of lowerpipe
        self.lowerPipes = [
            {'x': self.SCREENWIDTH + (200), 'y': self.newPipe1[1]['y']},
            {'x': self.SCREENWIDTH + (200) + (self.SCREENWIDTH / 2), 'y': self.newPipe2[1]['y']},
        ]

        self.pipeVelX = -4

        # player velocity, max velocity, downward accleration, accleration on flap
        self.playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
        self.playerMaxVelY =  10   # max vel along Y, max descend speed
        self.playerMinVelY =  -8   # min vel along Y, max ascend speed
        self.playerAccY    =   1   # players downward accleration
        self.playerRot     =  45   # player's rotation
        self.playerVelRot  =   3   # angular speed
        self.playerRotThr  =  20   # rotation threshold
        self.playerFlapAcc =  -9   # players speed on flapping
        self.playerFlapped = False # True when player flaps

#if __name__ == '__main__':
#    FlappyBird()
