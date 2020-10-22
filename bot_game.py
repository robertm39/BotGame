# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:46:26 2020

@author: rober
"""

from enum import Enum
from random import randint

def get_random_damage(power):
    #The sum of x {0, 1} dice, where x = power
    return sum([randint(0, 1) for _ in range(power)])

def filter_in_bounds_coords(coords_list, min_x, max_x, min_y, max_y):
    result = list()
    
    for x, y in coords_list:
        if min_x <= x <= max_x and min_y <= y <= max_y:
            result.append((x, y))
    
    return result

def coords_within_distance(coords,
                           distance,
                           min_x=0,
                           max_x=None,
                           min_y=0,
                           max_y=None):
    result = [coords]
    cx, cy = coords
    for d in range(1, distance+1):
        for x in range(0, d):
            y = d - x
            
            result.append(cx + x, cy + y)
            result.append(cx - y, cy + x)
            result.append(cx - x, cy - y)
            result.append(cx + y, cy - x)
    
    return filter_in_bounds_coords(result, min_x, max_x, min_y, max_y)

class MoveType(Enum):
    MOVE = 'MOVE'
    ATTACK = 'ATTACK'
    BUILD = 'BUILD'

class Direction(Enum):
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    UP = 'UP'
    DOWN = 'DOWN'

class Move(object):
    def __init__(self, move_type, **kwargs):
        super(self, Move).__init__()
        
        self.move_type = move_type
        
        for name, val in kwargs.items():
            self.__setattr__(name, val)

#MOVE:
#    direction: Direction

#ATTACK:
#    target_coords: (int, int)

#BUILD:
#TODO

#the battlefield is zero-indexed
class Battlefield:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.map = dict()
        
        self.bots = list()
        self.bots_from_speeds = dict()
        
        #Initialize map to an empty list everywhere
        for x in range(self.width):
            for y in range(self.height):
                self.map[x, y] = list()
    
    def get_items(self):
        return sum(self.map.values(), [])
    
    def add_item(self, item):
        """
        Add the given item to the map.
        """
        
        if type(item) is Bot:
            return self.add_bot(item)
        
        self.map[item.coords].append(item)
    
    def add_bot(self, bot):
        if bot in self.bots:
            print('bot already in self.bots: {}'.format(bot))
            return
            
        self.bots.append(bot)
        
        speed = bot.speed
        
        if not speed in self.bots_from_speeds:
            self.bots_from_speeds[speed] = list()
            
        self.bots_from_speeds[speed].append(bot)
    
    def remove_bot(self, bot):
        if not bot in self.bots:
            print('bot not in self.bots: {}'.format(bot))
            return
        
        self.bots.remove(bot)
        self.bots_from_speeds[bot.speed].remove(bot)
    
    def get_visible_coords(self, bot):
        #TODO incorporate line-of-sight checks
        return coords_within_distance(bot.coords, bot.sight)
    
    def set_coords(self, item, coords):
        old_coords = item.coords
        self.map[old_coords].remove(item)
        self.map[coords].append(item)
        item.coords = coords
    
    def give_bots_info(self):
        for bot in self.bots:
            visible_coords = self.get_visible_coords(bot)
            view = map()
            for coords in visible_coords:
                view[coords] = list()
                for item in self.map[coords]:
                    view[coords].append(item.view())
            
            bot.give_view(view)
    
    def get_bots_moves(self):
        return {bot:bot.get_moves() for bot in self.bots}
    
    def get_bots_from_movement_steps(self):
        bfs = self.bots_from_speeds
        return {speed:bfs[speed].copy() for speed in bfs}
    
    def process_attacks(self, attacks):
        for bot, move in attacks:
            tc = move.target_coords
            target_bot_list = [e for e in self.map[tc] if type(e) is Bot]
            
            if target_bot_list:
                damage = get_random_damage(bot.power)
                target_bot = target_bot_list[0]
                target_bot.take_damage(damage)
                if target_bot.dead():
                    self.remove_bot(target_bot)
    
    def process_moves(self, moves):
        """
        Process the movement orders.
        Algorithm: first assume all succeed (except for head-on ones), and then
        undo unsuccessfull moves.
        """
        moves_from_bots = {m[0]:m[1] for m in moves}
        moving_bots = list(moves_from_bots)
        
        # new_bots_from_coords
    
    def advance(self):
        self.give_bots_info()
        
        moves_from_bots = self.get_bots_moves()
        bots_from_movement_steps = self.get_bots_from_movement_steps()
        
        #The highest speed among the bots
        current_step = max(bots_from_movement_steps)
        while bots_from_movement_steps:
            current_bots = bots_from_movement_steps[current_step]
            moves = [(bot, moves_from_bots[bot][0]) for bot in current_bots]
            
            attacks = [m for m in moves if m[1].move_type == MoveType.ATTACK]
            movements = [m for m in moves if m[1].move_type == MoveType.MOVE]
            builds = [m for m in moves if m[1].move_type == MoveType.BUILD]
            
            self.process_attacks(attacks)
            self.process_moves(movements)
            self.process_builds(builds)
        

class Bot(object):
    def __init__(self,
                 coords,
                 hp,
                 power,
                 attack_range,
                 speed,
                 sight,
                 energy,
                 movement,
                 controller,
                 **special_stats):
        
        self.coords = coords
        self.hp = hp
        self.power = power
        self.attack_range = attack_range
        self.speed = speed
        self.sight = sight
        self.energy = energy
        self.movement = movement
        self.controller = controller
        
        for stat, val in special_stats.items():
            self.__setattr__(stat, val)

class EnergySource(object):
    def __init__(self, coords,amount):
        self.coords = coords
        self.amount = amount
    
    def bot_view(self):
        """
        Return the object to be given to the bot code.
        """
        return ('EnergySource', self.coords.copy(), self.amount)