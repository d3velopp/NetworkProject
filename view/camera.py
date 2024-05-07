import pygame as pg
from GameControl.setting import Setting


class Camera:

    def __init__(self, width, height):
        self.setting = Setting.getSettings()
        self.width = width
        self.height = height

        self.scroll = pg.Vector2(0, 0) #scroll is a vector
        self.scroll.x = - self.setting.getSurfaceWidth()/2 + self.width / 2
        self.scroll.y = - self.setting.getSurfaceHeight()/2 + self.height / 2
        self.dx = 0 #change in x
        self.dy = 0
        self.speed = 25 #speed of the camera

    def update(self):
        #DPI settings
        key = pg.key.get_pressed()
        if key[pg.K_RIGHT]:
            if ( self.scroll.x > - (self.setting.getSurfaceWidth() - 1920) ) :
                self.dx = -self.speed
            else:
                self.dx = 0
        elif key[pg.K_LEFT]:
            if ( self.scroll.x < 0):
                self.dx = self.speed
            else:
                self.dx = 0
        else:
            self.dx = 0

        if key[pg.K_DOWN]:
            if ( self.scroll.y > - (self.setting.getSurfaceHeight() - 1080) ):
                self.dy = -self.speed
            else:
                self.dy = 0
        elif key[pg.K_UP]:
            if ( self.scroll.y < 0):
                self.dy = self.speed
            else:
                self.dy = 0
        else:
            self.dy = 0

        self.scroll.x += self.dx
        self.scroll.y += self.dy
