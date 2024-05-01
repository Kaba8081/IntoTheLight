import pygame as pg
from typing import Literal

class Projectile():
    def __init__(self, 
                 start_pos: tuple[int,int], 
                 target_pos: tuple[int,int], 
                 type: Literal["laser", "missile", "beam"], 
                 damage: int = 1, 
                 speed: float = 5,
                 color: tuple[int,int,int] = (255,0,0),
                 lenght: int = 5,
                 width: int = 1,
                 delay: float = 0,
                 ):
        self.target_pos = target_pos
        self.type = type
        self.damage = damage
        self.speed = speed
        self.color = color
        self.width = width
        self.delay = delay
        self.hit_target = False # TODO: implement target hit logic

        self.vector2d_start = pg.math.Vector2(start_pos)
        self.vector2d_end = self.vector2d_start.move_towards(target_pos, lenght)
    
    def update(self, dt: float) -> None:
        """
        Update the projectile's position and draw it on the screen.
        :param dt: float - the time since the last frame
        """
        if self.delay <= 0:
            self.vector2d_start.move_towards_ip(self.target_pos, self.speed * dt)
            self.vector2d_end.move_towards_ip(self.target_pos, self.speed * dt)
        else:
            self.delay -= dt

        # TODO: implement target hit logic
        if self.vector2d_start == self.target_pos:
            self.hit_target = True
    
    def draw(self, screen: pg.surface.Surface) -> None:
        """
        Draw the projectile on the screen.
        :param screen: pg.surface.Surface - the screen to draw the projectile on
        """
        if self.delay <= 0:
            pg.draw.line(screen, self.color, self.vector2d_start, self.vector2d_end, self.width)