import pygame as pg

from modules.spaceship.spaceship import *

class Player(Spaceship):
    def __init__(self, 
                 ship_type: str = "scout"
                 ) -> None:
        Spaceship.__init__(self, ship_type)
    
    def update(self, dt: float) -> None:
        pass