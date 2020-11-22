# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:46:26 2020

@author: rober
"""

from enum import Enum

import effects as eff

#This function will used for line-of-sight
#I don't know what else for
def directions_for_coords(coords):
    x, y = coords
    
    result = list()
    if x >= 0:
        result.append(Direction.RIGHT)
    if x <= 0:
        result.append(Direction.LEFT)
    
    if y >= 0:
        result.append(Direction.DOWN)
    if y <= 0:
        result.append(Direction.UP)
    
    return result

def diff(coords_1, coords_2):
    x_1, y_1 = coords_1
    x_2, y_2 = coords_2
    
    return (x_2 - x_1, y_2 - y_1)

def is_in_bounds(coords, min_x, max_x, min_y, max_y):
    """
    Return whether the given coords are within the given bounds.
    
    Parameters:
        coords (int, int): The coords to check.
        min_x (int): The minimum x-value allowed.
        max_x (int): The maximum x-value allowed.
        min_y (int): The minimum y-value allowed.
        max_y (int): The maximum y-value allowed.
    """
    x, y = coords
    # print('is_in_bounds: {}'.format(coords))
    
    if (min_x != None) and min_x > x:
        return False
    if (max_x != None) and max_x < x:
        return False
    
    if (min_y != None) and min_y > y:
        return False
    if (max_y != None) and max_y < y:
        return False
    
    return True

def filter_in_bounds_coords(coordses, min_x, max_x, min_y, max_y):
    """
    Return the coords in coords_list within the given bounds.
    
    Parameters:
        coords_list [(int, int)]: The coords to check.
        min_x (int): The minimum x-value allowed.
        max_x (int): The maximum x-value allowed.
        min_y (int): The minimum y-value allowed.
        max_y (int): The maximum y-value allowed.
    """
    return [c for c in coordses if is_in_bounds(c, min_x, max_x, min_y, max_y)]

def distance(coords_1, coords_2):
    """
    Return the distance between the two given coords.
    
    Parameters:
        coords_1 (int, int): The first pair of coords.
        coords_2 (int, int): The second pair of coords.
    """
    x_1, y_1 = coords_1
    x_2, y_2 = coords_2
    
    return abs(x_1 - x_2) + abs(y_1 - y_2)

def coords_at_distance(coords,
                       distance,
                       min_x=0,
                       max_x=None,
                       min_y=0,
                       max_y=None):
    if distance == 0:
        return [coords]
    
    result = list()
    
    cx, cy = coords
    
    for x in range(0, distance):
        y = distance - x
        
        result.append((cx + x, cy + y))
        result.append((cx - y, cy + x))
        result.append((cx - x, cy - y))
        result.append((cx + y, cy - x))
    
    return result

def coords_within_distance(coords,
                           distance,
                           min_x=0,
                           max_x=None,
                           min_y=0,
                           max_y=None,
                           include_center=True):
    """
    Return all the coords within the given distance of the given coords,
    as long as they are in the given bounds.
    
    Parameters:
        coords (int, int): The coords to measure distance from.
        distance (int): The maximum distance.
        min_x (int): The minimum x-value allowed.
        max_x (int): The maximum x-value allowed.
        min_y (int): The minimum y-value allowed.
        max_y (int): The maximum y-value allowed.
    """
    result = [coords]
    cx, cy = coords
    for d in range(1, distance+1):
        for x in range(0, d):
            y = d - x
            
            result.append((cx + x, cy + y))
            result.append((cx - y, cy + x))
            result.append((cx - x, cy - y))
            result.append((cx + y, cy - x))
    
    if include_center:
        return filter_in_bounds_coords(result, min_x, max_x, min_y, max_y)
    
    result = filter_in_bounds_coords(result, min_x, max_x, min_y, max_y)
    if coords in result:
        result.remove(coords)
    return result

class MoveType(Enum):
    GIVE_ENERGY = 'GIVE_ENERGY'
    GIVE_LIFE = 'GIVE_LIFE'
    HEAL = 'HEAL'
    ATTACK = 'ATTACK'
    MOVE = 'MOVE'
    BUILD = 'BUILD'
    SET_MESSAGE = 'SET_MESSAGE'
    SELF_DESTRUCT = 'SELF_DESTRUCT'

class Direction(Enum):
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    UP = 'UP'
    DOWN = 'DOWN'

OPPOSITE = {Direction.LEFT:Direction.RIGHT,
            Direction.RIGHT:Direction.LEFT,
            Direction.UP:Direction.DOWN,
            Direction.DOWN:Direction.UP}

FIELDS_FROM_MOVE_TYPES = {MoveType.GIVE_ENERGY:(('target_coords', 'coords'),
                                                ('amount', int)),
                          MoveType.GIVE_LIFE:(('target_coords', 'coords'),
                                              ('amount', int)),
                          MoveType.HEAL:tuple([('amount', int)]),
                          MoveType.ATTACK:tuple([('target_coords', 'coords')]),
                          MoveType.MOVE:tuple([('direction', Direction)]),
                          MoveType.BUILD:tuple([('target_coords', 'coords')])}

def check_field_type(field, t):
    if t == 'coords':
        if not isinstance(field, tuple):
            return False
        
        if len(field) != 2:
            return False
        
        if not isinstance(field[0], int):
            return False
        
        if not isinstance(field[1], int):
            return False
        
        return True
    
    return isinstance(field, t)

class Move:
    def __init__(self, move_type, **kwargs):
        self.move_type = move_type
        
        for name, val in kwargs.items():
            self.__setattr__(name, val)
        
        self.valid = True
        self.check_vals()
    
    def check_vals(self):
        # print('')
        # print(str(self.move_type))
        for field, t in FIELDS_FROM_MOVE_TYPES[self.move_type]:
            # print('{}, {}'.format(field, hasattr(self, field)))
            if not hasattr(self, field):
                self.valid = False
                return
            
            if not check_field_type(getattr(self, field), t):
                self.valid = False
                return

#GIVE ENERGY:
#    target_coords: (int, int)
#    amount: int

#GIVE LIFE:
#    target_coords: (int, int)
#    amount: int

#HEAL
#    amount: int

#ATTACK:
#    target_coords: (int, int)

#MOVE:
#    direction: Direction

#BUILD:
#target_coords and other stuff

def coords_in_direction(coords, direction):
    x, y = coords
    
    if direction == Direction.LEFT:
        return (x-1, y)
    elif direction == Direction.RIGHT:
        return (x+1, y)
    elif direction == Direction.UP:
        return (x, y-1)
    elif direction == Direction.DOWN:
        return (x, y+1)
    else:
        raise ValueError('direction: {}'.format(direction))    

def get_direction(c1, c2):
    d = diff(c1, c2)
    
    if d == (1, 0):
        return Direction.RIGHT
    if d == (-1, 0):
        return Direction.LEFT
    if d == (0, 1):
        return Direction.DOWN
    if d == (0, -1):
        return Direction.UP
    
    return None

#the battlefield is zero-indexed
class Battlefield:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.map = dict()
        
        self.bots = list()
        self.bots_from_speeds = dict()
        
        self.edge_view = WallView('edge')
        self.corner_view = WallView('corner')
        
        #Initialize map to an empty list everywhere
        for x in range(self.width):
            for y in range(self.height):
                self.map[x, y] = list()
    
    def has_player_won(self):
        players = list(set([bot.player for bot in self.bots]))
        # print(players)
        return len(players) == 1
    
    def at(self, coords):
        return self.map.get(coords, list())
    
    def of_type_at(self, coords, t):
        items_at = self.at(coords)
        return [i for i in items_at if isinstance(i, t)]
    
    def bots_at(self, coords):
        items_at = self.at(coords)
        return [b for b in items_at if isinstance(b, Bot)]
    
    def get_items(self):
        return sum(self.map.values(), [])
    
    def get_bots(self):
        return self.bots.copy()
    
    def add_item(self, item):
        """
        Add the given item to the map.
        """
        
        if not item.coords in self.map:
            raise ValueError('item.coords: {}'.format(item.coords))
        
        if isinstance(item, Bot):
            return self.add_bot(item)
        
        self.map[item.coords].append(item)
    
    def remove_item(self, item, should_have=True):
        if isinstance(item, Bot):
            return self.remove_bot(item)
        
        items_there = self.at(item.coords)
        if not item in items_there:
            if should_have:
                print('item not in map: {}'.format(item))
            return
        items_there.remove(item)
    
    def add_bot(self, bot):
        if bot in self.bots:
            print('bot already in self.bots: {}'.format(bot))
            return
            
        if not bot.coords in self.map:
            raise ValueError('bot.coords: {}'.format(bot.coords))
        
        if hasattr(self, 'game_manager'):
            self.game_manager.handle_add_bot(bot)
        
        self.bots.append(bot)
        self.map[bot.coords].append(bot)
        
        speed = bot.speed
        
        if not speed in self.bots_from_speeds:
            self.bots_from_speeds[speed] = list()
            
        self.bots_from_speeds[speed].append(bot)
    
    def remove_bot(self, bot, should_have=True):
        if not bot in self.bots:
            if should_have:
                print('bot not in self.bots: {}'.format(bot))
            return
        
        if hasattr(self, 'game_manager'):
            self.game_manager.handle_remove_bot(bot)
        
        self.bots.remove(bot)
        self.map[bot.coords].remove(bot)
        self.bots_from_speeds[bot.speed].remove(bot)
    
    #invisible bots shouldn't block vision even if they're Tall
    #this is maybe implemented right
    def get_visible_coords(self,
                           bot=None,
                           c_coords=None,
                           s_range=None,
                           curved_s=False):
        """
        Return the coords visible to the given bot.
        
        Parameters:
            bot [Bot]: The bot to return the visible coords of.
        """
        #Start with the robot's square
        #expand outwards in 'straight' lines, not expanding into squares
        #with a Tall bot
        #any line that goes between two points in the minimal distance is
        #straight, even if it turns
        
        center_coords = c_coords if c_coords else bot.coords
        # sight = bot.sight if bot else s_range
        sight = s_range if s_range else bot.sight
        # curved = hasattr(bot, 'curved_sight') if bot else 
        curved = curved_s or hasattr(bot, 'curved_sight')
        
        result = [center_coords]
        outer_coords = [center_coords]
        for _ in range(sight):
            new_coords = set()
            for coords in outer_coords:
                d_coords = diff(center_coords, coords)
                
                directions = list(Direction) if curved else\
                             directions_for_coords(d_coords)
                for d in directions:
                    # print(d)
                    t_coords = coords_in_direction(coords, d)
                    if t_coords in result:
                        continue
                    
                    if not self.is_in_bounds(t_coords):
                        continue
                    bots_at = self.bots_at(t_coords)
                    
                    #If there aren't any bots there, it can be seen into
                    if not bots_at:
                        new_coords.add(t_coords)
                        continue
                    
                    bot_at = bots_at[0]
                    
                    #If the bot is tall, the square can't be seen past
                    #But it can be seen into
                    if hasattr(bot_at, 'tall'):
                        #If the bot would be invisible,
                        #it can still be seen through
                        
                        #If a bot isn't provided,
                        #we assume bot_at is visible
                        if (not bot) or bot_at.view(bot):
                            result.append(t_coords)
                            continue
                    new_coords.add(t_coords)
            
            result.extend(new_coords)
            outer_coords = list(new_coords)
        
        return result
    
    def is_visible_for(self, bot, t_coords, s_range=None, curved_s=None):
        """
        Return whether the given coords are visible for the given bot.
        
        Parameters:
            bot Bot: The bot to check visibility for.
            t_coords (int, int): The coords to check visibility of.
        
        Return:
            bool: Whether the given coords are visible for the given bot.
        """
        #This can be optimized, but it doesn't need to be
        return t_coords in self.get_visible_coords(bot,
                                                   s_range=s_range,
                                                   curved_s=curved_s)
    
    def set_coords(self, item, coords):
        """
        Move the item to the given coords, updating both the item's .coords
        attribute and the map.
        
        Parameters:
            item: The item whose coords to change.
            coords (int, int): The coords to move the item to.
        """
        if not coords in self.map:
            raise ValueError('coords: {}'.format(coords))
        
        old_coords = item.coords
        
        #Sometimes this will happen if a bot that was destroyed has a movement
        #It's easier to deal with it here than there
        if not item in self.at(old_coords):
            return
        
        self.map[old_coords].remove(item)
        self.map[coords].append(item)
        item.coords = coords
    
    def is_in_bounds(self, coords):
        """
        Return whether the given coords are within
        the bounds of this battlefield.
        
        Parameters:
            coords (int, int): The coords to test.
        """
        return is_in_bounds(coords, 0, self.width-1, 0, self.height-1)
    
    def get_wall_view(self, coords):
        """
        Return a list of the appropriate wall view if there is one, else [].
        
        Parameters:
            coords (int, int): The coords to return wall views of.
        
        Return:
            [WallView]: A list with the wall view, or else [].
        """
        x, y = coords
        #This works
        boundaries = sum([x==0, y==0, x==self.width-1, y==self.height-1])
        
        if boundaries == 1:
            return [self.edge_view]
        elif boundaries == 2:
            return [self.corner_view]
        return list()
    
    def test_energys_all_positive(self):
        """
        Raise a ValueError if any bots have negative energy.
        """
        for bot in self.bots:
            if bot.energy < 0:
                raise ValueError('bot with negative energy:\n{}'.format(bot))

class CodeDict:
    def __init__(self):
        self.codes_from_sources = {None:[]}
        self.codes_from_targets = {None:[]}
        self.codes_from_events = {None:[]}
        
        self.codes = list()
    
    def register_for_field(self, code, field, from_field):
        if not field:
            from_field[None].append(code)
        else:
            for f in field:
                if not f in from_field:
                    from_field[f] = [code]
                else:
                    from_field[f].append(code)
    
    def register_code(self, code):
        """
        Register the given code with the CodeDict.
        
        Parameters:
            code Code: The code to register with the CodeDict.
        """
        if code in self.codes:
            return
        
        self.codes.append(code)
        self.register_for_field(code, code.sources, self.codes_from_sources)
        self.register_for_field(code, code.targets, self.codes_from_targets)
        self.register_for_field(code, code.events, self.codes_from_events)
    
    def remove_for_field(self, code, field, from_field):
        if not field:
            from_field[None].remove(code)
        else:
            for f in field:
                from_field[f].remove(code)
    
    def remove_code(self, code):
        """
        Remove the given code from the CodeDict.
        
        Parameters:
            code Code: The code to remove from the CodeDict.
        """
        if not code in self.codes:
            raise ValueError('CodeDict.remove_code({}): {} not in CodeDict'\
                             .format(code, code))
        
        self.codes.remove(code)
        self.remove_for_field(code, code.sources, self.codes_from_sources)
        self.remove_for_field(code, code.targets, self.codes_from_targets)
        self.remove_for_field(code, code.events, self.codes_from_events)
    
    def __iter__(self):
        return self.codes.__iter__()
    
    def __getitem__(self, spec):
        source, target, event = spec
        # print('spec: {}'.format(spec))
        # print('source: {}'.format(source))
        
        from_source = self.codes_from_sources[None].copy()
        # for source in sources:
        from_source.extend(self.codes_from_sources.get(source, []))
        from_source = set(from_source)
        # print('from_source: {}'.format(from_source))
        
        from_target = self.codes_from_targets[None] + \
                      self.codes_from_targets.get(target, [])
        from_target = set(from_target)
        # print('from_target: {}'.format(from_target))
        
        from_event = self.codes_from_events[None] + \
                     self.codes_from_events.get(event, [])
        from_event = set(from_event)
        # print('from_event: {}'.format(from_event))
        # print('')
        
        return list(from_source.intersection(from_target, from_event))

class GameManager:
    def __init__(self, battlefield):
        self.battlefield = battlefield
        
        #This is mildly sketchy
        self.battlefield.game_manager = self
        
        self.waiting_codes = list()
        self.triggered_codes = CodeDict()
        self.replacement_codes = CodeDict()
        self.effects = list()
        
        self.process_funcs = {MoveType.GIVE_ENERGY: self.process_give_energys,
                              MoveType.GIVE_LIFE: self.process_give_lifes,
                              MoveType.HEAL: self.process_heals,
                              MoveType.ATTACK: self.process_attacks,
                              MoveType.MOVE: self.process_moves,
                              MoveType.BUILD: self.process_builds,
                              MoveType.SET_MESSAGE: self.process_set_messages}
    
    def handle_add_bot(self, bot):
        """
        Do what needs to be done when a bot is added to the battlefield.
        This includes registering all the bot's codes,
        and may include more later.
        
        Parameters:
            bot Bot: The bot that was added to the battlefield.
        """
        for code in bot.codes:
            if isinstance(code, builds.ReplacementCode):
                self.replacement_codes.register_code(code)
            else:
                self.triggered_codes.register_code(code)
    
    def handle_remove_bot(self, bot):
        """
        Do what needs to be done when a bot is removed from the battlefield.
        This includes removing all the bot's codes,
        and may include more later.
        
        Parameters:
            bot Bot: The bot that was removed from the battlefield.
        """
        for code in bot.codes:
            if isinstance(code, builds.ReplacementCode):
                self.replacement_codes.remove_code(code)
            else:
                self.triggered_codes.remove_code(code)
    
    def give_bots_info(self):
        """
        Give all bots their turn's information by calling their give_view()
        methods.
        """
        for bot in self.battlefield.bots:
            visible_coords = self.battlefield.get_visible_coords(bot)
            view = dict()
            for coords in visible_coords:
                # view[coords] = list()
                # view[coords] = self.battlefield.get_wall_view(coords)
                #Now view is {(int, int): {str: item_view}}
                #instead of  {(int, int): [item_view]}
                view[coords] = dict()
                wall_view = self.battlefield.get_wall_view(coords)
                if wall_view:
                    view[coords]['Wall'] = wall_view[0]
                    
                for item in self.battlefield.at(coords):
                    item_view = item.view(bot)
                    #If item_view == None, it's invisible
                    if item_view:
                        # view[coords].append(item_view)
                        view[coords][item_view.type] = item_view
            
            bot.give_view(view)
    
    def get_bots_moves(self):
        """
        Return all the bots' moves.
        
        Return:
            moves {MoveType: {Bot: [Move]}}
        """
        all_moves = dict()
        for bot in self.battlefield.bots:
            # try:
            all_moves[bot] = bot.get_moves()
            # except Exception as err:
            #     #If the bot's get_moves() method throws an exception,
            #     #The bot just doesn't do anything
            #     print('')
            #     print(type(err))
            #     print(repr(err))
            #     print('bot threw exception {}:\n{}'.format(err, bot))
            #     all_moves[bot] = dict()
        
        result = {t:dict() for t in MoveType}
        
        for bot, moves in all_moves.items():
            for move_type in moves:
                moves_of_type = moves[move_type]
                valid_moves = [m for m in moves_of_type if m.valid]
                result[move_type][bot] = valid_moves
        
        return result
    
    def register_triggered_code(self, code):
        self.triggered_codes.register_code(code)
    
    def register_replacement_code(self, code):
        self.replacement_codes.register_code(code)
    
    def register_effect(self, effect):
        """
        Register the given effect into self.effects.
        
        Parameters:
            effect Effect: The effect to register.
        """
        self.effects.append(effect)
    
    def check_replacement_codes(self, effect):
        """
        Trigger the first replacement code that fits, or none if none fit.
        
        Parameters:
            effect Effect: The effect to trigger replacement codes for.
        
        Return:
            bool: Whether any replacement codes were triggered.
        """
        spec = (effect.source, effect.target, type(effect))
        replacements = self.replacement_codes[spec]
        
        fitting_replacements = [r for r in replacements if r.fits(effect)]
        
        possible_replacements = [r for r in fitting_replacements\
                                 if not r in effect.replacement_codes]
        
        if not possible_replacements:
            return False
            
        possible_replacements.sort(key=lambda x: x.priority)
        
        replacement = possible_replacements[0]
        replacement.trigger(self, effect)
        return True
        
        # for replacement in replacements:
        #     if replacement.fits(effect):
        #         #An effect can only be replaced once
        #         #by each replacement code
        #         # print('replacement_codes: {}'.format(effect.replacement_codes))
        #         if not replacement in effect.replacement_codes:
        #             replacement.trigger(self, effect)
        #             return True
        # return False
    
    def check_triggered_codes(self, effect):
        """
        Trigger all triggered code that fit.
        
        Parameters:
            effect Effect: The effect to trigger triggered codes for.
        
        """
        spec = (effect.source, effect.target, type(effect))
        triggereds = self.triggered_codes[spec]
        for triggered in triggereds:
            if triggered.fits(effect):
                triggered.trigger(self, effect)
    
    def resolve_effects(self):
        """
        Resolve all the effects in self.effects, first checking for replacement
        code and then for triggered code.
        """
        #I can't do a normal for loop because effects might be added
        while self.effects:
            effect = self.effects[0]
            del self.effects[0]
            
            #Check for replacement codes, and if any trigger
            #don't resolve the effect
            if self.check_replacement_codes(effect):
                continue
            
            effect.resolve(self)
            
            self.check_triggered_codes(effect)
    
    def supply_energy(self):
        """
        Give energy to all bots on coords with an EnergySource.
        """
        #Give energy to bots on energy sources
        for coords, items in self.battlefield.map.items():
            sources = [i for i in items if isinstance(i, EnergySource)]
            if not sources:
                continue
            
            bots = [i for i in items if isinstance(i, Bot)]
            if not bots:
                continue
            
            es = sources[0]
            bot = bots[0]
            # effect = eff.GiveEnergyEffect([es], bot, es.amount)
            effect = eff.GiveEnergyEffect(es, bot, es.amount)
            self.register_effect(effect)
        self.resolve_effects()
    
    def newturns(self):
        """
        Call the new_turn function for all triggered and replacement codes.
        """
        for code in self.replacement_codes:
            code.new_turn(self)
        for code in self.triggered_codes:
            code.new_turn(self)
        
        for bot in self.battlefield.bots:
            bot.new_turn(self)
    
    def upkeep(self):
        """
        Perform upkeep tasks, like giving energy to bots on energy sources.
        """
        self.supply_energy()
        self.newturns()
        self.resolve_effects()
    
    # def is_in_range(self, coords, bot, r):
    #     return self.b
    
    def process_give_energys(self, moves_from_bots):
        """
        Process the GIVE_ENERGY moves.
        
        Parameters:
            moves_from_bots {Bot: [Move]}: The GIVE_ENERGY moves to process.
        """
        
        #All the bots that might end up with negative total energy
        possible_negatives = []
        for bot, moves in moves_from_bots.items():
            if not moves:
                continue
            if hasattr(bot, 'no_give_energy'):
                print('no_give_energy bot:\n{}'.format(bot))
                continue
            
            move = moves[0]
            
            # try:
                # m_dir = move.direction
            t_coords = move.target_coords
            r = bot.give_energy_range if hasattr(bot, 'give_energy_range') else 1
            
            #If the targeted square isn't in range, don't do the move
            if not self.battlefield.is_visible_for(bot, t_coords, s_range=r):
                continue
            # print('move.move_type: {}'.format(move.move_type))
            # print('move.valid: {}'.format(move.valid))
            m_amount = move.amount
            # except Exception as err:
            #     print('exception when processing GIVE_ENERGY move:')
            #     print(err)
            #     continue
            
            # t_coords = coords_in_direction(bot.coords, m_dir)
            
            items_at = self.battlefield.at(t_coords)
            targeted_bots = [b for b in items_at if isinstance(b, Bot)]
            if not targeted_bots:
                continue
            
            targeted_bot = targeted_bots[0]
            amount = m_amount
            
            #Check whether the transfers were valid later
            #this allows transfers to be chained
            bot.energy -= amount
            targeted_bot.energy += amount
            
            if bot.energy < 0:
                possible_negatives.append(bot)
        
        while possible_negatives:
            bot = possible_negatives[0]
            del possible_negatives[0]
            
            moves = moves_from_bots[bot]
            if not moves:
                continue
            move = moves[0]
            
            if bot.energy >= 0:
                continue
            
            t_coords = coords_in_direction(bot.coords, move.direction)
            
            targeted_bots = self.battlefield.bots_at(t_coords)
            
            if not targeted_bots:
                #At this point, the bot isn't giving energy to any bots,
                #but its energy is still negative, which is unacceptable
                raise ValueError('bot.energy: {}'.format(bot.energy))
            
            #Undo just enough energy transfer so that the bot ends up with
            #positive energy
            targeted_bot = targeted_bots[0]
            undo_amount = -bot.energy
            # amount = move.amount
            
            bot.energy += undo_amount
            targeted_bot.energy -= undo_amount
            
            #Now maybe the targeted bot has negative total energy,
            #so any transfers it did will also need to be undone
            if targeted_bot.energy < 0:
                possible_negatives.append(targeted_bot)
        
        self.battlefield.test_energys_all_positive()
    
    def process_give_lifes(self, moves_from_bots):
        """
        Process all the GIVE_LIFE orders.
        
        Parameters:
            moves_from_bots {Bot: [Move]}: All the GIVE_LIFE orders.
        """
        
        for bot, moves in moves_from_bots.items():
            if not moves:
                continue
            if bot.energy == 0:
                continue
            if not hasattr(bot, 'heal'):
                print('no heal bot:\n{}'.format(bot))
                continue
            
            move = moves[0]
            
            # try:
                # m_dir = move.direction
            t_coords = move.target_coords
            
            r = bot.give_life_range if hasattr(bot, 'give_life_range') else 1
            
            #If the targeted square isn't in range, don't do the move
            if not self.battlefield.is_in_range(bot, t_coords, s_range=r):
                continue
            
            amount = move.amount
            # except Exception as err:
            #     print('exception when processing GIVE_LIFE move:')
            #     print(err)
            #     continue
            
            # t_coords = coords_in_direction(bot.coords, move.direction)
            targeted_bots = self.battlefield.bots_at(t_coords)
            
            if not targeted_bots:
                continue
            
            targeted_bot = targeted_bots[0]
            # amount = move.amount
            
            #You can only heal by as much energy as you have
            amount = min(amount, bot.energy)
            
            #You can also only heal by as much damage as the healed bot has
            amount = targeted_bot.increase_hp(amount)
            
            bot.energy -= amount
        
        self.battlefield.test_energys_all_positive()
    
    def process_heals(self, moves_from_bots):
        """
        Process all the HEAL orders given.
        
        Parameters:
            moves_from_bots {Bot: [Move]}: All the HEAL orders to process.
        """
        
        for bot, moves in moves_from_bots.items():
            if not moves:
                continue
            if bot.energy == 0:
                continue
            if not hasattr(bot, 'heal'):
                # print('no heal bot:\n{}'.format(bot))
                continue
            
            move = moves[0]
            amount = move.amount
            
            #You can only heal by how much energy you have,
            #and also only by how much damage you have
            amount = min(amount, bot.energy, bot.get_stat('max_hp') - bot.hp)
            bot.increase_hp(amount)
            bot.energy -= amount
        
        self.battlefield.test_energys_all_positive()
    
    def process_attacks(self, moves_from_bots):
        """
        Process all the attack moves given.
        
        Parameters:
            attacks {Bot: [Move]}: All the ATTACK moves to process.
        """
        if not moves_from_bots:
            return
        
        #all bots can attack, some just have zero power
        #so there's no need to check whether bots can attack
        speeds = list(set([b.speed for b in moves_from_bots]))
        speeds.sort(reverse=True)
        
        bots_from_speeds = {s:[] for s in speeds}
        
        for bot in moves_from_bots:
            bots_from_speeds[bot.speed].append(bot)
        
        for speed in speeds:
            # print('speed: {}'.format(speed))
            attacked_coords = list()
            for bot in bots_from_speeds[speed]:
                if not bot in self.battlefield.bots:
                    continue
                
                moves = moves_from_bots[bot]
                if not moves:
                    continue
                
                move = moves[0]
                
                tc = move.target_coords
                if not self.battlefield.is_visible_for(bot, tc):
                    #Only do the attack if the target is in line-of-sight
                    continue
                
                attacked_coords.append(tc)
                
                attack_effect = eff.AttackEffect(bot, tc, bot.power)
                self.register_effect(attack_effect)
            
            self.resolve_effects()
    
    # def bots_with_move_order(self, moves_from_bots, i):
    #     """
    #     Return all the bots that still have move orders.
        
    #     Parameters:
    #         moves_from_bots {bot: [Move]}: All the MOVE moves.
    #         i: The movement step to check.
        
    #     Return:
    #         [Bot]: All the bots that still have movement orders left.
    #     """
        
    #     return [b for b, m in moves_from_bots.items() if len(m) > i]
        
    #     # result = list()
        
    #     # for bot, moves in moves_from_bots.items():
    #     #     if len(moves) > i:
    #     #         result.append(bot)
    #     # return result
    
    def do_one_move_round(self, bots, moves_from_bots, i):
        """
        Do one round of movement.
        
        Parameters:
            bots [Bot]: All the bots to do moves for.
            moves_from_bots {bot: [Move]}: All the MOVE moves to do.
            i int: The movement step to do.
        Return:
            [Bot]: All the bots that had movement orders left
            [Bot]: All the bots that moved
            [(int, int)]: All the coords with multiple bots
        """
        
        had_orders = list()
        moved = list()
        cramped = set()
        
        for bot, moves in moves_from_bots.items():
            #The bot has no more move orders left
            if not len(moves) > i:
                continue
            
            #The bot has no more movement left
            if not bot.movement > i:
                continue
            
            had_orders.append(bot)
            move = moves[i]
            
            t_coords = coords_in_direction(bot.coords, move.direction)
            
            #If the robot is trying to move out of bounds, it can't
            if not self.battlefield.is_in_bounds(t_coords):
                continue
            
            bots_at = self.battlefield.bots_at(t_coords)
            
            #If the bot would be moving into another bot
            #that would be moving into it, it doesn't move
            if bots_at:
                other_bot = bots_at[0]
                if other_bot in moves_from_bots and not other_bot in moved:
                    other_moves = moves_from_bots[other_bot]
                    if len(other_moves) > i:
                        other_move = other_moves[i]
                        other_t_coords = coords_in_direction(other_bot.coords,
                                                             other_move.direction)
                        if other_t_coords == bot.coords:
                            #It's a head-on move
                            #So bot doesn't move
                            continue
            
            #The bot can move
            moved.append(bot)
            self.battlefield.set_coords(bot, t_coords)
            if len(self.battlefield.bots_at(t_coords)) > 1:
                cramped.add(t_coords)
            
        return had_orders, moved, list(cramped)
    
    def undo_failed_moves(self, old_coords, cramped_coords, moved):
        while cramped_coords:
            cramped = cramped_coords[0]
            del cramped_coords[0]
            
            bots_at = self.battlefield.bots_at(cramped)
            moved_at = [b for b in bots_at if b in moved]
            
            to_move_back = list()
            
            #If one of the bots in this square didn't move,
            #All the ones that moved need to leave
            if len(moved_at) < len(bots_at):
                # to_move_back = moved_at.copy()
                to_move_back.extend(moved_at)
            else:
                #All the bots at this square moved
                #If one is faster than all the others, only the others leave
                #Otherwise, all the bots leave
                
                max_speed = max([b.speed for b in moved_at])
                fastest_bots = [b for b in moved_at if b.speed == max_speed]
                
                if len(fastest_bots) == 1:
                    fastest_bot = fastest_bots[0]
                    to_move_back = list([b for b in moved_at if b != fastest_bot])
                    # print('{} there,  moving back: {} at {}'.format(len(bots_at), len(to_move_back), cramped))
                else:
                    # to_move_back = moved_at.copy()
                    to_move_back.extend(moved_at)
            
            for bot in to_move_back:
                old_c = old_coords[bot]
                self.battlefield.set_coords(bot, old_c)
                moved.remove(bot) #Now this bot hasn't moved
                if len(self.battlefield.bots_at(old_c)) > 1:
                    cramped_coords.append(old_c)
    
    def test_none_cramped(self):
        for coords in self.battlefield.map:
            bots_at = self.battlefield.bots_at(coords)
            if len(bots_at) > 1:
                print('{} cramped with {} bots'.format(coords, len(bots_at)))
                raise AssertionError()
    
    #I think this isn't working
    #I'll need to fix it
    #It seems to let bots end up in the same place
    def process_moves(self, moves_from_bots):
        """
        Process the movement orders.
        Algorithm: first assume all succeed (except for head-on ones), and then
        undo unsuccessfull moves.
        
        Bots with higher speed have priority for movement.
        
        Parameters:
            moves_from_bots {Bot: [Move]}: All the MOVE moves to process.
        """
        # return #Testing
        #For multiple moves:
        #first do each bot's first move, then each second move, etc.
        #bots w\ higher speed have priority
        
        moving_bots = list(moves_from_bots)
        i = 0
        # moving_bots = self.bots_with_move_order(moves_from_bots, i)
        
        while moving_bots:
            old_coords = {b:b.coords for b in moving_bots}
            
            had_orders, moved, cramped = self.do_one_move_round(moving_bots,
                                                                moves_from_bots,
                                                                i)
            
            self.undo_failed_moves(old_coords, cramped, moved)
            self.test_none_cramped()
            
            moving_bots = [b for b in moving_bots if b in had_orders]
            
            i += 1
            
        #For each set of moves:
        #first, move each bot to the spot it's moving to
        #then, where two bots are in the same square, undo
        #one or both moves
        #continue until no bots are in same square
        
        # moving_bots = list(moves_from_bots)
        
        # i = 0
        # while(moving_bots):
        #     #Only bots that successfully move (the first try) get put here
        #     #so the only ones that don't are ones in head-on collisions
        #     already_moved = list()
            
        #     not_moving = list()
        #     moved_this_time = list()
            
        #     #First move all the bots
        #     for bot in moving_bots:
        #         moves = moves_from_bots[bot]
                
        #         if len(moves) <= i:
        #             not_moving.append(bot)
        #             continue
        #         #Check if the bot has enough movement
        #         if bot.movement <= i:
        #             not_moving.append(bot)
        #             continue
                
        #         move = moves[i]
        #         direction = move.direction
        #         new_coords = coords_in_direction(bot.coords, direction)
                
        #         #Check if this is in bounds
        #         if not self.battlefield.is_in_bounds(new_coords):
        #             not_moving.append(bot)
        #             continue
                
        #         #Check if this is a head-on move
        #         bots_at = self.battlefield.bots_at(new_coords)
                
        #         unmoved_at = [b for b in bots_at if not b in already_moved]
        #         if(unmoved_at):
        #             #There's an unmoved bot in the destination coords
        #             other_bot = unmoved_at[0]
                    
        #             other_moves = moves_from_bots.get(other_bot, list())
        #             if len(other_moves) > i:
        #                 #The bot is about to move
        #                 other_move = other_moves[i]
        #                 other_dir = other_move.direction
                        
        #                 other_dest = coords_in_direction(new_coords, other_dir)
                        
        #                 if other_dest == bot.coords:
        #                     #There's a head-on 
        #                     #So this movement fails
        #                     not_moving.append(bot)
        #                     continue
        #             else:
        #                 #The other bot isn't about to move, so you can't
        #                 #move into its square
        #                 not_moving.append(bot)
        #                 continue
                
        #         self.battlefield.set_coords(bot, new_coords)
        #         already_moved.append(bot)
        #         moved_this_time.append(bot)
            
        #     #We don't need this one to be accurate now
        #     #Because I just use moved_this_time to resolve conflicts
        #     #But I'll do it anyways
        #     for bot in not_moving:
        #         moving_bots.remove(bot)
            
        #     #Then undo unsuccessful moves
        #     packed_coords = set()
        #     for bot in moving_bots:
        #         num_bots_at = len(self.battlefield.bots_at(bot.coords))
                
        #         if(num_bots_at >= 2):
        #             packed_coords.add(bot.coords)
            
        #     #TODO store the old coords for bots instead of calculating them
        #     #it seems like the calculation might sometimes go wrong
            
        #     packed_coords = list(packed_coords)
        #     while packed_coords:
        #         packed_coord = packed_coords[0]
        #         del packed_coords[0]
                
        #         bots_at = self.battlefield.bots_at(packed_coord)
        #         moved_bots = [b for b in bots_at if b in moved_this_time]
                
        #         move_back = moved_bots.copy()
        #         #All the bots in this square moved
        #         if len(bots_at) == len(moved_bots):
        #             if moved_bots:
        #                 max_speed = max([b.speed for b in moved_bots])
        #                 fastest_bots = [b for b in moved_bots if b.speed == max_speed]
                        
        #                 #If one bot is faster than all the others (no ties)
        #                 if len(fastest_bots) == 1:
        #                     fastest_bot = fastest_bots[0]
                            
        #                     #One bot is faster than all the others
        #                     #So only move the slower bots back to their original spaces
        #                     move_back = [b for b in moved_bots if b != fastest_bot]
                
        #         for bot in move_back:
        #             coords = bot.coords
        #             direction = moves_from_bots[bot][i].direction
        #             old_coords = coords_in_direction(coords, OPPOSITE[direction])
        #             self.battlefield.set_coords(bot, old_coords)
                    
        #             #Check if this spot is crowded now
        #             if not coords in packed_coords:
        #                 bots_at = self.battlefield.bots_at(old_coords)
                        
        #                 if len(bots_at) >= 2:
        #                     packed_coords.append(coords)
                
        #     i += 1
    
    def process_builds(self, moves_from_bots):
        """
        Process the build orders.
        
        Parameters:
            moves_from_bots {Bot: [Move]}: All the build orders to process.
        """
        
        for bot, moves in moves_from_bots.items():
            if not moves:
                continue
            
            if hasattr(bot, 'no_build'):
                continue
            
            move = moves[0]
            
            try:
                t_coords = move.coords
                r = bot.build_range if hasattr(bot, 'build_range') else 1
                if not self.battlefield.is_visible_for(bot, t_coords, s_range=r):
                    continue
                
                if self.battlefield.bots_at(t_coords):
                    #Can't build a bot where there already is a bot
                    continue
                
                if move.cost > bot.energy:
                    #The bot cannot afford the build, so it doesn't happen
                    continue
                
                #Make a new controller of the same type
                #real controllers will have inits that don't take arguments
                controller = type(bot.controller)()
            
                new_bot = Bot(t_coords,
                              move.max_hp,
                              move.max_hp,
                              move.power,
                              move.attack_range,
                              move.speed,
                              move.sight,
                              move.energy,
                              move.movement,
                              bot.player,
                              move.message,
                              controller,
                              **move.special_stats_dict)
                
                self.battlefield.add_bot(new_bot)
                
                bot.energy -= move.cost
            except Exception as err:
                print('Exception when processing BUILD move:')
                print(err)
                continue
    
    def process_set_messages(self, moves_from_bots):
        for bot, moves in moves_from_bots:
            if not moves:
                continue
            
            move = moves[0]
            bot.message = move.message
    
    def process_self_destructs(self, moves_from_bots):
        for bot, moves in moves_from_bots:
            if not moves:
                continue
            
            self.battlefield.remove_bot(bot)
    
    def advance(self):
        """
        Advance the game by one turn.
        """
        if self.battlefield.has_player_won():
            print('game over')
            return False
        
        # self.ready_effects()
        self.upkeep()
        self.give_bots_info()
        
        moves = self.get_bots_moves()
        
        for move_type, moves_from_bots in moves.items():
            
            if not moves_from_bots:
                continue
            
            self.process_funcs[move_type](moves_from_bots)
            self.resolve_effects()
        
        return True

