import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "RogersIsRisen")
        self.myFood = None
        self.myTunnel = None
    
    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):

        """
        Code below this copied from 82 - 98 of FoodGatherer.py
        Credits give to Nuxoll and whoever made this code
        Credited August 29, 2021 by John Haas
        """
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn

        #the first time this method is called, the food and tunnel locations
        #need to be recorded in their respective instance variables
        if (self.myTunnel == None or True):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if (self.myFood == None or True):
            foods = getConstrList(currentState, None, (FOOD,))
            self.myFood = foods[0]
            #find the food closest to the tunnel
            bestDistSoFar = 1000 #i.e., infinity
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if (dist < bestDistSoFar):
                    self.myFood = food
                    bestDistSoFar = dist
        """
        Code above is copied
        """

        """
        Code below this partially copied from 101 - 103 of FoodGatherer.py
        Credits give to Nuxoll and whoever made this code
        Credited August 29, 2021 by John Haas
        """
        myQueen = myInv.getQueen()
        if(not myQueen.hasMoved and getConstrAt(currentState, myQueen.coords) != None and
                (getConstrAt(currentState, myQueen.coords).type == ANTHILL or 
                getConstrAt(currentState, myQueen.coords).type == FOOD or 
                getConstrAt(currentState, myQueen.coords).type == TUNNEL)):
            if(myQueen.coords[1] != 3 and 
                    getAntAt(currentState, (myQueen.coords[0], myQueen.coords[1] + 1))) == None:
                return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0], myQueen.coords[1] + 1)])
            elif myQueen.coords[1] != 0 and (getAntAt(currentState, (myQueen.coords[0], myQueen.coords[1] - 1)) == None):
                return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0], myQueen.coords[1] - 1)])
            elif myQueen.coords[0] != 0 and (getAntAt(currentState, (myQueen.coords[0] - 1, myQueen.coords[1])) == None):
                return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0] - 1, myQueen.coords[1])])
            elif myQueen.coords[0] != 9 and (getAntAt(currentState, (myQueen.coords[0] + 1, myQueen.coords[1])) == None):
                return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0] + 1, myQueen.coords[1])])
            else:
                return Move(MOVE_ANT, [myQueen.coords], None)
        elif (not myQueen.hasMoved):
            return Move(MOVE_ANT, [myQueen.coords], None)
        """
        Code above is copied
        """

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)

        numWorkers = len(getAntList(currentState, me, (WORKER,)))
        myAnthill = myInv.getAnthill()
        if numWorkers < 3 and getAntAt(currentState, myAnthill.coords) == None and myInv.foodCount > 0:
            print(getAntAt(currentState, myAnthill))
            return Move(BUILD, [myAnthill.coords], WORKER)
        else:
            #print("Number of Workers: " + str(numWorkers))
            #print("ANt")
            pass

       
        """
        Code below copied from 110-125 of FoodGatherer.py
        Credits give to Nuxoll and whoever made this code
        Credited August 29, 2021 by John Haas
        """
        #if the worker has already moved, we're done
        workers = getAntList(currentState, me, (WORKER,))
        for worker in workers:
            if worker.hasMoved:
                continue
            #if the worker has food, move toward tunnel
            if (worker.carrying):
                print(worker.UniqueID)
                print("Toward Tunnel")
                print("Tunnel Coords: " + str(self.myTunnel.coords))
                path = createPathToward(currentState, worker.coords,
                                        self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                print("Path: " + str(path))
                if len(path) == 1:
                    print("Obstruction")
                    possible_movements = listReachableAdjacent(currentState, path[0], 2)
                    if len(possible_movements) != 0:
                        random_number = random.randrange(0, len(possible_movements))
                        return Move(MOVE_ANT, [path[0], possible_movements[random_number]], None)
                #pdb.set_trace()
                return Move(MOVE_ANT, path, None)
                
            #if the worker has no food, move toward food
            if(not worker.carrying):
                print(worker.UniqueID)
                print("Toward food")
                print("Food Coords: " + str(self.myFood.coords))
                path = createPathToward(currentState, worker.coords,
                                        self.myFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                print("Path: " + str(path))
                if len(path) == 1:
                    print("Obstruction")
                    possible_movements = listReachableAdjacent(currentState, path[0], 2)
                    if len(possible_movements) != 0:
                        random_number = random.randrange(0, len(possible_movements))
                        return Move(MOVE_ANT, [path[0], possible_movements[random_number]], None)
                #pdb.set_trace()
                return Move(MOVE_ANT, path, None)
        """
        Code above is copied
        """

        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)]

        
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0,len(moves) - 1)]
            
        return selectedMove
    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
