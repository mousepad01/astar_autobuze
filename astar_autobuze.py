import copy
import time


class PriorityQueue:

    # cu privire la functia cmp, obiectele de tip PriorityQueue se comporta ca un minHeap
    # by default, functia de comparare este __lt__

    def __init__(self, initArr=None, compareFunction=None):

        if compareFunction is None:
            raise ValueError("functia de comparare a elementelor nu este specificata")

        if initArr is None:
            initArr = []

        self.pos = {}  # pozitiile elementelor in heap, pentru a executa heapify in timp logaritmic

        self.cmp = compareFunction

        self.heap = [None]
        for newElement in initArr:
            try:
                self.push(newElement)
            except ValueError:
                raise ValueError(f"found duplicate in initialisation array, element {newElement}")

    def __repr__(self):

        st = ''
        for el in self.heap[1:]:
            st += repr(el) + ' '

        return st[:-1]

    def __swapElsByPos(self, pos1, pos2):

        aux = self.heap[pos1]
        self.heap[pos1] = self.heap[pos2]
        self.heap[pos2] = aux

        self.pos[self.heap[pos2]] = pos2
        self.pos[self.heap[pos1]] = pos1

    def push(self, element):

        if element in self.pos.keys():
            raise ValueError(f"element already in the queue on heap array position {self.pos[element]}")

        self.heap.append(element)
        self.pos.update({element: len(self.heap) - 1})

        self.heapify(element)

    def heapify(self, element):

        try:
            elPos = self.pos[element]
        except KeyError as kerr:
            raise ValueError(f"eroare la ordonarea heap-ului la rearanjare: {kerr}")

        while elPos > 1 and not self.cmp(self.heap[elPos // 2], self.heap[elPos]):
            self.__swapElsByPos(elPos, elPos // 2)
            elPos //= 2

        heapSize = len(self.heap)

        done = False
        while not done:

            if elPos * 2 >= heapSize and elPos * 2 + 1 >= heapSize:
                done = True

            elif elPos * 2 < heapSize <= elPos * 2 + 1:

                if self.cmp(self.heap[elPos], self.heap[elPos * 2]):
                    done = True
                else:
                    self.__swapElsByPos(elPos, elPos * 2)
                    elPos *= 2

            else:

                if self.cmp(self.heap[elPos], self.heap[elPos * 2 + 1]) and self.cmp(self.heap[elPos],
                                                                                       self.heap[elPos * 2]):
                    done = True
                else:

                    if self.cmp(self.heap[elPos * 2], self.heap[elPos * 2 + 1]):
                        self.__swapElsByPos(elPos, elPos * 2)
                        elPos *= 2
                    else:
                        self.__swapElsByPos(elPos, elPos * 2 + 1)
                        elPos *= 2
                        elPos += 1

    def peekMin(self):
        return copy.deepcopy(self.heap[1])

    def getMin(self):
        return self.pop(self.heap[1])

    def pop(self, element):

        try:
            elPos = self.pos[element]
        except KeyError as kerr:
            raise ValueError(f"eroare la ordonarea heap-ului la stergere: {kerr}")

        heapSize = len(self.heap)

        self.__swapElsByPos(elPos, heapSize - 1)

        popped = self.heap.pop(-1)
        self.pos.pop(popped)
        heapSize -= 1

        if not self.empty() and elPos < heapSize:
            self.heapify(self.heap[elPos])

        return popped

    def empty(self):
        if len(self.heap) == 1:
            return True
        return False


class BusType:

    def __init__(self, id, price, timeOfLeaving, timeBetweenLocations):

        self.id = id
        self.price = price
        self.route = []  # [locatie.nume, ...]
        self.timeBetweenLocations = timeBetweenLocations
        self.timeOfLeaving = timeOfLeaving

    def routeIterator(self, reverse=False):

        l = len(self.route)

        prevLocationName = None
        currentLocationName = None
        futureLocationName = None

        flag = False  # pentru a ma ajuta sa nu repet locatiile de la capete

        if reverse is True:

            i = -1
            while i >= -l:

                currentLocationName = self.route[i]
                if i == -l:
                    futureLocationName = prevLocationName
                else:
                    futureLocationName = self.route[i - 1]

                yield (prevLocationName, currentLocationName, futureLocationName)

                prevLocationName = currentLocationName
                i -= 1

            flag = True

        while True:

            if flag is True:
                i = 1
            else:
                i = 0

            while i < l:

                currentLocationName = self.route[i]
                if i == l - 1:
                    futureLocationName = prevLocationName
                else:
                    futureLocationName = self.route[i + 1]

                yield (prevLocationName, currentLocationName, futureLocationName)

                prevLocationName = currentLocationName
                i += 1

            i = -2  # ultima pozitie parcursa deja in ultimul while
            while i >= -l:

                currentLocationName = self.route[i]
                if i == -l:
                    futureLocationName = prevLocationName
                else:
                    futureLocationName = self.route[i - 1]

                yield (prevLocationName, currentLocationName, futureLocationName)

                prevLocationName = currentLocationName
                i -= 1

            flag = True

    def __str__(self):
        return f"id {self.id}, price {self.price}, time between locations {self.timeBetweenLocations}, time of leaving {self.timeOfLeaving}\n{self.route}"


class Location:

    def __init__(self, name):

        self.name = name
        self.schedule = {}  # {minut: [(autobuz.id, autobuz.nr, locatie anterioare, locatie urmatoare),..]}

        self.buses = {}     # {bus.id: bus}
                            # autobuzele care trec prin aceasta locatie
                            # le as fi putut dedude din self.schedule, dar preprocesez pentru a optimiza timpul de rulare

    def __str__(self):
        return f"name {self.name}\n{self.schedule}\n{self.buses}"


# voi avea doau tipuri de stari in care se afla persoana
class Person:

    def __init__(self, name, money):

        self.name = name
        self.money = money
        self.personalRoute = []  # [locatie.nume, ...]
                                 # voi sterge locatiile pe masura ce sunt parcurse

        self.personalState = None   # daca se afla pe drum: "PE TRASEU"
                                    # daca se afla in statie: "IN STATIE"

        self.timeForArrival = 0   # timpul cat dureaza pana ajunge in urmatoarea statie
        self.currentBus = None    # autobuzul curent, daca e pe traseu
        self.currentBusNr = 0     # numarul autobuzului curent
        self.nextLocationName = None
        self.previousLocationName = None    # pentru a identifica complet in ce autobuz circula
                                            # pentru a evita intersectia persoanelor

        self.currentLocationName = None     # daca asteapta, statia curenta
        self.allowedBuses = set()  # pentru cazul cand asteapta in statie, si a refuzat sa ia un autobuz, il elimin
                                   # {autobuz.id: autobuz}

        # PRECIZARI:
        #
        # cand o persoana este in statie si decide sa nu urce in autobuz,
        # voi elimina din allowedBuses acel autobuz si in rest nu modific nimic
        #
        # cand o persoana este pe drum, ajunge intr-o statie si decide sa nu coboare
        # persoana va fi considerata tot pe drum, dar se va modifica timeForArrival si next & previous LocationName
        #
        # cand o persoana este pe drum, ajunge intr-o statie si decide sa coboare
        # voi seta timeForArrival, currentBus, next & prev LocationName pe 0 / None
        # voi seta currentLocationName corespunzator (fostul nextLocationName)
        # voi initializa allowedBuses cu toate autobuzele care trec prin acea locatie
        # in plus, daca locatia este urmatoarea din person.personalRoute, elimin statia din personalRoute
        #
        # cand o persoana este in statie si decide sa urce
        # setez allowedBuses pe {} (dict gol) si currentLocationName pe None
        # setez corespunzator timeForArrival , etc...
        # si scad din money pretul autobuzului in care urca

    def __str__(self):
        return f"name {self.name}, money {self.money}\n{self.personalRoute}\npersonal state {self.personalState}, \
            time for arrival {self.timeForArrival}, current bus {self.currentBus}, current bus nr {self.currentBusNr} \
            next location name {self.nextLocationName}, \
            previous location {self.previousLocationName}\n current location {self.currentLocationName}\n{self.allowedBuses}"


class Info:

    buses = {}  # {autobuz.id: autobuz}
    locations = {}  # {locatie.nume: locatie}
    persons = {}  # {persoana.nume: persoana}

    START_TIME = 0  # START_TIME si END_TIME intervalul zilei
    END_TIME = 0

    NSOL = 1

    # pentru euristici
    MIN_BUS_PRICE = float('inf')
    MAX_BUS_PRICE = -1

    # tot pt euristici
    MIN_BUS_TRAVEL_TIME = float('inf')

    @classmethod
    def parseHours(cls, l):

        l = l.split()

        h1 = 60 * (10 * int(l[0][0]) + int(l[0][1])) + 10 * int(l[0][3]) + int(l[0][4])
        h2 = 60 * (10 * int(l[1][0]) + int(l[1][1])) + 10 * int(l[1][3]) + int(l[1][4])

        return h1, h2

    @classmethod
    def parseInput(cls):

        inputFile = open("input.txt", "r")

        inputBuffer = inputFile.read()
        inputLines = inputBuffer.split('\n')

        cls.START_TIME, cls.END_TIME = cls.parseHours(inputLines[0])

        i = 1
        while inputLines[i][2:8] != "oameni":

            b = inputLines[i].split(",")

            j = 0
            while b[0][j] != '"':
                j += 1

            props = b[0][:j]
            b[0] = b[0][j:]
            props = props.split()

            bus = BusType(int(props[0]), float(props[1][:-3]), int(props[2][:-3]), int(props[3][:-3]))
            cls.buses.update({bus.id: bus})

            if cls.MIN_BUS_PRICE > bus.price:
                cls.MIN_BUS_PRICE = bus.price

            if cls.MAX_BUS_PRICE < bus.price:
                cls.MAX_BUS_PRICE = bus.price

            if cls.MIN_BUS_TRAVEL_TIME > bus.timeBetweenLocations:
                cls.MIN_BUS_TRAVEL_TIME = bus.timeBetweenLocations

            for loc in b:
                loc = loc[1:-1]

                if loc not in cls.locations.keys():

                    newLoc = Location(loc)
                    cls.locations.update({newLoc.name: newLoc})

                bus.route.append(loc)

            busNr = 0   # index ul fiecarui autobuz

            for min in range(cls.START_TIME, cls.END_TIME + 1, bus.timeOfLeaving):

                r = bus.routeIterator()
                for min2 in range(min, cls.END_TIME + 1, bus.timeBetweenLocations):

                    (prevLocationName, currentLocationName, nextLocationName) = next(r)

                    if bus.id not in cls.locations[currentLocationName].buses.keys():
                        cls.locations[currentLocationName].buses.update({bus.id: bus})

                    if min2 in cls.locations[currentLocationName].schedule.keys():
                        cls.locations[currentLocationName].schedule[min2].append((bus.id, busNr, prevLocationName, nextLocationName))
                    else:
                        cls.locations[currentLocationName].schedule.update({min2: [(bus.id, busNr, prevLocationName, nextLocationName)]})

                busNr += 1

                r = bus.routeIterator(reverse=True)
                for min2 in range(min, cls.END_TIME + 1, bus.timeBetweenLocations):

                    (prevLocationName, currentLocationName, nextLocationName) = next(r)

                    if bus.id not in cls.locations[currentLocationName].buses.keys():
                        cls.locations[currentLocationName].buses.update({bus.id: bus})

                    if min2 in cls.locations[currentLocationName].schedule.keys():
                        cls.locations[currentLocationName].schedule[min2].append((bus.id, busNr, prevLocationName, nextLocationName))
                    else:
                        cls.locations[currentLocationName].schedule.update({min2: [(bus.id, busNr, prevLocationName, nextLocationName)]})

                busNr += 1

            i += 1

        i += 1
        while i < len(inputLines):

            if len(inputLines[i]) == 0:
                break

            p = inputLines[i].split(",")

            j = 0
            while p[0][j] != '"':
                j += 1

            props = p[0][:j]
            p[0] = p[0][j:]
            props = props.split()

            person = Person(props[0], int(props[1][:-3]))
            cls.persons.update({person.name: person})

            for loc in p:
                loc = loc[1:-1]

                if loc not in cls.locations.keys():
                    raise ValueError(f"persoana {person.name} merge prin locatia neexistenta {loc}")

                person.personalRoute.append(loc)

            person.allowedBuses = set(cls.locations[person.personalRoute[0]].buses.keys())
            person.personalState = "IN STATIE"
            person.currentLocationName = person.personalRoute[0]
            person.personalRoute.pop(0)     # prima statie e eliminata deoarece incepe din ea

            i += 1


class State:

    def __init__(self, currentMinute, activePersons):

        self.currentMinute = currentMinute
        self.persons = activePersons  # [person, ...] - voi retine cate o copie a unui obiect de tip persoana pt fiecare state
        self.parentState = None

        self.hval = 0
        self.gtime = 0
        self.gmoney = 0

        self.nextNodes = []     # [state, ...]

        self.printStatus = ""

    def __hash__(self):
        return hash(self.getStateKey())

    def __eq__(self, other):
        return self.getStateKey() == other.getStateKey()

    def isFinalState(self):
        return self.persons == []

    def nextStateGenerator(self, heuristicFct):

        # calculez cel mai apropiat moment de decizie dintre toate disponibile (ex daca sa coboare sau nu etc)
        # incepand cu momentul curent (self.currentMinute)
        # iau acea decizie da/ nu, dar daca sunt mai multe minime
        # iau toate combinatiile posibile

        # verificari pentru a vedea daca starea este valida/ mai poate fi extinsa

        # verific daca nu s-a incheiat ziua
        if self.currentMinute >= Info.END_TIME:
            return None

        # verific daca exista vreo persoana care a ramas fara bani dar mai are statii de parcurs
        for person in self.persons:
            if len(person.personalRoute) > 0 >= person.money:
                return None

        # verific daca exista vreo persoana care are allowedBuses gol
        # adica daca a asteptat in statie si a refuzat toate autobuzele

        for person in self.persons:
            if person.personalState == "IN STATIE" and bool(person.allowedBuses) is False:
                return None

        # calculez cel mai apropiat eveniment (cele mai apropiate daca sunt mai multe cu timp minim)
        # minDecisionTime contine timpul absolut, nu relativ (exact ora din zi, nu decalajul fata de momentul actual)

        minDecisionTime = float('inf')

        # chair daca o decizie defapt nu e o decizie reala (ex nu poate urca in autobuz pentru ca e deja cineva acolo)
        # tot il voi lua in calcul, si voi genera in cel mai rau caz o singura stare urmatoare
        # acest fapt ma va interesa doar cand "iau decizia" (cand construiesc efectiv starile urmatoare)
        # fac asta pentru a pastra logica pe fiecare stare cat mai simpla

        # mai intai determin timpul minim de decizie
        for person in self.persons:

            if person.personalState == "PE TRASEU":
                if person.timeForArrival < minDecisionTime:
                    minDecisionTime = person.timeForArrival

            elif person.personalState == "IN STATIE":
                # in acest caz vad care autobuz va ajunge cel mai repede in statie
                # indiferent daca are o persoana deja in el sau nu

                found = False   # variabila care ma ajuta sa ies din for uri

                currentLocation = Info.locations[person.currentLocationName]
                for minute in range(self.currentMinute, Info.END_TIME):

                    if minute in currentLocation.schedule.keys():
                        for busInfo in currentLocation.schedule[minute]:

                            if busInfo[0] in person.allowedBuses:

                                minDecisionTime = minute
                                found = True
                                break

                    if found is True:
                        break

        # daca cel mai apropiat moment de decizie ar depasi
        # finalul zilei, inseamna ca nu mai pot avea succesori

        if minDecisionTime > Info.END_TIME or minDecisionTime == float('inf'):
            return None

        nextStates = []

        # iau doar una din deciziile cu timp minim
        # voi avea (cel mult) 2 succesori: cel in care evenimentul a avut loc (daca se poate),
        #                                  altul in care nu a avut loc
        print(self.currentMinute)
        for personIndex in range(len(self.persons)):

            person = self.persons[personIndex]
            #print(person.personalState)
            if person.personalState == "PE TRASEU":

                if person.timeForArrival == minDecisionTime:

                    # mai intai ma ocup de eventNotHappenedState
                    # cu siguranta voi putea sa nu cobor la urmatoarea statie
                    # (nu exista constrangeri pt a forta pasagerul sa coboare)

                    eventNotHappenedState = copy.deepcopy(self)
                    eventNotHappenedPerson = eventNotHappenedState.persons[personIndex]

                    arrivalLocation = Info.locations[person.nextLocationName]

                    busesList = arrivalLocation.schedule[minDecisionTime]

                    # gasesc autobuzul curent in schedule ul locatiei
                    busSch = None  # (bus id, bus nr, previous location, next location)
                    for b in busesList:
                        if b[0] == person.currentBus and b[2] == person.previousLocationName:
                            busSch = b

                    eventNotHappenedPerson.previousLocationName = arrivalLocation.name
                    eventNotHappenedPerson.nextLocationName = busSch[3]
                    eventNotHappenedPerson.timeForArrival = Info.buses[busSch[0]].timeBetweenLocations + minDecisionTime

                    eventNotHappenedState.currentMinute = minDecisionTime
                    eventNotHappenedState.parentState = self
                    eventNotHappenedState.gtime += minDecisionTime - self.currentMinute
                    eventNotHappenedState.hval = heuristicFct(eventNotHappenedState)

                    nextStates.append(eventNotHappenedState)

                    # acum ma ocup de eventHappenedState

                    # verific daca este vreo persoana care asteapta in statia
                    # unde persoana curenta ar putea sa coboare
                    # daca este, nu va putea cobora
                    # intrucat cu siguranta persoana care e in statie
                    # va putea urca in alt autobuz intr un timp >= momentul cand persoana curenta ajunge in dreptul statiei

                    canLeaveBus = True

                    for otherPersonIndex in range(len(self.persons)):
                        if otherPersonIndex != personIndex:

                            otherPerson = self.persons[otherPersonIndex]
                            if otherPerson.personalState == "IN STATIE" and otherPerson.currentLocationName == person.nextLocationName:
                                canLeaveBus = False
                                break

                    if canLeaveBus is True:

                        eventHappenedState = copy.deepcopy(self)
                        eventHappenedPerson = eventHappenedState.persons[personIndex]

                        if eventHappenedPerson.nextLocationName == person.personalRoute[0]:
                            eventHappenedPerson.personalRoute.pop(0)

                        if len(eventHappenedPerson.personalRoute) == 0:

                            eventHappenedState.persons.pop(personIndex)

                            eventHappenedState.printStatus += f"persoana {eventHappenedPerson.name} a coborat in statia" \
                                                              f" {eventHappenedPerson.nextLocationName} si si-a terminat traseul\n"

                        else:
                            eventHappenedPerson.personalState = "IN STATIE"
                            eventHappenedPerson.currentLocationName = eventHappenedPerson.nextLocationName
                            eventHappenedPerson.allowedBuses = set(arrivalLocation.buses.keys())

                            eventHappenedPerson.timeForArrival = 0
                            eventHappenedPerson.currentBus = None
                            eventHappenedPerson.currentBusNr = 0
                            eventHappenedPerson.nextLocationName = None
                            eventHappenedPerson.previousLocationName = None

                            eventHappenedState.printStatus += f"persoana {eventHappenedPerson.name} a coborat in statia" \
                                                              f" {eventHappenedPerson.currentLocationName}\n"

                        eventHappenedState.currentMinute = minDecisionTime
                        eventHappenedState.parentState = self
                        eventHappenedState.gtime += minDecisionTime - self.currentMinute
                        eventHappenedState.hval = heuristicFct(eventHappenedState)

                        nextStates.append(eventHappenedState)

                    if len(nextStates) < 2:
                        return None
                    return nextStates

            elif person.personalState == "IN STATIE":

                busesList = Info.locations[person.currentLocationName].schedule
                if minDecisionTime in busesList.keys():

                    # mai intai tratez cazul cand ramane in statie
                    # si refuza un singur autobuz dintre toate care ar veni in acel moment in statie
                    # pentru ca aceasta noua stare la randul ei sa poata lua in calcul
                    # urcarea persoanei in alt autobuz care ajunge in statie in acelasi moment
                    # sau nu

                    eventNotHappenedState = copy.deepcopy(self)
                    eventNotHappenedPerson = eventNotHappenedState.persons[personIndex]

                    allBusesSch = busesList[minDecisionTime]  # [(bus id, bus nr, previous location, next location)]
                    for busSch in allBusesSch:
                        if busSch[0] in eventNotHappenedPerson.allowedBuses:

                            eventNotHappenedPerson.allowedBuses.remove(busSch[0])
                            break

                    eventNotHappenedState.currentMinute = minDecisionTime
                    eventNotHappenedState.parentState = self
                    eventNotHappenedState.gtime += minDecisionTime - self.currentMinute
                    eventNotHappenedState.hval = heuristicFct(eventNotHappenedState)

                    nextStates.append(eventNotHappenedState)

                    # acum tratez cazul cand (vrea sa) ia un autobuz

                    for busSch in allBusesSch:
                        if busSch[0] in person.allowedBuses:

                            canTakeBus = True

                            # verific daca autobuzul ajuns contine alt om sau nu

                            for otherPersonIndex in range(len(self.persons)):
                                if otherPersonIndex != personIndex:

                                    otherPerson = self.persons[otherPersonIndex]
                                    if otherPerson.personalState == "PE TRASEU" and otherPerson.currentBus == busSch[0] \
                                            and otherPerson.currentBusNr == busSch[1] and \
                                            otherPerson.previousLocationName == busSch[2] and otherPerson.nextLocationName == busSch[3]:

                                        canTakeBus = False
                                        break

                            # verific daca are bani sa urce in autobuz sau nu

                            if Info.buses[busSch[0]].price > person.money:
                                canTakeBus = False

                            if canTakeBus is True:

                                eventHappenedState = copy.deepcopy(self)
                                eventHappenedPerson = eventHappenedState.persons[personIndex]

                                eventHappenedPerson.money -= Info.buses[busSch[0]].price

                                eventHappenedPerson.personalState = "PE TRASEU"
                                eventHappenedPerson.timeForArrival = minDecisionTime + Info.buses[busSch[0]].timeBetweenLocations
                                eventHappenedPerson.currentBus = busSch[0]
                                eventHappenedPerson.currentBusNr = busSch[1]
                                eventHappenedPerson.nextLocationName = busSch[3]
                                eventHappenedPerson.previousLocationName = eventHappenedPerson.currentLocationName

                                eventHappenedPerson.currentLocationName = None
                                eventHappenedPerson.allowedBuses = set()

                                # cateva procesari pentru afisare

                                currentStationIndex = Info.buses[busSch[0]].route.index(person.currentLocationName)
                                remainingRouteForPrinting = Info.buses[busSch[0]].route[currentStationIndex + 1:]

                                eventHappenedState.printStatus += f"persoana {eventHappenedPerson.name} a urcat in" \
                                                                  f"autobuzul cu numarul {busSch[0]} care are ruta" \
                                                                  f"{remainingRouteForPrinting};\n"

                                # -----------

                                eventHappenedState.currentMinute = minDecisionTime
                                eventHappenedState.parentState = self
                                eventHappenedState.gtime += minDecisionTime - self.currentMinute
                                eventHappenedState.gmoney += Info.buses[busSch[0]].price
                                eventHappenedState.hval = heuristicFct(eventHappenedState)

                                nextStates.append(eventHappenedState)

                if len(nextStates) < 2:
                    return None
                return nextStates

        if not nextStates:
            return None
        else:
            return nextStates

    def printPath(self, output):

        if self.parentState is not None:
            self.parentState.printPath(output)

        output.write(self.printStatus)

    def getFval(self):
        return self.gmoney + self.gtime + self.hval

    # metoda folosita pentru a verifica daca doua stari sunt egale
    # voi lua in calcul doar persoanele din stare, iar din persoane la randul lor
    # doar anumite atribute
    # metoda va fi folosita pentru a* cand verific daca deja am mai ajuns odata in acea stare
    # va returna un string al proprietatilor, care va fi folosita pentru a calcula hash ul starii
    def getStateKey(self):

        keyString = ""

        # trebuie sa ma asigur ca voi construi string ul cheie
        # cu persoanele in aceeasi ordine
        # le voi sorta dupa nume, presupunand ca au nume distincte

        auxPersons = copy.deepcopy(self.persons)
        auxPersons.sort(key=lambda e : e.name)

        for person in auxPersons:

            keyString += person.name
            keyString += str(person.money)
            keyString += str(person.personalRoute)
            keyString += person.personalState

            if person.personalState == "PE TRASEU":

                keyString += str(person.timeForArrival - self.currentMinute) # ma intereseaza doar distanta relativa fata de destinatie
                keyString += str(person.currentBus)
                keyString += str(person.currentBusNr)

                if person.previousLocationName is None:
                    keyString += "None"
                else:
                    keyString += person.previousLocationName

                keyString += person.nextLocationName

            elif person.personalState == "IN STATIE":

                keyString += person.currentLocationName
                keyString += str(person.allowedBuses)

            keyString += "_"

        return keyString

    @staticmethod
    def cmp(fstState, sndState):
        return (fstState.gtime + fstState.gmoney + fstState.hval) < (sndState.gtime + sndState.gmoney + sndState.hval)

    @staticmethod
    def UCS(_):
        return 0

    # euristica banala
    # returneaza numarul de oameni care nu si au terminat traseul
    @staticmethod
    def simpleHeuristic(state):
        return len(state.persons)

    # prima euristica admisibila
    # fac o suma, pentru fiecare om adun la suma
    # (nr statii ramase de parcurs - 1) * pret minim pe bilet
    # este admisibila deoarece
    # reprezinta exact costul cand o persoana
    # este intr un autobuz presupus de timp de calatorie intre statii 0
    # si cu pretul minim dintre toate autobuzele
    # si toate statiile de pe drum sunt fix cele ramase din traseu (le fiecare coboara si urca instantaneu inapoi)
    @staticmethod
    def fstAdmHeuristic(state):

        h = 0
        for person in state.persons:
            h += Info.MIN_BUS_PRICE * (len(person.personalRoute) - 1)

        return h

    # a doua euristica admisibila
    # aproape la fel ca prima
    # dar iau in calcul si timpul intre statii
    # cea mai potrivita euristica dintre toate prezentate
    # este admisibila deoarece
    # reprezinta exact costul cand o persoana este in autobuzul cu timp minim si cu pretul minim
    # dintre toate autobuzele (presupunand ca cel cu cost minim are si timp minim de parcurgere intre statii)
    # si toate statiile de pe drum sunt fix cele ramase din traseu (le fiecare coboara si urca instantaneu inapoi)
    @staticmethod
    def sndAdmHeuristic(state):

        h = 0
        for person in state.persons:
            h += Info.MIN_BUS_PRICE * (len(person.personalRoute) - 1)
            h += Info.MIN_BUS_TRAVEL_TIME * (len(person.personalRoute) - 1)

        return h

    # euristica neadmisibila
    # fac o suma, pentru fiecare om adun la suma
    # (nr statii ramase de parcurs) * pret MAXIM pe bilet
    # nu este admisibila, dau un contraexemplu
    # cand am toate autobuzele cu cost 1, si unul cu cost 10000000
    # iar cel putin o parte din calatori vor folosi doar autobuze de cost 1
    # euristica va intoarce cel mai probabil o valoare mult mai mare fata de valoarea reala a drumului
    @staticmethod
    def notAdmHeuristic(state):

        h = 0
        for person in state.persons:
            h += Info.MAX_BUS_PRICE * len(person.personalRoute)

        return h


# am folosit totusi openset optimizat
# dar nu am mai folosit closedset
# am optimizat openset pentru ca 1. nu exista nici un motiv pentru care sa nu il optimizez
#                                2. functiile de hash si eq sunt adaptate pentru astarOpenClosed si ar aparea probleme aici
def astar(heuristicFct, timeout, NSOL=Info.NSOL):

    startTime = time.time()
    output = open("astar" + str(Info.NSOL) + ".txt", "w")

    if NSOL <= 0:
        return

    startState = State(Info.START_TIME, list(Info.persons.values()))

    openStates = PriorityQueue([startState], State.cmp)

    while not openStates.empty():

        currentState = openStates.getMin()

        if time.time() - startTime > timeout:

            output.write(f"no solution found in {timeout} seconds; printing left stations for every person\n")

            for person in currentState.persons:
                output.write(str(person))
                output.write('\n')

            output.close()
            return

        if currentState.isFinalState():

            currentState.printPath(output)

            NSOL -= 1
            if NSOL == 0:
                return

        currentState.nextNodes = currentState.nextStateGenerator(heuristicFct)
        if currentState.nextNodes is not None:

            for nextState in currentState.nextNodes:

                if nextState not in openStates.pos.keys():
                    openStates.push(nextState)

                elif nextState in openStates.pos.keys() and State.cmp(nextState, openStates.heap[openStates.pos[nextState]]):

                    openStates.pop(nextState)
                    openStates.push(nextState)

    output.write("no solution found")
    output.close()


def astarOpenClosed(heuristicFct, timeout, NSOL=Info.NSOL):

    startTime = time.time()
    output = open("astarOpenClosed" + str(Info.NSOL) + ".txt", "w")

    if NSOL <= 0:
        return

    startState = State(Info.START_TIME, list(Info.persons.values()))

    openStates = PriorityQueue([startState], State.cmp)
    closedStates = {}   # {state: state}    -- functia de hash cuprinde in mod intentionat doar o parte din atribute
                        #                      prin functia getStateKey
                        #                      deci are sens sa am un astfel de dictionar

    while not openStates.empty():

        currentState = openStates.getMin()

        if time.time() - startTime > timeout:

            output.write(f"no solution found in {timeout} seconds; printing left stations for every person\n")

            for person in currentState.persons:
                output.write(str(person))
                output.write('\n')

            output.close()
            return

        closedStates.update({currentState: currentState})

        if currentState.isFinalState():

            output.write(f"stare finala atinsa: cost timp {currentState.gtime}, cost bani {currentState.gmoney}\n")
            currentState.printPath(output)

            NSOL -= 1
            if NSOL == 0:
                return

        currentState.nextNodes = currentState.nextStateGenerator(heuristicFct)
        if currentState.nextNodes is not None:

            for nextState in currentState.nextNodes:

                if nextState not in openStates.pos.keys() and nextState not in closedStates.keys():
                    openStates.push(nextState)

                elif nextState in openStates.pos.keys() and (State.cmp(nextState, openStates.heap[openStates.pos[nextState]]) is True):
                    print("here0")
                    openStates.pop(nextState)
                    openStates.push(nextState)

                elif nextState in closedStates.keys() and (State.cmp(nextState, closedStates[nextState]) is True):
                    print("here")
                    closedStates.pop(nextState)
                    openStates.push(nextState)

    output.write("no solution found")
    output.close()


#def idastar(heuristicFct, timeout, NSOL=Info.NSOL):


#----------------------------------------------------------------


Info.parseInput()
astarOpenClosed(State.UCS, 30)
























