import os

z = 0


def contains_elt_of_list(line, l):
    sp = line.split()
    for word in sp:
        for elt in l:
            if elt == word:
                return True
    return False


def extract_corpus(file, corpus):
    l = ['football', 'ballon', 'france']
    global z
    for line in file:
        if "<page>" in line:
            page, in_corpus = extract_page(file, l)
            if in_corpus:
                z += 1
                print(z)
                corpus.write(page)
            if z > 200000:
                break


def extract_page(file, l):
    page = "  <page>\n"
    in_corpus = False
    for line in file:
        page = page + "\t" * 3 + line
        if "</page>" in line:
            return (page, in_corpus)
        elif not in_corpus:
            in_corpus = contains_elt_of_list(line, l)


def main():
    f = open("corpus.xml", "a")
    directory = r'xmlfiles/cleans/'
    for filename in os.listdir(directory):
        with open(directory+filename, encoding='utf-8') as wiki_file:
            extract_corpus(wiki_file, f)


if __name__ == "__main__":
    main()
