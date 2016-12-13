import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import random
import time
from otherstuff import GetWeight as gw
from otherstuff import DistanceMinimum as dm
from otherstuff import DistanceCalculator as dc
import numpy as np
from collections import namedtuple

Close = namedtuple('Close', 'x y owner strength production')
myID, game_map = hlt.get_init()

import logging
logging.basicConfig(filename='debugging\debug.log',level=logging.DEBUG, filemode = 'w')
logging.debug('initiating new run')

def border_move(borderlen,neighbour,square,weight,dist2,falloff):
#    _, direction = next(((neighbor.strength, direction) for direction, neighbor in enumerate(game_map.neighbors(square)) if neighbor.owner != myID and neighbor.strength < square.strength), (None, None))
#    if direction is not None:
#        return Move(square, direction),
#    _, direction = next(((neighbor.strength, direction) for direction, neighbor in enumerate(game_map.neighbors(square)) for direction2, neighbor2 in enumerate(game_map.neighbors(square)) if neighbor.owner == myID and neighbor2.owner != myID and neighbor2.strength < neighbor.strength + square.strength), (None, None))
#    if direction is not None:
#        return Move(square,STILL), Move(neighbor2,hlt.opposite_cardinal(direction)), neighbor
    planck_weight = weight/(dist2**falloff)
    #for neighbor in neighbour:
        #logging.debug(neighbor)
    #get_there = planck_weight.index(np.argmax(plank_weight))
    get_there = ()
    plan_max = 0
    for i in range(len(planck_weight)):
        for j in range(len(planck_weight[0])):
            if planck_weight[i][j] >= plan_max:
                plan_max = planck_weight[i][j]
                get_there = (i,j)
    #logging.debug(weight)
    #logging.debug(dist2)
    #logging.debug(planck_weight)
    #logging.debug(get_there)
    movedists = []
    neborwait = []
    close = [square for square in game_map if (square.x==get_there[0] and square.y==get_there[1])]
    #logging.debug(close)
    for neighbor in enumerate(game_map.neighbors(square)):
        #logging.debug(neighbor)
        movedists.append(game_map.get_distance(neighbor[1], close[0]))
        neborwait.append(planck_weight[square.x,square.y])
    #logging.debug(movedists)
    for direction, neighbor in enumerate(game_map.neighbors(square)):
        if game_map.get_target(square,np.argmin(movedists)).owner != myID:
            #logging.debug(np.argmin(movedists))
            #logging.debug(np.argmin(movedists))
            if game_map.get_target(square,np.argmin(movedists)).strength < square.strength:
                return Move(square,np.argmin(movedists)),
#return Move(square,STILL),
            elif borderlen > 2:
                for direction2, neighbor2 in enumerate(game_map.neighbors(square)):
                    if neighbor2.owner == myID:
                        if game_map.get_target(square,np.argmin(movedists)).strength < min(square.strength + neighbor2.strength, 255):
                            return Move(neighbor2,hlt.opposite_cardinal(direction2)), Move(square,STILL), neighbor2
                        else:
                            #print('stillin', square, file=open('mvmnt.txt', 'a'))
                            return Move(square, STILL),
        else:
            for direction, neighbor in enumerate(game_map.neighbors(square)):
                if weight[neighbor.x,neighbor.y]==max(neborwait):
                    if neighbor.strength < square.strength and neighbor.owner != myID:
                        return Move(square,direction),
                    elif neighbor.owner != myID:
                        for direction2, neighbor2 in enumerate(game_map.neighbors(square)):
                            if neighbor2.owner == myID:
                                if neighbor.strength < min(square.strength + neighbor2.strength, 255):
                                    if borderlen:
                                        return Move(neighbor2,hlt.opposite_cardinal(direction2)), Move(square,STILL), neighbor2
                                else:
                                    return Move(square, STILL),
    #else: #square.strength < square.production * 5:
    #print('stillend', square, file=open('mvmnt.txt', 'a'))
    return Move(square, STILL),

def territory_move(neighbour,square,border,dist2):
    #logging.debug('territory move called')
    bordfar = []
    if square.strength > square.production*7:
        for bord in border:
            bordfar.append((bord,dist2[bord.x,bord.y]))
    #logging.debug(bordfar)
        close = dm.dist_min(bordfar)[0]
    #logging.debug(close)

        movedists = []
        for neighbor in enumerate(game_map.neighbors(square)):
        #logging.debug(neighbor)
            movedists.append(game_map.get_distance(neighbor[1], close))
        direction = np.argmin(movedists)
        tar_get = game_map.get_target(square,direction)
        #logging.debug(np.argmin(movedists))
        #if square.strength + tar_get.strength > 255:
        #    return Move(square,direction), Move(tar_get, hlt.opposite_cardinal(direction)), tar_get
        #else:
        return Move(square,direction),
    else:
        return Move(square, STILL),

weighter=gw(game_map).weighter
old_map = []
#for square in game_map:
#    old_map.append(square)
dists = dc.get_distance_matrix(game_map.width, game_map.height, 1)
weight , border , territory = gw.mapWeight(weighter,myID, game_map, 0.05, 1.0)
logging.debug(border,territory)
#logging.debug(weight)
hlt.send_init("RuBot v2.0")
while True:
    game_map.get_frame()
    moves = []
    skip_square = []
    skip_territory = []
    t0 = time.time()
    weight, border, territory, weighter = gw.updateWeight(weight, myID, game_map,0.1,1.0)
    #for square in game_map:
    #    if square.owner == myID:
    #        for neighbor in enumerate(game_map.neighbors(square)):
    #            if neighbor.owner != myID:
    #                border.append(square)
    #                break
    #        while square not in border:
    #            territory.append(square)
    #            break
    #logging.debug(weighter)
    y=True
    borderlen = len(border)
    for square in border:
        while square not in skip_square:
            t1 = time.time()
            #logging.debug(weighter[square])
            the_move = border_move(borderlen,weighter[square],square, weight, dists[square.x,square.y,:,:], 2.5)
            if len(the_move) == 3:
                moves.append(the_move[0])
                moves.append(the_move[1])
                skip_square.append(the_move[2])
                #logging.debug('square skipped')
                break
            else:
                moves.append(the_move[0])
                break
    t2 = time.time()
    for square in territory:
        while square not in skip_territory:
            #logging.debug('about to call the territory move')
            the_move = territory_move(weighter[square], square, border, dists[square.x,square.y,:,:])
            if len(the_move) == 3:
                moves.append(the_move[0])
                moves.append(the_move[1])
                skip_territory.append(the_move[2])
                #logging.debug('square skipped')
                break
            else:
                moves.append(the_move[0])
                break
        #moves.append(Move(square,STILL))
    t3 = time.time()
    #moves = [border_move(square) for square in border]
    old_map = []
    for square in game_map:
        old_map.append(square)
    hlt.send_frame(moves)
    logging.debug((t1-t0,t2-t1,t3-t2))
