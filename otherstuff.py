import numpy as np
import logging
logging.basicConfig(filename='debugging\distbug.log',level=logging.DEBUG, filemode ='w')
from collections import defaultdict
class GetWeight(object):

    def __init__(self, game_map):
        self.weighter = defaultdict(list)
        for square in game_map:
            self.weighter[square].append(game_map.neighbors(square))
        y = True
        if y == True:
            for neighbor in enumerate(self.weighter[square][0]):
                logging.debug(neighbor)
            y = False
        #{square: game_map.neighbors(square) for square in game_map}
            # rus a wee sniffer dog so he is, so he was, so it is, heres me

    def mapWeight(weighter,myID, game_map, neutral, splash):
        neutral_site_mult = neutral
        splash_mult = splash
        weight = np.zeros((game_map.width, game_map.height), dtype=float)
        border = []
        territory = []
        #logging.debug('weightcalc started')
        for square in game_map:
            #logging.debug('weightcalc gets to here')
            if square.owner == myID:
                for neighbor in game_map.neighbors(square):
                    if neighbor.owner != myID:
                        border.append(square)
                        break
                while square not in border:
                    territory.append(square)
                    break
            else:

                    #    logging.debug('weightcalc gets to here 2')
                if square.owner != 0:
                    new_strength = square.strength
                    #logging.debug(weighter[square])
                    for neighbor in enumerate(weighter[square][0]):
                        #logging.debug(neighbor)
                        if neighbor[1].owner != myID and neighbor[1].owner != 0:
                            new_strength = new_strength + neighbor.strength
                    weight[square.x,square.y] = square.production/(neutral * (square.strength + 1))
                else:
                    weight[square.x,square.y] = square.production/(neutral * (square.strength + 1))


        #logging.debug('weightcalc finished')
        return weight , border , territory

    def updateWeight(weight, myID, game_map, neutral, splash):
        neutral_site_mult = neutral
        splash_mult = splash
        #newMap=set(gameMap).intersection(gameMap2)
        border = []
        territory = []
        weighter = defaultdict(list)
        #logging.debug(weighter)
        y=True
        for square in game_map:
            weighter[square].append(game_map.neighbors(square))
        weighter2 = weighter
        for square in game_map:
            if square.owner != myID:
                if square.owner != 0:
                    new_strength = square.strength
                    for neighbor in enumerate(weighter[square][0]):
                        #logging.debug(neighbor)
                        if neighbor[1].owner != myID and neighbor[1].owner != 0:
                            new_strength = new_strength + neighbor[1].strength
                    weight[square.x,square.y] = square.production/(neutral * (square.strength + 1))
            else:
                weight[square.x,square.y] = 0.
                #for neighbor in enumerate(weighter[square][0]):
                #    logging.debug(neighbor)
                for neighbor in enumerate(weighter[square][0]):
                    if neighbor[1].owner != myID:
                        border.append(square)
                        break
                while square not in border:
                    territory.append(square)
                    break

        return weight, border, territory, weighter2

class DistanceMinimum(object):
    @classmethod
    def dist_min(self,bordfar):
        minimum = bordfar[0]

        for bord_tup in bordfar:
            if bord_tup[1] < minimum[1]:
                minimum = bord_tup

        return minimum


class DistanceCalculator(object):
    """Stolen entirely from DexGroves -
    Process and return a 4D array giving the distances between
    squares. Indexed by x, y, :, :, will return a 2D array of
    distances that all points lie from the point x, y.
    """

    @classmethod
    def get_distance_matrix(cls, width, height, falloff):
        D = cls.get_base_matrix(width, height, falloff)
        out = np.zeros((width, height, width, height), dtype=float)
        for x in range(width):
            for y in range(height):
                out[x, y, :, :] = cls.offset(D, x, y)
        return out

    @staticmethod
    def get_base_matrix(width, height, falloff):
        dists = np.zeros((width, height), dtype=float)

        for x in range(width):
            for y in range(height):
                min_x = min((x - 0) % width, (0 - x) % width)
                min_y = min((y - 0) % height, (0 - y) % height)
                dists[x, y] = max(min_x + min_y, 1)

        return dists ** falloff

    @staticmethod
    def offset(M, x, y):
        """Offset a matrix by x and y with wraparound.
        Used to position self.dists for other points.
        """

        #logging.debug(thing)
        return np.roll(np.roll(M, x, 0), y, 1)
