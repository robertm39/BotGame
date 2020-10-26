# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:46:26 2020

@author: rober
"""

from enum import Enum

import effects as eff

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
    GIVE_ENERGY = 'GIVE_ENERGY'
    GIVE_LIFE = 'GIVE_LIFE'
    HEAL = 'HEAL'
    ATTACK = 'ATTACK'
    MOVE = 'MOVE'
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

#GIVE ENERGY:
#    direction: Direction

#GIVE LIFE:
#    direction: Direction

#HEAL

#ATTACK:
#    target_coords: (int, int)

#MOVE:
#    direction: Direction

#BUILD:
#TODO

def cell_in_direction(coords, direction):
    x, y = coords
    
    if direction == Direction.LEFT:
        return (x-1, y)
    elif direction == Direction.RIGHT:
        return (x+1, y)
    elif direction == Direction.UP:
        return (x, y-1)
    elif direction == Direction.DOWN:
        return (x, y+1)
    else:
        raise ValueError('direction: {}'.format(direction))        

#the battlefield is zero-indexed
class Battlefield:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.map = dict()
        
        self.bots = list()
        self.bots_from_speeds = dict()
        
        self.effects = list()
        self.ready_effects = list()
        
        self.process_funcs = {MoveType.GIVE_ENERGY: self.process_give_energys,
                              MoveType.GIVE_LIFE: self.process_give_lifes,
                              MoveType.HEAL: self.process_heals,
                              MoveType.ATTACK: self.process_attacks,
                              MoveType.MOVE: self.process_moves,
                              MoveType.BUILD: self.process_builds}
        
        #Initialize map to an empty list everywhere
        for x in range(self.width):
            for y in range(self.height):
                self.map[x, y] = list()
    
    def get_items(self):
        return sum(self.map.values(), [])
    
    def get_bots(self):
        return self.bots.copy()
    
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
        """
        Return all the bots' moves.
        
        Return:
            moves: {MoveType: {Bot: [Move]}}
        """
        all_moves = {bot:bot.get_moves() for bot in self.bots}
        result = {t:{} for t in MoveType}
        
        for bot, moves in all_moves.items():
            for move_type in moves:
                result[move_type][bot] = moves[move_type]
        
        return result
    
    def get_bots_from_movement_steps(self):
        bfs = self.bots_from_speeds
        return {speed:bfs[speed].copy() for speed in bfs}
    
    def test_energys_all_positive(self):
        for bot in self.bots:
            if bot.energy < 0:
                raise ValueError('bot.energy: {}'.format(bot.energy))
    
    def ready_effects(self):
        for effect in self.effects:
            if effect in self.ready_effects:
                continue
            
            effect.new_turn(self)
            
            if effect.ready():
                self.ready_effects.append(effect)
    
    def register_effect(self, effect):
        self.effects.append(effect)
        if effect.ready():
            self.ready_effects.append(effect)
    
    def resolve_effects(self):
        for effect in self.ready_effects:
            effect.resolve(self)
    
    def process_give_energys(self, moves_from_bots):
        """
        Process the GIVE_ENERGY moves.
        
        Parameters:
            moves_from_bots {Bot: [Move]}: The GIVE_ENERGY moves to process.
        """
        
        #TODO add check for whether the bot can give energy
        #All the bots that might end up with negative total energy
        possible_negatives = []
        for bot, moves in moves_from_bots.items():
            if not moves:
                continue
            
            move = moves[0]
            
            t_coords = cell_in_direction(bot.coords, move.direction)
            
            targeted_bots = filter(lambda x: type(x) is Bot, map[t_coords])
            if not targeted_bots:
                continue
            
            targeted_bot = targeted_bots[0]
            amount = move.amount
            
            #Check whether the transfers were valid later
            #this allows transfers to be chained
            bot.energy -= amount
            targeted_bot.energy += amount
            
            if bot.energy < 0:
                possible_negatives.append(bot)
        
        while possible_negatives:
            bot = possible_negatives[0]
            del possible_negatives[0]
            
            moves = moves_from_bots[bot]
            if not moves:
                continue
            move = moves[0]
            
            if bot.energy >= 0:
                continue
            
            t_coords = cell_in_direction(bot.coords, move.direction)
            
            targeted_bots = filter(lambda x: type(x) is Bot, map[t_coords])
            if not targeted_bots:
                continue
            
            targeted_bot = targeted_bots[0]
            amount = move.amount
            
            #Undo the transfer if the transferring bot ended up with
            #negative total energy
            bot.energy += amount
            targeted_bot.energy -= amount
            
            #Now maybe the targeted bot has negative total energy,
            #so any transfers it did will also need to be undone
            if targeted_bot.energy < 0:
                possible_negatives.append(targeted_bot)
        
        self.test_energys_all_positive()
    
    def process_give_lifes(self, moves_from_bots):
        """
        Process all the GIVE_LIFE orders.
        
        Parameters:
            moves_from_bots {Bot: [Move]}: All the GIVE_LIFE orders.
        """
        #TODO add check for whether the bot can give life
        for bot, moves in moves_from_bots.items():
            if not moves:
                continue
            if bot.energy == 0:
                continue
            
            move = moves[0]
            
            t_coords = cell_in_direction(bot.coords, move.direction)
            
            targeted_bots = filter(lambda x: type(x) is Bot, map[t_coords])
            if not targeted_bots:
                continue
            
            targeted_bot = targeted_bots[0]
            amount = move.amount
            
            #You can only heal by as much energy as you have
            amount = min(amount, bot.energy)
            
            #You can also only heal by as much damage as the healed bot has
            amount = targeted_bot.increase_hp(amount)
            
            bot.energy -= amount
        
        self.test_energys_all_positive()
    
    def process_heals(self, moves_from_bots):
        """
        Process all the HEAL orders given.
        
        Parameters:
            moves_from_bots {Bot: [Move]}: All the HEAL orders to process.
        """
        #TODO add check for whether the bot can heal
        
        for bot, moves in moves_from_bots.items():
            if not moves:
                continue
            if bot.energy == 0:
                continue
            
            move = moves[0]
            amount = move.amount
            
            #You can only heal by how much energy you have,
            #and also only by how much damage you have
            amount = min(amount, bot.energy, bot.max_hp - bot.hp)
            bot.increase_hp(amount)
            bot.energy -= amount
        
        self.test_energys_all_positive()
    
    def process_attacks(self, moves_from_bots):
        """
        Process all the attack moves given.
        
        Parameters:
            attacks {Bot: [Move]}: All the ATTACK moves to process.
        """
        #TODO check for whether bot can attack
        speeds = list(set(map(list(moves_from_bots), lambda b: b.speed)))
        speeds.sort(reverse=True)
        print('speeds: {}'.format(speeds))
        
        bots_from_speeds = {s:[] for s in speeds}
        for bot in self.bots:
            bots_from_speeds[bot.speed].append(bot)
        
        for speed in speeds:
            dead_bots = list()
            for bot in bots_from_speeds[speed]:
                if not bot in self.bots:
                    continue
                
                moves = moves_from_bots[bot]
                if not moves:
                    continue
                
                move = moves[0]
                
                tc = move.target_coords
                
                attack_effect = eff.AttackEffect(bot, bot.speed, bot.power, tc)
                self.register_effect(attack_effect)
            
            self.resolve_effects()
            
            for bot in dead_bots:
                self.remove_bot(bot)
    
    def process_moves(self, moves):
        """
        Process the movement orders.
        Algorithm: first assume all succeed (except for head-on ones), and then
        undo unsuccessfull moves.
        
        Bots with higher speed have priority for movement.
        
        Parameters:
            moves {Bot: [Move]}
        """
        moves_from_bots = {m[0]:m[1] for m in moves}
        moving_bots = list(moves_from_bots)
        
        # new_bots_from_coords
    
    def advance(self):
        self.ready_effects()
        self.give_bots_info()
        
        moves = self.get_bots_moves()
        
        for move_type, moves_from_bots in moves.items():
            print(move_type)
            
            self.process_funcs[move_type](moves_from_bots)
            

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
        self.max_hp = hp
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
    
    def increase_hp(self, amount):
        """
        Increase the bot.hp by the nonnegative amount given.
        The bot.hp will remain <= bot.max_hp.
        
        Parameters:
            amount int: The amount to increase hp by. Must be nonnegative.
        
        Return:
            int: The nonnegative amount that bot.hp actually increase by.
        """
        if amount < 0:
            raise ValueError('amount: {}'.format(amount))
        
        increase = min(self.hp + amount, self.max_hp) - self.hp
        self.hp += increase
        return increase
    
    def decrease_hp(self, amount):
        """
        Decrease the bot.hp by the nonnegative amount given.
        THe bot.hp will remain >= 0.
        
        Parameters:
            amount int: The amount to decrease hp by. Must be nonnegative.
        
        Return:
            int: The nonnegative amount that bot.hp actually decreased by.
        """
        if amount < 0:
            raise ValueError('amount: {}'.format(amount))
        
        decrease = min(self.hp, amount)
        self.hp -= decrease
        
        return decrease
    
    def change_hp(self, amount):
        """
        Change the bot's hp by the given amount.
        It will remain that 0 <= bot.hp <= bot.max_hp
        
        Parameters:
            amount int: The amount to change hp by.
        
        Return:
            int: The amount that bot.hp actually changed by.
        """
        result = self.hp + amount
        result = max(0, min(self.max_hp, result))
        change = result - self.hp
        self.hp = result
        
        return change
    
    def take_damage(self, amount):
        """
        Take the given nonnegative amount of damage.
        
        Parameters:
            amount int: The amount of damage to take. Must be nonnegative.
        
        Return:
            int: The nonnegative amount that bot.hp actually decreased by.
        """
        if amount < 0:
            raise ValueError('amount: {}'.format(amount))
        
        return self.decrease_hp(amount)
    
    def is_dead(self):
        """
        Return whether the bot is dead.
        
        Return:
            boolean: Whether the bot is dead.
        """
        return self.hp <= 0
    
    def get_moves(self):
        """
        Return the bot's moves.
        
        Return:
            moves: {MoveType -> [Move]}
        """
        pass

class EnergySource(object):
    def __init__(self, coords,amount):
        self.coords = tuple(coords)
        self.amount = amount
    
    def bot_view(self):
        """
        Return the object to be given to the bot code.
        """
        return ('EnergySource', self.coords.copy(), self.amount)