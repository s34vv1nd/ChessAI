import copy
from chessprocesssing import *


class GamePosition:
    def __init__(self, board, player, castling_rights, enp_target, HMC, history={}):
        self.board = board
        self.player = player
        self.castling = castling_rights
        self.EnP = enp_target
        self.HMC = HMC
        self.history = history

    def getboard(self):
        return self.board

    def setboard(self, board):
        self.board = board

    def getplayer(self):
        return self.player

    def setplayer(self, player):
        self.player = player

    def getCastleRights(self):
        return self.castling

    def setCastleRights(self, castling_rights):
        self.castling = castling_rights

    def getEnP(self):
        return self.EnP

    def setEnP(self, EnP_Target):
        self.EnP = EnP_Target

    def getHMC(self):
        return self.HMC

    def setHMC(self, HMC):
        self.HMC = HMC

    def checkRepition(self):
        return any(value >= 3 for value in self.history.values())

    def addtoHistory(self, position):
        key = pos2key(position)
        self.history[key] = self.history.get(key, 0) + 1

    def gethistory(self):
        return self.history

    def clone(self):
        clone = GamePosition(copy.deepcopy(self.board),
                             self.player,
                             copy.deepcopy(self.castling),
                             self.EnP,
                             self.HMC)
        return clone
