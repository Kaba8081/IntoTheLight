
import pygame as pg
import json
import os

from modules.display import Display
from modules.player import Player

PATH = os.path.dirname(os.path.realpath(__file__))

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
    display = Display(screen, 0.5, player)

    while True: # game loop
        mouse_pos = pg.mouse.get_pos()
        mouse_clicked = pg.mouse.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        
        for room in player.rooms:
            room.update(mouse_pos, mouse_clicked)

        display.draw()

        pg.display.flip()
        screen.fill((0,0,0))
        dt = clock.tick(60) / 1000 # cap the game's framerate at 60 fps
 
if __name__ == "__main__":
    main()
    pg.quit()  
    exit(0)