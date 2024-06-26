import time
import pygame as pg
from typing import Union
from random import randint
import threading

from modules.display import Display
from modules.player import Player
from modules.enemy import Enemy
from modules.resources import *

class IntoTheLight:
    # public
    THREAD_INTERVAL: float
    THREAD_INTERVAL = 0.2
    MAIN_THREAD_RUNNING = True
    
    player: Player

    # private
    _enemy_events: list[GameEvents]
    _enemy_actions: dict[EnemyActions, any]
    _game_events: list[GameEvents]
    _enemy: Union[Enemy, None]

    def __init__(self) -> None:
        pg.init()

        self.resolution = [int(value) for value in CONFIG["resolution"].split("x")]

        self._enemy_events = ThreadVariable([], threading.Lock())
        self._enemy_actions = ThreadVariable({}, threading.Lock())
        self._game_events = ThreadVariable([], threading.Lock())

        self.player = None
        self._enemy = None

    def game_loop(self) -> None:
        mouse_event = False
        clock = pg.time.Clock()
        dt = 0

        self.screen = pg.display.set_mode(self.resolution)
        pg.display.set_caption("IntoTheLight")
        load_textures()

        self.player = Player()
        self.display = Display(self.screen, self.resolution, float(CONFIG["ratio"]), self.player)
        self.enemy = Enemy(screen_size=(self.resolution[0] * float(CONFIG["ratio"]), self.resolution[1]), offset=(self.resolution[0] * float(CONFIG["ratio"]),0))
        mouse_pos = (0,0)

        while self.MAIN_THREAD_RUNNING: # game loop
            mouse_focused = pg.mouse.get_focused()
            if mouse_focused:
                mouse_pos = pg.mouse.get_pos()
                mouse_event = False

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.MAIN_THREAD_RUNNING = False
                    return
                
                if event.type == pg.MOUSEBUTTONDOWN and mouse_focused:
                    mouse_event = True
                    mouse_clicked = pg.mouse.get_pressed()
                    self.display.mouse_clicked(mouse_pos, mouse_clicked)
                    if event.button == 1:
                        self.player.update(dt, mouse_pos, mouse_clicked)

                if event.type == pg.KEYDOWN and event.key in keybinds.values():
                    self.player.key_pressed(event.key)
                
                # spawn enemy ship
                if event.type == pg.KEYDOWN and event.key == pg.K_F1:
                    if self.enemy == None:
                        self.enemy = Enemy(screen_size=(self.resolution[0] * float(CONFIG["ratio"]), self.resolution[1]), offset=(self.resolution[0] * float(CONFIG["ratio"]),0))

            # if the mouse was not clicked, check if it's hovering over objects
            if not mouse_event:
                self.display.check_mouse_hover(mouse_pos)

            self.player.update(dt, mouse_pos)
            if self.enemy is not None:
                self._enemy_events.set_value(self.enemy.update(dt))
            self.display.update()
            self.display.draw()

            pg.display.flip()
            self.screen.fill((0,0,0))
            dt = clock.tick(60) / 1000 # cap the game's framerate at 60 fps
        
    def enemy_controller(self) -> None:
        """Controls the enemy ship's actions."""
        
        while self.MAIN_THREAD_RUNNING:
            if self.enemy is None:
                time.sleep(2)
            else:
                for event in self._enemy_events.get_value():
                    match event:
                        case GameEvents.SHIP_DESTROYED:
                            pass
                        case GameEvents.REMOVE_ENEMY:
                            print("Enemy destroyed, stopping thread...")

                            self.player.scrap += randint(10, 20)
                            del self.enemy
                            return

                        case GameEvents.TOOK_DAMAGE: # TODO: send crew to the damaged system
                            print("Enemy system took damage")
                            continue
                self._enemy_events.revert_default()

                # TODO: implement a timer so the checks don't happend every thread tick
                self.enemy.check_weapon_states(self.player)
                self.enemy.manage_power()
            time.sleep(self.THREAD_INTERVAL)

    @property
    def enemy(self) -> Union[Enemy, None]:
        return self._enemy
    
    @enemy.setter
    def enemy(self, value: Enemy) -> None:
        self._enemy = value
        self.display.enemy_ship = self._enemy

        enemy_controller_thread = threading.Thread(target=game_instance.enemy_controller)
        enemy_controller_thread.start()

    @enemy.deleter
    def enemy(self) -> None:
        self._enemy = None
        self._enemy_events.set_value([])

        del self.display.enemy_ship

if __name__ == "__main__":
    game_instance = IntoTheLight()

    game_loop_thread = threading.Thread(target=game_instance.game_loop)
    game_loop_thread.start()

    game_loop_thread.join()

    pg.quit()  
    exit(0)