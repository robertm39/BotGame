# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:46:26 2020

@author: rober
"""

from enum import Enum

import effects as eff

def is_in_bounds(coords, min_x, max_x, min_y, max_y):
    """
    Return whether the given coords are within the given bounds.
    
    Arguments:
        coords (int, int): The coords to check.
        min_x (int): The minimum x-value allowed.
        max_x (int): The maximum x-value allowed.
        min_y (int): The minimum y-value allowed.
        max_y (int): The maximum y-value allowed.
    """
    x, y = coords
    
    if min_x and min_x > x:
        return False
    if max_x and max_x < x:
        return False
    
    if min_y and min_y > y:
        return False
    if max_y and max_y < y:
        return False
    
    return True

def filter_in_bounds_coords(coordses, min_x, max_x, min_y, max_y):
    """
    Return the coords in coords_list within the given bounds.
    
    Arguments:
        coords_list [(int, int)]: The coords to check.
        min_x (int): The minimum x-value allowed.
        max_x (int): The maximum x-value allowed.
        min_y (int): The minimum y-value allowed.
        max_y (int): The maximum y-value allowed.
    """
    return [c for c in coordses if is_in_bounds(c, min_x, max_x, min_y, max_y)]

def distance(coords_1, coords_2):
    """
    Return the distance between the two given coords.
    
    Arguments:
        coords_1 (int, int): The first pair of coords.
        coords_2 (int, int): The second pair of coords.
    """
    x_1, y_1 = coords_1
    x_2, y_2 = coords_2
    
    return abs(x_1 - x_2) + abs(y_1 - y_2)

def coords_within_distance(coords,
                           distance,
                           min_x=0,
                           max_x=None,
                           min_y=0,
                           max_y=None):
    """
    Return all the coords within the given distance of the given coords,
    as long as they are in the given bounds.
    
    Arguments:
        coords (int, int): The coords to measure distance from.
        distance (int): The maximum distance.
        min_x (int): The minimum x-value allowed.
        max_x (int): The maximum x-value allowed.
        min_y (int): The minimum y-value allowed.
        max_y (int): The maximum y-value allowed.
    """
    result = [coords]
    cx, cy = coords
    for d in range(1, distance+1):
        for x in range(0, d):
            y = d - x
            
            result.append((cx + x, cy + y))
            result.append((cx - y, cy + x))
            result.append((cx - x, cy - y))
            result.append((cx + y, cy - x))
    
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

OPPOSITE = {Direction.LEFT:Direction.RIGHT,
            Direction.RIGHT:Direction.LEFT,
            Direction.UP:Direction.DOWN,
            Direction.DOWN:Direction.UP}

class Move:
    def __init__(self, move_type, **kwargs):
        self.move_type = move_type
        
        for name, val in kwargs.items():
            self.__setattr__(name, val)

#GIVE ENERGY:
#    direction: Direction

#GIVE LIFE:
#    direction: Direction
#    amount: int

#HEAL
#    amount: int

#ATTACK:
#    target_coords: (int, int)

#MOVE:
#    direction: Direction

#BUILD:
#TODO

def coords_in_direction(coords, direction):
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
        
        #Initialize map to an empty list everywhere
        for x in range(self.width):
            for y in range(self.height):
                self.map[x, y] = list()
    
    def at(self, coords):
        return self.map.get(coords, list())
    
    def bots_at(self, coords):
        items_at = self.at(coords)
        return [b for b in items_at if type(b) is Bot]
    
    def get_items(self):
        return sum(self.map.values(), [])
    
    def get_bots(self):
        return self.bots.copy()
    
    def add_item(self, item):
        """
        Add the given item to the map.
        """
        
        if not item.coords in self.map:
            raise ValueError('item.coords: {}'.format(item.coords))
        
        if type(item) is Bot:
            return self.add_bot(item)
        
        self.map[item.coords].append(item)
    
    def add_bot(self, bot):
        if bot in self.bots:
            print('bot already in self.bots: {}'.format(bot))
            return
            
        if not bot.coords in self.map:
            raise ValueError('bot.coords: {}'.format(bot.coords))
        
        self.bots.append(bot)
        self.map[bot.coords].append(bot)
        
        speed = bot.speed
        
        if not speed in self.bots_from_speeds:
            self.bots_from_speeds[speed] = list()
            
        self.bots_from_speeds[speed].append(bot)
    
    def remove_bot(self, bot):
        if not bot in self.bots:
            print('bot not in self.bots: {}'.format(bot))
            return
        
        self.bots.remove(bot)
        self.map[bot.coords].remove(bot)
        self.bots_from_speeds[bot.speed].remove(bot)
    
    def get_visible_coords(self, bot):
        """
        Return the coords visible to the given bot.
        
        Arguments:
            bot [Bot]: The bot to return the visible coords of.
        """
        #TODO incorporate line-of-sight checks
        return coords_within_distance(bot.coords, bot.sight)
    
    def set_coords(self, item, coords):
        """
        Move the item to the given coords, updating both the item's .coords
        attribute and the map.
        
        Arguments:
            item: The item whose coords to change.
            coords (int, int): The coords to move the item to.
        """
        if not coords in self.map:
            raise ValueError('coords: {}'.format(coords))
        
        old_coords = item.coords
        
        #Sometimes this will happen if a bot that was destroyed has a movement
        #It's easier to deal with it here than there
        if not item in self.at(old_coords):
            return
        
        self.map[old_coords].remove(item)
        self.map[coords].append(item)
        item.coords = coords
    
    def is_in_bounds(self, coords):
        return is_in_bounds(coords, 0, self.width-1, 0, self.height-1)

class GameManager:
    def __init__(self, battlefield):
        self.battlefield = battlefield
        
        self.waiting_codes = list()
        self.triggered_codes = list()
        self.replacement_codes = list()
        self.effects = list()
    
        self.process_funcs = {MoveType.GIVE_ENERGY: self.process_give_energys,
                              MoveType.GIVE_LIFE: self.process_give_lifes,
                              MoveType.HEAL: self.process_heals,
                              MoveType.ATTACK: self.process_attacks,
                              MoveType.MOVE: self.process_moves,
                              MoveType.BUILD: self.process_builds}
    
    def give_bots_info(self):
        """
        Give all bots their turn's information by calling their give_view()
        methods.
        """
        for bot in self.battlefield.bots:
            visible_coords = self.battlefield.get_visible_coords(bot)
            view = dict()
            for coords in visible_coords:
                view[coords] = list()
                for item in self.battlefield.at(coords):
                    view[coords].append(item.view())
            
            bot.give_view(view)
    
    def get_bots_moves(self):
        """
        Return all the bots' moves.
        
        Return:
            moves {MoveType: {Bot: [Move]}}
        """
        all_moves = {bot:bot.get_moves() for bot in self.battlefield.bots}
        
        result = {t:dict() for t in MoveType}
        
        for bot, moves in all_moves.items():
            for move_type in moves:
                result[move_type][bot] = moves[move_type]
        
        return result
    
    def register_effect(self, effect):
        """
        Register the given effect into self.effects.
        
        Arguments:
            effect Effect: The effect to register.
        """
        self.effects.append(effect)
    
    def resolve_effects(self):
        """
        Resolve all the effetcs in self.effects, first checking for replacement
        code and then for triggered code.
        """
        #Implement replacement code and triggered code later
        for effect in self.effects:
            effect.resolve(self)
            
        self.effects.clear()
    
    def upkeep(self):
        """
        Perform upkeep tasks, like giving energy to bots on energy sources.
        """
        
        #Give energy to bots on energy sources
        for coords, items in self.battlefield.map.items():
            sources = [i for i in items if type(i) is EnergySource]
            if not sources:
                continue
            
            bots = [i for i in items if type(i) is Bot]
            if not bots:
                continue
            
            es = sources[0]
            bot = bots[0]
            effect = eff.GiveEnergyEffect([es], es.amount, bot)
            self.register_effect(effect)
        self.resolve_effects()
    
    def process_give_energys(self, moves_from_bots):
        """
        Process the GIVE_ENERGY moves.
        
        Arguments:
            moves_from_bots {Bot: [Move]}: The GIVE_ENERGY moves to process.
        """
        
        #TODO add check for whether the bot can give energy
        #All the bots that might end up with negative total energy
        possible_negatives = []
        for bot, moves in moves_from_bots.items():
            if not moves:
                continue
            
            move = moves[0]
            
            t_coords = coords_in_direction(bot.coords, move.direction)
            
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
            
            t_coords = coords_in_direction(bot.coords, move.direction)
            
            # items_at = self.battlefield.at(t_coords)
            # targeted_bots = filter(lambda x: type(x) is Bot, items_at)
            targeted_bots = self.battlefield.bots_at(t_coords)
            
            if not targeted_bots:
                #At this point, the bot isn't giving energy to any bots,
                #but its energy is still negative, which is unacceptable
                raise ValueError('bot.energy: {}'.format(bot.energy))
            
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
        
        self.battlefield.test_energys_all_positive()
    
    def process_give_lifes(self, moves_from_bots):
        """
        Process all the GIVE_LIFE orders.
        
        Arguments:
            moves_from_bots {Bot: [Move]}: All the GIVE_LIFE orders.
        """
        #TODO add check for whether the bot can give life
        for bot, moves in moves_from_bots.items():
            if not moves:
                continue
            if bot.energy == 0:
                continue
            
            move = moves[0]
            
            t_coords = coords_in_direction(bot.coords, move.direction)
            
            
            # items_at = self.battlefield.at(t_coords)
            # targeted_bots = filter(lambda x: type(x) is Bot, items_at)
            targeted_bots = self.battlefield.bots_at(t_coords)
            
            if not targeted_bots:
                continue
            
            targeted_bot = targeted_bots[0]
            amount = move.amount
            
            #You can only heal by as much energy as you have
            amount = min(amount, bot.energy)
            
            #You can also only heal by as much damage as the healed bot has
            amount = targeted_bot.increase_hp(amount)
            
            bot.energy -= amount
        
        self.battlefield.test_energys_all_positive()
    
    def process_heals(self, moves_from_bots):
        """
        Process all the HEAL orders given.
        
        Arguments:
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
        
        self.battlefield.test_energys_all_positive()
    
    def process_attacks(self, moves_from_bots):
        """
        Process all the attack moves given.
        
        Arguments:
            attacks {Bot: [Move]}: All the ATTACK moves to process.
        """
        if not moves_from_bots:
            return
        
        #TODO check for whether bot can attack
        speeds = list(set([b.speed for b in moves_from_bots]))
        speeds.sort(reverse=True)
        
        bots_from_speeds = {s:[] for s in speeds}
        
        for bot in moves_from_bots:
            bots_from_speeds[bot.speed].append(bot)
        
        for speed in speeds:
            # print('speed: {}'.format(speed))
            attacked_coords = list()
            for bot in bots_from_speeds[speed]:
                if not bot in self.battlefield.bots:
                    continue
                
                moves = moves_from_bots[bot]
                if not moves:
                    continue
                
                move = moves[0]
                
                tc = move.target_coords
                attacked_coords.append(tc)
                
                attack_effect = eff.AttackEffect([bot], bot.power, tc)
                self.register_effect(attack_effect)
            
            self.resolve_effects()
            
            #Remove all dead bots
            for coords in attacked_coords:
                items = self.battlefield.at(coords)
                bots = [i for i in items if type(i) is Bot]
                if not bots:
                    continue
                
                bot = bots[0]
                if bot.is_dead():
                    self.battlefield.remove_bot(bot)
    
    def process_moves(self, moves_from_bots):
        """
        Process the movement orders.
        Algorithm: first assume all succeed (except for head-on ones), and then
        undo unsuccessfull moves.
        
        Bots with higher speed have priority for movement.
        
        Arguments:
            moves {Bot: [Move]}: All the MOVE moves to process.
        """
        
        #TODO check how many moves a bot can have
        
        #For multiple moves:
        #first do each bot's first move, then each second move, etc.
        #bots w\ higher speed have priority
        
        #For each set of moves:
        #first, move each bot to the spot it's moving to
        #then, where two bots are in the same square, undo
        #one or both moves
        #continue until no bots are in same square
        
        moving_bots = list(moves_from_bots)
        
        i = 0
        while(moving_bots):
            #Only bots that successfully move (the first try) get put here
            #so the only ones that don't are ones in head-on collisions
            already_moved = list()
            
            not_moving = list()
            moved_this_time = list()
            
            #First move all the bots
            for bot in moving_bots:
                moves = moves_from_bots[bot]
                
                if not len(moves) > i:
                    not_moving.append(bot)
                    continue
                
                move = moves[i]
                direction = move.direction
                new_coords = coords_in_direction(bot.coords, direction)
                
                #Check if this is in bounds
                # if not new_coords in self.battlefield.map:
                if not self.battlefield.is_in_bounds(new_coords):
                    continue
                
                #Check if this is a head-on move
                # items_at = self.at_new_coo
                # bots_at = [b for b in self.at(new_coords) if type(b) is Bot]
                bots_at = self.battlefield.bots_at(new_coords)
                
                unmoved_at = [b for b in bots_at if not b in already_moved]
                if(unmoved_at):
                    #There's an unmoved bot in the destination coords
                    other_bot = unmoved_at[0]
                    
                    other_moves = moves_from_bots.get(other_bot, list())
                    if len(other_moves) > i:
                        #The bot is about to move
                        move = other_moves[i]
                        other_dir = move.direction
                        
                        other_dest = coords_in_direction(new_coords, other_dir)
                        
                        if other_dest == bot.coords:
                            #There's a head-on 
                            #So this movement fails
                            continue
                    else:
                        #The other bot isn't about to move, so you can't
                        #move into its square
                        continue
                
                self.battlefield.set_coords(bot, new_coords)
                already_moved.append(bot)
                moved_this_time.append(bot)
            
            #We don't need this one to be accurate now
            #Because I just use moved_this_time to resolve conflicts
            #But I'll do it anyways
            for bot in not_moving:
                moving_bots.remove(bot)
            
            #Then undo unsuccessful moves
            packed_coords = set()
            for bot in moving_bots:
                # items_at = self.at(bot.coords)
                # num_bots_at = len([b for b in items_at if type(b) is Bot])
                num_bots_at = len(self.battlefield.bots_at(bot.coords))
                
                if(num_bots_at >= 2):
                    packed_coords.add(bot.coords)
            
            packed_coords = list(packed_coords)
            while packed_coords:
                packed_coord = packed_coords[0]
                del packed_coords[0]
                
                # items_at = self.at(packed_coord)
                # bots_at = [b for b in items_at if type(b) is Bot]
                bots_at = self.battlefield.bots_at(packed_coord)
                
                moved_bots = [b for b in bots_at if b in moved_this_time]
                
                max_speed = max([b.speed for b in moved_bots])
                fastest_bots = [b for b in moved_bots if b.speed == max_speed]
                
                move_back = moved_bots.copy()
                if len(fastest_bots) == 1:
                    fastest_bot = fastest_bots[0]
                    
                    #One bot is faster than all the others
                    #So only move the slower bots back to their original spaces
                    move_back = [b for b in moved_bots if b != fastest_bot]
                
                for bot in move_back:
                    coords = bot.coords
                    direction = moves_from_bots[bot][i].direction
                    old_coords = coords_in_direction(coords, OPPOSITE[direction])
                    self.battlefield.set_coords(bot, old_coords)
                    
                    #Check if this spot is crowded now
                    if not coords in packed_coords:
                        # items_at = self.at(old_coords)
                        # bots_at = [b for b in items_at if type(b) is Bot]
                        bots_at = self.battlefield.bots_at(old_coords)
                        
                        if len(bots_at) >= 2:
                            packed_coords.append(coords)
                
            i += 1
    
    def process_builds(self, moves_from_bots):
        """
        Process the build orders.
        
        Arguments:
            moves_from_bots {Bot: [Move]}: All the build orders to process.
        """
        
        for bot, moves in moves_from_bots.items():
            if not moves:
                continue
            move = moves[0]
            t_coords = coords_in_direction(bot.coords, move.direction)
            
            if self.battlefield.bots_at(t_coords):
                #Can't build a bot where there already is a bot
                continue
            
            # print('move.cost: {}'.format(move.cost))
            if move.cost > bot.energy:
                #The bot cannot afford the build, so it doesn't happen
                continue
            
            bot.energy -= move.cost
            
            #Make a new controller of the same type
            #real controllers will need inits that only take message
            #as an argument
            controller = type(bot.controller)(move.message)
            
            new_bot = Bot(t_coords,
                          move.max_hp,
                          move.max_hp,
                          move.power,
                          move.attack_range,
                          move.speed,
                          move.sight,
                          move.energy,
                          move.movement,
                          bot.player,
                          move.message,
                          controller,
                          move.special_stats,
                          **move.special_stats_dict)
            
            self.battlefield.add_bot(new_bot)
    
    def advance(self):
        """
        Advance the game by one turn.
        """
        # self.ready_effects()
        self.upkeep()
        self.give_bots_info()
        
        moves = self.get_bots_moves()
        
        for move_type, moves_from_bots in moves.items():
            
            if not moves_from_bots:
                continue
            
            self.process_funcs[move_type](moves_from_bots)

