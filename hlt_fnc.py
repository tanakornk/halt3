import random
import logging
from hlt import Position
from operator import itemgetter

# Getting all position info
def get_map_info(game_map):
    width = game_map.width
    height = game_map.height
    halite_info = [[0 for j in range(height)] for i in range(width)]
    for i in range(width):
        for j in range(height):
            halite_info[i][j] = game_map[Position(i,j)].halite_amount
    
    total_halite = sum(sum(halite_info,[]))
    # max_halite = max(sum(halite_info,[]))
    # min_halite = min(sum(halite_info,[]))
    avg_halite = total_halite/(width*height)
    
    return halite_info, total_halite, avg_halite
    
# Check surrounding of ship
def check_surrounding(ship):
    id = ship.id
    cur_pos = ship.position
    logging.info("Ship {} {}".format(id,cur_pos))
    # surrounding = cur_pos.get_surrounding_cardinals()
              
# Check if there is available position around ship
def avail_surrounding(game, ship):
    surrounding = ship.position.get_surrounding_cardinals()
    is_occupied = [game.game_map[sr].is_occupied for sr in surrounding]
    is_enemy = [(game.game_map[sr].ship.owner != game.me.id if game.game_map[sr].ship != None else False) for sr in surrounding]
    avail_pos = []
    for i in range(len(surrounding)):
        logging.info(is_enemy[i])
        if is_occupied[i] == False or is_enemy == True:
            avail_pos.append(surrounding[i])
    return avail_pos
    
def surrounding_halite(game, ship, size):
    cur_position = ship.position
    sur_positions = [Position(cur_position.x+x, cur_position.y+y) for x in range(-size,size+1) for y in range(-size,size+1)]
    sur_halites = [game.game_map[pos].halite_amount for pos in sur_positions]
    surrounding = [(sur_positions[i], sur_halites[i]) for i in range(len(sur_positions))]
    return surrounding

def move_to_max_halite(game, ship, size):
    surrounding = surrounding_halite(game, ship, size)
    ranked_positions = sorted(surrounding, key=itemgetter(1), reverse=True)
    for pos in ranked_positions:
        if game.game_map[pos[0]].is_empty:
            direction = game.game_map.naive_navigate(ship, pos[0])
            break
    return ship.move(direction)

def random_move(game, ship):
    avail_pos = avail_surrounding(game, ship)
    if len(avail_pos) != 0:
        destination = random.choice(avail_pos)
        direction = game.game_map.naive_navigate(ship, destination)
        return ship.move(direction)
    else:
        return ship.stay_still()
    
def random_move_with_condition(game, ship):
    cur_game_map = game.game_map[ship.position]
    cur_halite = cur_game_map.halite_amount
    cur_has_structure = cur_game_map.has_structure
    logging.info('Halite {}, Structure {}'.format(cur_halite,cur_has_structure))
    if cur_halite <= 10 or cur_has_structure == True:
        return random_move(game, ship)
    else:
        return ship.stay_still()

def build_ship(game, command_queue, last_ship_built):
    command_queue.append(game.me.shipyard.spawn())
    last_ship_built = game.turn_number

def get_opposite_ships_num(game):
    my_id = game.me.id
    ships_num = []
    for player_id in game.players:
        if player_id != my_id:
            ships_num.append(len(game.players[player_id].get_ships()))
    return ships_num
