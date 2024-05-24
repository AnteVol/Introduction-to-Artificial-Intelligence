import sys
import heapq

inputfile = sys.argv[sys.argv.index("--ss") + 1]
filename = '/UUUI/autograder[4]/autograder/data/lab1/files/istra.txt'
name = filename.split("/")[-1]
with open(inputfile, 'r') as file:
    lines = file.readlines()

linesWithOutComments = []
for line in lines:
    if not line.startswith("#"):
        linesWithOutComments.append(line)

startState = linesWithOutComments[0].rstrip('\n')
goalStates = linesWithOutComments[1].split(" ")
goalStates = [state.rstrip('\n') for state in goalStates]
remainingStates = linesWithOutComments[2:]

dictOfCosts = {}

for line in remainingStates:
    splitedLine = line.split(" ")
    help = {}
    for sublines in splitedLine[1:]:
        splitedSubline = sublines.split(",")
        help[splitedSubline[0]] = splitedSubline[1].rstrip('\n')
    dictOfCosts[splitedLine[0][:-1]] = help

dictOfHeruistic = {}
linesHeruistic = ""

class Node:
    def __init__(self, name, comeFrom, cost):
        self.name = name
        self.cost = cost
        self.comeFrom = comeFrom

    def __lt__(self, other):
        return self.cost < other.cost


# BFS
def findStates(state):
    result = dictOfCosts[state.name]
    toReturn = []
    for name, cost in result.items():
        toReturn.append(Node(name, state, state.cost + int(cost)))
    return toReturn


def BFS(s0, succ, goal):
    open = [Node(s0, "a", 0)]
    visited = set()
    while open:
        current = open.pop(0)
        visited.add(current.name)
        if current.name in goal:
            return current, len(visited)
        succ = findStates(current)
        for state in succ:
            if state.name not in visited:
                open.append(state)
            else:
                continue
    return -1


def UCS(s0, succ, goal):
    open = [Node(s0, "a", 0)]  # better to use heapq
    heapq.heapify(open)
    visited = set()

    while open:
        current = heapq.heappop(open)
        visited.add(current.name)

        if current.name in goal:
            return current, len(visited)

        successors = findStates(current)
        for state in successors:
            if state.name not in visited:
                heapq.heappush(open, state)
            else:
                continue

    return -1


def findSameState(list, state):
    for element in list:
        if (element.name == state.name) and (element.cost <= state.cost):
            return True
    return False


def Astar(s0, succ, goal, h):
    open = [Node(s0, "a", 0)]
    closed = set()
    while open:
        current = open.pop(0)
        if current.name in goal:
            return current, len(closed)
        closed.add(current)
        succ = findStates(current)
        for state in succ:
            if (findSameState(open, state) | findSameState(closed, state)):
                continue
            else:
                count = 0
                for openElement in open:
                    if openElement.name == state.name:
                        open = open[0:count] + open[count + 1:]
                    count = count + 1
                count = 0
                for closedElement in closed:
                    if closedElement.name == state.name:
                        closed = closed[0:count] + closed[count + 1:]
                    count = count + 1
            open.append(state)
            open = sorted(open, key=lambda x: (x.cost + int(h[x.name])))
    return -1


def Heuristic_Optimistic(h):
    returnResult = True
    for key, value in h.items():
        result, nothing = UCS(key, "", goalStates)
        if float(result.cost) < float(value):
            print("[CONDITION]: [ERR] h(" + key + ") <= h*: " + str(float(value)) + " <= " + str(float(result.cost)))
            returnResult = False
        else:
            print("[CONDITION]: [OK] h(" + key + ") <= h*: " + str(float(value)) + " <= " + str(float(result.cost)))
    return returnResult


def Heuristic_Consistent(dc, h):
    returnResult = True
    for state, dict in dc.items():
        for destinationState, cost in dict.items():
            help = float(h[destinationState]) + float(cost)
            result = float(h[state]) <= help
            if result:
                print("[CONDITION]: [OK] h(" + state + ") <= h(" + destinationState + ") + c: " + str(
                    float(h[state])) + " <= " + str(float(h[destinationState])) + " + " + str(float(cost)))
            else:
                returnResult = False
                print("[CONDITION]: [ERR] h(" + state + ") <= h(" + destinationState + ") + c: " + str(
                    float(h[state])) + " <= " + str(float(h[destinationState])) + " + " + str(float(cost)))
    return returnResult

