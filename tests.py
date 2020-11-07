# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 11:46:22 2020

@author: rober
"""

import bot_game
import controllers

def get_bot(coords,
            max_hp=1,
            hp=1,
            power=1,
            attack_range=1,
            speed=1,
            sight=1,
            energy=0,
            movement=1,
            player=1,
            message='',
            controller=None,
            **special_stats):
    
    controller = controller if controller else controllers.SitController()
    
    return bot_game.Bot(coords,
                        max_hp=max_hp,
                        hp=hp,
                        power=power,
                        attack_range=attack_range,
                        speed=speed,
                        sight=sight,
                        energy=energy,
                        movement=movement,
                        player=player,
                        message=message,
                        controller=controller,
                        **special_stats)

def print_visible_coords_result(bot_coords, result, blocked):
    x_s = list([x for x, y in result+blocked])
    y_s = list([y for x, y in result+blocked])
    
    min_x = min(x_s)
    max_x = max(x_s)
    
    min_y = min(y_s)
    max_y = max(y_s)
    
    for y in range(min_y, max_y+1):
        line = []
        for x in range(min_x, max_x+1):
            coords = (x, y)
            if coords == bot_coords:
                line.append('B')
            elif coords in result:
                line.append('O')
            elif coords in blocked:
                line.append('X')
            else:
                line.append(' ')
        print(''.join(line))

def get_visible_coords_test_one_case(coords, sight, result, blocked=None):
    battlefield = bot_game.Battlefield(100, 100)
    seeing_bot = get_bot(coords, sight=sight)
    
    battlefield.add_bot(seeing_bot)
    
    if blocked:
        for blocked_coords in blocked:
            bot = get_bot(blocked_coords, tall=1)
            battlefield.add_bot(bot)
    
    visible_coords = battlefield.get_visible_coords(seeing_bot)
    if set(visible_coords) == set(result):
        print('Test passed: coords={}, sight={}'.format(coords, sight))
        return True
    else:
        print('')
        print('Test failed: coords={}, sight={}'.format(coords, sight))
        print('Result was:')
        print_visible_coords_result(coords, visible_coords, blocked)
        
        print('')
        print('Should have been:')
        print_visible_coords_result(coords, result, blocked)
        print('')
        return False

def get_bot_coords_in_layout(layout):
    y = 0
    for line in layout:
        if not 'B' in line:
            y += 1
            continue
        x = line.find('B')
        return (x, y)

def get_gvc_case(x, y, sight, layout):
    coords = (x, y)
    # check_layout_width(layout)
    b_x, b_y = get_bot_coords_in_layout(layout)
    
    result = [coords]
    blocked = list()
    
    for l_y, line in enumerate(layout):
        for l_x, char in enumerate(line):
            true_x = x + l_x - b_x
            true_y = y + l_y - b_y
            true_coords = (true_x, true_y)
            if char == 'O':
                result.append(true_coords)
            elif char == 'X':
                blocked.append(true_coords)
    
    return coords, sight, result, blocked

def read_gvc_test_cases(file_name='tests\\gvc_tests.txt'):
    cases = list()
    with open(file_name) as file:
        while True:
            try:
                next(file) #Consume newline put there for human-readability
            except StopIteration:
                #This feels really janky
                break
            
            x, y, sight = [int(s) for s in next(file).split()]
            
            layout = list()
            line = next(file)
            while not 'END' in line:
                layout.append(line)
                line = next(file)
            
            cases.append(get_gvc_case(x, y, sight, layout))
    
    return cases

def get_visible_coords_test():
    total = 0
    successful = 0
    for case in read_gvc_test_cases():
        total += 1
        if get_visible_coords_test_one_case(*case):
            successful += 1
    
    print('{} Tests, {} Succeeded, {} Failed'\
          .format(total, successful, total-successful))

def main():
    get_visible_coords_test()

if __name__ == '__main__':
    main()