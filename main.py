import pygame as pg

from modules.display import Display
from modules.player import Player
from modules.enemy import Enemy
from modules.resources import keybinds, load_config

def main() -> None:
    pg.init()

    config = load_config()
    RATIO = 0.65
    resolution = [int(value) for value in config["resolution"].split("x")]
    screen = pg.display.set_mode(resolution)
    pg.display.set_caption("IntoTheLight")
    clock = pg.time.Clock()
    dt = 0

    player = Player()
    enemy = Enemy(offset=(resolution[0] * RATIO,0))
    display = Display(screen, resolution, RATIO, player, enemy)

    mouse_pos = pg.mouse.get_pos()
    mouse_event = False

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
                display.mouse_clicked(mouse_pos, mouse_clicked)
                if event.button == 1:
                    player.update(dt, mouse_pos, mouse_clicked)

            if event.type == pg.KEYDOWN and event.key in keybinds.values():
                player.key_pressed(event.key)

        # if the mouse was not clicked, check if it's hovering over objects
        if not mouse_event:
            display.check_mouse_hover(mouse_pos)

        player.update(dt, mouse_pos)
        enemy.update(dt)
        display.update()
        display.draw()

        pg.display.flip()
        screen.fill((0,0,0))
        dt = clock.tick(60) / 1000 # cap the game's framerate at 60 fps
 
if __name__ == "__main__":
    main()
    pg.quit()  
    exit(0)