class Bot:
    def __init__(self,
                 coords,
                 max_hp,
                 hp,
                 power,
                 attack_range,
                 speed,
                 sight,
                 energy,
                 movement,
                 player,
                 message,
                 controller,
                 special_stats,
                 **special_stats_dict):
        
        self.coords = coords
        self.max_hp = max_hp
        self.hp = max(0, min(self.max_hp, hp))
        self.power = power
        self.attack_range = attack_range
        self.speed = speed
        self.sight = sight
        self.energy = energy
        self.movement = movement
        self.player = player
        self.message = message
        self.controller = controller
        
        self.special_stats = special_stats.copy()
        self.special_stats_dict = special_stats_dict.copy()
        
        for stat, val in special_stats_dict.items():
            self.__setattr__(stat, val)
    
    def increase_hp(self, amount):
        """
        Increase the bot.hp by the nonnegative amount given.
        The bot.hp will remain <= bot.max_hp.
        
        Arguments:
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
        
        Arguments:
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
        
        Arguments:
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
        
        Arguments:
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
    
    def view(self):
        result = BotView(coords=self.coords,
                         max_hp=self.max_hp,
                         hp=self.hp,
                         power=self.power,
                         attack_range=self.attack_range,
                         speed=self.speed,
                         sight=self.sight,
                         energy=self.energy,
                         movement=self.movement,
                         player=self.player,
                         message=self.message,
                         **self.special_stats_dict)
        
        return result
    
    def give_view(self, view):
        """
        Give the controller the view of the battlefield along with this
        bot's coords.
        
        Arguments:
            view {(int, int): [item.view() return]}: The battlefield view.
        """
        self.controller.give_view(view, self.view())
    
    def get_moves(self):
        """
        Return the bot's moves.
        
        Return:
            moves: {MoveType -> [Move]}
        """
        return self.controller.get_moves()
    
    def __str__(self):
        return 'Bot at ({}, {}),\n'.format(self.coords[0], self.coords[1]) + \
               'hp={}, max_hp={},\n'.format(self.max_hp, self.hp) + \
               'power={}, attack_range={},\n'.format(self.power, self.attack_range) + \
               'speed={},\n'.format(self.speed) + \
               'sight={},\n'.format(self.sight) + \
               'energy={},\n'.format(self.energy) + \
               'movement={},\n'.format(self.movement) + \
               'player={},\n'.format(self.player) + \
               'message={}'.format(self.message)

class BotView:
    def __init__(self,
                 coords,
                 max_hp,
                 hp,
                 power,
                 attack_range,
                 speed,
                 sight,
                 energy,
                 movement,
                 player,
                 message,
                 **special_stats):
        
        self.type = 'Bot'
        self.coords = coords
        self.max_hp = max_hp
        self.hp = max(0, min(self.max_hp, hp))
        self.power = power
        self.attack_range = attack_range
        self.speed = speed
        self.sight = sight
        self.energy = energy
        self.movement = movement
        self.player = player
        self.message = message
        
        for stat, val in special_stats.items():
            self.__setattr__(stat, val)
        
        self._initialized = True
    
    def __setattr__(self, name, val):
        if hasattr(self, '_initialized'):
            if name[0] != '_':
                err_message = 'cannot set attr of view: {} {}'.format(name, val)
                raise RuntimeError(err_message)
        
        self.__dict__[name] = val
    
    def __str__(self):
        return 'Bot view at ({}, {}),\n'.format(self.coords[0], self.coords[1]) + \
               'hp={}, max_hp={},\n'.format(self.max_hp, self.hp) + \
               'power={}, attack_range={},\n'.format(self.power, self.attack_range) + \
               'speed={},\n'.format(self.speed) + \
               'sight={},\n'.format(self.sight) + \
               'energy={},\n'.format(self.energy) + \
               'movement={},\n'.format(self.movement) + \
               'player={},\n'.format(self.player) + \
               'message=' + self.message

class EnergySource:
    def __init__(self, coords,amount):
        self.coords = tuple(coords)
        self.amount = amount
        self.cached_view = EnergySourceView(self.coords, self.amount)
    
    def view(self):
        """
        Return the object to be given to the bot code.
        """
        return self.cached_view
    
    def __str__(self):
        return 'Energy Source at ({}, {}), amount={}'\
               .format(self.coords[0], self.coords[1], self.amount)

class EnergySourceView:
    def __init__(self, coords, amount):
        self.type = 'EnergySource'
        self.coords = tuple(coords)
        self.amount = amount
        self._initialized = True
    
    def __setattr__(self, name, val):
        if hasattr(self, '_initialized'):
            if name[0] != '_':
                err_message = 'cannot set attr of view: {} {}'.format(name, val)
                raise RuntimeError(err_message)
        
        self.__dict__[name] = val
    
    def __str__(self):
        return 'Energy Source view at ({}, {}), amount={}'\
               .format(self.coords[0], self.coords[1], self.amount)