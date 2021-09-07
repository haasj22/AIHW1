import random
import sys

from SettingsPane import QuickStartFrame
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
import operator

#Class used for finding good locations for food
class EnemyNode():
    def __init__(self, coords, distance):
        self.coords = coords
        self.distance_from_drop_off = distance

##
# getBestLocationsForFood
# 
# Method that finds the best location for the food by distance from tunnels and anthills
#
# Parameters:
#    currentstate - current game state
# 
# Return: a list of locations where food can go sorted by distance to drop off location
def getBestLocationsForFood(currentState):
    #stores the location for the tunnel and anthill
    enemyAnthill = getEnemyInv(None, currentState).getAnthill().coords
    enemyTunnel = getEnemyInv(None, currentState).getTunnels()[0].coords

    #gets the location from the anthill and tunnel 
    #for each available place on the enemy side and stores the min distance in an array
    enemyLocations = []
    for x in range(BOARD_LENGTH):
        for y in range(BOARD_LENGTH - 4, BOARD_LENGTH):
            if currentState.board[x][y].constr == None:
                tunnelLength = stepsToReach(currentState, (x, y), enemyTunnel)
                anthillLength = stepsToReach(currentState, (x, y), enemyAnthill)
                enemyLocations.append(EnemyNode((x,y), min(tunnelLength, anthillLength)))
    #sorts the list and returns it
    enemy_locations = sorted(enemyLocations, key = operator.attrgetter('distance_from_drop_off'))
    return enemy_locations

