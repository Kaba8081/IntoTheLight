import pygame as pg
from os import path

from modules.spaceship.room import Room
from modules.spaceship.door import Door
from modules.spaceship.upgrades import *
from modules.resources import ship_layouts

class Spaceship:
    def __init__(self, ship_type: str, enemy: bool = False) -> None:
        self.rooms = []
        self.doors = pg.sprite.Group()
        for room in ship_layouts[ship_type]["rooms"]:
            self.rooms.append(Room(
                room["pos"], 
                room["tiles"],
                role=room["role"] if "role" in room else None,
                upgrade_slots=room["upgrade_slots"] if "upgrade_slots" in room else {},
                enemy_ship=enemy)
                )

    def draw(self, screen: pg.Surface) -> None:
        for group in self.rooms:
            group.draw(screen)

        self.doors.draw(screen)

    def get_center(self) -> tuple[int, int]:
        """Return the center of the spaceship in pixels."""

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
        
        return ((highest_x + lowest_x)/2, (highest_y + lowest_y)/2)

    def move_by_distance(self, distance: tuple[int, int]) -> None:
        """Move the spaceship by a distance in pixels."""

        for room in self.rooms:
            room.rect.x += distance[0]
            room.rect.y += distance[1]

            for tile in room.sprites():
                tile.rect.x += distance[0]
                tile.rect.y += distance[1]

    def connect_rooms(self, room1, room2) -> tuple:
        """Connect adjecent rooms with doors."""
        
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

    def find_bordering_rooms(self) -> None:
        """Find rooms that are next to each other."""

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