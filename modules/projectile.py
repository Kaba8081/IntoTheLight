import pygame as pg
from typing import Literal

class Projectile():
    def __init__(self, 
                 start_pos: tuple[int,int], 
                 target_pos: tuple[int,int], 
                 type: Literal["laser", "missile", "beam"], 
                 damage: int = 1, 
                 speed: float = 0.5,
                 color: tuple[int,int,int] = (255,255,255),
                 lenght: int = 5,
                 ):
        self.target_pos = target_pos
        self.type = type
        self.damage = damage
        self.speed = speed
        self.color = color

        self.vector2d_start = pg.math.Vector2(start_pos)
        self.vector2d_end = self.vector2d_start.move_towards(target_pos, lenght)
    
    def update(self, dt: float) -> None:
        """
        Update the projectile's position and draw it on the screen.
        :param dt: float - the time since the last frame
        """

        self.vector2d_start.move_towards_ip(self.target_pos, self.speed * dt)
        self.vector2d_end.move_towards_ip(self.target_pos, self.speed * dt)
    
    def draw(self, screen: pg.surface.Surface) -> None:
        """
        Draw the projectile on the screen.
        :param screen: pg.surface.Surface - the screen to draw the projectile on
        """

        pg.draw.line(screen, self.color, self.vector2d_start, self.vector2d_end)