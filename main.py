
import pygame as pg
import json
import os

from modules.display import Display
from modules.player import Player
from modules.enemy import Enemy

def load_config() -> dict:
    with open("config.json", "r", encoding="utf-8-sig") as file:
        return json.load(file)

def main() -> None:
    pg.init()

    config = load_config()
    resolution = [int(value) for value in config["resolution"].split("x")]
    screen = pg.display.set_mode(resolution)
    pg.display.set_caption("IntoTheLight")
    clock = pg.time.Clock()
    dt = 0

    player = Player()
    enemy = Enemy()
    display = Display(screen, resolution, 0.6, player, enemy)

    while True: # game loop
        mouse_pos = pg.mouse.get_pos()
        mouse_event = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_event = True
                mouse_clicked = pg.mouse.get_pressed()
                display.update_mouse(mouse_pos, mouse_clicked)
                if event.button == 1:
                    player.update(dt, mouse_pos, mouse_clicked)
        # if the mouse was not clicked, check if it's hovering over objects
        if not mouse_event:
            display.check_mouse_hover(mouse_pos)

        player.update(dt, mouse_pos)
        display.update()
        display.draw()

        pg.display.flip()
        screen.fill((0,0,0))
        dt = clock.tick(69) / 1000 # cap the game's framerate at 60 fps
 
if __name__ == "__main__":
    main()
    pg.quit()  
    exit(0)