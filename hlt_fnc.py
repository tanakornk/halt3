import random
import logging
from hlt import Position

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
    
def halite_surrounding(game, ship):
    return None
    # cur_pos = ship.position
    # cur_halite = game.game_map[cur_pos].halite_amount
    # surrounding = ship.position.get_surrounding_cardinals()
    # halite_amount = [game.game_map[sr].ihalite_amount for sr in surrounding]

def random_move(game, ship):
    avail_pos = avail_surrounding(game, ship)
    if len(avail_pos) != 0:
        destination = random.choice(avail_pos)
        dir = game.game_map.naive_navigate(ship, destination)
        return ship.move(dir)
    else:
        return ship.stay_still()
    
def random_move_with_condition(game, ship):
    cur_game_map = game.game_map[ship.position]
    cur_halite = cur_game_map.halite_amount
    cur_has_structure = cur_game_map.has_structure
    logging.info('Halite {}, Structure {}'.format(cur_halite,cur_has_structure))
    if cur_halite <= 20:
        random_move(game, ship)
    elif cur_has_structure == True:
        random_move(game, ship)

def build_ship(game, command_queue, last_ship_built):
    command_queue.append(game.me.shipyard.spawn())
    last_ship_built = game.turn_number
