#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt import Position

import random
import logging

# Getting all position info
def get_map_info(game_map):
    width = game_map.width
    height = game_map.height
    halite_info = [[0 for j in range(height)] for i in range(width)]
    for i in range(width):
        for j in range(height):
            halite_info[i][j] = game_map[Position(i,j)].halite_amount
    
    total_halite = sum(sum(halite_info,[]))
    max_halite = max(sum(halite_info,[]))
    min_halite = min(sum(halite_info,[]))
    avg_halite = total_halite/(width*height)
    
    return halite_info, total_halite, avg_halite
    

# Check surrounding of ship
def check_surrounding(ship):
    id = ship.id
    cur_pos = ship.position
    logging.info("Ship {} {}".format(id,cur_pos))
    surrounding = cur_pos.get_surrounding_cardinals()
#    for sur_pos in surrounding:
#        logging.info('Ship {} {}'.format(id,sur_pos))
        
        
# Check if there is available position around ship
def avail_surrounding(ship):
    surrounding = ship.position.get_surrounding_cardinals()
    is_occupied = [game.game_map[sr].is_occupied for sr in surrounding]
    is_enemy = [(game.game_map[sr].ship.owner != game.me.id if game.game_map[sr].ship != None else False) for sr in surrounding]
    avail_pos = []
    for i in range(len(surrounding)):
        logging.info(is_enemy[i])
        if is_occupied[i] == False or is_enemy == True:
            avail_pos.append(surrounding[i])
    return avail_pos
    
def halite_surrounding(ship):
    cur_pos = ship.position
    cur_halite = game.game_map[cur_pos].halite_amount
    surrounding = ship.position.get_surrounding_cardinals()
    halite_amount = [game.game_map[sr].ihalite_amount for sr in surrounding]


#def log_avail_surrounding(ship):
#    avail_pos = avail_surrounding(ship)
#    pos_str = ''
#    for pos in avail_pos:
#        pos_str += pos+' '
#    logging.info('Ship {} avail {}'.format(ship.id,pos_str))

def random_move(ship):
    avail_pos = avail_surrounding(ship)
    if len(avail_pos) != 0:
        destination = random.choice(avail_pos)
        dir = game.game_map.naive_navigate(ship, destination)
        return ship.move(dir)
    else:
        return ship.stay_still()
    
def random_move_with_condition(ship):
    cur_game_map = game.game_map[ship.position]
    cur_halite = cur_game_map.halite_amount
    cur_has_structure = cur_game_map.has_structure
    logging.info('Halite {}, Structure {}'.format(cur_halite,cur_has_structure))
    if cur_halite <= 20:
        random_move(ship)
    elif cur_has_structure == True:
        random_move(ship)

def build_ship(command_queue,last_ship_built):
    command_queue.append(game.me.shipyard.spawn())
    last_ship_built = game.turn_number


# This game object contains the initial game state.
game = hlt.Game()
# Respond with your name.
game.ready("MyPythonBot")
ship_status = {}
last_ship_built = 0;

players = game.players

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    turn = game.turn_number
    
    # Show the current stat
    halite_info, total_halite, avg_halite = get_map_info(game_map)
    logging.info('Total halite: {}\nAvg halite: {}'.format(total_halite,avg_halite))
    
#    shipyards_position = [[sy.owner,sy.id,sy.position] for sy in shipyard]
#    logging.info(shipyard_position)

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    for ship in me.get_ships():
        logging.info(ship.owner)
        logging.info("Ship {} has {} halite.".format(ship.id,ship.halite_amount))
        check_surrounding(ship)
#        log_avail_surrounding(ship)
        
        
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"
        
        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                command_queue.append(ship.move(move))
                continue
        elif ship.halite_amount >= constants.MAX_HALITE / 2:
            ship_status[ship.id] = "returning"
        elif turn >= 400:
            ship_status[ship.id] = "returning"
    
    
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            command_queue.append(random_move(ship))

#                ship.move(random.choice(["n", "s", "e", "w"])))
        else:
            command_queue.append(ship.stay_still())

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
#    if game.turn_number > 1 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and len(me.get_ships()) < 5:
#        command_queue.append(game.me.shipyard.spawn())
        
    if turn == 1:
        build_ship(command_queue,last_ship_built)
    elif me.halite_amount >= 3000 and turn - last_ship_built >= 20 and len(me.get_ships())<= 8 and not game_map[me.shipyard].is_occupied:
        build_ship(command_queue,last_ship_built)
    elif turn <= 50 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        build_ship(command_queue,last_ship_built)
        
    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
