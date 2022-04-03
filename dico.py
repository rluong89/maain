import re, sys, unicodedata
import nltk
from nltk.corpus import stopwords
from collections import Counter
from tf_idf import dico_bfs_file

stop_words = set(stopwords.words('french'))

# Get most nb frequent words in list l
def list_words(wiki_file, nb):
    wordcount = {}
    dico_bfs = dico_bfs_file()
    titleswords = set()
    p_end_page = re.compile(r'</page>')
    p_text = re.compile(r'<text.*>')
    p_end_text = re.compile(r'^\s*(.*)</text>')
    p_title = re.compile(r'<title>(.*)</title>')
    in_page = False
    in_title = False
    compt = 0

    for line in wiki_file:
        
        if (r := re.search(p_title, line)) is not None: 
            title = r.group(1)
            if dico_bfs[title] is not None:
                titleswords.update(clean_line(title))
                in_title = True 

        elif re.search(p_text, line) is not None:
            in_page = True
        
        elif re.search(p_end_page, line) is not None:
            in_page = False
            in_title = False
            compt += 1
            print(compt)
            

        elif in_page and in_title :

            if (r := re.search(p_end_text, line)) is not None:
                if r.group(1): 
                    line = r.group(1)

            for word in clean_line(line):
                if len(word) > 1 :     
                    if word not in wordcount:
                        wordcount[word] = 1
                    else:
                        wordcount[word] += 1            

    word_counter = Counter(wordcount)

    words = Counter(dict(word_counter.most_common(nb))) + Counter(titleswords)

    return [w for w in words]


def write_to_file(l, file):
    for w in sorted(l):
        file.write(w + '\n')


# Nettoyages des lignes
def clean_line(st: str):
    tokenizer = nltk.RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(st)
    l = []
    for words in tokens:
        w = clean_accents(words).lower()
        if w not in stop_words:
            l.append(w)
    return l
    

def clean_accents(st: str):
    st = unicodedata.normalize('NFKD', st)\
        .encode('ascii', 'ignore')\
        .decode("utf-8")
    
    return str(st)


def main():
    with open('corpus.xml', encoding='utf-8') as wiki_file:
        words = list_words(wiki_file, 10000)
        f = open("list_of_words", "w")
        write_to_file(words, f)

if __name__ == "__main__":
    main()
