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
            # print('No enemies')
            return dict()
            
        closest_enemy = enemies[0]
        
        moves = dict()
        
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
        if not self.direction:
            message = self.owner_view.message
            self.direction = bg.Direction.__dict__.get(message, None)
        
        if not self.direction:
            return dict()
        
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

class SpreadAttackController:
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
            return dict()
        
        coords = self.owner_view.coords
        
        #Target a square that makes it so that the spread doesn't
        #hit this robot
        t_coords = coords
        attack_range = self.owner_view.attack_range
        spread = self.owner_view.spread
        for _ in range(min(attack_range, spread + 1)):
            t_coords = bg.coords_in_direction(t_coords, self.direction)
        
        attack = bg.Move(bg.MoveType.ATTACK, target_coords=t_coords)
        moves = dict()
        moves[bg.MoveType.ATTACK] = [attack]
        return moves

#Some utility methods

def get_approach_moves(current, target):
    """
    Return a move that moves toward a coord with the given displacement from
    the current coord.
    
    Parameters:
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

def get(view, coords=None, item_type=None, player=None):
    if coords:
        v = {c:view[c] for c in coords if c in view}
    else:
        v = view
    
    if player:
        item_type = 'Bot'
    
    #Get all items of the given type
    items = [view_at[item_type] for _, view_at in v.items() if item_type in view_at]
    
    if player and item_type == 'Bot':
        items = [i for i in items if i.player == player]
    
    return items

#This will be the first general controller
#The idea is to spread out, colonize energy sources, and attack enemies

class BasicController:
    def __init__(self):
        self.view = None
        self.owner_view = None
        self.directions = list()
        self.message_to_give = ''
    
    def set_directions(self):
        message = self.owner_view.message
        if message:
            # print('')
            for word in message.split():
                # print(word)
                d = bg.Direction.__dict__.get(word, None)
                # print('d: {}'.format(d))
                if d:
                    self.directions.append(d)
        else:
            #Should be the first bot
            x, y = self.owner_view.coords
            if x == 0:
                if y == 0:
                    #Upper-left
                    self.directions = [bg.Direction.DOWN, bg.Direction.RIGHT]
                else:
                    #Lower-left
                    self.directions = [bg.Direction.UP, bg.Direction.RIGHT]
            else:
                if y == 0:
                    #Upper-right
                    self.directions = [bg.Direction.DOWN, bg.Direction.LEFT]
                else:
                    #Lower-right
                    self.directions = [bg.Direction.UP, bg.Direction.LEFT]
                    
    
    def give_view(self, view, owner_view):
        self.view = view
        self.owner_view = owner_view
        self.coords = self.owner_view.coords
        self.player = self.owner_view.player
        
        if not self.directions:
            self.set_directions()
            if not self.owner_view.message:
                for d in self.directions:
                    add = str(d).split('.')[1]
                    self.message_to_give = self.message_to_give + ' ' + add
            else:
                self.message_to_give = self.owner_view.message
    
    #If you're on an energy source, either build or give energy
    #If you're not, either go to an energy source, fight, or search
    def get_moves(self):
        coords = self.owner_view.coords
        items_at = self.view[coords]
        
        is_es_at = 'EnergySource' in items_at
        
        #Get all this info up front
        adj = bg.coords_within_distance(coords,
                                        1,
                                        include_center=False)
        
        #Only deal with visible coords
        adj = [c for c in adj if c in self.view]
        
        adj_wo_bot = [c for c in adj if not 'Bot' in self.view[c]]
        adj_w_bot = [c for c in adj if not c in adj_wo_bot]
        adj_w_ally = [c for c in adj_w_bot if\
                      self.view[c]['Bot'].player == self.owner_view.player]
        # adj_w_enemy = [b for b in adj_w_bot if not b in adj_w_ally]
        
        moves = dict()
        
        #Always attack if there's an enemy adjacent
        attack_range = 1
        in_range = bg.coords_at_distance(coords, attack_range)
        in_range = [c for c in in_range if c in self.view]
        in_range_w_bot = [c for c in in_range if 'Bot' in self.view[c]]
        in_range_w_enemy = [c for c in in_range_w_bot if\
                            self.view[c]['Bot'].player != self.owner_view.player]
        if in_range_w_enemy:
            attack_coords = choice(in_range_w_enemy)
            
            attack_move = bg.Move(move_type=bg.MoveType.ATTACK,
                                  target_coords=attack_coords)
            
            moves[bg.MoveType.ATTACK] = [attack_move]
                
        if is_es_at:
            #Either build or give energy
            adj = bg.coords_within_distance(coords,
                                            1,
                                            include_center=False)
            # print('adj_wo_bot: {}'.format(adj_wo_bot))
            
            
            #Build in one of the empty spots
            building = False
            if adj_wo_bot:
                building = True
                build_coords = choice(adj_wo_bot)
                
                build_move = builds.BuildMove(build_coords,
                                              max_hp=10,
                                              power=10,
                                              attack_range=attack_range,
                                              speed=0,
                                              sight=4,
                                              energy=0,
                                              movement=1,
                                              message=self.message_to_give)
                
                moves[bg.MoveType.BUILD] = [build_move]
            
            #There's a bot in one of the empty spots
            
            if adj_w_ally and not building:
                give_en_coords = choice(adj_w_ally)
                
                give_energy_move = bg.Move(move_type=bg.MoveType.GIVE_ENERGY,
                                           target_coords=give_en_coords,
                                           amount=self.owner_view.energy)
                #Add amount later
                moves[bg.MoveType.GIVE_ENERGY] = [give_energy_move]
            
            return moves
        else:
            #Not on an energy source
            #Either look for an energy source or look for an enemy
            
            #Look for an energy source
            energy_sources = list()
            
            for _, items in self.view.items():
                if 'EnergySource' in items and not 'Bot' in items:
                    energy_sources.append(items['EnergySource'])
            
            if energy_sources:
                target_coords = choice(energy_sources).coords
                
                approach_moves = get_approach_moves(self.coords,
                                                    target_coords)
                moves[bg.MoveType.MOVE] = approach_moves
            else:
                #Look for an enemy instead
                enemies = list()
                for _, items in self.view.items():
                    if 'Bot' in items and items['Bot'].player != self.player:
                        enemies.append(items['Bot'])
                
                if enemies:
                    target_coords = choice(enemies).coords
                    
                    approach_moves = get_approach_moves(self.coords,
                                                        target_coords)
                    moves[bg.MoveType.MOVE] = approach_moves
                elif self.directions:
                    #There's nothing in sight, so just wander
                    d = choice(self.directions)
                    move = bg.Move(bg.MoveType.MOVE,
                                   direction=d)
                    moves[bg.MoveType.MOVE] = [move]
                else:
                    #We don't have any directions
                    #So just go up
                    print('no directions, going up')
                    move = bg.Move(bg.MoveType.MOVE,
                                   direction=bg.Direction.UP)
                    moves[bg.MoveType.MOVE] = [move]
        
        return moves

#A controller that should be a bit better than the first basic controller
#Changes:
#Bots on an energy source will try to move to a better one
#Not all bots will be made with the same speed 
#Some bots have absorb

#Todo:
#Bots will preferentially build onto energy sources
#Some bots will be fighter bots that will target enemies over energy sources

class RandomStatGetter:
    def __init__(self, period, func):
        self.period = period
        self.func = func
        self.val = self.func()
        self.i = 0
    
    def update(self):
        self.i += 1
        if self.i >= self.period:
            self.i = 0
            self.val = self.func()

class BasicController2:
    def __init__(self):
        self.view = None
        self.owner_view = None
        self.directions = list()
        self.message_to_give = ''
        
        self.next_speed = RandomStatGetter(10, lambda : randint(1, 5))
    
    def set_directions(self):
        message = self.owner_view.message
        if message:
            # print('')
            for word in message.split():
                # print(word)
                d = bg.Direction.__dict__.get(word, None)
                # print('d: {}'.format(d))
                if d:
                    self.directions.append(d)
        else:
            #Should be the first bot
            x, y = self.owner_view.coords
            if x == 0:
                if y == 0:
                    #Upper-left
                    self.directions = [bg.Direction.DOWN, bg.Direction.RIGHT]
                else:
                    #Lower-left
                    self.directions = [bg.Direction.UP, bg.Direction.RIGHT]
            else:
                if y == 0:
                    #Upper-right
                    self.directions = [bg.Direction.DOWN, bg.Direction.LEFT]
                else:
                    #Lower-right
                    self.directions = [bg.Direction.UP, bg.Direction.LEFT]
                    
    
    def give_view(self, view, owner_view):
        self.view = view
        self.owner_view = owner_view
        self.coords = self.owner_view.coords
        self.player = self.owner_view.player
        
        if not self.directions:
            self.set_directions()
            if not self.owner_view.message:
                for d in self.directions:
                    add = str(d).split('.')[1]
                    self.message_to_give = self.message_to_give + ' ' + add
            else:
                self.message_to_give = self.owner_view.message
    
    #If you're on an energy source, either build or give energy
    #If you're not, either go to an energy source, fight, or search
    def update(self):
        self.next_speed.update()
    
    def get_moves(self):
        self.update()
        
        coords = self.owner_view.coords
        items_at = self.view[coords]
        
        is_es_at = 'EnergySource' in items_at
        
        #Get all this info up front
        adj = bg.coords_within_distance(coords,
                                        1,
                                        include_center=False)
        
        #Only deal with visible coords
        adj = [c for c in adj if c in self.view]
        
        adj_wo_bot = [c for c in adj if not 'Bot' in self.view[c]]
        adj_w_bot = [c for c in adj if not c in adj_wo_bot]
        adj_w_ally = [c for c in adj_w_bot if\
                      self.view[c]['Bot'].player == self.owner_view.player]
        adj_w_enemy = [b for b in adj_w_bot if not b in adj_w_ally]
        
        moves = dict()
        
        #Always attack if there's an enemy adjacent
        if adj_w_enemy:
                attack_coords = choice(adj_w_enemy)
                
                attack_move = bg.Move(move_type=bg.MoveType.ATTACK,
                                      target_coords=attack_coords)
                
                moves[bg.MoveType.ATTACK] = [attack_move]
                
        if is_es_at:
            #Either build or give energy
            es_at = self.view[self.coords]['EnergySource']
            es_amount = es_at.amount
            
            #Find if there's a better EnergySource to move to
            adj_w_es = [c for c in adj if 'EnergySource' in self.view[c]]
            adj_w_es = [c for c in adj_w_es if c in adj_wo_bot]
            
            if adj_w_es:
                best_adj_es_coords = adj_w_es[0]
                best_adj_es = self.view[best_adj_es_coords]['EnergySource']
                highest_adj_es_amount = best_adj_es.amount
                
                for es_coords in adj_w_es[1:]:
                    amount_there = self.view[es_coords]['EnergySource'].amount
                    
                    if amount_there > highest_adj_es_amount:
                        highest_adj_es_amount = amount_there
                        best_adj_es_coords = es_coords
                
                #There's a better ES to move to
                if highest_adj_es_amount > es_amount:
                    movement = get_approach_moves(self.coords, best_adj_es_coords)
                    moves[bg.MoveType.MOVE] = movement
                    return moves
            
            #Build in one of the empty spots
            building = False
            if adj_wo_bot:
                building = True
                build_coords = choice(adj_wo_bot)
                
                build_move = builds.BuildMove(build_coords,
                                              max_hp=1,
                                              power=1,
                                              attack_range=1,
                                              speed=0,#self.next_speed.val,
                                              sight=1,
                                              energy=0,
                                              movement=1,
                                              message=self.message_to_give,
                                              #spread=70,
                                              absorb=15)
                                              #absorb=40)
                
                moves[bg.MoveType.BUILD] = [build_move]
            
            #There's a bot in one of the empty spots
            
            if adj_w_ally and not building:
                give_en_coords = choice(adj_w_ally)
                
                give_energy_move = bg.Move(move_type=bg.MoveType.GIVE_ENERGY,
                                           target_coords=give_en_coords,
                                           amount=self.owner_view.energy)
                #Add amount later
                moves[bg.MoveType.GIVE_ENERGY] = [give_energy_move]
            
            return moves
        else:
            #Not on an energy source
            #Either look for an energy source or look for an enemy
            
            #Look for an energy source
            energy_sources = list()
            
            for _, items in self.view.items():
                if 'EnergySource' in items and not 'Bot' in items:
                    energy_sources.append(items['EnergySource'])
            
            if energy_sources:
                target_coords = choice(energy_sources).coords
                
                approach_moves = get_approach_moves(self.coords,
                                                    target_coords)
                moves[bg.MoveType.MOVE] = approach_moves
            else:
                #Look for an enemy instead
                enemies = list()
                for _, items in self.view.items():
                    if 'Bot' in items and items['Bot'].player != self.player:
                        enemies.append(items['Bot'])
                
                if enemies:
                    target_coords = choice(enemies).coords
                    
                    approach_moves = get_approach_moves(self.coords,
                                                        target_coords)
                    moves[bg.MoveType.MOVE] = approach_moves
                elif self.directions:
                    #There's nothing in sight, so just wander
                    d = choice(self.directions)
                    move = bg.Move(bg.MoveType.MOVE,
                                   direction=d)
                    moves[bg.MoveType.MOVE] = [move]
                else:
                    #We don't have any directions
                    #So just go up
                    print('no directions, going up')
                    move = bg.Move(bg.MoveType.MOVE,
                                   direction=bg.Direction.UP)
                    moves[bg.MoveType.MOVE] = [move]
        
        return moves

#Make one bot with very high spread
class MegaBombController:
    def __init__(self):
        self.view = None
        self.owner_view = None
        self.directions = list()
        self.message_to_give = ''
    
    def set_directions(self):
        message = self.owner_view.message
        if message:
            for word in message.split():
                d = bg.Direction.__dict__.get(word, None)
                if d:
                    self.directions.append(d)
        else:
            #Should be the first bot
            x, y = self.owner_view.coords
            if x == 0:
                if y == 0:
                    #Upper-left
                    self.directions = [bg.Direction.DOWN, bg.Direction.RIGHT]
                else:
                    #Lower-left
                    self.directions = [bg.Direction.UP, bg.Direction.RIGHT]
            else:
                if y == 0:
                    #Upper-right
                    self.directions = [bg.Direction.DOWN, bg.Direction.LEFT]
                else:
                    #Lower-right
                    self.directions = [bg.Direction.UP, bg.Direction.LEFT]
                    
    
    def give_view(self, view, owner_view):
        self.view = view
        self.owner_view = owner_view
        self.coords = self.owner_view.coords
        self.player = self.owner_view.player
        
        if not self.directions:
            self.set_directions()
            if not self.owner_view.message:
                for d in self.directions:
                    add = str(d).split('.')[1]
                    self.message_to_give = self.message_to_give + ' ' + add
            else:
                self.message_to_give = self.owner_view.message
    
    def get_moves(self):
        
        coords = self.owner_view.coords
        # items_at = self.view[coords]
        
        # is_es_at = 'EnergySource' in items_at
        is_first = self.owner_view.sight == 1
        
        #Get all this info up front
        adj = bg.coords_within_distance(coords,
                                        1,
                                        include_center=False)
        
        moves = dict()
        
        if is_first:
            build_coords = choice(adj)
            
            #Always build
            build_move = builds.BuildMove(build_coords,
                                          max_hp=1,
                                          power=1,
                                          attack_range=0,
                                          speed=0,#self.next_speed.val,
                                          sight=0,
                                          energy=0,
                                          movement=0,
                                          message=self.message_to_give,
                                          spread=64,
                                          absorb=3)
                                          #absorb=40)
            
            moves[bg.MoveType.BUILD] = [build_move]
            
            return moves
        else:
            #Always attack 
            # attack_coords = choice(adj)
            attack_coords = self.owner_view.coords
            
            attack_move = bg.Move(move_type=bg.MoveType.ATTACK,
                                  target_coords=attack_coords)
            
            moves[bg.MoveType.ATTACK] = [attack_move]
            
            #go the to center
            t_coords = (32, 32)
            movement = get_approach_moves(self.owner_view.coords, t_coords)
            moves[bg.MoveType.MOVE] = movement
        
            return moves

class BasicPoisonController:
    def __init__(self):
        self.view = None
        self.owner_view = None
        self.directions = list()
        self.message_to_give = ''
        self.first = False
    
    def set_directions(self):
        message = self.owner_view.message
        chance_random = True
        if message and message[0] == '!':
            message = message[1:]
            chance_random = False
        
        if chance_random:
            #random directions
            if True:#randint(0, 1) == 1:
                self.directions = choice(([bg.Direction.DOWN, bg.Direction.RIGHT],
                                          [bg.Direction.UP, bg.Direction.RIGHT],
                                          [bg.Direction.DOWN, bg.Direction.LEFT],
                                          [bg.Direction.UP, bg.Direction.LEFT]))
                return
        
        if message:
            for word in message.split():
                d = bg.Direction.__dict__.get(word, None)
                if d:
                    self.directions.append(d)
        else:
            self.first = True
            #Should be the first bot
            x, y = self.owner_view.coords
            if x == 0:
                if y == 0:
                    #Upper-left
                    self.directions = [bg.Direction.DOWN, bg.Direction.RIGHT]
                else:
                    #Lower-left
                    self.directions = [bg.Direction.UP, bg.Direction.RIGHT]
            else:
                if y == 0:
                    #Upper-right
                    self.directions = [bg.Direction.DOWN, bg.Direction.LEFT]
                else:
                    #Lower-right
                    self.directions = [bg.Direction.UP, bg.Direction.LEFT]
                    
    
    def give_view(self, view, owner_view):
        self.view = view
        self.owner_view = owner_view
        self.coords = self.owner_view.coords
        self.player = self.owner_view.player
        
        if not self.directions:
            self.set_directions()
            if not self.owner_view.message:
                for d in self.directions:
                    add = str(d).split('.')[1]
                    self.message_to_give = self.message_to_give + ' ' + add
                if self.first:
                    self.message_to_give = '!' + self.message_to_give
            else:
                self.message_to_give = self.owner_view.message
    
    #If you're on an energy source, either build or give energy
    #If you're not, either go to an energy source, fight, or search
    def get_moves(self):
        coords = self.owner_view.coords
        items_at = self.view[coords]
        
        is_es_at = 'EnergySource' in items_at
        
        #Get all this info up front
        adj = bg.coords_within_distance(coords,
                                        1,
                                        include_center=False)
        
        #Only deal with visible coords
        adj = [c for c in adj if c in self.view]
        
        adj_wo_bot = [c for c in adj if not 'Bot' in self.view[c]]
        adj_w_bot = [c for c in adj if not c in adj_wo_bot]
        adj_w_ally = [c for c in adj_w_bot if\
                      self.view[c]['Bot'].player == self.owner_view.player]
        # adj_w_enemy = [b for b in adj_w_bot if not b in adj_w_ally]
        
        moves = dict()
        
        attack_range = 3
        spread = 2
        
        
        #Of all the squares to attack,
        #choose the one that hits the most enemies
        #of the ones that don't hit any allies
        in_range = bg.coords_within_distance(coords, attack_range)
        in_range = list([c for c in in_range if c in self.view])
        
        num_enemy_hit_from_c = dict()
        for c in in_range:
            hit_coords = bg.coords_within_distance(c, spread)
            allies_hit = get(self.view, hit_coords, player=self.player)
            if allies_hit:
                continue
            
            num_enemies_hit = len(get(self.view,
                                      hit_coords, 
                                      item_type='Bot'))
            #Don't attack
            #You might just hit an ally anyways
            if not num_enemies_hit:
                continue
            
            num_enemy_hit_from_c[c] = num_enemies_hit
        
        attack_candidates = list(num_enemy_hit_from_c)
        
        #There's a good place to attack, so attack there
        if attack_candidates:
            # print(self.coords)
            # print('')
            attack_candidates.sort(key=lambda c:num_enemy_hit_from_c[c])
            attack_coords = attack_candidates[-1]
            
            attack_move = bg.Move(move_type=bg.MoveType.ATTACK,
                                  target_coords=attack_coords)
            
            moves[bg.MoveType.ATTACK] = [attack_move]
                
        if is_es_at:
            #Either build or give energy
            adj = bg.coords_within_distance(coords,
                                            1,
                                            include_center=False)
            # print('adj_wo_bot: {}'.format(adj_wo_bot))
            
            
            #Build in one of the empty spots
            building = False
            if adj_wo_bot:
                building = True
                build_coords = choice(adj_wo_bot)
                
                build_move = builds.BuildMove(build_coords,
                                              max_hp=3,
                                              power=2,
                                              attack_range=attack_range,
                                              speed=0,
                                              sight=4,
                                              energy=0,
                                              movement=1,
                                              message=self.message_to_give,
                                              poison=1, #Testing poison
                                              spread=spread,
                                              absorb=4)
                
                moves[bg.MoveType.BUILD] = [build_move]
            
            #There's a bot in one of the empty spots
            
            if adj_w_ally and not building:
                give_en_coords = choice(adj_w_ally)
                
                give_energy_move = bg.Move(move_type=bg.MoveType.GIVE_ENERGY,
                                           target_coords=give_en_coords,
                                           amount=self.owner_view.energy)
                #Add amount later
                moves[bg.MoveType.GIVE_ENERGY] = [give_energy_move]
            
            return moves
        else:
            #Not on an energy source
            #Either look for an energy source or look for an enemy
            
            #Look for an energy source
            energy_sources = list()
            
            for _, items in self.view.items():
                if 'EnergySource' in items and not 'Bot' in items:
                    energy_sources.append(items['EnergySource'])
            
            if energy_sources:
                target_coords = choice(energy_sources).coords
                
                approach_moves = get_approach_moves(self.coords,
                                                    target_coords)
                moves[bg.MoveType.MOVE] = approach_moves
            else:
                #Look for an enemy instead
                enemies = list()
                for _, items in self.view.items():
                    if 'Bot' in items and items['Bot'].player != self.player:
                        enemies.append(items['Bot'])
                
                if enemies:
                    target_coords = choice(enemies).coords
                    
                    approach_moves = get_approach_moves(self.coords,
                                                        target_coords)
                    moves[bg.MoveType.MOVE] = approach_moves
                elif self.directions:
                    #There's nothing in sight, so just wander
                    d = choice(self.directions)
                    move = bg.Move(bg.MoveType.MOVE,
                                   direction=d)
                    moves[bg.MoveType.MOVE] = [move]
                else:
                    #We don't have any directions
                    #So just go up
                    print('no directions, going up')
                    move = bg.Move(bg.MoveType.MOVE,
                                   direction=bg.Direction.UP)
                    moves[bg.MoveType.MOVE] = [move]
        
        return moves

#A controller to test the Fragile stat
class FragileTestController:
    def __init__(self):
        self.view = None
        self.owner_view = None
        self.directions = list()
        self.message_to_give = ''
    
    def set_directions(self):
        message = self.owner_view.message
        if message:
            for word in message.split():
                d = bg.Direction.__dict__.get(word, None)
                if d:
                    self.directions.append(d)
        else:
            #Should be the first bot
            x, y = self.owner_view.coords
            if x == 0:
                if y == 0:
                    #Upper-left
                    self.directions = [bg.Direction.DOWN, bg.Direction.RIGHT]
                else:
                    #Lower-left
                    self.directions = [bg.Direction.UP, bg.Direction.RIGHT]
            else:
                if y == 0:
                    #Upper-right
                    self.directions = [bg.Direction.DOWN, bg.Direction.LEFT]
                else:
                    #Lower-right
                    self.directions = [bg.Direction.UP, bg.Direction.LEFT]
                    
    
    def give_view(self, view, owner_view):
        self.view = view
        self.owner_view = owner_view
        self.coords = self.owner_view.coords
        self.player = self.owner_view.player
        
        if not self.directions:
            self.set_directions()
            if not self.owner_view.message:
                for d in self.directions:
                    add = str(d).split('.')[1]
                    self.message_to_give = self.message_to_give + ' ' + add
            else:
                self.message_to_give = self.owner_view.message
    
    #If you're on an energy source, either build or give energy
    #If you're not, either go to an energy source, fight, or search
    def get_moves(self):
        coords = self.owner_view.coords
        items_at = self.view[coords]
        
        is_es_at = 'EnergySource' in items_at
        
        #Get all this info up front
        adj = bg.coords_within_distance(coords,
                                        1,
                                        include_center=False)
        
        #Only deal with visible coords
        adj = [c for c in adj if c in self.view]
        
        adj_wo_bot = [c for c in adj if not 'Bot' in self.view[c]]
        adj_w_bot = [c for c in adj if not c in adj_wo_bot]
        adj_w_ally = [c for c in adj_w_bot if\
                      self.view[c]['Bot'].player == self.owner_view.player]
        # adj_w_enemy = [b for b in adj_w_bot if not b in adj_w_ally]
        
        moves = dict()
        
        #Always attack if there's an enemy adjacent
        attack_range = 1
        in_range = bg.coords_at_distance(coords, attack_range)
        in_range = [c for c in in_range if c in self.view]
        in_range_w_bot = [c for c in in_range if 'Bot' in self.view[c]]
        in_range_w_enemy = [c for c in in_range_w_bot if\
                            self.view[c]['Bot'].player != self.owner_view.player]
        if in_range_w_enemy:
            attack_coords = choice(in_range_w_enemy)
            
            attack_move = bg.Move(move_type=bg.MoveType.ATTACK,
                                  target_coords=attack_coords)
            
            moves[bg.MoveType.ATTACK] = [attack_move]
                
        if is_es_at:
            #Either build or give energy
            adj = bg.coords_within_distance(coords,
                                            1,
                                            include_center=False)
            # print('adj_wo_bot: {}'.format(adj_wo_bot))
            
            
            #Build in one of the empty spots
            building = False
            if adj_wo_bot:
                building = True
                build_coords = choice(adj_wo_bot)
                
                build_move = builds.BuildMove(build_coords,
                                              max_hp=70,
                                              power=10,
                                              attack_range=attack_range,
                                              speed=0,
                                              sight=4,
                                              energy=0,
                                              movement=1,
                                              message=self.message_to_give,
                                              fragile=1)
                
                moves[bg.MoveType.BUILD] = [build_move]
            
            #There's a bot in one of the empty spots
            
            if adj_w_ally and not building:
                give_en_coords = choice(adj_w_ally)
                
                give_energy_move = bg.Move(move_type=bg.MoveType.GIVE_ENERGY,
                                           target_coords=give_en_coords,
                                           amount=self.owner_view.energy)
                #Add amount later
                moves[bg.MoveType.GIVE_ENERGY] = [give_energy_move]
            
            return moves
        else:
            #Not on an energy source
            #Either look for an energy source or look for an enemy
            
            #Look for an energy source
            energy_sources = list()
            
            for _, items in self.view.items():
                if 'EnergySource' in items and not 'Bot' in items:
                    energy_sources.append(items['EnergySource'])
            
            if energy_sources:
                target_coords = choice(energy_sources).coords
                
                approach_moves = get_approach_moves(self.coords,
                                                    target_coords)
                moves[bg.MoveType.MOVE] = approach_moves
            else:
                #Look for an enemy instead
                enemies = list()
                for _, items in self.view.items():
                    if 'Bot' in items and items['Bot'].player != self.player:
                        enemies.append(items['Bot'])
                
                if enemies:
                    target_coords = choice(enemies).coords
                    
                    approach_moves = get_approach_moves(self.coords,
                                                        target_coords)
                    moves[bg.MoveType.MOVE] = approach_moves
                elif self.directions:
                    #There's nothing in sight, so just wander
                    d = choice(self.directions)
                    move = bg.Move(bg.MoveType.MOVE,
                                   direction=d)
                    moves[bg.MoveType.MOVE] = [move]
                else:
                    #We don't have any directions
                    #So just go up
                    print('no directions, going up')
                    move = bg.Move(bg.MoveType.MOVE,
                                   direction=bg.Direction.UP)
                    moves[bg.MoveType.MOVE] = [move]
        
        return moves