import builds

OVERRIDABLE = ('increase_hp',
               'decrease_hp',
               'change_hp',
               'take_damage',
               'is_dead',
               'view',
               'give_view',
               'get_moves')

BASE_STATS = ('max_hp',
              'power',
              'attack_range',
              'speed',
              'sight',
              'movement')

class ModifierManager:
    """
    Keeps track of modifiers to base stats.
    
    For each base stat, there can be any modifier-sources, each with one
    modifier amount associated with it. The modifier for a base stat is the
    sum of all the modifier amounts for all the modifier-sources.
    """
    def __init__(self, parent_bot):
        self.parent_bot = parent_bot
        self.mods = dict()
        
    def add_mod(self, stat, amount, source):
        """
        Add a modifier.
        
        Parameters:
            stat str: The stat to add a modifier for. Must be in BASE_STATS.
            amount int: The modifier amount to add.
            source obj: The source of the modifier. Can be any object.
        """
        if not stat in BASE_STATS:
            raise ValueError('stat not in BASE_STATS: {}'.format(stat))
        
        if not stat in self.mods:
            self.mods[stat] = dict()
        
        
        for_stat = self.mods[stat]
        if not source in for_stat:
            for_stat[source] = amount
        else:
            for_stat[source] += amount
        
        self.parent_bot.notify_mod_added(stat, amount)
    
    def remove_source(self, source):
        """
        Remove all modifiers with the given source.
        
        Parameters:
            source obj: The source to remove all modifiers for.
        """
        for stat in self.mods:
            for_stat = self.mods[stat]
            if source in for_stat:
                del[for_stat][source]
    
    def __getitem__(self, stat):
        """
        Get the total modifier for the given stat.
        
        Parameters:
            stat str: The stat to get the modifier for. Does not have to be in
                      self.mods. If stat isn't in self.mods, return 0.
        
        Return:
            int: The total modifier for the given stat.
        """
        return sum([m for s, m in self.mods.get(stat, {}).items()])
    
