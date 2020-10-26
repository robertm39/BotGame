# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 16:39:18 2020

@author: rober
"""

from random import randint

import bot_game as bg

class Effect:
    pass

class DamageEffect(Effect):
    def __init__(self, sources, speed, damage, bot):
        self.sources = tuple(sources)
        self.speed = speed
        self.damage = damage
        self.bot = bot
    
    def new_turn(self, battlefield):
        pass
    
    def ready(self):
        return True
    
    def resolve(self, battlefield):
        self.bot.take_damage(self.damage)
        
def get_random_damage(power):
    #The sum of x {0, 1} dice, where x = power
    return sum([randint(0, 1) for _ in range(power)])

class AttackEffect(Effect):
    def __init__(self, sources, speed, power, coords):
        self.sources = tuple(sources)
        self.speed = speed
        self.power = power
        self.coords = coords
    
    def new_turn(self, battlefield):
        pass
    
    def ready(self):
        return True
    
    def resolve(self, battlefield):
        
        items_at = battlefield.map[self.coords]
        bots_at = [b for b in items_at if type(b) is bg.Bot]
        if not bots_at:
            return
        
        bot = bots_at[0]
        damage = get_random_damage(self.power)
        
        damage_effect = DamageEffect(self, self.speed, damage, bot)
        battlefield.register_effect(damage_effect)