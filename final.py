# Worked with: Benjamin Khoury, Oliver Dahl
# December 14, 2018
# final.py

#This code contains our final product


import random

#Global Variables
HEIGHT = 25
WIDTH = 25
NUMSTATES = 5
NUMCOMMANDS = 45
PATTERNS = ["xxxx", "Nxxx", "NExx", "NxWx", "xxxS", "xExS", "xxWS", "xExx", "xxWx"]
LISTNUMSTATES = list(range(NUMSTATES))
DIRECTIONS = ["N", "E", "W", "S"]
TRIALS = 50
STEPS = 1000
CUTOFF = .10
PROBMUTATION = .1

class Program(object):
    def __init__(self):
        """Creates a program with and empty set of rules"""
        self.rules = {}

    def __repr__(self):
        """ Represents the program by printing the rules in a form that can be copyed and pasted into the picobot program and run."""
        Keys = list( self.rules.keys() )  
        sortedKeys = sorted(Keys)
        endstring =""
        for i in range(NUMCOMMANDS):
            endstring += str(sortedKeys[i][0])+ " "+ sortedKeys[i][1]+ " -> "+ str(self.rules[sortedKeys[i]][0])+ " "+ str(self.rules[sortedKeys[i]][1])+"\n"
        return endstring

    def __gt__(self, other):
        """Greater-than operator -- works randomly, but works!"""
        return random.choice([True, False])

    def __lt__(self, other):
        """Less-than operator -- works randomly, but works!"""
        return random.choice([True, False])

    def randomize(self):
        """Generates a random set of valid rules for self"""
        for i in range(NUMSTATES):
            for j in range(len(PATTERNS)):
                openDirection = []
                for k in range(4):
                    if DIRECTIONS[k] not in PATTERNS[j]:
                        openDirection += DIRECTIONS[k]
                self.rules[LISTNUMSTATES[i],PATTERNS[j]] = (random.choice(openDirection), random.choice(LISTNUMSTATES))
    
    def getMove(self, state, surroundings):
        """returns the next move according to a given state and surroundinds found by looking at self.rules"""
        return self.rules[state, surroundings]

    def mutate(self):
        """randomly selects a key in self.rules and changes its value into another valid direction and state"""
        key = random.choice(list(self.rules.keys()))
        rule = self.rules[key]
        openDirection = []
        for k in range(4):
            if DIRECTIONS[k] not in key[1]:
                openDirection += DIRECTIONS[k]
        newRule = rule
        while newRule == rule:
            newRule = (random.choice(openDirection), random.choice(LISTNUMSTATES))
        
        self.rules[key] = newRule
   
    def crossover(self,other):
        """ Creates a new program who's rules are made up of self and others rules"""
        crossoverstate = random.randint(0,4)
        newRules = {}
        key = list(self.rules.keys())
        for i in range(NUMCOMMANDS):
            if key[i][0] <= crossoverstate:
                newRules[key[i]] = self.rules[key[i]]
            else:
                newRules[key[i]] = other.rules[key[i]]
        np = Program()
        np.rules = newRules
        return np


