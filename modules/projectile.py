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
                 length: int = 5,
                 width: int = 1,
                 delay: float = 0,
                 ):
        self.type = type
        self.damage = damage
        self.speed = speed
        self.color = color
        self.length = length
        self.width = width
        self.delay = delay

        self.switched_screens = False
        self.hit_target = False # TODO: implement target hit logic
        
        self._target_pos = target_pos
        self._vector2d_start = pg.math.Vector2(start_pos)
        self._vector2d_end = self._vector2d_start.move_towards(target_pos, length)
    
    def update(self, dt: float) -> None:
        """
        Update the projectile's position and draw it on the screen.
        :param dt: float - the time since the last frame
        """
        if self.delay <= 0:
            self._vector2d_start.move_towards_ip(self._target_pos, self.speed * dt)
            self._vector2d_end.move_towards_ip(self._target_pos, self.speed * dt)
        else:
            self.delay -= dt

        # TODO: implement target hit logic
        if self._vector2d_start == self._target_pos:
            self.hit_target = True
    
    def draw(self, screen: pg.surface.Surface) -> None:
        """
        Draw the projectile on the screen.
        :param screen: pg.surface.Surface - the screen to draw the projectile on
        """
        if self.delay <= 0:
            pg.draw.line(screen, self.color, self._vector2d_start, self._vector2d_end, self.width)

    def update_vectors(self, new_pos: tuple[int, int], new_target: tuple[int, int]) -> None:
        """
        Update the projectile's position and target.
        :param new_pos: tuple[int, int] - the new position of the projectile
        :param new_target: tuple[int, int] - the new target of the projectile
        """
        self._vector2d_start = pg.math.Vector2(new_pos)
        self._vector2d_end = self._vector2d_start.move_towards(new_target, self.length)

    def position(self) -> tuple[float, float, int]:
        """
        Returns the projectile's position and length.
        :return: tuple[float, float, int] - the projectile's start x, y and length
        """

        return self._vector2d_start.x, self._vector2d_start.y, self.length