class Bot:
    def __init__(self,
                 coords,
                 max_hp,
                 hp,
                 power,
                 attack_range,
                 speed,
                 sight,
                 energy,
                 movement,
                 player,
                 message,
                 controller,
                 **special_stats_dict):
        
        self._overrides = dict()
        
        self.coords = coords
        self.max_hp = max_hp
        self.hp = max(0, min(self.max_hp, hp))
        self.power = power
        self.attack_range = attack_range
        self.speed = speed
        self.sight = sight
        self.energy = energy
        self.movement = movement
        self.player = player
        self.message = message
        self.controller = controller
        
        self.special_stats_dict = special_stats_dict.copy()
        self.special_stats = list()
        
        #Modifiers to stats
        #effects use these instead of directly changing them
        self.mod_manager = ModifierManager(self)
        
        self.codes = list()
        
        for stat, val in special_stats_dict.items():
            self.__setattr__(stat, val)
            special_stat = builds.STATS_FROM_NAMES[stat](val, self)
            self.special_stats.append(special_stat)
            self.codes.extend(special_stat.get_codes())
            
            #The overrides system allows special stats to modify the behavior
            #of the bot
            #This should let me move more stat code to where the stats are
            #defined
            for name in dir(special_stat):
                if name[0] == '_':
                    continue
                # print('name: {}'.format(name))
                if not name in OVERRIDABLE:
                    continue
                override = getattr(special_stat, name)
                if not callable(override):
                    continue
                if name in self._overrides:
                    print('conflicting override: {}'.format(name))
                self._overrides[name] = override
    
    #__getattr__ is only called if there aren't any matching attributes
    def __getattribute__(self, name):
        if name[0] == '_':
            return super().__getattribute__(name)
        
        if name in self._overrides:
            return self._overrides[name]
        
        return super().__getattribute__(name)
    
    def get_stat(self, stat):
        mod = self.mod_manager[stat]
        return getattr(self, stat) + mod
    
    def notify_mod_added(self, stat, amount):
        if stat == 'max_hp':
            self.hp = min(self.hp, self.get_stat('max_hp'))
    
    def new_turn(self, game_manager):
        for stat in self.special_stats:
            stat.new_turn(game_manager)
    
    def _increase_hp(self, amount):
        """
        Increase the bot.hp by the nonnegative amount given.
        The bot.hp will remain <= bot.get_stat('max_hp').
        
        Parameters:
            amount int: The amount to increase hp by. Must be nonnegative.
        
        Return:
            int: The nonnegative amount that bot.hp actually increase by.
        """
        if amount < 0:
            raise ValueError('amount: {}'.format(amount))
        
        max_hp = self.get_stat('max_hp')
        
        increase = min(self.hp + amount, max_hp) - self.hp
        self.hp += increase
        return increase
    
    #This pattern allows special stats to access the default methods
    #The core methods start with _, so they can't be overridden
    def increase_hp(self, amount):
        return self._increase_hp(amount)
    
    def _decrease_hp(self, amount):
        """
        Decrease the bot.hp by the nonnegative amount given.
        THe bot.hp will remain >= 0.
        
        Parameters:
            amount int: The amount to decrease hp by. Must be nonnegative.
        
        Return:
            int: The nonnegative amount that bot.hp actually decreased by.
        """
        if amount < 0:
            raise ValueError('amount: {}'.format(amount))
        
        decrease = min(self.hp, amount)
        self.hp -= decrease
        
        return decrease
    
    def decrease_hp(self, amount):
        return self._decrease_hp(amount)
    
    def _change_hp(self, amount):
        """
        Change the bot's hp by the given amount.
        It will remain that 0 <= bot.hp <= bot.get_stat(max_hp)
        
        Parameters:
            amount int: The amount to change hp by.
        
        Return:
            int: The amount that bot.hp actually changed by.
        """
        max_hp = self.get_stat('max_hp')
        
        result = self.hp + amount
        result = max(0, min(max_hp, result))
        change = result - self.hp
        self.hp = result
        
        return change
    
    def change_hp(self, amount):
        return self._change_hp(amount)
    
    def _take_damage(self, amount):
        """
        Take the given nonnegative amount of damage.
        
        Parameters:
            amount int: The amount of damage to take. Must be nonnegative.
        
        Return:
            int: The nonnegative amount that bot.hp actually decreased by.
        """
        if amount < 0:
            raise ValueError('amount: {}'.format(amount))
        
        return self.decrease_hp(amount)
    
    def take_damage(self, amount):
        return self._take_damage(amount)
    
    def _is_dead(self):
        """
        Return whether the bot is dead.
        
        Return:
            boolean: Whether the bot is dead.
        """
        return self.hp <= 0
    
    def is_dead(self):
        return self._is_dead()
    
    def _view(self, bot):
        """
        Return the view that will be given to controllers.
        
        Return:
            BotView: The view of the bot that will be given to controllers.
        """
        result = BotView(coords=self.coords,
                         max_hp=self.get_stat('max_hp'),
                         hp=self.hp,
                         power=self.get_stat('power'),
                         attack_range=self.get_stat('attack_range'),
                         speed=self.get_stat('speed'),
                         sight=self.get_stat('sight'),
                         energy=self.energy,
                         movement=self.get_stat('movement'),
                         player=self.player,
                         message=self.message,
                         **self.special_stats_dict)
        
        return result
    
    def view(self, bot):
        return self._view(bot)
    
    def _give_view(self, view):
        """
        Give the controller the view of the battlefield along with this
        bot's coords.
        
        Parameters:
            view {(int, int): [item.view() return]}: The battlefield view.
        """
        self.controller.give_view(view, self.view(self))
    
    def give_view(self, view):
        return self._give_view(view)
    
    def _get_moves(self):
        """
        Return the bot's moves.
        
        Return:
            moves: {MoveType -> [Move]}
        """
        return self.controller.get_moves()
    
    def get_moves(self):
        return self._get_moves()
    
    def __str__(self):
        max_hp = self.get_stat('max_hp')
        attack_range = self.get_stat('attack_range')
        power = self.get_stat('power')
        speed = self.get_stat('speed')
        sight = self.get_stat('sight')
        movement = self.get_stat('movement')
        
        return 'Bot at ({}, {}),\n'.format(self.coords[0], self.coords[1]) + \
               'hp={}, max_hp={},\n'.format(max_hp, self.hp) + \
               'power={}, attack_range={},\n'.format(power, attack_range) + \
               'speed={},\n'.format(speed) + \
               'sight={},\n'.format(sight) + \
               'energy={},\n'.format(self.energy) + \
               'movement={},\n'.format(movement) + \
               'player={},\n'.format(self.player) + \
               'message={}'.format(self.message)