if sys.argv.__contains__("--alg"):
    algorithmTOUSe = sys.argv[sys.argv.index("--alg") + 1]
    if algorithmTOUSe == "bfs":
        BFS_result, statesVisited = BFS(startState, "", goalStates)
        if (BFS_result != -1):
            print("# BFS " + inputfile)
            print("[FOUND_SOLUTION]: yes")
            print("[STATES_VISITED]: " + str(statesVisited))
            BFS_name = BFS_result.name
            BFS_cost = BFS_result.cost
            BFS_way = []
            while BFS_result.name != startState:
                BFS_way.append(BFS_result.name)
                BFS_result = BFS_result.comeFrom
                if BFS_result.name == startState:
                    BFS_way.append(startState)
            correctOrder = BFS_way[::-1]
            print("[PATH_LENGTH]: " + str(len(correctOrder)))
            print("[TOTAL_COST]: " + str(float(BFS_cost) + 1))
            print("[PATH]: " + " => ".join(correctOrder))
        else:
            print("[FOUND_SOLUTION]: no")
    elif algorithmTOUSe == "ucs":
        UCS_result, statesVisited = UCS(startState, "", goalStates)
        if (UCS_result != -1):
            print("# UCS " + inputfile)
            print("[FOUND_SOLUTION]: yes")
            print("[STATES_VISITED]: " + str(statesVisited))
            UCS_name = UCS_result.name
            UCS_cost = UCS_result.cost
            UCS_way = []
            while UCS_result.name != startState:
                UCS_way.append(UCS_result.name)
                UCS_result = UCS_result.comeFrom
                if UCS_result.name == startState:
                    UCS_way.append(startState)
            correctOrder = UCS_way[::-1]
            print("[PATH_LENGTH]: " + str(len(correctOrder) + 1))
            print("[TOTAL_COST]: " + str(float(UCS_cost)))
            print("[PATH]: " + " => ".join(correctOrder))
        else:
            print("[FOUND_SOLUTION]: no")
    else:
        heuristicString = sys.argv[sys.argv.index("--h") + 1]
        filenameHeruistic = '/home/ante/PycharmProjects/pythonProject/UUUI/autograder[4]/autograder/data/lab1/files/istra_pessimistic_heuristic.txt'
        nameHeruistic = filename.split("/")[-1]
        with open(heuristicString, 'r') as file:
            linesHeruistic = file.readlines()
        for line in linesHeruistic:
            splitedLine = line.split(": ")
            dictOfHeruistic[splitedLine[0]] = splitedLine[1].rstrip('\n')
        Astar_result, statesVisited = Astar(startState, "", goalStates, dictOfHeruistic)
        if (Astar_result != -1):
            print("# A-STAR " + heuristicString)
            print("[FOUND_SOLUTION]: yes")
            print("[STATES_VISITED]: " + str(statesVisited + 1))
            Astar_name = Astar_result.name
            Astar_cost = Astar_result.cost
            Astar_way = []
            while Astar_result.name != startState:
                Astar_way.append(Astar_result.name)
                Astar_result = Astar_result.comeFrom
                if Astar_result.name == startState:
                    Astar_way.append(startState)
            correctOrder = Astar_way[::-1]
            print("[PATH_LENGTH]: " + str(len(correctOrder)))
            print("[TOTAL_COST]: " + str(float(Astar_cost)))
            print("[PATH]: " + " => ".join(correctOrder))
        else:
            print("[FOUND_SOLUTION]: no")

elif sys.argv.__contains__("--check-optimistic"):
    heuristicString = sys.argv[sys.argv.index("--h") + 1]
    filenameHeruistic = '/home/ante/PycharmProjects/pythonProject/UUUI/autograder[4]/autograder/data/lab1/files/istra_pessimistic_heuristic.txt'
    nameHeruistic = filename.split("/")[-1]
    with open(heuristicString, 'r') as file:
        linesHeruistic = file.readlines()
    # pozovi optimalnost
    for line in linesHeruistic:
        splitedLine = line.split(": ")
        dictOfHeruistic[splitedLine[0]] = splitedLine[1].rstrip('\n')
    print("# HEURISTIC_OPTIMISTIC " + heuristicString)
    Heuristic_Optimistic_result = Heuristic_Optimistic(dictOfHeruistic)
    if Heuristic_Optimistic_result:
        print("[CONCLUSION]: Heuristic is optimistic.")
    else:
        print("[CONCLUSION]: Heuristic is not optimistic.")

elif sys.argv.__contains__("--check-consistent"):
    heuristicString = sys.argv[sys.argv.index("--h") + 1]
    filenameHeruistic = '/home/ante/PycharmProjects/pythonProject/UUUI/autograder[4]/autograder/data/lab1/files/istra_pessimistic_heuristic.txt'
    nameHeruistic = filename.split("/")[-1]
    with open(heuristicString, 'r') as file:
        linesHeruistic = file.readlines()
    # pozovi consistent
    for line in linesHeruistic:
        splitedLine = line.split(": ")
        dictOfHeruistic[splitedLine[0]] = splitedLine[1].rstrip('\n')
    print("# HEURISTIC_CONSISTENT " + heuristicString)
    Heuristic_Consistent_result = Heuristic_Consistent(dictOfCosts, dictOfHeruistic)
    if Heuristic_Consistent_result:
        print("[CONCLUSION]: Heuristic is consistent.")
    else:
        print("[CONCLUSION]: Heuristic is not consistent.")



