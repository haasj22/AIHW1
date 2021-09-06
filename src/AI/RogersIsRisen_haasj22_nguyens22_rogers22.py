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
    #getGrassLocation <!-- ITERATIVE -->
    #
    #  coordinates to place Grass on the border.
    #
    #Parameters:
    #   construction: the Construction to place.
    #   moves: list of squares already taken.
    #   currentState: the state of the game.
    #
    #Return: coordinates to place Construction at.
    #
    def getGrassLocation(self, moves, currentState):
        availableSpaces = []

        for i in range(0, 10):
            currentSpace = (i, 3)

            if currentState.board[i][y].constr is None and (i, y) not in moves:
                availableSpaces.append(currentSpace)

        # Can be anywhere legal.
        # Help from https://www.w3schools.com/python/ref_random_randint.asp: randint's parameters are included.
        index = random.randint(0, len(availableSpaces) - 1)
        return availableSpaces[index]

    ##
    #getFoodLocation
    #
    #Gets coordinates to place food at, with ideal locations being 2+ squares away from the enemy anthill and tunnel.
    #
    #Parameters:
    #   enemyAnthill: the location of the enemy anthill.
    #   enemyTunnel: the location of the enemy tunnel.
    #   moves: list of squares already taken.
    #   currentState: the state of the game.
    #
    #Return: list of possible coordinates to place food at.
    #Help from https://www.w3schools.com/python/python_tuples_access.asp: tuples are like lists when being accessed.
    #Help from John Haas: choose squares based on minimum distances from the anthill and tunnel.
    #
    def getFoodLocations(self, enemyAnthill, enemyTunnel, moves, currentState):
        # Have a list of all available squares, with another for those 2+ squares away from enemy anthill/tunnel.
        availableSquares = []
        foodLocations = []
        dist = 0  # Arbitrary value to be updated as longer distances are found.

        # Add available squares.
        for i in range(0, 10):
            for j in range(6, 10):
                if currentState.board[i][j].constr is None and (i, j) not in moves:
                    availableSquares.append((i, j))

        # Get all squares' min distances from enemy structures.
        for i in availableSquares:
            distanceFromHill = stepsToReach(currentState, enemyAnthill, i)
            distanceFromTunnel = stepsToReach(currentState, enemyTunnel, i)
            minDistance = min(distanceFromHill, distanceFromTunnel)
            foodLocations.append(minDistance)

        maxDistance = max(foodLocations)

        # Get point whose min distance from structures corresponds to current distance.
        for i in availableSquares:
            currentDistanceFromHill = stepsToReach(currentState, enemyAnthill, i)
            currentDistanceFromTunnel = stepsToReach(currentState, enemyTunnel, i)
            if min(currentDistanceFromHill, currentDistanceFromTunnel) == maxDistance:
                return i

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
    # Help from https://www.geeksforgeeks.org/python-call-function-from-another-function/: self.function() calls
    # a function from the same class.
    ##
    def getPlacement(self, currentState):
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            numGrass = 9
            moves = []

            # Place anthill on "bottom" row.
            anthillX = random.randint(0, 2)
            anthillLocation = (anthillX, 0)
            moves.append(anthillLocation)

            # Place tunnel on second row from bottom away from the anthill.
            tunnelX = random.randint(6, 8)
            tunnelLocation = (tunnelX, 1)
            moves.append(tunnelLocation)

            # Place one layer of grass around anthill.
            grassLayerLocation = listAdjacent(anthillLocation)

            for point in grassLayerLocation:
                if currentState.board[point[0]][point[1]].constr is None and (point[0], point[1]) not in moves:
                    moves.append(point)
                    numGrass -= 1

            # Add remaining grass on outer edge.
            while numGrass != 0:
                moves.append(self.getGrassLocation(moves, currentState))
                numGrass -= 1

            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            foodMoves = []

            # Get enemy anthill/tunnel locations.
            # Help from John Haas: getEnemyInv can help in getting enemy anthill/tunnel locations.
            enemyAnthill = getEnemyInv(None, currentState).getAnthill().coords
            enemyTunnel = getEnemyInv(None, currentState).getTunnels()[0].coords

            # Place 2 foods.
            for i in range(0, 2):
                foodMoves.append(self.getFoodLocations(enemyAnthill, enemyTunnel, foodMoves, currentState))

            return foodMoves
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
        if (self.myTunnel == None):
            #ASK NUXOLL ABOUT THIS
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if (self.myFood == None):
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
        if (not myQueen.hasMoved and getConstrAt(currentState, myQueen.coords).type != ANTHILL):
            print(getConstrAt(currentState, myQueen.coords).type)
            print("First")
            return Move(MOVE_ANT, [myQueen.coords], None)
        elif(not myQueen.hasMoved):
            print("Second")
            if(myQueen.coords[1] != 3):
                return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0], myQueen.coords[1] + 1)])
            else:
                return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0], myQueen.coords[1] - 1)])
        """
        Code above is copied
        """

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)



        if numAnts < 3:

            pass

        """
        Code below copied from 110-125 of FoodGatherer.py
        Credits give to Nuxoll and whoever made this code
        Credited August 29, 2021 by John Haas
        """
        #if the worker has already moved, we're done
        myWorker = getAntList(currentState, me, (WORKER,))[0]
        if (myWorker.hasMoved):
            return Move(END, None, None)

        #if the worker has food, move toward tunnel
        if (myWorker.carrying):
            path = createPathToward(currentState, myWorker.coords,
                                    self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
            return Move(MOVE_ANT, path, None)

        #if the worker has no food, move toward food
        if(not myWorker.carrying):
            path = createPathToward(currentState, myWorker.coords,
                                    self.myFood.coords, UNIT_STATS[WORKER][MOVEMENT])
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