class World(object): #Complete
    def __init__(self, initial_row, initial_col, program):
        """creates a world object and makes an empty room surrounded by walls"""
        self.prow = initial_row
        self.pcol = initial_col
        self.state = 0
        self.prog = program
        self.room = [[' ']*WIDTH for row in range(HEIGHT)]
        self.visited = []
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if i == 0 or i == HEIGHT-1:
                    self.room[i][j] = "+"
                elif j == 0 or j == WIDTH-1:
                    self.room[i][j] = "+"

    def __repr__(self):
        """ this method returns a string representation
            for an object of type World
        """
        s = ''   # the string to return
        for row in range( HEIGHT ):
            for col in range( WIDTH ):
                if(row == self.prow and col == self.pcol):
                    s += 'P '
                elif((row, col) in self.visited):
                    s += 'o '
                else:
                    s += self.room[row][col] + ' '
            s += '\n'
        return s

    def getCurrentSurroundings(self):
        """Returns the current surroundings of our pico bot"""
        pos = "xxxx"

        if self.room[self.prow-1][self.pcol] == "+":
            pos = "N" + pos[1:]
        if self.room[self.prow+1][self.pcol] == "+":
            pos = pos[:3] + "S"
        if self.room[self.prow][self.pcol-1] == "+":
            pos = pos[:2]+"W"+ pos[3]
        if self.room[self.prow][self.pcol+1] == "+":
            pos = pos[0]+"E"+pos[2:]
        return(pos)

    def step(self):
        """moves the pico bot one move based on its curret location and set of rules """
        if((self.prow, self.pcol) not in self.visited):
            self.visited.append((self.prow, self.pcol))
        nextMove = self.prog.getMove(self.state,self.getCurrentSurroundings())
        if nextMove[0] == "N":
            self.prow += -1
        elif nextMove[0] == "S":
            self.prow += 1
        elif nextMove[0] == "E":
            self.pcol += 1
        else:
            self.pcol += -1
        self.state = nextMove[1]
    
    def run(self, steps):
        """moves the pico bot 'steps' number of times"""
        for i in range(steps):
            self.step()

    def fractionVisitedCells(self):
        """returns the fraction of cells that the current pico bot visited"""
        totalCells = (HEIGHT-2)*(WIDTH-2)
        totalVisited = len(self.visited)
        return totalVisited/totalCells

def populator(size):
    """generates a list of programs 'size' long"""
    populations = []
    for i in range(size):
        p = Program()
        p.randomize()
        populations.append(p)
    return populations

def evaluateFitness(program,trials,steps):
    """ evaluates the Fitness of 'program' by running it 'trials' times each time with 'steps' steps and finding the avg fraction of cells visited"""
    fitnessSum = 0
    for i in range(trials):
        w = World(random.choice(range(1,HEIGHT-1)),random.choice(range(1,WIDTH-1)),program)
        w.run(steps)
        fitnessSum += w.fractionVisitedCells()
    return fitnessSum/trials
    
def GA(popsize, numgens):
    """ creates popsize random picobot programs and then loops through numgen times each time killing the bottom 90% of the programs 
    and replacing them with new programs made with crossover and then mutate of the survivers of the previous gen"""
   
    print("Fitness is measured using ", TRIALS," random trials and running for ", STEPS, " steps per trial:")
    initpop = populator(popsize)
    
    for gen in range(numgens):                      #loop through each generation
        fitnesses = []
        AVGF = 0
        for i in range(popsize):
            fitnesses.append(( evaluateFitness(initpop[i] , TRIALS, STEPS) , initpop[i]))
            AVGF += evaluateFitness(initpop[i] , TRIALS, STEPS)
        AVGF = AVGF/popsize
        sortedFitnesses = sorted(fitnesses)
        cutoff = round(CUTOFF * popsize)
        cutoffPop = sortedFitnesses[-cutoff:]
        BF = cutoffPop[-1][0]
        print("Generation ", gen )
        print("     Average fitness: ", AVGF)
        print("     Best fitness: ", BF)
        childpop = []
        
        for i in range(popsize-len(cutoffPop)):     #fill the rest of the population with child programs
            p1 = random.choice(cutoffPop)
            p2 = p1
            while p2 == p1:                         #ensure the parents are the same program
                p2 = random.choice(cutoffPop)
            child = p1[1].crossover(p2[1])
            
            for i in range(NUMCOMMANDS):            #possibly mutate the child numcommands number of times
                if PROBMUTATION >= random.random():        
                    child.mutate()

            childpop.append(child)

        initpop = childpop
        for i in range(len(cutoffPop)):             #recreate initpop for next generation
            initpop.append(cutoffPop[i][1])

       
    
    lastgenf = []
    for i in range(popsize):                        #sort the last generation by fitness
        lastgenf.append(( evaluateFitness(initpop[i] , TRIALS, STEPS) , initpop[i]))
        sortedLastgen = sorted(lastgenf)
    
    bestP = sortedLastgen[-1][1]
    return bestP
    

        
        #create new children from random parents (from cutoffPop)
        #we do tshis using crossover
        #we then mutate them depending on a certain chance of it mutating
    #childrenpop + cutoffPop = new initpop
    #repeat numgens times
    #then return best program from last generation
    

    