import pygame as pg
from typing import Union
from random import randint
from collections import OrderedDict

from modules.spaceship.room import Room
from modules.spaceship.door import Door
from modules.spaceship.tile import Tile
from modules.spaceship.upgrades import *
from modules.misc.pathfinding import astar_pathfinding
from modules.crewmate import Crewmate
from modules.resources import GameEvents, CrewmateRaces, crewmate_names, ship_layouts, systems

class Spaceship:
    # public
    screen_size: tuple[int, int]
    doors: pg.sprite.Group
    crewmates: pg.sprite.Group
    rooms: list[Room]
    projectiles: list[Projectile]
    installed_systems: OrderedDict[str, Room]
    installed_weapons: dict[str, Weapon]
    installed_thrusters: dict[str, Thruster]
    installed_shield: Union[Shield, None]
    hull_hp: int
    destroyed: bool
    event_queue: list[GameEvents]
    autofire: bool
    enemy: bool

    # private
    _room_enine: Union[Room, None]
    _room_weapons: Union[Room, None]
    _room_oxygen: Union[Room, None]
    _room_pilot: Union[Room, None]

    _destroy_anim_index: int
    _destroy_anim_ticks: int

    _display_offset: tuple[int, int]

    def __init__(self, ship_type: str, screen_size: tuple[int, int], enemy: bool = False, offset: tuple[int, int] = (0,0)) -> None:
        """
        :param ship_type: str - The type of the spaceship.
        :param screen_size: tuple[int, int] - The size of the screen the ship is rendered on.
        :param enemy: bool - If the spaceship is an enemy.
        :param offset: tuple[int, int] - The offset of the spaceship.
        """
        self.screen_size = screen_size
        self.doors = pg.sprite.Group()
        self.crewmates = pg.sprite.Group()
        self.projectiles = []
        self.event_queue = []
        self.autofire = False

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
        self._destroy_anim_ticks = 300

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
        # sort the rooms by their role
        temp_systems = [system for system in systems if system in self.installed_systems] # get the intersection of the two lists
        self.installed_systems = OrderedDict((k, self.installed_systems[k]) for k in temp_systems)
        del temp_systems

        if enemy: # flip all the rooms hitboxes horizontally
            centery = self.get_center()[0]

            for room in self.rooms:
                hitbox_y = room.hitbox.centery
                room.hitbox.centery = centery - hitbox_y + centery

        self.spawn_crewmate("pilot")
        self.spawn_crewmate("shields")
        self.spawn_crewmate("weapons")

    def draw(self, screen: pg.Surface) -> None:
        """
        Draw's the spaceship and it's components on screen.
        :param screen: The screen to draw the spaceship on.
        :param enemy_screen: pg.Surface - The screen of the enemy.
        """

        for group in self.rooms:
            group.draw(screen)

        self.doors.draw(screen)

        for crewmate in self.crewmates:
            crewmate.draw(screen)

        if self.installed_shield is not None:
            self.installed_shield.draw(screen)
    
    def draw_projectiles(self, screen: pg.Surface, enemy_screen: pg.Surface) -> None:
        for projectile in self.projectiles:
            v_pos = projectile.position()

            if v_pos[0] >= screen.get_width() and not projectile.switched_screens:
                projectile.switched_screens = True
                projectile.update_vectors((
                    enemy_screen.get_width(),
                    enemy_screen.get_height()//2  + randint(-25, 25)
                ))

            if projectile.switched_screens:
                projectile.draw(enemy_screen)
            else:
                projectile.draw(screen)

    def update(self, dt: float) -> list[GameEvents]:
        if self.hull_hp <= 0 or self.destroyed:
            if not hasattr(self, "_destroy_anim_index"):
                self.event_queue.append(GameEvents.SHIP_DESTROYED)
            if self.enemy and hasattr(self, "_destroy_anim_index") and self._destroy_anim_index >= self._destroy_anim_ticks:
                self.event_queue.append(GameEvents.REMOVE_ENEMY)

            self._anim_destroy()

        for projectile in self.projectiles:
            if projectile.hit_target:
                self.projectiles.remove(projectile)
                del projectile
            else:
                projectile.update(dt)

        self.crewmates.update()
        self.doors.update()

        if not self.destroyed: # update the ship components only if it's not destroyed
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
            
            if self.installed_shield is not None:
                max_shields = self.installed_systems["shields"].power // 2 if "shields" in self.installed_systems.keys() else 0
                self.installed_shield.update(dt, max_shields)
        
        temp_events = self.event_queue[:] if len(self.event_queue) > 0 else None
        self.event_queue = []
        return temp_events

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
            room.rect.move_ip(distance)
            room.hitbox.move_ip(distance)

            for tile in room.sprites():
                tile.rect.move_ip(distance)
                tile.hitbox.move_ip(distance) if hasattr(tile, "hitbox") else None

        for door in self.doors:
            door.rect.move_ip(distance)
            door.hitbox.move_ip(distance)

        for crewmate in self.crewmates:
            crewmate.rect.move_ip(distance)
            crewmate.hitbox.move_ip(distance)

        if self.installed_shield is not None:
            self.installed_shield.shield_sprite.rect = self.installed_shield.shield_sprite.image.get_rect(center=self.get_center())

    def move_hitbox_by_distance(self, distance: tuple[int, int]) -> None:
        """
        Move the hitboxes of the spaceship by a distance in pixels.
        :param distance: The distance to move the hitboxes by.
        """
        
        for room in self.rooms:
            room.hitbox.move_ip(distance)
            for tile in room.sprites():
                tile.hitbox.move_ip(distance) if hasattr(tile, "hitbox") else None
        
        for crewmate in self.crewmates:
            crewmate.hitbox.move_ip(distance)
        
        for door in self.doors:
            door.hitbox.move_ip(distance)

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

    def activate_weapon(self, weapon: Weapon) -> bool:
        """
        Try to activate a weapon if there is enough power left. If successful, return True.
        :param weapon: Weapon - the weapon to activate
        """

        curr_power = self.current_power
        max_power = self.max_power 
        power_left = max_power - curr_power

        if power_left >= weapon.req_power and self.check_if_system_accepts_power("weapons", weapon.req_power):
            self.toggle_system_power(("weapons", True), weapon.req_power)
            weapon.activate()
            return True

        return False
    
    def toggle_system_power(self, action: tuple[str, bool], value: int = 1) -> None:
        """ 
        Toggles the power level of a system. 

        :param action: tuple[str, bool] - the name of the system and whether add/remove power (True/False)
        :param value: int - the amount of power to add/remove (default = 1)
        """

        system_name, action = action
        for installed_system_name in self.installed_systems.keys():
            if installed_system_name == system_name:
                room = self.installed_systems[installed_system_name]

                if action:
                    room.power += value
                else:
                    room.power -= value

                return
    
    def get_system_max_power(self, system: str) -> int:
        """
        Get the maximum power level of a system.
        :param system: str - the name of the system
        """

        for installed_system_name in self.installed_systems.keys():
            if installed_system_name == system:
                room = self.installed_systems[installed_system_name]
                return room.max_power
        
        print("Could not get the rooms max power: System not found!")
        return 0
    
    def check_if_system_accepts_power(self, system: str, value: int) -> bool:
        """
        Check's if the given system can accept the given power level.
        :param system: str - the name of the system
        :param value: int - the power level to check
        """

        for installed_system_name in self.installed_systems.keys():
            if installed_system_name == system:
                room = self.installed_systems[installed_system_name]
                return room.power + value <= room.max_power
        
        print("Could not check if system accepts power: System not found!")
        return False

    def spawn_crewmate(self, origin_system: str = "NULL", race: CrewmateRaces = CrewmateRaces.HUMAN, name:str = "NULL") -> None:
        """Spawn a crewmate on the ship.
        :param origin_system: str - the system to spawn the crewmate in
        :param race: CrewmateRaces object,
        :param name: str - the name of the crewmate"""

        origin_pos = (0,0)

        # if no name was specified, pick a random name from the list
        if name == "NULL":
            name = crewmate_names[race.name.lower()][randint(0, len(crewmate_names)-1)]

        # get a random tile from the origin system, or if occupied pick a random system
        while origin_system == "NULL" or self.installed_systems[origin_system].get_random_tile().occupied:
            origin_system = list(self.installed_systems.keys())[randint(0, len(self.installed_systems)-1)]
        
        origin_pos = self.installed_systems[origin_system].get_random_tile().rect.topleft
        
        Crewmate(name, self, origin_pos, (0,0), self.crewmates, race, enemy=self.enemy)
        
        return

    def get_path_between_tiles(self, start_tile: Tile, end_tile: Tile) -> list[Tile]:
        """
        Get the path between two tiles.
        :param start_tile: modules.Tile - The start tile.
        :param end_tile: modules.Tile - The end tile.
        :return list[modules.Tile] - The path between the two tiles.
        """

        curr_room = None
        result_path = []

        for room in self.rooms:
            if start_tile in room.sprites():
                curr_room = room
                break
        
        while True:
            # find next best room to move to
            best_room = None
            best_dist = pg.math.Vector2(curr_room.rect.topleft).distance_to(pg.math.Vector2(end_tile.rect.topleft))
            for room in curr_room.adjecent_rooms.keys():
                if best_room is None or pg.math.Vector2(room.rect.topleft).distance_to(pg.math.Vector2(end_tile.rect.topleft)) < best_dist:
                    best_dist = pg.math.Vector2(room.rect.topleft).distance_to(pg.math.Vector2(end_tile.rect.topleft))
                    best_room = room

            # Make path to door between the rooms
            relative_path = astar_pathfinding(curr_room.room_layout, start_tile.pos, curr_room.adjecent_rooms[best_room][0].pos)

            # transform the relative path into the list[Tile] format
            for pos in relative_path:
                result_path.append(curr_room.room_tile_layout[pos[0]][pos[1]])

            #append a list of tiles to the path
            result_path.append(curr_room.adjecent_rooms[best_room][1])
            start_tile = curr_room.adjecent_rooms[best_room][1]

            # if the room is the end room, break from the loop
            curr_room = best_room
            if end_tile in best_room.sprites():
                break

        # append a path from door to end_tile
        relative_path = astar_pathfinding(curr_room.room_layout, start_tile.pos, end_tile.pos)

        for pos in relative_path:
            result_path.append(curr_room.room_tile_layout[pos[0]][pos[1]])

        return result_path

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
    
    @property
    def max_power(self) -> int:
        """Return the maximum power that the ship generates."""

        return 6 + self._room_enine.level * 2 # base generation 6 + each level of the engine provides 2 power

    @property
    def current_power(self) -> int:
        """Return the current power usage of the ship."""

        power_level = 0
        for system in self.installed_systems:
            power_level += self.installed_systems[system].power
        return power_level

    @property
    def usable_power(self) -> int:
        """Return the amount of power that can be used by the player."""

        return self.max_power - self.current_power
    
    @property
    def evade_stat(self) -> int:
        return 10 + self._room_enine.power * 5 if self._room_enine.power > 0 else 0
    
    @property
    def oxygen(self) -> int: # TODO: implement oxygen system
        return 100