import time
import pygame as pg
from threading import Thread

from modules.display import Display
from modules.player import Player
from modules.enemy import Enemy
from modules.resources import keybinds, CONFIG, load_textures

class IntoTheLight:
    def __init__(self):
        pg.init()

        self.resolution = [int(value) for value in CONFIG["resolution"].split("x")]

    def game_loop(self):
        mouse_event = False

        self.screen = pg.display.set_mode(self.resolution)
        pg.display.set_caption("IntoTheLight")
        clock = pg.time.Clock()
        dt = 0

        load_textures()
        self.player = Player()
        self.enemy = Enemy(offset=(self.resolution[0] * float(CONFIG["ratio"]),0))
        self.display = Display(self.screen, self.resolution, float(CONFIG["ratio"]), self.player, self.enemy)

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
            self.enemy.update(dt)
            self.display.update()
            self.display.draw()

            pg.display.flip()
            self.screen.fill((0,0,0))
            dt = clock.tick(60) / 1000 # cap the game's framerate at 60 fps

    def enemy_controller(self):
        while True:
            if not hasattr(self, "enemy"):
                time.sleep(2)
            else:
                # TODO: implement basic enemy ai
                pass

if __name__ == "__main__":
    game_instance = IntoTheLight()
    game_loop_thread = Thread(target=game_instance.game_loop)
    enemy_controller_thread = Thread(target=game_instance.enemy_controller)

    game_loop_thread.start()
    enemy_controller_thread.start()

    game_loop_thread.join()
    enemy_controller_thread.join()

    pg.quit()  
    exit(0)