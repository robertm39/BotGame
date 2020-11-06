# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 13:23:23 2020

@author: rober
"""

from random import randint, choice

import bot_game as bg
import builds

class SitController:
    def __init__(self, message=''):
        pass
    
    def give_view(self, view, owner_view):
        pass
    
    def get_moves(self):
        return dict()

class WalkController:
    def __init__(self, direction=bg.Direction.RIGHT):
        self.direction = direction
    
    def give_view(self, view, owner_view):
        pass
    
    def get_moves(self):
        move = bg.Move(bg.MoveType.MOVE, direction=self.direction)
        moves = {bg.MoveType.MOVE: [move]}
        return moves

def get_approach_moves(current, target):
    """
    Return a move that moves toward a coord with the given displacement from
    the current coord.
    
    Arguments:
        x_diff int: The target_coords.x - current_coords.x
        y_diff int: The target_coords.y - current_coords.y
    """
    cx, cy = current
    tx, ty = target
    
    x_diff = tx - cx
    y_diff = ty - cy
    
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
            return [bg.Move(bg.MoveType.MOVE, direction=x_dir)]
        else:
            return [bg.Move(bg.MoveType.MOVE, direction=y_dir)]
    elif x_dir:
        return [bg.Move(bg.MoveType.MOVE, direction=x_dir)]
    elif y_dir:
        return [bg.Move(bg.MoveType.MOVE, direction=y_dir)]
    
    #we're already at the target
    return list()

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
        # x_diff = closest_enemy.coords[0] - coords[0]
        # y_diff = closest_enemy.coords[1] - coords[1]
        
        # x_dir = None
        # y_dir = None
        
        # if x_diff > 0:
        #     x_dir = bg.Direction.RIGHT
        # elif x_diff < 0:
        #     x_dir = bg.Direction.LEFT
        # if y_diff < 0:
        #     y_dir = bg.Direction.UP
        # elif y_diff > 0:
        #     y_dir = bg.Direction.DOWN
        
        # if x_dir and y_dir:
        #     if randint(0, 1) == 0:
        #         move = bg.Move(bg.MoveType.MOVE, direction=x_dir)
        #         moves[bg.MoveType.MOVE] = [move]
        #     else:
        #         move = bg.Move(bg.MoveType.MOVE, direction=y_dir)
        #         moves[bg.MoveType.MOVE] = [move]
        # elif x_dir:
        #     move = bg.Move(bg.MoveType.MOVE, direction=x_dir)
        #     moves[bg.MoveType.MOVE] = [move]
        # elif y_dir:
        #     move = bg.Move(bg.MoveType.MOVE, direction=y_dir)
        #     moves[bg.MoveType.MOVE] = [move]
        approach_moves = get_approach_moves(coords, closest_enemy.coords)
        moves[bg.MoveType.MOVE] = approach_moves
        
        if bg.distance(coords, closest_enemy.coords) <= attack_range:
            attack = bg.Move(bg.MoveType.ATTACK,
                             target_coords=closest_enemy.coords)
            moves[bg.MoveType.ATTACK] = [attack]
        
        return moves

class SeekEnergyController:
    def __init__(self):
        self.view = None
        self.owner_view = None
        self.target_coords = None
    
    def give_view(self, view, owner_view):
        self.view = view
        self.owner_view = owner_view
    
    def get_moves(self):
        coords = self.owner_view.coords
        
        # print('energy: {}'.format(self.owner_view.energy))
        
        #Seek energy
        if not self.target_coords:
            energy_sources = list()
            for _, items in self.view.items():
                sources_at = [s for s in items if s.type == 'EnergySource']
                bots_at = [s for s in items if s.type == 'Bot']
                #Don't go to occupied places
                if not bots_at:
                    energy_sources.extend(sources_at)
            
            if energy_sources:
                self.target_coords = choice(energy_sources).coords
            else:
                return dict()
        
        approach_moves = get_approach_moves(coords, self.target_coords)
        moves = {bg.MoveType.MOVE:approach_moves}
        
        #Make more bots
        #don't check for energy because the game manager already does
        directions = list()
        for direction in bg.Direction:
            t_coords = bg.coords_in_direction(coords, direction)
            items_at = self.view[t_coords]
            bots_at = [b for b in items_at if b.type == 'Bot']
            if not bots_at:
                directions.append(direction)
        
        if directions:
            direction = choice(directions)
            build_move = builds.BuildMove(direction,
                                          max_hp=10,
                                          power=10,
                                          attack_range=1,
                                          speed=0,
                                          sight=10,
                                          energy=0,
                                          movement=1,
                                          message='')
            moves[bg.MoveType.BUILD] = [build_move]
       
        return moves

class ChainEnergyController:
    def __init__(self):
        self.view = None
        self.owner_view = None
        self.direction = None
    
    def give_view(self, view, owner_view):
        self.view = view
        self.owner_view = owner_view
    
    def get_moves(self):
        if not self.direction:
            message = self.owner_view.message
            self.direction = bg.Direction.__dict__.get(message, None)
        
        if not self.direction:
            return
        
        coords = self.owner_view.coords
        target_coords = bg.coords_in_direction(coords, self.direction)
        items_at = self.view.get(target_coords, list())
        bots_at = [b for b in items_at if b.type == 'Bot']
        
        moves = dict()
        #If there's a bot there, give it energy
        #otherwise try to build a bot
        if bots_at:
            give_energy_move = bg.Move(bg.MoveType.GIVE_ENERGY,
                                       direction=self.direction,
                                       amount=self.owner_view.energy)
            moves[bg.MoveType.GIVE_ENERGY] = [give_energy_move]
            # print('giving energy')
        else:
            build_move = builds.BuildMove(self.direction,
                                          max_hp=10,
                                          power=10,
                                          attack_range=1,
                                          speed=0,
                                          sight=5,
                                          energy=0,
                                          movement=1,
                                          message=self.owner_view.message)
            moves[bg.MoveType.BUILD] = [build_move]
            # print('building')
        
        return moves

class GiveLifeController:
    def __init__(self):
        self.view = None
        self.owner_view = None
        self.direction = None
    
    def give_view(self, view, owner_view):
        self.view = view
        self.owner_view = owner_view
    
    def get_moves(self):
        print('energy: {}'.format(self.owner_view.energy))
        
        if not self.direction:
            message = self.owner_view.message
            self.direction = bg.Direction.__dict__.get(message, None)
        
        if not self.direction:
            return
        
        coords = self.owner_view.coords
        target_coords = bg.coords_in_direction(coords, self.direction)
        items_at = self.view.get(target_coords, list())
        bots_at = [b for b in items_at if b.type == 'Bot']
        
        moves = dict()
        #If there's a bot there, give it energy
        #otherwise try to build a bot
        if bots_at:
            give_life_move = bg.Move(bg.MoveType.GIVE_LIFE,
                                     direction=self.direction,
                                     amount=self.owner_view.energy)
            moves[bg.MoveType.GIVE_LIFE] = [give_life_move]
            # print('giving energy')
        else:
            heal_move = bg.Move(bg.MoveType.HEAL,
                                amount=self.owner_view.energy)
            moves[bg.MoveType.HEAL] = [heal_move]
            # print('building')
        
        return moves