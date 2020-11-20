# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 15:39:11 2020

@author: rober
"""

import tkinter as tk

import bot_game
import controllers
# from tests import get_bot
import setups

class BotGameDisplayFrame(tk.Frame):
    def __init__(self,
                 parent,
                 game_manager,
                 view_width=500,
                 view_height=500,
                 square_size=10,
                 font_size=10,
                 frame_delay=1000):
        tk.Frame.__init__(self, parent, background='white')
        
        self.parent = parent
        self.parent.title('Bot Game')
        
        self.battlefield = game_manager.battlefield
        self.game_manager = game_manager
        
        self.view_width = view_width
        self.view_height = view_height
        self.square_size = square_size
        self.font_size = font_size
        
        self.frame_delay = frame_delay
        
        self.init_gui()
    
    # def config_canvas(self, *args):
    #     pass
    #     # w, h = self.winfo_width(), self.winfo_height()
    #     # self.canvas.config(width=w, height=h)
    
    def init_gui(self):
        self.pack(fill=tk.BOTH)#, expand=True)
        
        self.width = self.square_size * self.battlefield.width + 1
        self.height = self.square_size * self.battlefield.height + 1
        
        self.config(width=self.width, height=self.height)
        
        self.right_scroll = tk.Scrollbar(self)
        # self.right_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_scroll.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.bottom_scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        # self.bottom_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.bottom_scroll.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        
        # w, h = self.winfo_width(), self.winfo_height()
        
        self.canvas = tk.Canvas(self,
                                width=self.view_width,
                                height=self.view_height,
                                borderwidth=0,
                                highlightthickness=0,
                                yscrollcommand=self.right_scroll.set,
                                xscrollcommand=self.bottom_scroll.set,
                                bd=1,
                                bg='white')
        
        #Configure the canvas when the size of this widget is changed (??)
        # self.bind('<Configure>', self.config_canvas)
        
        # self.canvas.pack(side=tk.TOP, fill=tk.BOTH)
        self.canvas.grid(row=0, column=0)#, stick=tk.N+tk.S+tk.E+tk.W)
        
        self.right_scroll.config(command=self.canvas.yview)
        self.bottom_scroll.config(command=self.canvas.xview)
        
        # self.canvas.config(scrollregion=self.canvas.bbox('all'))
        self.canvas.config(scrollregion=[0, 0, self.width, self.height])
        
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
                                    font=('Consolas', self.font_size),
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
            
            #Different players have different colors
            color = 'red' if bot.player == '1' else 'blue'
            
            self.canvas.create_oval(x*self.square_size + upper_left + 1,
                                    y*self.square_size + upper_left + 1,
                                    x*self.square_size + size + 1,
                                    y*self.square_size + size + 1,
                                    outline='black',
                                    # fill='lightgray',
                                    fill=color,
                                    tags='BOT')
            
            self.canvas.create_text((x+0.5)*self.square_size + 1,
                                    (y+0.5)*self.square_size + 1,
                                    font=('Consolas', self.font_size),
                                    text=str(bot.hp),
                                    tags='BOT')
    
    def update_frame(self):
        result = self.game_manager.advance()
        self.draw_bots()
        return result
    
    def loop(self):
        game_still_going = self.update_frame()
        self.frame_num += 1
        print('Frame {}'.format(self.frame_num))
        
        #Something is up with this
        #It keeps increasing
        # print(len(self.battlefield.bots))
        # for coords, items in self.battlefield.map.items():
        #     bots = [b for b in items if isinstance(b, bot_game.Bot)]
        #     print('{}, {}'.format(coords, len(bots)))
        
        # dead_bots = [b for b in self.battlefield.bots if b.hp == 0]
        # print(len(dead_bots))
        
        if game_still_going:
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

def burn_test_1(battlefield):
    fight_controller_1 = controllers.SeekAndFightController()
    burn_bot = bot_game.Bot(coords=(1, 1),
                            max_hp=100,
                            hp=100,
                            power=1,
                            attack_range=1,
                            speed=0,
                            sight=5,
                            energy=0,
                            movement=1,
                            player='1',
                            message='RIGHT',
                            controller=fight_controller_1,
                            burn=9)
    battlefield.add_bot(burn_bot)
    
    sit_controller = controllers.SitController()
    sit_bot = bot_game.Bot(coords=(2, 1),
                            max_hp=100,
                            hp=100,
                            power=1,
                            attack_range=1,
                            speed=0,
                            sight=5,
                            energy=0,
                            movement=1,
                            player='2',
                            message='RIGHT',
                            controller=sit_controller,)
    battlefield.add_bot(sit_bot)

def burn_and_spread_test_1(battlefield):
    spread_controller = controllers.SpreadAttackController()
    spread_bot = bot_game.Bot(coords=(1, 1),
                              max_hp=100,
                              hp=100,
                              power=1,
                              attack_range=2,
                              speed=0,
                              sight=5,
                              energy=0,
                              movement=1,
                              player='1',
                              message='RIGHT',
                              controller=spread_controller,
                              spread=1,
                              burn=9)
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

def stealth_test_1(battlefield):
    # sit_controller = controllers.SitController()
    controller_1 = controllers.SeekAndFightController()
    stealth_bot = bot_game.Bot(coords=(5, 5),
                               max_hp=100,
                               hp=100,
                               power=20,
                               attack_range=1,
                               speed=0,
                               sight=10,
                               energy=0,
                               movement=1,
                               player='1',
                               message='RIGHT',
                               controller=controller_1,
                               stealth=1)
    battlefield.add_bot(stealth_bot)
    
    fight_controller = controllers.SeekAndFightController()
    fight_bot = bot_game.Bot(coords=(0, 0),
                                     max_hp=100,
                                     hp=100,
                                     power=20,
                                     attack_range=1,
                                     speed=0,
                                     sight=10,
                                     energy=0,
                                     movement=1,
                                     player='2',
                                     message='RIGHT',
                                     controller=fight_controller)
    battlefield.add_bot(fight_bot)

def setups_test_1(battlefield):
    setups.make_random_energy_sources(battlefield, num=10, border=3)
    
    es_1, es_2 = setups.get_start_energy_sources(10, battlefield)
    battlefield.add_item(es_1)
    battlefield.add_item(es_2)
    
    con_1 = controllers.BasicController2()
    # con_1 = controllers.MegaBombController()
    
    # con_2 = controllers.BasicController()
    con_2 = controllers.BasicController2()
    
    bot_1, bot_2 = setups.get_start_bots(con_1, con_2, battlefield)
    battlefield.add_item(bot_1)
    battlefield.add_item(bot_2)

def main():
    root = tk.Tk()
    root.geometry('720x720+400+30')
    
    #Full size is 64x64
    #But I want to see the whole thing for testing
    battlefield = bot_game.Battlefield(32, 32)
    
    game_manager = bot_game.GameManager(battlefield)
    
    #You can only add bots to the battlefield after the game_manager is made
    # test_1(battlefield)
    # give_life_test_1(battlefield)
    # heal_test_1(battlefield)
    # absorb_test_1(battlefield)
    # absorb_test_2(battlefield)
    # spread_test_1(battlefield)
    # burn_test_1(battlefield)
    # burn_and_spread_test_1(battlefield)
    # stealth_test_1(battlefield)
    setups_test_1(battlefield)
    
    frame = BotGameDisplayFrame(root,
                                game_manager,
                                view_width=700,
                                view_height=700,
                                square_size=20,
                                font_size=8,
                                frame_delay=1)
    tk.app = frame
    
    frame.start_loop()
    root.mainloop()

if __name__ == '__main__':
    main()