import copy
import math
import sys
import os
from timeit import default_timer
import stopit


# informatii despre un nod din arborele de parcurgere (nu din graful initial)
class NodParcurgere:
    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  # consider cost=1 pentru o mutare
        self.h = h
        self.f = self.g + self.h

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, timp, lung):  # returneaza si lungimea drumului
        # f.write("Solutie cu A*: " + "\n")
        f.write("Timp: " + str(timp) + "\n")
        f.write("Lungime vector: " + str(lung) + "\n")
        # l = self.obtineDrum()
        f.write("Cost: " + str(self.g) + "\n")
        f.write("Lungime: " + str(len(self.obtineDrum())))
        f.write("\n--------------------------------\n\n")

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte
        return False

    def __repr__(self):
        sir = ""
        sir += str(self.info)
        return sir

    def __str__(self):
        sir = ""
        for linie in self.info:
            sir += " ".join([str(elem) for elem in linie]) + "\n"
        sir += "\n"
        return sir


class Graph:  # graful problemei
    def __init__(self, nume_fisier):
        f = open(nume_fisier, "r")
        sirFisier = f.read()
        try:
            listaLinii = sirFisier.strip().split("\n")
            self.start = []
            for linie in listaLinii:
                self.start.append([x for x in linie.strip().split(" ")])  # citim graful
        except:
            f.write("Eroare la parsare!" + "\n")
            print("Eroare la parsare!")
            sys.exit(0)  # iese din program

    def nuAreSolutii(self, infoNod):
        listaMatrice = sum(infoNod, [])
        nrInversiuni = 0
        for i in range(len(listaMatrice)):
            if listaMatrice[i] != 0:
                for j in range(i + 1, len(listaMatrice)):
                    if listaMatrice[j] != 0:
                        if listaMatrice[i] > listaMatrice[j]:
                            nrInversiuni += 1
        return nrInversiuni % 2 == 1

    def genereazaSuccesori(self, nodCurent, tip_euristica):  # va genera succesorii sub forma de noduri in arborele de parcurgere
        listaSuccesori = []
        cGol = lGol = -1
        for lGol in range(1, len(nodCurent.info)):
            try:
                cGol = nodCurent.info[lGol].index('0')
                break
            except:
                pass
        if lGol < 0 or cGol < 0:
            f.write("Nu are solutii!\n--------------------------------\n")

        directii = [[lGol, cGol - 1], [lGol, cGol + 1], [lGol - 1, cGol], [lGol + 1, cGol]]  # stanga, dreapta, sus, jos
        for lPlacuta, cPlacuta in directii:
            if 1 <= lPlacuta <= 3 and 1 <= cPlacuta <= 3:
                copieMatrice = copy.deepcopy(nodCurent.info)
                copieMatrice[lGol][cGol] = copieMatrice[lPlacuta][cPlacuta]
                copieMatrice[lPlacuta][cPlacuta] = '0'
                if not nodCurent.contineInDrum(copieMatrice):  # and not self.nuAreSolutii(copieMatrice):
                    costArc = 1
                    listaSuccesori.append(NodParcurgere(copieMatrice, nodCurent, nodCurent.g + costArc,
                                                        self.calculeaza_h(copieMatrice, tip_euristica)))
        return listaSuccesori

    def calculeazaIesire(self):
        n = len(self.start)
        for i in range(n):
            if self.start[0][i] != '#':
                return 1, i
            elif self.start[n-1][i] != '#':
                return n-2, i
            elif self.start[i][0] != '#':
                return i, 1
            elif self.start[i][n-1] != '#':
                return i, n-2

    def testeaza_scop(self, nodCurent, x, y):
        return nodCurent.info[x][y] == '1'

    def calculeaza_h(self, infoNod, tip_euristica):
        # if infoNod in self.scopuri:
        #     return 0
        if tip_euristica == "euristica banala":  # euristica banală: daca nu e stare scop, returnez 1, altfel 0
            return 1

        # euristica manhattan
        elif tip_euristica == "euristica nebanala":
            h = 0
            for lPlacutaC in range(len(infoNod)):
                for cPlacutaC in range(len(infoNod[0])):
                    if infoNod[lPlacutaC][cPlacutaC] != '0' and infoNod[lPlacutaC][cPlacutaC] != '#':
                        placuta = infoNod[lPlacutaC][cPlacutaC]
                        lPlacutaF = (int(placuta) - 1) // len(infoNod[0])
                        cPlacutaF = (int(placuta) - 1) % len(infoNod[0])
                        h += abs(lPlacutaF - lPlacutaC) + abs(cPlacutaF - cPlacutaC)
            return h

        # TODO, euristica euclidiana
        # elif tip_euristica == "euristica euclidiana":
        #     x, y = gr.calculeazaIesire()
        #     print(infoNod)
        #     x1, y1 = infoNod
        #     dx = abs(x1 - x)
        #     dy = abs(y1 - y)
        #     return math.sqrt(dx * dx + dy * dy)

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return sir