class BotView:
    def __init__(self,
                 coords,
                 max_hp,
                 hp,
                 power,
                 attack_range,
                 speed,
                 sight,
                 energy,
                 movement,
                 player,
                 message,
                 **special_stats):
        
        self.type = 'Bot'
        self.coords = coords
        self.max_hp = max_hp
        self.hp = max(0, min(self.max_hp, hp))
        self.power = power
        self.attack_range = attack_range
        self.speed = speed
        self.sight = sight
        self.energy = energy
        self.movement = movement
        self.player = player
        self.message = message
        
        for stat, val in special_stats.items():
            self.__setattr__(stat, val)
        
        self._initialized = True
    
    def __setattr__(self, name, val):
        if hasattr(self, '_initialized'):
            if name[0] != '_':
                err_message = 'cannot set attr of view: {} {}'.format(name, val)
                raise RuntimeError(err_message)
        
        self.__dict__[name] = val
    
    def __str__(self):
        return 'Bot view at ({}, {}),\n'.format(self.coords[0], self.coords[1]) + \
               'hp={}, max_hp={},\n'.format(self.max_hp, self.hp) + \
               'power={}, attack_range={},\n'.format(self.power, self.attack_range) + \
               'speed={},\n'.format(self.speed) + \
               'sight={},\n'.format(self.sight) + \
               'energy={},\n'.format(self.energy) + \
               'movement={},\n'.format(self.movement) + \
               'player={},\n'.format(self.player) + \
               'message=' + self.message

