import pygame as pg
from typing import Union
from random import randint

from modules.spaceship.room import Room
from modules.spaceship.door import Door
from modules.spaceship.tile import Tile
from modules.spaceship.upgrades import *
from modules.resources import ship_layouts, systems

class Spaceship:
    # public
    screen_size: tuple[int, int]
    doors: pg.sprite.Group
    rooms: list[Room]
    projectiles: list[Projectile]
    installed_systems: dict[str, Room]
    installed_weapons: dict[str, Weapon]
    installed_thrusters: dict[str, Thruster]
    installed_shield: Union[Shield, None]
    hull_hp: int
    destroyed: bool

    # private
    _room_enine: Union[Room, None]
    _room_weapons: Union[Room, None]
    _room_oxygen: Union[Room, None]
    _room_pilot: Union[Room, None]


    def __init__(self, ship_type: str, screen_size: tuple[int, int], enemy: bool = False, offset: tuple[int, int] = (0,0)) -> None:
        """
        :param ship_type: str - The type of the spaceship.
        :param screen_size: tuple[int, int] - The size of the screen the ship is rendered on.
        :param enemy: bool - If the spaceship is an enemy.
        :param offset: tuple[int, int] - The offset of the spaceship.
        """
        self.screen_size = screen_size
        self.doors = pg.sprite.Group()
        self.projectiles = []

        # required systems
        self._room_enine = None
        self._room_weapons = None
        self._room_oxygen = None
        self._room_pilot = None
        self.rooms = []

        # required data about these systems
        self.installed_systems = {}
        self.installed_weapons = {}
        self.installed_thrusters = {}
        self.installed_shield = None
        
        self.hull_hp = 30
        self.destroyed = False

        for room in ship_layouts[ship_type]["rooms"]:
            self.rooms.append(Room(
                (room["pos"][0]*32, room["pos"][1]*32),
                (room["pos"][0]*32 + offset[1], room["pos"][1]*32 + offset[0]),
                room["tiles"],
                self,
                role=room["role"] if "role" in room else None,
                level=room["level"] if "level" in room else 0,
                upgrade_slots=room["upgrade_slots"] if "upgrade_slots" in room else {},
                enemy_ship=enemy
            ))
            if "role" in room and room["role"] in systems:
                self.installed_systems[room["role"]] = self.rooms[-1]

        # find and power essential systems
        for system_name in systems:
            match system_name:
                case "engines":
                    self._room_enine = self.installed_systems[system_name]
                    self._room_enine.power = 1
                case "weapons":
                    self._room_weapons = self.installed_systems[system_name]
                case "medbay":
                    self._room_medbay = self.installed_systems[system_name]
                case "oxygen":
                    self._room_oxygen = self.installed_systems[system_name]
                    self._room_oxygen.power = 1
                case "pilot":
                    self._room_pilot = self.installed_systems[system_name]
                    self._room_pilot.power = 1
        
        if enemy: # flip all the rooms hitboxes horizontally
            centery = self.get_center()[0]

            for room in self.rooms:
                hitbox_y = room.hitbox.centery
                room.hitbox.centery = centery - hitbox_y + centery

    def draw(self, screen: pg.Surface, enemy_screen: pg.Surface = None) -> None:
        """
        Draw's the spaceship and it's components on screen.
        :param screen: The screen to draw the spaceship on.
        :param enemy_screen: pg.Surface - The screen of the enemy.
        """

        for group in self.rooms:
            group.draw(screen)

        self.doors.draw(screen)

        if self.installed_shield is not None:
            self.installed_shield.draw(screen)
    
    def draw_projectiles(self, screen: pg.Surface, enemy_screen: pg.Surface) -> None:
        for projectile in self.projectiles:
            v_pos = projectile.position()

            if self.enemy: # TODO: create the same function for enemy projectiles
                pass
            else:
                if v_pos[0] >= screen.get_width():
                    projectile.switched_screens = True
                    projectile.update_vectors((
                        enemy_screen.get_width(),
                        enemy_screen.get_height()//2  + randint(-25, 25)
                    ))

            if projectile.switched_screens:
                projectile.draw(enemy_screen)
            else:
                projectile.draw(screen)

    def update(self, dt: float) -> None:
        if self.hull_hp <= 0:
            self._anim_destroy()
            return

        for weapon in self.weapons:
            if weapon.state == "ready" and bool(weapon) and weapon.target is not None:
                self.projectiles += weapon.fire(
                    (self.screen_size[0]+100, 
                     self.screen_size[1]//2 + randint(-25,25)),
                    weapon.target)
                if hasattr(self, "autofire") and not self.autofire:
                    weapon.target.targeted = False
                    weapon.target = None

            weapon.update(dt)
        
        for projectile in self.projectiles:
            if projectile.hit_target:
                self.projectiles.remove(projectile)
                del projectile
            else:
                projectile.update(dt)

    def get_corners(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Return the top left and bottom right corners of the spaceship in pixels.
        :return tuple[tuple[int, int], tuple[int, int]] - The top left and bottom right corners of the spaceship.
        """

        lowest_x = None
        lowest_y = None

        highest_x = None
        highest_y = None

        # find the lowest x and y values
        for room in self.rooms:
            if lowest_x is None or room.rect.left < lowest_x:
                lowest_x = room.rect.left
            if  lowest_y is None or room.rect.top < lowest_y:
                lowest_y = room.rect.top
        
        # find the highest x and y values
        for room in self.rooms:
            if highest_x is None or room.rect.right > highest_x:
                highest_x = room.rect.right
            if highest_y is None or room.rect.bottom > highest_y:
                highest_y = room.rect.bottom

        return (lowest_x, lowest_y), (highest_x, highest_y)

    def get_center(self) -> tuple[int, int]:
        """
        Return the center of the spaceship in pixels.
        :return tuple[int, int] - The center of the spaceship.
        """

        lowest, highest = self.get_corners()
        
        return ((highest[0] + lowest[0])/2, (highest[1] + lowest[1])/2)

    def move_by_distance(self, distance: tuple[int, int]) -> None:
        """
        Move the spaceship by a distance in pixels.
        :param distance: The distance to move the spaceship by.
        """

        for room in self.rooms:
            room.move_by_distance(distance)

    def connect_rooms(self, room1: Room, room2: Room) -> tuple[Tile, Tile]:
        """
        Connect adjecent rooms with doors.
        :param room1: modules.Room - The first room to connect.
        :param room2: modules.Room - The second room to connect.
        :return tuple[modules.Tile, modules.Tile] - The two tiles that are connected.
        """
        
        # TODO: can be optimized
        # find two tiles that are closest to each other
        closest_tile1 = None
        closest_tile2 = None
        closest_distance = None

        for tile1 in room1.sprites():
            for tile2 in room2.sprites():
                distance = (
                    abs(tile1.rect.centerx - tile2.rect.centerx) + 
                    abs(tile1.rect.centery - tile2.rect.centery)
                    )
                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance
                    closest_tile1 = tile1
                    closest_tile2 = tile2

        return closest_tile1, closest_tile2

    def place_doors(self) -> None:
        """
        Place doors on the connected rooms inside the spaceship.
        """

        for room in self.rooms:
            for adj_room in self.rooms:
                if room is adj_room:
                    continue
                elif adj_room in room.adjecent_rooms:
                    continue

                if (room.rect.left == adj_room.rect.right and 
                        adj_room.rect.top < room.rect.bottom and 
                        adj_room.rect.bottom > room.rect.top):
                    connected_tiles = self.connect_rooms(room, adj_room)
                    room.adjecent_rooms[adj_room] = connected_tiles
                    adj_room.adjecent_rooms[room] = connected_tiles[::-1] # reverse the tuple
                    door_coords = (
                                (connected_tiles[0].rect.centerx + connected_tiles[1].rect.centerx )/2, 
                                (connected_tiles[0].rect.centery + connected_tiles[1].rect.centery)/2
                                )
                    Door(door_coords, self.doors, True)
                elif (room.rect.right == adj_room.rect.left and 
                        adj_room.rect.top < room.rect.bottom and 
                        adj_room.rect.bottom > room.rect.top):
                    connected_tiles = self.connect_rooms(room, adj_room)
                    room.adjecent_rooms[adj_room] = connected_tiles
                    adj_room.adjecent_rooms[room] = connected_tiles[::-1]
                    door_coords = (
                                (connected_tiles[0].rect.centerx + connected_tiles[1].rect.centerx )/2, 
                                (connected_tiles[0].rect.centery + connected_tiles[1].rect.centery)/2
                                )
                    Door(door_coords, self.doors, True)
                elif (room.rect.top == adj_room.rect.bottom and
                        adj_room.rect.left < room.rect.right and
                        adj_room.rect.right > room.rect.left):
                    connected_tiles = self.connect_rooms(room, adj_room)
                    room.adjecent_rooms[adj_room] = connected_tiles
                    adj_room.adjecent_rooms[room] = connected_tiles[::-1]
                    door_coords = (
                                (connected_tiles[0].rect.centerx + connected_tiles[1].rect.centerx )/2, 
                                (connected_tiles[0].rect.centery + connected_tiles[1].rect.centery)/2
                                )
                    Door(door_coords, self.doors)
                elif (room.rect.bottom == adj_room.rect.top and
                        adj_room.rect.left < room.rect.right and
                        adj_room.rect.right > room.rect.left):
                    connected_tiles = self.connect_rooms(room, adj_room)
                    room.adjecent_rooms[adj_room] = connected_tiles
                    adj_room.adjecent_rooms[room] = connected_tiles[::-1]
                    door_coords = (
                                (connected_tiles[0].rect.centerx + connected_tiles[1].rect.centerx )/2, 
                                (connected_tiles[0].rect.centery + connected_tiles[1].rect.centery)/2
                                )
                    Door(door_coords, self.doors)
    
    def dev_draw_room_hitboxes(self, screen: pg.surface.Surface) -> None:
        """
        Draw the hitbox of the rooms for debugging.
        :param screen: pg.surface.Surface - the screen to draw on
        """

        for room in self.rooms:
            room.dev_draw_hitbox(screen)

    def _anim_destroy(self) -> None: # TODO: implement destruction animation
        if hasattr(self, "_destroy_anim_index"):
            self._destroy_anim_index += 1
        else: # initialize the animation and cleanup game elements
            self.destroyed = True
            self._destroy_anim_index = 0

            print("The ship was destroyed!")

            room: Room
            for room in self.rooms:
                for weapon in room.targeted_by:
                    weapon.target = None

        return

    @property
    def empty_upgrade_slots(self) -> Union[list[UpgradeSlot], None]:
        empty_slots = []
        for room in self.rooms:
            room_slots = room.upgrade_slots
            if room_slots is not None:
                empty_slots.append(room_slots)
            
        return empty_slots if len(empty_slots) > 0 else None

    @property
    def weapons(self) -> list[Weapon]:
        weapons = []
        for room in self.rooms:
            room_weapons = room.weapons
            if room_weapons is not None:
                weapons = weapons + room_weapons
            
        return weapons
    
    @property
    def thrusters(self) -> Union[list[Thruster], None]:
        thrusters = []
        for room in self.rooms:
            room_thrusters = room.thrusters
            if room_thrusters is not None:
                thrusters.append(room_thrusters)
            
        return thrusters if len(thrusters) > 0 else None