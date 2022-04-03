import re
import bisect
import time


n = 132428


class Cli:

    def __init__(self, filename=None, source=None):
        if(source and filename):
            r = re.compile(r'\[\[(.*?)(\|.*?)?\]\]')
            positions = bfs(source, r, filename)
            bfs_serialization(positions)
            c, l, i = cli(source, r, filename, positions)
            self.c = c
            self.l = l
            self.i = i
        else:
            self.c = []
            self.l = []
            self.i = []
            self.deserialize()
    # Serialisation de la CLI
    def serialize(self):
        file_c = open("dump/c.dump", "a")
        file_l = open("dump/l.dump", "a")
        file_i = open("dump/i.dump", "a")

        for i in self.c:
            file_c.write(str(i)+"\n")
        for i in self.l:
            file_l.write(str(i)+"\n")
        for i in self.i:
            file_i.write(str(i)+"\n")
        file_c.close()
        file_l.close()
        file_i.close()
    # Deserialisation de la CLI
    def deserialize(self):
        with open("dump/c.dump", "r", encoding="utf-8") as file_c:
            for line in file_c:
                self.c += [(float(line))]
        with open("dump/l.dump", "r") as file_l:
            for line in file_l:
                self.l += [int(line)]
        with open("dump/i.dump", "r") as file_i:
            for line in file_i:
                self.i += [int(line)]
    # Produit matrice vecteur
    def matrix_prod(self, v, epsilon):
        p = [0 for i in range(n)]
        s = 0
        for i in range(n):
            if self.c[i] == self.c[i+1]:
                s += v[i]
            else:
                for j in range(self.l[i], self.l[i+1]):
                    p[self.i[j]] += self.c[j] * v[i]
        s = s/n
        for i in range(n):
            p[i] = (1-epsilon)*(p[i]+s)+(epsilon/n)
        return p
    # Calcul du pagerank
    def pagerank(self, epsilon):
        pi = [1/n for i in range(n)]
        for i in range(50):
            pi = self.matrix_prod(pi, epsilon)
        return pi
    # Serialisation du pagerank
    def serialize_pagerank(self):
        l = self.pagerank(0.15)
        with open("dump/pagerank.dump", "a", encoding="utf-8") as pr:
            for i in l:
                pr.write(str(i)+"\n")

# Deserialisation du page rank
def deserialize_pagerank():
    l = []
    with open("dump/pagerank.dump", "r") as pr:
        for i in pr:
            l += [float(i)]
    return l

# Serialisation du bfs
def bfs_serialization(positions):
    bfs_file = open("dump/bfs_file", "a")
    for elt in positions:
        pos, index = positions[elt]
        bfs_file.write(elt + "->" + str(pos) + " " + str(index) + "\n")
    bfs_file.close()

# Deserialisation du bfs
def bfs_deserialization():
    with open("dump/bfs_file", "r", encoding="utf-8") as f:
        positions = dict()
        for line in f:
            sp = line.split('->')
            title = sp[0]
            index, pos = sp[1].split(' ')
            pos = pos.strip()
            positions[title] = (index, pos)
    return positions


def extract_group(lg):
    s = set()
    for elt in lg:
        s.add(elt[0])
    return s


def add_queue(lg, queue):
    for elt in extract_group(lg):
        queue.append(elt)

# création du dictionnaire de positions
def pages_position(filename):
    dic = dict()
    z = 0
    with open(filename, encoding='utf-8') as wiki_file:
        line = wiki_file.readline()
        while line:
            if "<page>" in line:
                z += 1
                print(z)
                line = wiki_file.readline()
                title = get_title_from_line(line)
                dic[title] = (wiki_file.tell(), -1)
            else:
                line = wiki_file.readline()
    return dic


def get_title_from_line(l):
    reg = re.compile(r'.*<title>(.*?)<\/title>')
    return reg.match(l).group(1)


def get_page_by_title(t, filename):
    with open(filename, encoding='utf-8') as wiki_file:
        line = wiki_file.readline()
        while line:
            if "<page>" in line:
                prev_pos = wiki_file.tell()  # we are at l pos
                title = get_title_from_line(
                    wiki_file.readline())  # we are at l + 1 pos
                if title == t:
                    return wiki_file.tell()
                else:
                    wiki_file.seek(prev_pos)  # we go back to l pos
            line = wiki_file.readline()


def bfs(title, r, filename):
    position = pages_position(filename)
    visited = []
    index = 0
    queue = [title]
    while queue:
        t = queue.pop()
        if t in position and t not in visited:
            visited.append(t)
            pos = position[t][0]
            position[t] = (pos, index)
            index += 1
            with open(filename, encoding='utf-8') as page:
                page.seek(position[t][0])
                for line in page:
                    if "</page>" in line:
                        break
                    lg = r.findall(line)
                    add_queue(lg, queue)
    return position

def add_queue_cli(c, l, i, lg, queue, dic, l_index):
    count = 0
    for elt in extract_group(lg):
        if elt in dic:
            i.append(dic[elt][1])
            queue.append(elt)
            count += 1
    for j in range(count):
        c.append(1/count)
    l.append(l[l_index] + count)


def cli(title, r, filename, dic):
    queue = [title]
    visited = []
    l_index = 0
    c = []
    l = [0]
    i = []
    while queue:
        t = queue.pop()
        print(l_index)
        if dic[t][1] not in visited:
            bisect.insort(visited, dic[t][1])
            with open(filename, encoding='utf-8') as page:
                txt = ""
                page.seek(dic[t][0])
                for line in page:
                    txt += line
                    if "</page>" in line:
                        break
                lg = r.findall(txt)
                add_queue_cli(c, l, i, lg, queue, dic, l_index)
                l_index += 1
    return (c, l, i)


'''
[1.0, 1.0, 0.5, 0.5]                                                                                                                  
[0, 1, 2, 4, 4]                                                                                                                       
[1, 2, 1, 3]
'''

# r = re.compile(r'\[\[(.*?)(\|.*?)?\]\]')
# positions = bfs("sport", r, "corpus.xml")
# bfs_serialization(positions)
# cli = Cli()
# cli.serialize()
# cli.serialize_pagerank()
# print(sum(deserialize_pagerank()))
