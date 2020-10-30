# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 13:23:23 2020

@author: rober
"""

from random import randint

import bot_game as bg

class SitController:
    def give_view(self, view, owner_view):
        pass
    
    def get_moves(self):
        return dict()

class WalkController:
    def __init__(self, direction):
        self.direction = direction
    
    def give_view(self, view, owner_view):
        pass
    
    def get_moves(self):
        move = bg.Move(bg.MoveType.MOVE, direction=self.direction)
        moves = {bg.MoveType.MOVE: [move]}
        return moves

class SeekAndFightController:
    def __init__(self):
        # self.direction = direction
        # self.fight = fight
        
        self.view = None
        self.owner_view = None
    
    def give_view(self, view, owner_view):
        self.view = view.copy()
        self.owner_view = owner_view
    
    def get_moves(self):
        # print('energy: {}'.format(self.owner_view.energy))
        
        coords = self.owner_view.coords
        attack_range = self.owner_view.attack_range
        # in_range_coords = bg.coords_within_distance(coords, attack_range)
        # in_range_coords.remove(coords)
        
        player = self.owner_view.player
        
        enemies = list()
        for _, items in self.view.items():
            # items = self.view.get(coords, list())
            bots = [i for i in items if i.type == 'Bot']
            enemies.extend([b for b in bots if b.player != player])
            
        enemies.sort(key=lambda b:bg.distance(coords, b.coords))
        
        #If there are no enemies, hold
        if not enemies:
            return dict()
            
        closest_enemy = enemies[0]
        
        moves = dict()
        
        #Move toward the closest enemy
        x_diff = closest_enemy.coords[0] - coords[0]
        y_diff = closest_enemy.coords[1] - coords[1]
        
        x_dir = None
        y_dir = None
        
        if x_diff > 0:
            x_dir = bg.Direction.RIGHT
        elif x_diff < 0:
            x_dir = bg.Direction.LEFT
        if y_diff < 0:
            y_dir = bg.Direction.UP
        elif y_diff > 0:
            y_dir = bg.Direction.DOWN
        
        if x_dir and y_dir:
            if randint(0, 1) == 0:
                move = bg.Move(bg.MoveType.MOVE, direction=x_dir)
                moves[bg.MoveType.MOVE] = [move]
            else:
                move = bg.Move(bg.MoveType.MOVE, direction=y_dir)
                moves[bg.MoveType.MOVE] = [move]
        elif x_dir:
            move = bg.Move(bg.MoveType.MOVE, direction=x_dir)
            moves[bg.MoveType.MOVE] = [move]
        elif y_dir:
            move = bg.Move(bg.MoveType.MOVE, direction=y_dir)
            moves[bg.MoveType.MOVE] = [move]
        
        if bg.distance(coords, closest_enemy.coords) <= attack_range:
            attack = bg.Move(bg.MoveType.ATTACK,
                             target_coords=closest_enemy.coords)
            moves[bg.MoveType.ATTACK] = [attack]
        
        return moves
            