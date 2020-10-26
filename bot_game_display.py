# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 15:39:11 2020

@author: rober
"""

import tkinter as tk

import bot_game

class BotGameDisplayFrame(tk.Frame):
    def __init__(self, parent, battlefield, square_size=10):
        tk.Frame.__init__(self, parent, background='white')
        
        self.parent = parent
        self.parent.title('Bot Game')
        
        self.battlefield = battlefield
        self.square_size = square_size
        
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
        
        bots = filter(lambda x: type(x) is bot_game.BOT,
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
                                    tags='ENERGY_SOURCE')
            
            self.canvas.create_text((x+0.5)*self.square_size + 1,
                                    (y+0.5)*self.square_size + 1,
                                    font=('Consolas', 15),
                                    text=str(es.energy),
                                    tags='ENERGY_SOURCE')
    
    def update_frame(self):
        pass

def main():
    root = tk.Tk()
    root.geometry('600x600+400+100')
    
    battlefield = bot_game.Battlefield(10, 10)
    energy_source_1 = bot_game.EnergySource((1, 1), 5)
    energy_source_2 = bot_game.EnergySource((2, 3), 10)
    battlefield.add_item(energy_source_1)
    battlefield.add_item(energy_source_2)
    
    tk.app = BotGameDisplayFrame(root, battlefield, square_size=50)
    
    root.mainloop()

if __name__ == '__main__':
    main()