class EnergySource:
    def __init__(self, coords,amount):
        self.coords = tuple(coords)
        self.amount = amount
        self.cached_view = EnergySourceView(self.coords, self.amount)
    
    def view(self, bot):
        """
        Return the object to be given to the bot code.
        """
        return self.cached_view
    
    def __str__(self):
        return 'Energy Source at ({}, {}), amount={}'\
               .format(self.coords[0], self.coords[1], self.amount)

class EnergySourceView:
    def __init__(self, coords, amount):
        self.type = 'EnergySource'
        self.coords = tuple(coords)
        self.amount = amount
        self._initialized = True
    
    def __setattr__(self, name, val):
        if hasattr(self, '_initialized'):
            if name[0] != '_':
                err_message = 'cannot set attr of view: {} {}'.format(name, val)
                raise RuntimeError(err_message)
        
        self.__dict__[name] = val
    
    def __str__(self):
        return 'Energy Source view at ({}, {}), amount={}'\
               .format(self.coords[0], self.coords[1], self.amount)

#The purpose of this is so that bots will know the boundaries of the field
#It is not the view of any object
class WallView:
    def __init__(self, t):
        self.type = t
        self._initialized = True
    
    def __setattr__(self, name, val):
        if hasattr(self, '_initialized'):
            if name[0] != '_':
                err_message = 'cannot set attr of view: {} {}'.format(name, val)
                raise RuntimeError(err_message)
        
        self.__dict__[name] = val
    
    def __str__(self):
        return self.type