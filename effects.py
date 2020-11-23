# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 16:39:18 2020

@author: rober
"""

from random import randint

import bot_game as bg

class Event:
    def __init__(self, source, target):
        self.source = source
        self.target = target

class Effect(Event):
    def __init__(self, source, target, replacement_codes=tuple([])):
        super().__init__(source, target)
        self.replacement_codes = tuple(replacement_codes)
        # self.sources = tuple(sources)
        # self.target = target
        
#Every effect has a list of sources
#and one target
class DieEffect(Effect):
    def __init__(self, source, target, replacement_codes=tuple([])):
        super().__init__(source, target, replacement_codes)
    
    def resolve(self, game_manager):
        game_manager.battlefield.remove_bot(self.target, should_have=False)

class DamageEffect(Effect):
    def __init__(self, source, target, damage, replacement_codes=tuple([])):
        super().__init__(source, target, replacement_codes)
        self.damage = damage
    
    def resolve(self, game_manager):
        self.target.take_damage(self.damage)
        
        #Use the DieEffect now
        if self.target.is_dead():
            effect = DieEffect(self.source,
                               self.target,
                               self.replacement_codes)
            game_manager.register_effect(effect)
            # game_manager.battlefield.remove_bot(self.target, should_have=False)
        
def get_random_damage(power):
    #The sum of x {0, 1} dice, where x = power
    return sum([randint(0, 1) for _ in range(power)])

class AttackEffect(Effect):
    def __init__(self, source, target, power, replacement_codes=tuple([])):
        super().__init__(source, target, replacement_codes)
        self.power = power
    
    def resolve(self, game_manager):
        battlefield = game_manager.battlefield
        
        # items_at = battlefield.map[self.target]
        items_at = battlefield.at(self.target)
        bots_at = [b for b in items_at if type(b) is bg.Bot]
        if not bots_at:
            return
        
        bot = bots_at[0]
        damage = get_random_damage(self.power)
        
        # damage_effect = DamageEffect(self.sources + tuple([self]), bot, damage)
        damage_effect = DamageEffect(self.source, bot, damage)
        game_manager.register_effect(damage_effect)

class GiveEnergyEffect(Effect):
    def __init__(self, sources, target, amount, replacement_codes=tuple([])):
        super().__init__(sources, target, replacement_codes)
        self.amount = amount
    
    def resolve(self, game_manager):
        self.target.energy += self.amount

#Effects tied to particular abilities
class PoisonEffect(Effect):
    def __init__(self, sources, target, amount, replacement_codes=tuple([])):
        super().__init__(sources, target, replacement_codes)
        self.amount = amount
    
    def resolve(self, game_manager):
        hurt_bot = self.target
        
        hurt_bot.mod_manager.add_mod('max_hp', -self.amount, self)
        
        #Check if it's dead
        #maybe move all these to GameManager
        if hurt_bot.is_dead():
            effect = DieEffect(self.source,
                               hurt_bot,
                               self.replacement_codes)
            game_manager.register_effect(effect)