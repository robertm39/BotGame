# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 15:39:11 2020

@author: rober
"""

import tkinter as tk

import bot_game
import controllers
from tests import get_bot

class BotGameDisplayFrame(tk.Frame):
    def __init__(self, parent, game_manager, square_size=10, frame_delay=1000):
        tk.Frame.__init__(self, parent, background='white')
        
        self.parent = parent
        self.parent.title('Bot Game')
        
        self.battlefield = game_manager.battlefield
        self.game_manager = game_manager
        self.square_size = square_size
        
        self.frame_delay = frame_delay
        
        self.init_gui()
    
    def init_gui(self):
        self.pack(fill=tk.BOTH, expand=True)
        
        self.width = self.square_size * self.battlefield.width + 1
        self.height = self.square_size * self.battlefield.height + 1
        
        self.canvas = tk.Canvas(self,
                                width=self.width,
                                height=self.height,
                                borderwidth=0,
                                highlightthickness=0,
                                bd=1,
                                bg='white')
        self.canvas.pack(side=tk.TOP)
        
        # self.canvas.create_line(10, 10, 10, 10, fill='blue')
        
        self.draw_grid()
        self.draw_energy_sources()
        self.draw_bots()
    
    def draw_grid(self):
        #Delete old grid
        self.canvas.delete('GRID')
        
        #Draw square around grid
        self.canvas.create_rectangle(1,
                                     1,
                                     self.width,
                                     self.height,
                                     outline='black',
                                     tags='GRID')
        
        for x in range(self.battlefield.width):
            for y in range(self.battlefield.height):
                self.canvas.create_rectangle(self.square_size * x + 1,
                                             self.square_size * y + 1,
                                             self.square_size * (x + 1) + 1,
                                             self.square_size * (y + 1) + 1,
                                             outline='black',
                                             tags='GRID')
    
    def draw_energy_sources(self):
        #Delete old energy source render
        self.canvas.delete('ENERGY_SOURCE')
        
        energy_sources = filter(lambda x: type(x) is bot_game.EnergySource,
                                self.battlefield.get_items())
        energy_sources = list(energy_sources)
        
        #This always makes an odd number
        proportion = 0.85
        
        size = round((self.square_size - 1) * proportion / 2) * 2 + 1
        upper_left = self.square_size - size
        
        for es in energy_sources:
            # break
            x, y = es.coords
            
            self.canvas.create_oval(x*self.square_size + upper_left + 1,
                                    y*self.square_size + upper_left + 1,
                                    x*self.square_size + size + 1,
                                    y*self.square_size + size + 1,
                                    outline='black',
                                    fill='lightgreen',
                                    tags='ENERGY_SOURCE')
            
            self.canvas.create_text((x+0.5)*self.square_size + 1,
                                    (y+0.5)*self.square_size + 1,
                                    font=('Consolas', 15),
                                    text=str(es.amount),
                                    tags='ENERGY_SOURCE')
    
    def draw_bots(self):
        #Delete old bots
        self.canvas.delete('BOT')
        
        bots = filter(lambda x: type(x) is bot_game.Bot,
                      self.battlefield.get_items())
        
        #This always makes an odd number
        proportion = 0.85
        
        size = round((self.square_size - 1) * proportion / 2) * 2 + 1
        upper_left = self.square_size - size
        
        for bot in bots:
            x, y = bot.coords
            
            self.canvas.create_oval(x*self.square_size + upper_left + 1,
                                    y*self.square_size + upper_left + 1,
                                    x*self.square_size + size + 1,
                                    y*self.square_size + size + 1,
                                    outline='black',
                                    fill='lightgray',
                                    tags='BOT')
            
            self.canvas.create_text((x+0.5)*self.square_size + 1,
                                    (y+0.5)*self.square_size + 1,
                                    font=('Consolas', 15),
                                    text=str(bot.hp),
                                    tags='BOT')
    
    def update_frame(self):
        self.game_manager.advance()
        self.draw_bots()
    
    def loop(self):
        self.update_frame()
        self.frame_num += 1
        print('\nFrame {}'.format(self.frame_num))
        self.after(self.frame_delay, self.loop)
    
    def start_loop(self):
        self.frame_num = 0
        print('Frame {}'.format(self.frame_num))
        self.after(self.frame_delay, self.loop)

def test_1(battlefield):
    energy_source_1 = bot_game.EnergySource((1, 1), 10)
    energy_source_2 = bot_game.EnergySource((2, 3), 10)
    energy_source_3 = bot_game.EnergySource((4, 2), 10)
    energy_source_4 = bot_game.EnergySource((1, 4), 10)
    energy_source_5 = bot_game.EnergySource((3, 5), 10)
    battlefield.add_item(energy_source_1)
    battlefield.add_item(energy_source_2)
    battlefield.add_item(energy_source_3)
    battlefield.add_item(energy_source_4)
    battlefield.add_item(energy_source_5)
    
    ctlr_1 = controllers.SeekEnergyController()
    bot_1 = bot_game.Bot(coords=(0, 0),
                         max_hp=10,
                         hp=10,
                         power=10,
                         attack_range=1,
                         speed=0,
                         sight=10,
                         energy=0,
                         movement=1,
                         player='1',
                         message='',
                         controller=ctlr_1)
    battlefield.add_item(bot_1)

def give_energy_test_1(battlefield):
    """
    Test GIVE_ENERGY processing.
    """
    energy_source = bot_game.EnergySource((0, 0), 10)
    battlefield.add_item(energy_source)
    
    controller = controllers.ChainEnergyController()
    bot = bot_game.Bot(coords=(0, 0),
                       max_hp=10,
                       hp=10,
                       power=10,
                       attack_range=1,
                       speed=0,
                       sight=5,
                       energy=0,
                       movement=1,
                       player='1',
                       message='RIGHT',
                       special_stats=dict(),
                       controller=controller)
    battlefield.add_item(bot)

def heal_test_1(battlefield):
    energy_source = bot_game.EnergySource((0, 0), 10)
    battlefield.add_item(energy_source)
    
    heal_controller = controllers.GiveLifeController()
    heal_bot = bot_game.Bot(coords=(0, 0),
                            max_hp=100,
                            hp=10,
                            power=10,
                            attack_range=1,
                            speed=0,
                            sight=5,
                            energy=0,
                            movement=1,
                            player='1',
                            message='RIGHT',
                            controller=heal_controller,
                            heal=1)
    
    battlefield.add_item(heal_bot)

def give_life_test_1(battlefield):
    energy_source = bot_game.EnergySource((0, 0), 10)
    battlefield.add_item(energy_source)
    
    heal_controller = controllers.GiveLifeController()
    heal_bot = bot_game.Bot(coords=(0, 0),
                            max_hp=100,
                            hp=10,
                            power=10,
                            attack_range=1,
                            speed=0,
                            sight=5,
                            energy=0,
                            movement=1,
                            player='1',
                            message='RIGHT',
                            controller=heal_controller,
                            heal=1)
    battlefield.add_item(heal_bot)
    print('heal_bot.heal: {}'.format(heal_bot.heal))
    
    sit_controller = controllers.SitController()
    hurt_bot = bot_game.Bot(coords=(1, 0),
                            max_hp=100,
                            hp=10,
                            power=10,
                            attack_range=1,
                            speed=0,
                            sight=5,
                            energy=0,
                            movement=1,
                            player='1',
                            message='RIGHT',
                            special_stats=dict(),
                            controller=sit_controller)
    battlefield.add_item(hurt_bot)

def absorb_test_1(battlefield):
    fight_controller_1 = controllers.SeekAndFightController()
    absorb_bot = bot_game.Bot(coords=(0, 0),
                              max_hp=200,
                              hp=200,
                              power=20,
                              attack_range=1,
                              speed=0,
                              sight=5,
                              energy=0,
                              movement=1,
                              player='1',
                              message='RIGHT',
                              controller=fight_controller_1,
                              absorb=1)
    
    fight_controller_2 = controllers.SeekAndFightController()
    plain_bot = bot_game.Bot(coords=(1, 0),
                             max_hp=200,
                             hp=200,
                             power=20,
                             attack_range=1,
                             speed=0,
                             sight=5,
                             energy=0,
                             movement=1,
                             player='2',
                             message='RIGHT',
                             # absorb=1,
                             controller=fight_controller_2)
    
    battlefield.add_bot(absorb_bot)
    battlefield.add_bot(plain_bot)

def absorb_test_2(battlefield):
    fight_controller_1 = controllers.SeekAndFightController()
    absorb_bot = bot_game.Bot(coords=(1, 1),
                              max_hp=100,
                              hp=100,
                              power=10,
                              attack_range=1,
                              speed=0,
                              sight=5,
                              energy=0,
                              movement=1,
                              player='1',
                              message='RIGHT',
                              controller=fight_controller_1,
                              absorb=10)
    
    fight_controller_2 = controllers.SeekAndFightController()
    plain_bot_1 = bot_game.Bot(coords=(1, 0),
                               max_hp=100,
                               hp=100,
                               power=10,
                               attack_range=1,
                               speed=0,
                               sight=5,
                               energy=0,
                               movement=1,
                               player='2',
                               message='DOWN',
                               controller=fight_controller_2)
    
    fight_controller_3 = controllers.SeekAndFightController()
    plain_bot_2 = bot_game.Bot(coords=(0, 1),
                               max_hp=100,
                               hp=100,
                               power=10,
                               attack_range=1,
                               speed=0,
                               sight=5,
                               energy=0,
                               movement=1,
                               player='2',
                               message='RIGHT',
                               controller=fight_controller_3)
    
    battlefield.add_bot(absorb_bot)
    battlefield.add_bot(plain_bot_1)
    battlefield.add_bot(plain_bot_2)

def spread_test_1(battlefield):
    spread_controller = controllers.SpreadAttackController()
    spread_bot = bot_game.Bot(coords=(1, 1),
                              max_hp=100,
                              hp=100,
                              power=10,
                              attack_range=2,
                              speed=0,
                              sight=5,
                              energy=0,
                              movement=1,
                              player='1',
                              message='RIGHT',
                              controller=spread_controller,
                              spread=2)
    battlefield.add_bot(spread_bot)
    
    target_coords = [(3, 1), (2, 1), (4, 1), (3, 0), (3, 2)]
    for coords in target_coords:
        controller = controllers.SitController()
        bot = bot_game.Bot(coords=coords,
                           max_hp=100,
                           hp=100,
                           power=10,
                           attack_range=0,
                           speed=0,
                           sight=5,
                           energy=0,
                           movement=1,
                           player='2',
                           message='RIGHT',
                           controller=controller)
        battlefield.add_bot(bot)

def main():
    root = tk.Tk()
    root.geometry('600x600+400+100')
    
    battlefield = bot_game.Battlefield(10, 10)
    
    game_manager = bot_game.GameManager(battlefield)
    
    #You can only add bots to the battlefield after the game_manager is made
    # test_1(battlefield)
    # give_life_test_1(battlefield)
    # heal_test_1(battlefield)
    # absorb_test_1(battlefield)
    # absorb_test_2(battlefield)
    spread_test_1(battlefield)
    
    frame = BotGameDisplayFrame(root,
                                game_manager,
                                square_size=50,
                                frame_delay=1000)
    tk.app = frame
    
    frame.start_loop()
    root.mainloop()

if __name__ == '__main__':
    main()