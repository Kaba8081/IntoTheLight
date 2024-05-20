import time
import pygame as pg
from typing import Union
import threading

from modules.display import Display
from modules.player import Player
from modules.enemy import Enemy
from modules.resources import *

class IntoTheLight:
    # public
    THREAD_INTERVAL: float
    THREAD_INTERVAL = 0.2

    # private
    _enemy_events: list[GameEvents]
    _enemy_events_lock: threading.Lock

    _game_events: list[GameEvents]
    _game_events_lock: threading.Lock

    def __init__(self) -> None:
        pg.init()

        self.resolution = [int(value) for value in CONFIG["resolution"].split("x")]

        self._enemy_events = []
        self._enemy_events_lock = threading.Lock()

        self._game_events = []
        self._game_events_lock = threading.Lock()

    def game_loop(self) -> None:
        mouse_event = False

        self.screen = pg.display.set_mode(self.resolution)
        pg.display.set_caption("IntoTheLight")
        clock = pg.time.Clock()
        dt = 0

        load_textures()
        self.player = Player()
        self.enemy = Enemy(offset=(self.resolution[0] * float(CONFIG["ratio"]),0))
        self.display = Display(self.screen, self.resolution, float(CONFIG["ratio"]), self.player, self.enemy)
        mouse_pos = (0,0)

        while True: # game loop
            mouse_focused = pg.mouse.get_focused()
            if mouse_focused:
                mouse_pos = pg.mouse.get_pos()
                mouse_event = False

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                
                if event.type == pg.MOUSEBUTTONDOWN and mouse_focused:
                    mouse_event = True
                    mouse_clicked = pg.mouse.get_pressed()
                    self.display.mouse_clicked(mouse_pos, mouse_clicked)
                    if event.button == 1:
                        self.player.update(dt, mouse_pos, mouse_clicked)

                if event.type == pg.KEYDOWN and event.key in keybinds.values():
                    self.player.key_pressed(event.key)

            # if the mouse was not clicked, check if it's hovering over objects
            if not mouse_event:
                self.display.check_mouse_hover(mouse_pos)

            self.player.update(dt, mouse_pos)
            self.enemy_events = self.enemy.update(dt)
            self.display.update()
            self.display.draw()

            pg.display.flip()
            self.screen.fill((0,0,0))
            dt = clock.tick(60) / 1000 # cap the game's framerate at 60 fps

    def enemy_controller(self) -> None:
        while True:
            if not hasattr(self, "enemy"):
                time.sleep(2)
            else:
                for event in self.enemy_events:
                    match event:
                        case GameEvents.SHIP_DESTROYED:
                            print("Enemy destroyed, stopping thread...")
                            return
                        case GameEvents.TOOK_DAMAGE: # TODO: send crew to the damaged system
                            print("Enemy system took damage")
                            continue  
                               
                del self.enemy_events
            time.sleep(self.THREAD_INTERVAL)
    @property
    def enemy_events(self) -> list[GameEvents]:
        with self._enemy_events_lock:
            return self._enemy_events
    
    @enemy_events.setter
    def enemy_events(self, event: Union[GameEvents, list[GameEvents], None]) -> None:
        if event is not None:
            return threading.Thread(target=self._enemy_events_thread_setter, args=(event)).start()
        return
    
    @enemy_events.deleter
    def enemy_events(self) -> None:
        with self._enemy_events_lock:
            self._enemy_events = []
    
    def _enemy_events_thread_setter(self, event: Union[GameEvents, list[GameEvents]]) -> None:
        while True:
            time.sleep(self.THREAD_INTERVAL)
            if self._enemy_events_lock.locked():
                continue
            
            if isinstance(event, list):
                with self._enemy_events_lock:
                    self._enemy_events = event
            else:
                with self._enemy_events_lock:
                    self._enemy_events.append(event)
            return

if __name__ == "__main__":
    game_instance = IntoTheLight()
    game_loop_thread = threading.Thread(target=game_instance.game_loop)
    enemy_controller_thread = threading.Thread(target=game_instance.enemy_controller)

    game_loop_thread.start()
    enemy_controller_thread.start()

    game_loop_thread.join()
    enemy_controller_thread.join()

    pg.quit()  
    exit(0)