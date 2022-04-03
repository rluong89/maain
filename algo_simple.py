import wand, time, tf_idf

dico_tf = tf_idf.dico_tf
pagerank = wand.pageranks
a = wand.alpha


def enum_pages(requete):
    ll = [dico_tf.get(mot) for mot in requete if dico_tf.get(mot)]
   
    matches = []
    pointers = [0] * len(ll)
    lens = [len(m)-1 for m in ll]
    run = True
    while run:
        elems = [l[e][0] for l,e in zip(ll, pointers)]
        values = set(elems)

        if len(values) == 1:
            matches.append(ll[0][pointers[0]])
            pointers = [p+1 for p in pointers]
            for i in range(len(pointers)):
                if pointers[i] == len(ll[i]):
                    run = False
                    break

        elif pointers == lens:
            break
    
        else:
            m = max(values)
            for p in range(len(pointers)):
                j = pointers[p]
                while j < len(ll[p]):
                    pointers[p] = j
                    v = ll[p][j][0] 
                    if v >= m:
                        break
                    else:
                        if pointers[p] == len(ll[p]) - 1:
                            run = False
                            break
                        j += 1
    return matches


def score(index, requete):
    b = 1 - a
    sc = tf_idf.score_frequence(index, requete)
    pg = pagerank[index]
    return a*sc + b*pg

def init(requete):
    pages = enum_pages(requete)
    top_k = sorted([(p[0], score(p[0], requete)) for p in pages], key=lambda x: x[1], reverse=True)
    return list(map(lambda x: x[0], top_k)) 

def main():
    print("TEMPS ALGORITHME SIMPLE : ")
    start = time.time()
    init(["football"])
    print(time.time() - start)

if __name__ == "__main__":
    main()