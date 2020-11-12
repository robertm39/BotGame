# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 14:38:53 2020

@author: rober
"""

import random

import bot_game

def get_start_bots(con_1, con_2, width, height):
    bot_1 = bot_game.Bot(coords=(0, 0),
                         max_hp=1,
                         hp=1,
                         power=0,
                         attack_range=0,
                         speed=0,
                         sight=1,
                         energy=0,
                         movement=1,
                         player='1',
                         message='',
                         controller=con_1)
    
    bot_2 = bot_game.Bot(coords=(width-1, height-1),
                         max_hp=1,
                         hp=1,
                         power=0,
                         attack_range=0,
                         speed=0,
                         sight=1,
                         energy=0,
                         movement=1,
                         player='2',
                         message='',
                         controller=con_2)
    
    return bot_1, bot_2

def get_start_energy_sources(width, height):
    es_1 = bot_game.EnergySource((0, 0), 5)
    es_2 = bot_game.EnergySource((width-1, height-1), 5)
    
    return es_1, es_2

def make_random_energy_sources(battlefield,
                               amounts=None,
                               num=20,
                               border=5):
    width, height = battlefield.width, battlefield.height
    
    if amounts == None:
        amounts = [3, 5, 10, 20]
    
    for _ in range(num):
        x = random.randint(border, width-1-border)
        y = random.randint(border, height-1-border)
        
        m = random.randint(1, len(amounts))
        sub_amounts = amounts[:m][::-1]
        

def setup_1(con_1, con_2):
    """
    Return a plain battlefield with con_1 in the upper-left corner
    and con_2 in the lower-right corner.
    """
    
    width, height = 100, 100
    
    battlefield = bot_game.Battlefield(width, height)
    game_manager = bot_game.GameManager(battlefield)
    
    bot_1, bot_2 = get_start_bots(con_1, con_2, width, height)
    
    battlefield.add_bot(bot_1)
    battlefield.add_bot(bot_2)
    
    #Add energy sources
    es_1, es_2 = get_start_energy_sources(width, height)
    battlefield.add_item(es_1)
    battlefield.add_item(es_2)
    
    return battlefield, game_manager