##
# findMyFood
#
# finds the food closest to the tunnel
#  
# PARAMETERS:
#   currentState - the current game state
#   tunnel - the construction for the tunnel
# 
# Returns the food object closest to the tunnel
def findMyFood(currentState, tunnel):
    """
    Code below this copied from 82 - 98 of FoodGatherer.py
    Credits give to Nuxoll and whoever made this code
    Credited August 29, 2021 by John Haas
    """
    #gets all the food and initializes closest food to firston
    foods = getConstrList(currentState, None, (FOOD,))
    closestFood = foods[0]
    #locates the food closest to the tunnel
    bestDistSoFar = 1000 #i.e., infinity
    for food in foods:
        dist = stepsToReach(currentState, tunnel.coords, food.coords)
        if (dist < bestDistSoFar):
            closestFood = food
            bestDistSoFar = dist
    #returns the food closest to the tunnel
    return closestFood

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
    # addSecondLayer
    #
    # Returns coordinates for a layer of grass on the border in front of the anthill/tunnel.
    #
    # Parameters:
    #   anthillX: the anthill's x coordinate.
    #   tunnelX: the tunnel's x coordinate.
    #   currentState: the state of the game.
    #
    # Return: coordinates to place grass at.
    #
    def addSecondLayer(self, anthillX, tunnelX, currentState):
        grassLocations = []
        anthillXBorderPoint = (anthillX, 3)
        tunnelXBorderPoint = (tunnelX, 3)

        # Add grass on border where x coordinate is the same as the anthill/tunnel.
        grassLocations.append(anthillXBorderPoint)
        grassLocations.append(tunnelXBorderPoint)

        # Add grass on adjacent squares that are also on the border.
        for i in listAdjacent(anthillXBorderPoint):
            if i[1] == 3 and getConstrAt(currentState, i) is None:
                grassLocations.append(i)

        for i in listAdjacent(tunnelXBorderPoint):
            if i[1] == 3 and getConstrAt(currentState, i) is None:
                grassLocations.append(i)

        return grassLocations

    ##
    #getGrassLocation
    #
    #Get coordinates where grass will be placed.
    #
    #Parameters:
    #   moves: list of squares already taken.
    #   currentState: the state of the game.
    #
    #Return: coordinates to place grass at.
    #
    def getGrassLocation(self, moves, currentState):
        availableSpaces = []

        # Only the border is considered.
        for i in range(0, 10):
            currentSpace = (i, 3)

            if currentState.board[i][3].constr is None and (i, 3) not in moves:
                availableSpaces.append(currentSpace)

        # Can be any of the viable squares.
        # Help from https://www.w3schools.com/python/ref_random_randint.asp: randint's parameters are included.
        index = random.randint(0, len(availableSpaces) - 1)
        return availableSpaces[index]

    ##
    #getFoodLocation
    #
    #Gets coordinates to place food at.
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
    def getFoodLocation(self, enemyAnthill, enemyTunnel, moves, currentState):
        # Have a list of all available squares, with another for potential food locations.
        availableSquares = []
        foodLocations = []

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

        # Help from https://www.geeksforgeeks.org/python-program-to-find-largest-number-in-a-list/.
        # max() gets the entry with the highest value in a tuple.
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
            borderGrassLocations = self.addSecondLayer(anthillX, tunnelX, currentState)

            for i in borderGrassLocations:
                moves.append(i)
                numGrass -= 1

            while numGrass != 0:
                moves.append(self.getGrassLocation(moves, currentState))
                numGrass -= 1

            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            foodMoves = []

            # Get enemy anthill/tunnel locations.
            # Help from John Haas: getEnemyInv() can help in getting enemy anthill/tunnel locations.
            enemyAnthill = getEnemyInv(None, currentState).getAnthill().coords
            enemyTunnel = getEnemyInv(None, currentState).getTunnels()[0].coords

            # Place 2 foods.
            for i in range(0, 2):
                foodMoves.append(self.getFoodLocation(enemyAnthill, enemyTunnel, foodMoves, currentState))

            return foodMoves
        else:
            return [(0, 0)]
    
    ##
    # moveQueen
    #
    # Description: Handles the movement of the queen and returns necessary moves
    #
    # Parameters:
    #   self - the AI Player Object
    #   currentState - the game state object
    #   myInv - the Inventory object
    #
    # Returns the Move the queen should make
    def moveQueen(self, currentState, myInv):
        """
        Code above is copied
        """

        """
        Code below this partially copied from 101 - 103 of FoodGatherer.py
        Credits give to Nuxoll and whoever made this code
        Credited August 29, 2021 by John Haas
        """
        #gets the queen
        myQueen = myInv.getQueen()
        #moves the queen off necessary constructions
        if(not myQueen.hasMoved and getConstrAt(currentState, myQueen.coords) != None and
                (getConstrAt(currentState, myQueen.coords).type == ANTHILL or 
                getConstrAt(currentState, myQueen.coords).type == FOOD or 
                getConstrAt(currentState, myQueen.coords).type == TUNNEL)):
            #moves the queen in a way it can move
            if(myQueen.coords[1] != 3 and 
                    getAntAt(currentState, (myQueen.coords[0], myQueen.coords[1] + 1))) == None:
                return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0], myQueen.coords[1] + 1)])
            elif myQueen.coords[1] != 0 and \
                    (getAntAt(currentState, (myQueen.coords[0], myQueen.coords[1] - 1)) == None):
                return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0], myQueen.coords[1] - 1)])
            elif myQueen.coords[0] != 0 and \
                    (getAntAt(currentState, (myQueen.coords[0] - 1, myQueen.coords[1])) == None):
                return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0] - 1, myQueen.coords[1])])
            elif myQueen.coords[0] != 9 and \
                    (getAntAt(currentState, (myQueen.coords[0] + 1, myQueen.coords[1])) == None):
                return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0] + 1, myQueen.coords[1])])
            else:
                return Move(MOVE_ANT, [myQueen.coords], None)
        #else tells queen to stand still
        elif (not myQueen.hasMoved):
            return Move(MOVE_ANT, [myQueen.coords], None)
        """
        Code above is copied
        """
        #only necessary if queen has already moved
        return None

    ##
    # getBuildMoves
    #
    # determines if the agent must build an ant and if so return that move
    # 
    # Parameters:
    #   currentState - the current game state
    #   myInv - the agent's inventory
    #   numSoldiers - the number of soldiers the agent has
    #   numDrones - the number of drones the agent has
    #   numWorkers - the number of workers the agent has
    #   myAnthill - the construction containing the agent's anthill
    def getBuildMoves(self, currentState, myInv, numSoldiers, numDrones, numWorkers, myAnthill):
        if numSoldiers < 1 and getAntAt(currentState, myAnthill.coords) == None and \
                myInv.foodCount > 1:
            return Move(BUILD, [myAnthill.coords], SOLDIER)
        if numDrones < 1 and numSoldiers > 0 and \
                getAntAt(currentState, myAnthill.coords) == None and myInv.foodCount > 1:
            return Move(BUILD, [myAnthill.coords], DRONE)
        if numWorkers < 3 and numSoldiers > 0 and numDrones > 0 and \
                getAntAt(currentState, myAnthill.coords) == None and \
                myInv.foodCount > 0 or numWorkers == 0 \
                and getAntAt(currentState, myAnthill.coords) == None \
                and myInv.foodCount > 0:
            return Move(BUILD, [myAnthill.coords], WORKER)
        return None

    ##
    # getDesperationMoves
    #
    # determines if the agent is in a desperate state and needs to move differently 
    # and returns those desperate moves if so
    #
    # Parameters:
    #   currentState - the current game state
    #   myInv - the inventory of the agent
    #   playerID - the ID of the player
    #   workers - the workers the player has
    #   soldiers - the soldiers the player has
    #   drones - the drones the player has
    def getDesperationMoves(self, currentState, myInv, playerID, workers, soldiers, drones):
        #only checks if the user is desperate
        if(len(workers) == 0 and myInv.foodCount == 0):
            #gets enemy queen
            enemyQueen = getAntList(currentState, (playerID + 1) % 2, (QUEEN, ))
            #attempts to charge the queen with whatever soldiers and drones remain
            for soldier in soldiers:
                if soldier.hasMoved:
                    continue
                else:
                    path = createPathToward(currentState, soldier.coords,
                                       enemyQueen[0].coords, UNIT_STATS[SOLDIER][MOVEMENT])
                    return Move(MOVE_ANT, path, None)
            for drone in drones:
                if drone.hasMoved:
                    continue
                else:
                    path = createPathToward(currentState, drone.coords,
                                       enemyQueen[0].coords, UNIT_STATS[DRONE][MOVEMENT])
                    return Move(MOVE_ANT, path, None)
        #return None if not in desperate position
        return None

    ##
    # moveWorkers
    #
    # checks if the workers can be moved and returns the move if possible
    #
    # Parameters:
    #   currentState - the current game state
    #   playerID - the playerID of the agent
    def moveWorkers(self, currentState, workers):
        """
        Code below copied from 110-125 of FoodGatherer.py
        Credits give to Nuxoll and whoever made this code
        Credited August 29, 2021 by John Haas
        """
        #if the worker has already moved, we're done
        for worker in workers:
            if worker.hasMoved:
                continue
            #if the worker has food, move toward tunnel
            if (worker.carrying):
                path = createPathToward(currentState, worker.coords,
                                        self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                if len(path) == 1:
                    possible_movements = listReachableAdjacent(currentState, path[0], 2)
                    if len(possible_movements) != 0:
                        random_number = random.randrange(0, len(possible_movements))
                        return Move(MOVE_ANT, [path[0], possible_movements[random_number]], None)
                return Move(MOVE_ANT, path, None)
                
            #if the worker has no food, move toward food
            if(not worker.carrying):
                path = createPathToward(currentState, worker.coords,
                                        self.myFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                if len(path) == 1:
                    possible_movements = listReachableAdjacent(currentState, path[0], 2)
                    if len(possible_movements) != 0:
                        random_number = random.randrange(0, len(possible_movements))
                        return Move(MOVE_ANT, [path[0], possible_movements[random_number]], None)
                return Move(MOVE_ANT, path, None)
        """
        Code above is copied
        """
        return None
    
    ##
    # moveSoldiers
    #
    # tells the agent how to move the soldiers
    #
    # Parameters:
    #   currentState - the current game state
    #   myAnthill - the construction representing the agent's anthill
    #   soldiers - the soldiers the agent has 
    def moveSoldiers(self, currentState, myAnthill, soldiers):
        #tells the soldier if it exists to move two spaces to the left of the anthill
        for soldier in soldiers:
            path = None
            if soldier.hasMoved:
                continue
            else:
                if getConstrAt(currentState, (myAnthill.coords[0]+2, myAnthill.coords[1])) == None or \
                        getConstrAt(currentState, (myAnthill.coords[0]+2, myAnthill.coords[1])).type != FOOD:
                    path = createPathToward(currentState, soldier.coords,
                                        (myAnthill.coords[0]+2, myAnthill.coords[1]), UNIT_STATS[SOLDIER][MOVEMENT])
                elif getConstrAt(currentState, (myAnthill.coords[0]+3, myAnthill.coords[1])) == None or \
                        getConstrAt(currentState, (myAnthill.coords[0]+3, myAnthill.coords[1])).type != FOOD:
                    path = createPathToward(currentState, soldier.coords,
                                        (myAnthill.coords[0]+3, myAnthill.coords[1]), UNIT_STATS[SOLDIER][MOVEMENT])
                else:
                    path = createPathToward(currentState, soldier.coords,
                                        (myAnthill.coords[0]+4, myAnthill.coords[1]), UNIT_STATS[SOLDIER][MOVEMENT])
            return Move(MOVE_ANT, path, None)
        #if no soldier return None
        return None

    ##
    # moveDrones
    # tells the agent how to move the drones
    #
    # Parameters:
    #   currentState - the current game state
    #   playerID - the ID of the agent
    #   myAnthill - the construction of the agents anthill
    #   drones - the list of the agents drones
    def moveDrones(self, currentState, playerID, myAnthill, drones):
        #goes through the drones in the agents inventory
        for drone in drones:
            if drone.hasMoved:
                continue
            else:
                #gets the enemy ants
                enemyWorkerAnts = getAntList(currentState, (playerID + 1) % 2, (WORKER,))
                enemyDroneAnts = getAntList(currentState, (playerID + 1) % 2, (DRONE,))
                enemyFood = getConstrList(currentState, 2, (FOOD,))

                #attacks the enemy ants if they exist
                if len(enemyWorkerAnts) > 0:
                    path = createPathToward(currentState, drone.coords,
                                        enemyWorkerAnts[0].coords, UNIT_STATS[DRONE][MOVEMENT])
                    return Move(MOVE_ANT, path, None)
                elif len(enemyDroneAnts) > 0:
                    path = createPathToward(currentState, drone.coords,
                                        enemyDroneAnts[0].coords, UNIT_STATS[DRONE][MOVEMENT])
                    return Move(MOVE_ANT, path, None)
                #else moves the ant next to the enemy food
                else:
                        path = createPathToward(currentState, drone.coords,
                                        enemyFood[((playerID * 2)) % 4].coords, UNIT_STATS[DRONE][MOVEMENT])
                        return Move(MOVE_ANT, path, None)
        #if no drones returns None
        return None

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

        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn

        #the first time this method is called, the food and tunnel locations
        #need to be recorded in their respective instance variables
        if (self.myTunnel == None or True):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if (self.myFood == None or True):
            self.myFood = findMyFood(currentState, self.myTunnel)

        #moves the queen if its needed and possible to
        queensMove = self.moveQueen(currentState, myInv)
        if queensMove != None:
            return queensMove

        #information I need to make choices
        numSoldiers = len(getAntList(currentState, me, (SOLDIER,)))
        numDrones = len(getAntList(currentState, me, (DRONE,)))
        numWorkers = len(getAntList(currentState, me, (WORKER,)))
        myAnthill = myInv.getAnthill()

        #builds an ant if necessary
        buildMove = self.getBuildMoves(currentState, myInv, numSoldiers, numDrones, numWorkers, myAnthill)
        if buildMove != None:
            return buildMove
        
        #moves workers if possible
        workers = getAntList(currentState, me, (WORKER,))
        workersMove = self.moveWorkers(currentState, workers)
        if workersMove != None:
            return workersMove
        
        soldiers = getAntList(currentState, me, (SOLDIER,))
        drones = getAntList(currentState, me, (DRONE,))

        #performs a final desperate attack if necessary
        desperateMove = self.getDesperationMoves(currentState, myInv, me, workers, soldiers, drones)
        if desperateMove != None:
            return desperateMove

        #tells the agent how to move the soldier if it exists
        soldierMove = self.moveSoldiers(currentState, myAnthill, soldiers)
        if soldierMove != None:
            return soldierMove
        
        droneMove = self.moveDrones(currentState, me, myAnthill, drones)
        if droneMove != None:
            return droneMove

        return Move(END, None, None)
    


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
