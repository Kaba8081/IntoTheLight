import pygame as pg

from modules.spaceship.spaceship import *

class Enemy(Spaceship):
    def __init__(self, 
                 ship_type: str = "cruiser"
                 ) -> None:
        Spaceship.__init__(self, ship_type, enemy=True)
    
    def update(self, dt: float) -> None:
        pass