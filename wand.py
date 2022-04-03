import heapq
import tf_idf
from random import randint, choice
from cli import deserialize_pagerank
import time

#pour trier la relation mot-page par pagerank décroissant
def sort_tuples(l, pageranks):
    return sorted(l, key=lambda x: pageranks[x[0]], reverse=True)

#pour récupérer la liste de listes des tuples
def sorted_lists_from_request(req, rel, pageranks):
    all_lists = []
    for w in req:
        sorted_tuples = sort_tuples(rel[w], pageranks)
        add_max_tuples = list(map(lambda x: (x[0], x[1], 0.0), sorted_tuples))
        all_lists.append(
            [0, add_max_tuples, len(rel[w]), w])
    return all_lists

#on détermine le maximum 
def maximum_all(all_lists):
    max = -1.0
    for l in all_lists:
        relations = l[1]
        request_word = l[3]
        idf_word = tf_idf.idf(request_word)
        for i in range (len(relations) - 1, -1, -1) :
            relation = relations[i]
            computed_maximum = idf_word * relation[1]
            if computed_maximum > max:
                max = computed_maximum
            relations[i] = (relation[0], relation[1], max)

def increment_pointer(l):
    l[0] = l[0] + 1

# pour savoir si une liste est out of bounds
def is_list_not_oob(l):
    return l[0] < l[2]

# on retire les listes out of bounds
def remove_oob_lists(all_lists):
    return list(filter(lambda l: is_list_not_oob(l), all_lists))

# tri des pointeurs
def sort_pointers(all_lists):
    return sorted(all_lists, key=lambda x: x[0])

# calcul du score total
def total_score(alpha, d, req, pageranks):
    beta = 1 - alpha
    return alpha * tf_idf.score_frequence(d, req) + beta * pageranks[d]

# remplissage du top k initial
def fill_top_k(top_k, all_lists, pageranks, max_k, alpha, req):
    k = 0
    added = False
    while k != max_k and len(all_lists) > 0:
        max_page = -1
        max_pagerank = -1
        max_list_index = -1
        all_lists = remove_oob_lists(all_lists)
        for i, l in list(enumerate(all_lists)):
            pointed_page = get_pointed_page(l)
            pagerank = pageranks[pointed_page]
            if pagerank > max_pagerank:
                max_pagerank = pagerank
                max_list_index = i
                max_page = pointed_page
        if len(all_lists) > 0 :
            max_total_score = total_score(alpha, max_page, req, pageranks)
            increment_pointer(all_lists[max_list_index])
            # pour éviter d'ajouter des doublons dans le top k
            for i, m in list(enumerate(top_k)):
                if m[1] == max_page :
                    if m[0] < max_total_score :
                        top_k[i] = (total_score, max_page)
                        added = True
                        break
                    else :
                        added = True
                        break
            
            if not added :        
                heapq.heappush(top_k, (max_total_score, max_page))
                k += 1
            added = False            
# récupère la page pointée dans la liste l
def get_pointed_page(l):
    relation = l[1]
    pointer = l[0]
    return relation[pointer][0]

# pour trouver la liste contenant le pivot
def find_pivot_list_index(all_lists, first_pagerank, gamma, alpha, request):
    max_sum = 0
    beta = 1 - alpha
    beta_times_first_pagerank = beta * first_pagerank
    for i, l in list(enumerate(all_lists)):
        relation = l[1][l[0]]
        current_max = relation[2]
        max_sum += current_max
        computation = beta_times_first_pagerank + alpha / tf_idf.norme(request) * max_sum 
        if computation >= gamma :
            return i
    return -1

# recherche dichotomique pour se déplacer
def binary_search(l, start, end, pivot, pageranks) :
    while(start < end) :
        mid = start + (end - start) // 2
        pointed_page = l[mid][0]
        if(pageranks[pointed_page] > pageranks[pivot]) :
            start = mid + 1
        else :
            end = mid
    pointed_page = l[start][0]
    if pageranks[pointed_page] <= pageranks[pivot] :
        return start
    return -1
'''    
# sans recherche dichotomique pour se déplacer
def increment_pointer_according_to_pivot(l, target_pagerank, pageranks):
    while l[0] < l[2]:
        pointed_page = get_pointed_page(l)
        pagerank = pageranks[pointed_page]
        if pagerank <= target_pagerank:
            return
        else:
            increment_pointer(l)
'''

# on augmente les pointeurs jusqu'à trouver une page dont le pagerank est inférieure ou égale au pivot
def increment_pointer_according_to_pivot(l, pivot, pageranks):
    current_pointer = l[0]
    last_index = l[2] - 1
    #print(l)
    new_pos = binary_search(l[1], current_pointer, last_index, pivot, pageranks)
    if new_pos == -1 :
        l[0] = l[2] #taille de la liste, pas de problemes car on verifiera le depassement
    else :
        l[0] = new_pos

# on retire le min et on ajoute au top K
def update_top_k(top_k, new_element):
    heapq.heappop(top_k)
    heapq.heappush(top_k, new_element)

# on détermine si il y a assez mots de la requêtes
def enough_words_from_request(req, all_lists, pivot, pivot_list_index, threshold):
    counter = 0
    for i in range(0, pivot_list_index + 1):
        l = all_lists[i]
        if l[0] < l[2]:  # on veille à ne pas sortir de la liste
            pointed_page = get_pointed_page(l)
            if pointed_page == pivot:
                counter += 1
    return counter / len(req) >= threshold