def uniform_cost(gr, nrSolutiiCautate, timeout):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    time = timeout
    start = default_timer()
    lung = 0
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, "euristica banala"))]
    x, y = gr.calculeazaIesire()
    cnt = 0
    while len(c) > 0:
        nodCurent = c.pop(0)
        if len(c) > lung:
            lung = len(c)
        f.write("Pas: " + str(cnt) + "\n" + str(nodCurent))
        cnt += 1
        moment = default_timer()
        if moment - start > time:
            f.write("Timeout!\n--------------------------------\n")
            break

        if gr.testeaza_scop(nodCurent, x, y):
            stop = default_timer()
            timp = stop - start
            f.write("Solutie cu UCS: " + "\n")
            nodCurent.afisDrum(timp, lung)
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return

        lSuccesori = gr.genereazaSuccesori(nodCurent, "euristica banala")
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # ordonez dupa cost(notat cu g aici și în desenele de pe site)
                if c[i].g > s.g:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


def a_star(gr, nrSolutiiCautate, tip_euristica, timeout):
    time = timeout
    start = default_timer()
    lung = 0
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))]  # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    x, y = gr.calculeazaIesire()
    cnt = 0
    while len(c) > 0:
        nodCurent = c.pop(0)
        if len(c) > lung:
            lung = len(c)
        f.write("Pas: " + str(cnt) + "\n" + str(nodCurent))
        cnt += 1
        moment = default_timer()
        if moment - start > time:
            f.write("Timeout!\n--------------------------------\n")
            break

        if gr.testeaza_scop(nodCurent, x, y):
            stop = default_timer()
            timp = stop - start
            f.write("Solutie cu A*: " + "\n")
            nodCurent.afisDrum(timp, lung)
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return

        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                if c[i].f >= s.f:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


def a_star_opt(gr, nrSolutiiCautate, tip_euristica, timeout):
    time = timeout
    start = default_timer()
    lung = 0
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))]  # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    x, y = gr.calculeazaIesire()
    cnt = 0
    while len(c) > 0:
        nodCurent = c.pop(0)
        if len(c) > lung:
            lung = len(c)
        f.write("Pas: " + str(cnt) + "\n" + str(nodCurent))
        cnt += 1
        moment = default_timer()
        if moment - start > time:
            f.write("Timeout!\n--------------------------------\n")
            break

        if gr.testeaza_scop(nodCurent, x, y):
            stop = default_timer()
            timp = stop - start
            f.write("Solutie cu A* optim: " + "\n")
            nodCurent.afisDrum(timp, lung)
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return

        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        for s in lSuccesori:
            gasitC = False
            for nodC in c:
                if s.info == nodC.info:
                    gasitC = True
                    if s.f >= nodC.f:
                        lSuccesori.remove(s)
                    else:  # s.f<nodC.f
                        c.remove(nodC)
                    break
            if not gasitC:
                for nodC in c:
                    if s.info == nodC.info:
                        if s.f >= nodC.f:
                            lSuccesori.remove(s)
                        else:  # s.f<nodC.f
                            c.remove(nodC)
                        break
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez crescator dupa f
                # daca f-urile sunt egale ordonez descrescator dupa g
                if c[i].f > s.f or (c[i].f == s.f and c[i].g <= s.g):
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


if __name__ == "__main__":  # python Klotski8.py
    for i in range(len(sys.argv)):
        input = sys.argv[1]  # C:\Users\mihai\Desktop\Serios\Projects\pythonProject\IA\input_astar
        output = sys.argv[2]  # C:\Users\mihai\Desktop\Serios\Projects\pythonProject\IA\output_astar
        nrSolutiiCautate = int(sys.argv[3])  # 1
        time_out = float(sys.argv[4])  # 0.02

    for numeFisier in os.listdir(input):
        gr = Graph(input + '/' + numeFisier)
        # if not os.path.exists("output_" + numeFisier):
        #     os.mkdir("output_" + numeFisier)
        numeFisierOutput = "output_" + numeFisier
        f = open(output + '/' + numeFisierOutput, "w")

        uniform_cost(gr, nrSolutiiCautate, timeout=time_out)
        a_star(gr, nrSolutiiCautate, tip_euristica="euristica nebanala", timeout=time_out)
        a_star(gr, nrSolutiiCautate, tip_euristica="euristica banala", timeout=time_out)
        # a_star(gr, nrSolutiiCautate, tip_euristica="euristica euclidiana", timeout=time_out)
        a_star_opt(gr, nrSolutiiCautate, tip_euristica="euristica nebanala", timeout=time_out)
        a_star_opt(gr, nrSolutiiCautate, tip_euristica="euristica banala", timeout=time_out)

        f.close()
