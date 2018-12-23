#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
import hlt_fnc as hf
from hlt import constants
from hlt import Position, Direction

import random
import logging


# This game object contains the initial game state.
game = hlt.Game()
# Respond with your name.
game.ready("TBot")
ship_status = {}
last_ship_built = 0

players = game.players

max_turn = constants.MAX_TURNS
logging.info('Max turn {}, Max Halite {}'.format(max_turn,constants.MAX_HALITE))

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    turn = game.turn_number
    
    # Show the current stat
    halite_info, total_halite, avg_halite = hf.get_map_info(game_map)
    logging.info('Total halite: {}\nAvg halite: {}'.format(total_halite,avg_halite))
    
    # A command queue holds all the commands you will run this turn.
    command_queue = []

    for ship in me.get_ships():
        logging.info(ship.owner)
        logging.info("Ship {} has {} halite.".format(ship.id,ship.halite_amount))
        hf.check_surrounding(ship)        
        
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"
        
        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                command_queue.append(ship.move(move))
                continue
        elif ship_status[ship.id] == "endgame":
            possible_move = game_map.get_unsafe_moves(ship.position, me.shipyard.position)
            if len(possible_move) > 0:
                command_queue.append(ship.move(possible_move[0]))
            continue
        elif ship.halite_amount >= constants.MAX_HALITE / random.uniform(1,2):
            ship_status[ship.id] = "returning"
        elif max_turn-turn <= 10:
            ship_status[ship.id] = "endgame"
    
    
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            # command_queue.append(hf.random_move_with_condition(game, ship))
            command_queue.append(hf.move_to_max_halite(game, ship, 3))
        else:
            command_queue.append(ship.stay_still())

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.

    max_op_ships_num = max(hf.get_opposite_ships_num(game))
    current_ships_num = len(me.get_ships())
    logging.info("Current ship {}\nMax Opponent ship {}".format(current_ships_num,max_op_ships_num))
    max_ship = max(max_op_ships_num + 1,10) if current_ships_num <= 20 else 20
    ship_building_interval = random.randint(10,40)
    
    if turn == 1:
        hf.build_ship(game, command_queue,last_ship_built)
    elif me.halite_amount >= 3000 and turn - last_ship_built >= ship_building_interval and current_ships_num<= max_ship and not game_map[me.shipyard].is_occupied:
        hf.build_ship(game, command_queue,last_ship_built)
    elif turn <= 50 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        hf.build_ship(game, command_queue,last_ship_built)
        
    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
