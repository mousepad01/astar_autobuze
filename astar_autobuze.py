import copy


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

        self.__heap = [None]
        for newElement in initArr:
            try:
                self.push(newElement)
            except ValueError:
                raise ValueError(f"found duplicate in initialisation array, element {newElement}")

    def __repr__(self):

        st = ''
        for el in self.__heap[1:]:
            st += repr(el) + ' '

        return st[:-1]

    def __swapElsByPos(self, pos1, pos2):

        aux = self.__heap[pos1]
        self.__heap[pos1] = self.__heap[pos2]
        self.__heap[pos2] = aux

        self.pos[self.__heap[pos2]] = pos2
        self.pos[self.__heap[pos1]] = pos1

    def push(self, element):

        if element in self.pos.keys():
            raise ValueError(f"element already in the queue on heap array position {self.pos[element]}")

        self.__heap.append(element)
        self.pos.update({element: len(self.__heap) - 1})

        self.heapify(element)

    def heapify(self, element):

        try:
            elPos = self.pos[element]
        except KeyError as kerr:
            raise ValueError(f"eroare la ordonarea heap-ului la rearanjare: {kerr}")

        while elPos > 1 and not self.cmp(self.__heap[elPos // 2], self.__heap[elPos]):
            self.__swapElsByPos(elPos, elPos // 2)
            elPos //= 2

        heapSize = len(self.__heap)

        done = False
        while not done:

            if elPos * 2 >= heapSize and elPos * 2 + 1 >= heapSize:
                done = True

            elif elPos * 2 < heapSize <= elPos * 2 + 1:

                if self.cmp(self.__heap[elPos], self.__heap[elPos * 2]):
                    done = True
                else:
                    self.__swapElsByPos(elPos, elPos * 2)
                    elPos *= 2

            else:

                if self.cmp(self.__heap[elPos], self.__heap[elPos * 2 + 1]) and self.cmp(self.__heap[elPos],
                                                                                       self.__heap[elPos * 2]):
                    done = True
                else:

                    if self.cmp(self.__heap[elPos * 2], self.__heap[elPos * 2 + 1]):
                        self.__swapElsByPos(elPos, elPos * 2)
                        elPos *= 2
                    else:
                        self.__swapElsByPos(elPos, elPos * 2 + 1)
                        elPos *= 2
                        elPos += 1

    def peekMin(self):
        return copy.deepcopy(self.__heap[1])

    def getMin(self):
        return self.pop(self.__heap[1])

    def pop(self, element):

        try:
            elPos = self.pos[element]
        except KeyError as kerr:
            raise ValueError(f"eroare la ordonarea heap-ului la stergere: {kerr}")

        heapSize = len(self.__heap)

        self.__swapElsByPos(elPos, heapSize - 1)

        popped = self.__heap.pop(-1)
        self.pos.pop(popped)
        heapSize -= 1

        if not self.empty() and elPos < heapSize:
            self.heapify(self.__heap[elPos])

        return popped

    def empty(self):
        if len(self.__heap) == 1:
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

        while True:

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

            i = -1      # TODO: fix :se dubleaza pozitia finala
            while i >= -l:

                currentLocationName = self.route[i]
                if i == -l:
                    futureLocationName = prevLocationName
                else:
                    futureLocationName = self.route[i - 1]

                yield (prevLocationName, currentLocationName, futureLocationName)

                prevLocationName = currentLocationName
                i -= 1


class Location:

    def __init__(self, name):

        self.name = name
        self.schedule = {}  # {minut: (autobuz.id, locatie anterioare, locatie urmatoare)}

        self.buses = {}     # {bus.id: bus}
                            # autobuzele care trec prin aceasta locatie
                            # le as fi putut dedude din self.schedule, dar preprocesez pentru a optimiza timpul de rulare


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
        self.nextLocationName = None
        self.previousLocationName = None    # pentru a identifica complet in ce autobuz circula
                                            # pentru a evita intersectia persoanelor

        self.currentLocationName = None     # daca asteapta, statia curenta
        self.allowedBuses = {}  # pentru cazul cand asteapta in statie, si a refuzat sa ia un autobuz, il marchez cu false
                                # {autobuz.id: True/False}

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

class Info:

    buses = {}  # {autobuz.id: autobuz}
    locations = {}  # {locatie.nume: locatie}
    persons = {}  # {persoana.nume: persoana}

    START_TIME = 0  # START_TIME si END_TIME intervalul zilei
    END_TIME = 0

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

            for loc in b:
                loc = loc[1:-1]

                if loc not in cls.locations.keys():

                    newLoc = Location(loc)
                    cls.locations.update({newLoc.name: newLoc})

                bus.route.append(loc)

            for min in range(cls.START_TIME, cls.END_TIME + 1, bus.timeOfLeaving):

                r = bus.routeIterator()
                for min2 in range(min, cls.END_TIME + 1, bus.timeBetweenLocations):

                    (prevLocationName, currentLocationName, nextLocationName) = next(r)

                    if bus.id not in cls.locations[currentLocationName].buses.keys():
                        cls.locations[currentLocationName].buses.update({bus.id: bus})

                    cls.locations[currentLocationName].schedule.update({min2: (bus.id, prevLocationName, nextLocationName)})

                r = bus.routeIterator(reverse=True)
                for min2 in range(min, cls.END_TIME + 1, bus.timeBetweenLocations):

                    (prevLocationName, currentLocationName, nextLocationName) = next(r)

                    if bus.id not in cls.locations[currentLocationName].buses.keys():
                        cls.locations[currentLocationName].buses.update({bus.id: bus})

                    cls.locations[currentLocationName].schedule.update({min2: (bus.id, prevLocationName, nextLocationName)})

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

            for b in cls.buses.keys():
                person.allowedBuses.update({b.name: True})

            i += 1


class State:

    def __init__(self, currentMinute, activePersons):

        self.currentMinute = currentMinute
        self.persons = activePersons  # [person, ...] - voi retine cate o copie a unui obiect de tip persoana pt fiecare state
        self.parentState = None

    def isFinalState(self):
        return self.persons == []

    def nextStateGenerator(self):

        # calculez cel mai apropiat moment de decizie dintre toate disponibile (ex daca sa coboare sau nu etc)
        # incepand cu momentul curent (self.currentMinute)
        # iau acea decizie da/ nu, dar daaca sunt mai multe minime
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

        # calculez cel mai apropiat eveniment (cele mai apropiate daca sunt mai multe cu timp minim)

        minDecisionTime = float('inf')
        personEventList = []    # lista in care voi retine momentele de decizie care sunt cele mai apropiate
                                # va retine defapt persoanele, deducand evenimentul din starea lor
                                # deci va fi o submultime a self.persons

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


Info.parseInput()