# on avance les pointeurs qui pointent vers le pivot
def increment_pivot_pointers(all_lists, pivot):
    for l in all_lists:
        if(l[0] < l[2]) :
            pointed_page = get_pointed_page(l)
            if pointed_page == pivot:
                increment_pointer(l)

# mon plus grand cauchemard
def wand(request, pageranks, relation, alpha):
    top_k = []
    all_lists = sorted_lists_from_request(request, relation, pageranks)
    maximum_all(all_lists)
    fill_top_k(top_k, all_lists, pageranks, 1000, alpha, request)
    gamma = top_k[0][0]
    all_lists = remove_oob_lists(all_lists)

    while len(all_lists) != 0:
        all_lists = sort_pointers(all_lists)
        first_pagerank = pageranks[get_pointed_page(all_lists[0])]
        pivot_list_index = find_pivot_list_index(
            all_lists, first_pagerank, gamma, alpha, request)
        if pivot_list_index == - 1:
            return top_k
        else:
            pivot = get_pointed_page(all_lists[pivot_list_index])
            for i in range(0, pivot_list_index):
                increment_pointer_according_to_pivot(
                    all_lists[i], pivot, pageranks)
            if enough_words_from_request(request, all_lists, pivot, pivot_list_index, 0.25):
                pivot_score = total_score(alpha, pivot, request, pageranks)
                if pivot_score > gamma :
                    update_top_k(top_k, (pivot_score, pivot))
                    gamma = top_k[0][0]
                    increment_pivot_pointers(all_lists, pivot)
                else :
                    return top_k
        increment_pivot_pointers(all_lists, pivot)
        all_lists = remove_oob_lists(all_lists)
    return top_k

# Permet de récupérer le Max entre les listes du parcours simple
def getMax(pages, index_list):
    maxPage = -1
    indexMax = 0
    for i in range(len(pages)):
        index = index_list[i]
        if pages[i][index] > maxPage:
            maxPage = pages[i][index]
            indexMax = i
    return (maxPage, i)

# Vérifie si on est sorti d'une liste
def outOfBounds(liste_page, liste_index):
    for i in range(len(liste_page)):
        if len(liste_page[i]) <= liste_index[i]:
            return True
    return False

# Calcul d'alpha
def processAlpha(totalf, total_pagerank, numberOfIter):
    if numberOfIter == 0:
        return 0
    totalf = totalf/numberOfIter
    total_pagerank = total_pagerank/numberOfIter

    if totalf != 0:
        return total_pagerank / totalf
    return 0


def allEquals(liste_page, liste_index):
    l = []
    for i in range(len(liste_page)):
        l.append(liste_page[i][liste_index[i]])

    return len(set(l)) == 1

# Permet de tirer une requête aléatoire
def randomRequest(relation):
    requestLength = randint(1, 5)
    # print(list(relation.keys()))
    res = []
    request = []
    for i in range(requestLength):
        s = choice(list(relation.keys()))
        tuple_list = relation.get(s)
        list_of_page = list(map(lambda tuple: tuple[0], tuple_list))
        list_of_page.sort()
        res.append(list_of_page)
        request.append(s)
    return (res, request)

# Permet de calculer alpha a partir d'une requête
def base_alpha(relation, pagerank):
    (liste_page, r) = randomRequest(relation)
    totalf = 0
    total_pagerank = 0
    liste_index = [0 for i in range(len(liste_page))]
    (max_page, index_max) = getMax(liste_page, liste_index)
    numberOfIter = 0
    while numberOfIter < 1000:
        for j in range(len(liste_page)):
            tmp_index = liste_index[j]
            while tmp_index < len(liste_page[j]) and liste_page[j][tmp_index] < max_page:
                tmp_index += 1
            liste_index[j] = tmp_index
        if outOfBounds(liste_page, liste_index):
            return processAlpha(totalf, total_pagerank, numberOfIter)
        if allEquals(liste_page, liste_index):
            currentPage = liste_page[j][liste_index[j]]
            totalf += tf_idf.score_frequence(currentPage, r)
            total_pagerank += pagerank[currentPage]
            numberOfIter += 1
        (max_page, index_max) = getMax(liste_page, liste_index)
    return processAlpha(totalf, total_pagerank, numberOfIter)

# Fait la moyenne d'alpha sur 1000 requêtes aléatoires
def echantillonage(relation, pagerank):
    alphasum = 0
    echantillon = 1000
    print("beg echantillonage")
    for i in range(echantillon):
        #print(i)
        alphasum += base_alpha(relation, pagerank)
    print("end echantillonage")
    return alphasum / 1000

# tri du top k par score décroissant
def sorted_pages_from_top_k(top_k):
    top_k = sorted(top_k, key=lambda x: x[0], reverse=True)
    return list(map(lambda x: x[1], top_k))


pageranks = deserialize_pagerank()
#Alpha mesuré avec : alpha = echantillonage(tf_idf.dico_tf, pageranks)
alpha = 0.00013023353880217285

# Permet de lancer wand à partir d'une requête
def wand_with_init(request):
    return sorted_pages_from_top_k(wand(request, pageranks, tf_idf.dico_tf, alpha))

def main():
    print("TEMPS WAND : ")
    start = time.time()
    l = wand_with_init(["football", "francais", "ballon"])
    #l = algo_simple.init(["football", "francais", "ballon"])
    #for i in range(10) :
     #   print(l[i])
    #print(l)
    print(time.time() - start)

if __name__ == "__main__":
    main()
