import re, sys, math, unicodedata, nltk, pickle, time
from collections import Counter

# nb de pages
D = 132428

# pattern pour la cherche dans le corpus
p_page = re.compile(r'<page>')
p_end_page = re.compile(r'</page>')
p_text = re.compile(r'<text.*>')
p_end_text = re.compile(r'^\s*(.*)</text>')
p_title = re.compile(r'<title>(.*)</title>')

def dico_tf_file():
    return pickle.load(open("relation-mp-v2.p", "rb"))
    
def dico_idf_file():
    dict_idf = {}
    with open("idf", encoding="utf-8") as file:
        for l in file.readlines():
            l = l.split()
            dict_idf[l[0]] = float(l[1])
    return dict_idf


def dico_nd_file():
    dico = {}
    with open("nd", encoding="utf-8") as file :
        for f in file:
            line = f.split("->")
            dico[line[0]] = float(line[1].split()[0])
    return dico


def dico_bfs_file():
    dico = {}
    with open("dump/bfs_file", encoding="utf-8") as file :
        for f in file:
            line = f.split("->")
            value = line[1].split()[1]
            dico[line[0]] = None if value == "-1" else int(value)
    return dico


#chargement en mémoire de la table tf:
dico_tf = dico_tf_file()
dico_idf = dico_idf_file()
dico_nd = dico_nd_file()
dico_bfs = dico_bfs_file()
dico_bfs_nd = {dico_bfs[k]: (k,dico_nd[k]) for k in dico_bfs and dico_nd}

# retourne l'idf du mot si il est présent dans le dico
# sinon 0
def idf(mot: str):
    return dico_idf.get(mot, 0)


#IDF(m) = log10(|D| /{|d € D : m € d|})
def build_idf(l, f_read, dico_bfs):
    idfs = { w:(0, True) for w in l}
    in_page = False
    in_title = False
    compt = 0
    for line in f_read:
        if (r := re.search(p_title, line)) is not None: 
            title = r.group(1)
            if dico_bfs[title] is not None:
                in_title = True 

        elif "<text" in line:
            in_page = True

        elif "</page>" in line and in_title:
            in_page = False
            in_title = False
            for i in idfs:
                idfs[i] = (idfs[i][0], True)
            compt += 1
            print(compt)
        
        elif in_page and in_title:
            if (r := re.search(p_end_text, line)) is not None:
                if r.group(1): 
                    line = r.group(1)

            for word in clean_line(line):
                if word in idfs and idfs[word][1]:
                    idfs[word] = (idfs[word][0]+1, False)

    f_write = open("idf", "w")
    for w in idfs:
        f_write.write(w + " " + str(round(math.log10(D / idfs[w][0]), 2)) + "\n")
    f_write.close()

def clean_line(st: str):
    tokenizer = nltk.RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(st)
    l = [clean_accents(w).lower() for w in tokens]
    return l

def clean_accents(st: str):
    st = unicodedata.normalize('NFKD', st)\
        .encode('ascii', 'ignore')\
        .decode("utf-8")
    
    return str(st)


def nd(file, dico_bfs):
    wordcount = {}
    nd_dico = {}
    compt = 0
    in_page = False
    in_title = False
    title = ""  
    for line in file:
        if (r := re.search(p_title, line)) is not None: 
            title = r.group(1)
            if dico_bfs[title] is not None:
                in_title = True  
            
        elif "<text" in line:
            in_page = True

        elif "</page>" in line and in_title:
            
            v_nd = 0
            for w in wordcount:
                v_nd += math.pow(1 + math.log10(wordcount[w]), 2) 
            
            nd_dico[title+"->"] = str(round(math.sqrt(v_nd), 2))
            wordcount.clear()
            in_page = False
            in_title = False
            compt += 1
            print(compt)

        elif in_page and in_title:
            if (r := re.search(p_end_text, line)) is not None:
                if r.group(1): 
                    line = r.group(1)
                
            for word in clean_line(line):
                if word not in wordcount:
                    wordcount[word] = 1
                else:
                    wordcount[word] += 1

    f = open("nd", "w")
    for k,v in nd_dico.items():
        f.write(k + v + "\n")
    f.close()


def tf(file, l):
    dico_bfs_nd = {k: (dico_bfs[k],dico_nd[k]) for k in dico_bfs and dico_nd}

    wordcount = {}
    tf_dico = {x:[] for x in l}
    in_page = False
    in_title = False
    nd = 0 
    id = 0
    compt = 0
    for line in file:

        if (r := re.search(p_title, line)) is not None: 
            title = r.group(1)
            if dico_bfs_nd.get(title) is not None:
                in_title = True
                id = dico_bfs_nd[title][0]
                nd = dico_bfs_nd[title][1]

        elif "<text" in line:
            in_page = True

        elif "</page>" in line and in_title:
            
            wordcount = {k: wordcount[k] for k in wordcount if k in l}
            
            for w in wordcount:
                tf_normalise = float(round((1 + math.log10(wordcount[w])) / nd , 3))
                tf_dico[w].append((id , tf_normalise))

            in_page = False
            in_title = False
            wordcount.clear()
            compt += 1
            print(compt)
        
        elif in_page and in_title:
            if (r := re.search(p_end_text, line)) is not None:
                if r.group(1): 
                    line = r.group(1)
                    
            for word in clean_line(line):  
                if word not in wordcount:
                    wordcount[word] = 1
                else:
                    wordcount[word] += 1

    f = open("relation-mot-pages", "w")
    for m in tf_dico:
        f.write(m + "->")
        new_list = map(str, tf_dico[m])
        f.write(";".join(new_list) + "\n")
    f.close()


def score_frequence(index, requete):
    nr = norme(requete)
    nd = 0 if dico_bfs_nd.get(index) is None else dico_bfs_nd.get(index, 0)[1]
    sum_tf_idf = 0
    
    for mot in requete:
        idf = dico_idf.get(mot, 0)
        tf = dico_tf.get(mot, 0)
        if tf != 0:
            elm = recherche_dichotomique(index, tf)
            sum_tf_idf += idf * (tf[elm][1] * nd)
    
    return 0 if (nd == 0 or nr == 0) else round(float(sum_tf_idf / (nd * nr)),2)


def recherche_dichotomique(element, liste_triee):
    a = 0
    b = len(liste_triee) - 1
    m = (a+b)//2
    while a < b :
        if liste_triee[m][0] == element :
            return m
        elif liste_triee[m][0] > element :
            b = m-1
        else :
            a = m+1
        m = (a+b)//2
    return a

def norme(requete):
    s_idf = 0
    for mot in requete:
        s_idf += dico_idf.get(mot, 0) ** 2
    return math.sqrt(s_idf)    


def n_pages(file):
    count = 0
    for line in file:
        if re.search(p_page, line) is not None:
            count += 1
    return count

def list_of_words(file):
    content = file.readlines()
    return [x.strip() for x in content]

def remove_duplicate_list():
    tf = pickle.load(open("relation-mp-v2.p", "rb"))
    for i in tf.items():
        i[1].sort(key=lambda x:x[0])
    pickle.dump(tf, open("relation-mp-v2.p", "wb"))


def main():
    #print(dico_tf.get("football"))
    pass

if __name__ == "__main__":
    main()
