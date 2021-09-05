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
    # getConstrLocation <!-- ITERATIVE -->
    #
    # Get coordinates to place a given Construction (either tunnel or grass that's not surrounding the anthill) at.
    #
    # Parameters:
    # construction: the Construction to place.
    # moves: list of squares already taken.
    # currentState: the state of the game.
    #
    # Return: coordinates to place Construction at.
    #
    def getConstrLocation(self, construction, moves, currentState):
        availableSpaces = []

        # Tunnel on bottom row, grass on border.
        for i in range(0, 10):
            y = 0

            if construction == GRASS:
                y = 3

            currentSpace = (i, y)

            if currentState.board[i][y].constr is None and (i, y) not in moves:
                availableSpaces.append(currentSpace)

        # Can be anywhere legal.
        # Help from https://www.w3schools.com/python/ref_random_randint.asp: randint's parameters are included.
        index = random.randint(0, len(availableSpaces) - 1)
        return availableSpaces[index]

    ##
    # getLocation <!-- ITERATIVE -->
    #
    # Gets the location of a desired Construction.
    #
    # Parameters:
    # constr: the Construction to find.
    # currentState: the state of the game.
    #
    # Return: a set of coordinates that correspond to desired construction's location.
    # Help from John Haas: need to make sure Constr at given point is not None, use .type to determine constr.
    #
    def getLocation(self, constr, currentState):
        for i in range(0, 10):
            for j in range(6, 10):
                if currentState.board[i][j].constr is not None \
                        and getConstrAt(currentState, (i, j)).type == constr:
                    constrPoint = (i, j)
                    return constrPoint

    ##
    # getFoodLocation <!-- ITERATIVE -->
    #
    # Gets coordinates to place food at, with ideal locations being 2+ squares away from the enemy anthill and tunnel.
    #
    # Parameters:
    # enemyAnthill: the location of the enemy anthill.
    # enemyTunnel: the location of the enemy tunnel.
    # moves: list of squares already taken.
    # currentState: the state of the game.
    #
    # Return: coordinates to place food at.
    # Help from https://www.w3schools.com/python/python_tuples_access.asp: tuples are like lists when being accessed.
    #
    def getFoodLocation(self, enemyAnthill, enemyTunnel, moves, currentState):
        # Have a list of all available squares, with another for those 2+ squares away from enemy anthill/tunnel.
        availableSquares = []
        squaresTwoOrMoreAway = []

        # Add available squares.
        for i in range(0, 10):
            for j in range(6, 10):
                if currentState.board[i][j].constr is None and (i, j) not in moves:
                    availableSquares.append((i, j))

        # Get all spots 2+ squares away from enemy structures.
        for point in availableSquares:
            distanceFromHill = stepsToReach(currentState, enemyAnthill, point)
            distanceFromTunnel = stepsToReach(currentState, enemyTunnel, point)

            if distanceFromHill >= 2 and distanceFromTunnel >= 2:
                squaresTwoOrMoreAway.append(point)

        food = 0  # Need "dummy" index.
        foodLocation = (0, 0)  # Need "dummy" coordinates.

        # Choose spot 2+ squares away from enemy structures if able.
        if len(squaresTwoOrMoreAway) >= 1:
            food = random.randint(0, len(squaresTwoOrMoreAway) - 1)
            foodLocation = squaresTwoOrMoreAway[food]

            # Chosen square may not be empty.
            while currentState.board[foodLocation[0]][foodLocation[1]].constr is not None \
                    and (foodLocation[0], foodLocation[1]) in moves:
                food = random.randint(0, len(squaresTwoOrMoreAway))
                foodLocation = squaresTwoOrMoreAway[food]
        else:
            food = random.randint(0, len(availableSquares))
            foodLocation = availableSquares[food]

            # Chosen square may not be empty.
            while currentState.board[foodLocation[0]][foodLocation[1]].constr is not None\
                    and (foodLocation[0], foodLocation[1]) in moves:
                food = random.randint(0, len(availableSquares))
                foodLocation = availableSquares[food]

        return foodLocation

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

            # Place anthill and tunnel somewhere on "bottom" row.
            anthillX = random.randint(0, 9)
            anthillLocation = (anthillX, 0)
            moves.append(anthillLocation)
            moves.append(self.getConstrLocation(TUNNEL, moves, currentState))

            # Place one layer of grass around anthill.
            grassLayerLocation = listAdjacent(anthillLocation)

            for point in grassLayerLocation:
                if currentState.board[point[0]][point[1]].constr is None and (point[0], point[1]) not in moves:
                    moves.append(point)
                    numGrass -= 1

            # Add remaining grass on outer edge.
            while numGrass != 0:
                moves.append(self.getConstrLocation(GRASS, moves, currentState))
                numGrass -= 1

            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            foodMoves = []

            # Get enemy anthill/tunnel locations.
            enemyAnthill = self.getLocation(ANTHILL, currentState)
            enemyTunnel = self.getLocation(TUNNEL, currentState)

            # Place 2 foods.
            for i in range(0, 2):
                foodMoves.append(self.getFoodLocation(enemyAnthill, enemyTunnel, foodMoves, currentState))

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
