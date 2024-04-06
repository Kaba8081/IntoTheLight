import pygame as pg

from modules.room import Room
from modules.spaceship import *

class Player(Spaceship):
    def __init__(self, 
                 ship_type: str = "cruiser"
                 ) -> None:
        Spaceship.__init__(self, ship_type)
    
    def update(self, dt: float) -> None:
        pass