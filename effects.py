# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 16:39:18 2020

@author: rober
"""

from random import randint

import bot_game as bg

class Effect:
    pass

class GameEffect(Effect):
    """
    An effect that directly affects the game.
    For example, a damage effect, and attack effect,
    an energy transfer effect.
    These effects do not wait to be readied.
    """
    def new_turn(self, battlefield):
        raise RuntimeError('Game Effect newturned: {}'.format(self))
    
    def ready(self):
        return True

class UtilEffect(Effect):
    pass

class DamageEffect(GameEffect):
    def __init__(self, sources, damage, bot):
        self.sources = tuple(sources)
        self.damage = damage
        self.bot = bot
    
    def resolve(self, battlefield):
        # print('resolving')
        self.bot.take_damage(self.damage)
        
def get_random_damage(power):
    #The sum of x {0, 1} dice, where x = power
    return sum([randint(0, 1) for _ in range(power)])

class AttackEffect(GameEffect):
    def __init__(self, sources, power, coords):
        self.sources = tuple(sources)
        self.power = power
        self.coords = coords
    
    def resolve(self, battlefield):
        
        items_at = battlefield.map[self.coords]
        bots_at = [b for b in items_at if type(b) is bg.Bot]
        if not bots_at:
            return
        
        bot = bots_at[0]
        damage = get_random_damage(self.power)
        
        damage_effect = DamageEffect([self], damage, bot)
        battlefield.register_effect(damage_effect)

class GiveEnergyEffect(GameEffect):
    def __init__(self, sources, amount, bot):
        self.sources = sources
        self.amount = amount
        self.bot = bot
    
    def resolve(self, battlefield):
        self.bot.energy += self.amount