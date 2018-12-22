#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
import hlt_fnc as hf
from hlt import constants
from hlt import Position

import random
import logging


# This game object contains the initial game state.
game = hlt.Game()
# Respond with your name.
game.ready("TBot")
ship_status = {}
last_ship_built = 0

players = game.players

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
    
#    shipyards_position = [[sy.owner,sy.id,sy.position] for sy in shipyard]
#    logging.info(shipyard_position)

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    for ship in me.get_ships():
        logging.info(ship.owner)
        logging.info("Ship {} has {} halite.".format(ship.id,ship.halite_amount))
        hf.check_surrounding(ship)
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
            command_queue.append(hf.random_move(game, ship))

#                ship.move(random.choice(["n", "s", "e", "w"])))
        else:
            command_queue.append(ship.stay_still())

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
#    if game.turn_number > 1 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and len(me.get_ships()) < 5:
#        command_queue.append(game.me.shipyard.spawn())
        
    if turn == 1:
        hf.build_ship(game, command_queue,last_ship_built)
    elif me.halite_amount >= 3000 and turn - last_ship_built >= 20 and len(me.get_ships())<= 8 and not game_map[me.shipyard].is_occupied:
        hf.build_ship(game, command_queue,last_ship_built)
    elif turn <= 50 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        hf.build_ship(game, command_queue,last_ship_built)
        
    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
