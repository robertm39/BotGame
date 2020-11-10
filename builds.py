# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 16:39:48 2020

@author: rober
"""

import bot_game as bg
import effects

BASE_STATS = ('max_hp',
              'power',
              'attack_range',
              'speed',
              'sight',
              'energy',
              'movement')

def get_base_cost(max_hp, power, attack_range, speed, sight, movement):
    base = max_hp + power + 2**speed - 1
    
    range_mult = 0.75 + (attack_range / 4.0)
    sight_mult = 0.2 if sight == 0 else 0.5 + sight/2.0
    movement_mult = 0.5 + movement/2.0
    
    #I'll use round instead
    #to guard against floating point errors
    result = round(base * range_mult * sight_mult * movement_mult)
    
    #Every unit must cost at least one energy
    return max(1, result)

class Code:
    def __init__(self, sources, targets, events):
        self.sources = tuple(sources)
        self.targets = tuple(targets)
        self.events = tuple(events)
    
    def list_fits(self, l1, l2):
        return (not l1) or (set(l1).intersection(l2))
    
    def fits(self, event):
        if not self.list_fits(self.sources, event.sources):
            return False
        if not self.list_fits(self.targets, [event.target]):
            return False
        if not self.list_fits(self.events, [type(event)]):
            return False
        
        #This must be overriden for more specific matches
        return True
    
    #This must be overriden to do anything
    def new_turn(self, game_manager):
        pass
    
    #This must be overriden to do anything
    def trigger(self, game_manager, event):
        pass

class ReplacementCode(Code):
    pass

class SpecialStat:
    def get_codes(self):
        return list()

STATS_FROM_NAMES = dict()

class AbsorbStat(SpecialStat):
    def __init__(self, value, bot):
        self.value = value
        self.bot = bot
        self.code = AbsorbReplacementCode(self.value, self.bot)
    
    def get_codes(self):
        return [self.code]
    
    def multiplier(self):
        return 1.0 + self.value / 10.0

class AbsorbReplacementCode(ReplacementCode):
    def __init__(self, value, bot):
        super().__init__([], [bot], [effects.DamageEffect])
        self.value = value
        self.bot = bot
        
        self.reduction_this_turn = 0
    
    def new_turn(self, game_manager):
        self.reduction_this_turn = 0
    
    def fits(self, effect):
        if not super().fits(effect):
            return False
        return self.reduction_this_turn < self.value
    
    def trigger(self, game_manager, effect):
        reduction_left = self.value - self.reduction_this_turn
        damage = effect.damage
        damage_reduction = min(reduction_left, damage)
        self.reduction_this_turn += damage_reduction
        
        reduced_damage = effect.damage - damage_reduction
        new_effect = effects.DamageEffect(effect.sources + tuple([self]),
                                          effect.target,
                                          reduced_damage)
        game_manager.register_effect(new_effect)
STATS_FROM_NAMES['absorb'] = AbsorbStat

class TallStat(SpecialStat):
    def __init__(self, value, bot):
        #This is a binary stat
        #Either you have it or you don't
        self.value = 1
    
    def multiplier(self):
        return 1.5
STATS_FROM_NAMES['tall'] = TallStat

class BurnStat(SpecialStat):
    def __init__(self, value, bot):
        self.value = value
        self.bot = bot
        
        self.code = BurnReplacementCode(self.value, self.bot)
        
        if self.value < 1:
            raise ValueError('value: {}'.format(value))
        if round(self.value) != self.value:
            raise ValueError('value: {}'.format(value))
    
    def get_codes(self):
        return [self.code]
    
    def multiplier(self):
        return 1 + self.value * 0.5

class Burn:
    def __init__(self, sources, target, power):
        self.sources = tuple(sources)
        self.target = target
        self.power = power

class BurnReplacementCode(ReplacementCode):
    def __init__(self, value, bot):
        super().__init__([bot], [], [effects.AttackEffect])
        self.value = value
        self.bot = bot
        
        self.burns = dict()
    
    #Default fits() behavior works
    
    #Do all the burn damage in the new_turn step
    #This makes the burn effect better because the first burn happens
    #before the other bot has the chance to realized it's being burned and
    #run away
    #Unless that bot knew all along it was facing a bot with burn
    def new_turn(self, game_manager):
        for burn in self.burns:
            attack_effect = effects.AttackEffect(burn.sources,
                                                 burn.target,
                                                 burn.power)
            game_manager.register_effect(attack_effect)
        
        #Decrement the amount of time left on all burns
        #and get rid of the ones that would be left at zero
        self.burns = {b:i-1 for b, i in self.burns.items() if i > 1}
    
    def trigger(self, game_manager, effect):
        t_coords = effect.target
        burn = Burn(effect.sources + tuple([self]), t_coords, effect.power)
        self.burns[burn] = self.value
        
        new_attack = effects.AttackEffect(effect.sources + tuple([self]),
                                          t_coords,
                                          effect.power)
        game_manager.register_effect(new_attack)
STATS_FROM_NAMES['burn'] = BurnStat

class SpreadStat(SpecialStat):
    def __init__(self, value, bot):
        self.value = value
        self.bot = bot
        
        if self.value < 1:
            raise ValueError('value: {}'.format(value))
        if round(self.value) != self.value:
            raise ValueError('value: {}'.format(value))
        
        self.code = SpreadReplacementCode(self.value, self.bot)
    
    def get_codes(self):
        return [self.code]
    
    def multiplier(self):
        #The number of squares hit is equal to
        #2n^2 + 2n + 1
        #Where n is the spread range
        #So the number of additional squares hit is 2n^2 + 2n
        #And half of that is n^2 + n
        #Remove the n because you need a high attack range to avoid
        #hurting yourself
        return 1 + self.value**2

class SpreadReplacementCode(ReplacementCode):
    def __init__(self, value, bot):
        #Whenever this bot attacks anywhere
        super().__init__([bot], [], [effects.AttackEffect])
        self.value = value
        self.bot = bot
    
    #Default fits() behavior works
    
    def trigger(self, game_manager, effect):
        c_coords = effect.target
        battlefield = game_manager.battlefield
        t_coords = battlefield.get_visible_coords(c_coords=c_coords,
                                                  s_range=self.value)
        
        for t_coord in t_coords:
            attack = effects.AttackEffect(effect.sources + tuple([self]),
                                          t_coord,
                                          effect.power)
            game_manager.register_effect(attack)
STATS_FROM_NAMES['spread'] = SpreadStat

class NoGiveEnergyStat(SpecialStat):
    def __init__(self, value, bot):
        self.value = 1
    
    def multiplier(self):
        return 0.9
STATS_FROM_NAMES['no_give_energy'] = NoGiveEnergyStat

class NoBuildStat(SpecialStat):
    def __init__(self, value, bot):
        self.value = 1
    
    def multiplier(self):
        return 0.9
STATS_FROM_NAMES['no_build'] = NoBuildStat

class HealStat(SpecialStat):
    def __init__(self, value, bot):
        self.value = 1
        
    def multiplier(self):
        return 2.0
STATS_FROM_NAMES['heal'] = HealStat

#Implemented special stats:
#Absorb X
#Spread X
#Heal
#NoGiveEnergy
#NoBuild
#Tall

#Unimplemented special stats:
#Burn X *
#Stealth
#Curved Sight

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
        self.message = message
        self.special_stats_dict = special_stats.copy() #{name: val}
        self.special_stats = list()
        
        for name, val in special_stats.items():
            self.__setattr__(name, val)
            stat_class = STATS_FROM_NAMES[name]
            stat = stat_class(val)
            self.special_stats.append(stat)
        
        self.calculate_cost()
        #Now self.cost is initialized
    
    def calculate_cost(self):
        """
        Calculate the cost of the build. The build will fail if the bot does
        not have enough energy to pay for the cost
        """
        base_cost = get_base_cost(self.max_hp,
                                  self.power,
                                  self.attack_range,
                                  self.speed,
                                  self.sight,
                                  self.movement)
        
        multiplier = 1.0
        for stat in self.special_stats:
            multiplier *= stat.multiplier()
        
        self.cost = base_cost * multiplier
            