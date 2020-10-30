# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 16:39:48 2020

@author: rober
"""

import math

import bot_game as bg

BASE_STATS = ('max_hp',
              'power',
              'attack_range',
              'speed',
              'sight',
              'energy',
              'movement')

def base_cost(max_hp, power, attack_range, speed, sight, movement):
    base = max_hp + power + 2**speed - 1
    
    range_mult = 0.75 + (attack_range / 4.0)
    sight_mult = 0.2 if speed == 0 else 0.5 + sight/2.0
    movement_mult = 0.5 + movement/2.0
    
    result = math.floor(base * range_mult * sight_mult * movement_mult)
    
    #Every unit must cost at least one energy
    return max(1, result)

class SpecialStat:
    pass

#I'll actually implement this later
#for now I'll just have this
class TallStat(SpecialStat):
    def __init__(self):
        #This is a binary stat
        #Either you have it or you don't
        self.value = 1
    
    def multiplier(self):
        return 1.5

class BurnStat(SpecialStat):
    def __init__(self, value):
        self.value = value
        
        if self.value < 1:
            raise ValueError('value: {}'.format(value))
        if round(self.value) != self.value:
            raise ValueError('value: {}'.format(value))
    
    def multiplier(self):
        return 1 + self.value * 0.5

class BuildMove(bg.Move):
    def __init__(self,
                 direction,
                 max_hp,
                 power,
                 attack_range,
                 speed,
                 sight,
                 energy,
                 movement,
                 player,
                 message,
                 **special_stats):
        self.direction = direction
        self.max_hp = max_hp
        self.power = power
        self.attack_range = attack_range
        self.speed = speed
        self.sight = sight
        self.energy = energy
        self.movement = movement
        self.player = player
        self.message = message
        self.special_stats = special_stats
        
        for name, val in special_stats.items():
            self.__setattr__(name, val)
        
        self.calculate_cost()
    
    def calculate_cost(self):
        """
        Calculate the cost of the build. The build will fail if the bot does
        not have enough energy to pay for the cost
        """
        pass