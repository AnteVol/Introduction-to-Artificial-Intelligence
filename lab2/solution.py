import sys


clausesSet = set()
lastLine = ""

def cnfConvert(clause):
    toSplit = clause.lower().rstrip("\n")
    elements = clause.lower().rstrip("\n").split(" v ")
    counter = 0
    help = []
    for element in elements:
        if(element[0] == "~"):
            toAdd = element[1:].lower().rstrip("\n")
        else:
            toAdd = "~" + element.lower().rstrip("\n")
        help.append(frozenset(toAdd.split(".")))
    return help
def removeDuplicates(list):
    help = []
    for element in list:
        if element not in help:
            help.append(element)
    return help

def readLines(filename):
    filenameClauses = filename

    with open(filenameClauses, 'r') as file:
        linesClauses = file.readlines()

    clausesList = []
    noLinewWithOutComment = 0
    for line in linesClauses:
        if not line.startswith("#"):
            noLinewWithOutComment = noLinewWithOutComment + 1
    count = 0
    G = ""
    notG = linesClauses[-1].rstrip("\n")
    for line in linesClauses:
        if not line.startswith("#"):
            if noLinewWithOutComment == count + 1:
                G = line
                notG = cnfConvert(line)
            else:
                clausesList.append(frozenset(line.lower().rstrip("\n").split(" v ")))
            count = count + 1
    clauses = removeDuplicates(clausesList)

    return clauses, G, notG

def removeRedudantClauses(clauses):
    clauses = set(clauses)
    help = clauses.copy()
    for c1 in help:
        for c2 in help:
            if c1.issubset(c2) and c1 != c2:
                clauses.discard(c2)
    return clauses
def removeUnimportantClauses(clauses):
    help = clauses
    for clause in help:
        for literal1 in clause:
            for literal2 in clause:
                if literal1!=literal2:
                    if literal1 == "~"+literal2 or literal2 == "~"+literal1:
                        if clause in clauses:
                            clauses.remove(clause)
    return clauses
def selectClauses(clauses, negG, new):

    new1 = removeRedudantClauses(new)
    new2 = removeUnimportantClauses(new1)
    clauses = set(removeRedudantClauses(clauses + negG)) | new2
    Sos = set(negG) | new2

    clausesCombination= []
    for c1 in Sos:
        for c2 in clauses:
            if c1 != c2:
                clausesCombination.append((c1, c2))
    return clausesCombination

def plResolve(c1, c2):

    remove = set()
    changed = False
    for literal1 in c1:
        for literal2 in c2:
            if literal1 == "~" + literal2:
                changed = True
                first = len(c1)
                second = len(c2)

                if first == 1 and second == 1:
                    return "NIL"
                remove.add(literal1)
                remove.add(literal2)
            elif literal2 == "~" + literal1:
                changed = True
                first = len(c1)
                second = len(c2)
                if first == 1 and second == 1:
                   # print("NIL")
                    return "NIL"
                remove.add(literal1)
                remove.add(literal2)
    if changed:
        resolvents = set(frozenset(c1) | frozenset(c2))
        for element in remove:
            resolvents.remove(element)

      #  print("Rezultat micanja: " + " v ".join(resolvents))
        return frozenset(resolvents)
    else:
     #   print("Nisam mijenjao")
        return 0
def recursivePrint(clause, way=[]):
    if clause in dictForPrint.keys():
        toPrint = str(dictForPrint[clause][0]) + "." + " " + clause + " (" + dictForPrint[clause][1] + ", " + dictForPrint[clause][2] + ")"
        way.append(toPrint)
        first = dictForPrint[clause][1]
        second = dictForPrint[clause][2]
        recursivePrint(first)
        recursivePrint(second)
    return way

dictForPrint = {}
def plResolution(clauses, G, notG):
    if type(notG) != list:
        notG = [notG]
    new = set()
    allClauses = removeDuplicates(clauses + notG)
    resolved = set()
#    print("Printam sve")
#    print(allClauses)
    counter = 1
    for clause in allClauses:
        print(str(counter) + ". " + " v ".join(clause))
        counter = counter + 1
    print("===================")

    while 1:
        for (c1, c2) in selectClauses(clauses, notG, new):
            if frozenset([c1, c2]) not in resolved:
                resolvent = plResolve(c1, c2)
            if "NIL" == resolvent:
                printResult = recursivePrint(" v ".join(c1))
                way = printResult.__reversed__()
                if(way is not None):
                    for w in way:
                     print(w)
                print("NIL(" + " v ".join(c1) + ", " + " v ".join(c2) +")")
                return True, G
            if resolvent != 0:
                resolved.add(frozenset([c1, c2]))
                if resolvent not in allClauses and resolvent not in new:
                    dictForPrint[" v ".join(resolvent)] = [counter, " v ".join(c1), " v ".join(c2)]
                    counter = counter + 1
                new.add(resolvent)

        setClauses = set(allClauses)
        if new.issubset(setClauses):
            return False, G
        allClauses = removeDuplicates(allClauses + list(new))

def cookingFunction(path, commands):
    with open(path, 'r') as file:
        clauses = file.readlines()

    clausesList = []

    for line in clauses:
        if not line.startswith("#"):
            clausesList.append(frozenset(line.lower().rstrip("\n").split(" v ")))

    listOfClauses = removeDuplicates(clausesList)

    with open(commands, 'r') as file:
        com = file.readlines()

    listOfCommands = []
    for line in com:
        if not line.startswith("#"):
            help = line.rstrip("\n")
            operation = help[-1]
            listOfCommands.append((help[:-2].lower(), operation))

    return listOfClauses, listOfCommands

def cook(listOfClauses, listOfCommands):
    for k in listOfCommands:
        clause = k[0]
        action = k[1]
        if action == "?":
            G = clause
            notG = cnfConvert(G)
            result, nothing = plResolution(listOfClauses, G, notG)
            if result == True:
                print("[CONCLUSION]: " + G +" is true")
            else:
                print("[CONCLUSION]: " + G + " is unknown")
        elif action == "+":
            toAdd = frozenset(k[0].split(" v "))
            listOfClauses.append(toAdd)
            print("Added " + k[0])
        else:
            help = listOfClauses
            for element in help:
                if frozenset(k[0].split(" v ")) == element:
                    listOfClauses.remove(element)
            print("removed " + k[0])


if sys.argv[1] == "resolution":
    path = sys.argv[2]
    clauses, G, notG = readLines(path)
    result, lastLineResult = plResolution(clauses, G, notG)

    if(result == True):
        print("====================")
        print("[CONCLUSION]: " + lastLineResult.rstrip("\n").lower() + " is true")
    else:
        print("[CONCLUSION]: " + lastLineResult.rstrip("\n").lower() + " is unknown")

if sys.argv[1] == "cooking":
    path = sys.argv[2]
    commands = sys.argv[3]
    listOfClauses, listOfCommands = cookingFunction(path, commands)
    cook(listOfClauses, listOfCommands)


