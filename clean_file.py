import re
import sys
import os


# Patterns qui conserve que les balises intéressante
page_pattern = re.compile(
    r'<page>.*?(<title>.*?</title>).*?(<id>.*?</id>).*?<revision>.*?(<text.*?>)(.*?</text>).*?</revision>.*?</page>', re.DOTALL)

# Filtre les sections de liens externes
liens_externes_pattern = re.compile(
    r"===? liens externes ===?\n(\t\t\t\*.*?\n)*\t\t\t\n", re.DOTALL)

# Filtre les liens externes
external_link_pattern = re.compile(
    r"(\[)[^\[\]]*?https?://[^\[\]]*?(\])")

# Filtre différents types de liens
link_not_in_braces = re.compile(
    r"(url|lire en ligne|présentation en ligne|site) ?= ?https?://.*?\s")

# Sous sections de page
sections_pattern = re.compile(r"(\[\[.*?)#.*?\|(.*?\]\])")

# [[catégorie:naissance à staten island]]
double_dot_pattern = re.compile(r"\[\[[^\[\]]*?:[^\[\]]*?\]\]")
simple_double_one_line_braces = re.compile(r"{{.*?}}|{.*?}")
simple_double_multi_line_braces = re.compile(r"{{.*?}}|{.*?}", re.DOTALL)


# Tabulations
prettier = "\n"+("\t"*2)



# Boucle sur le fichier
def parseFile(wiki_file, f):
    z = 0
    for line in wiki_file:
        if "<page>" in line:
            s = handleContent(wiki_file)
            new_string = re.sub(
                page_pattern, r"<page>"+prettier+r"\1"+prettier+r"\2"+prettier+r"\3\n\t\t\t\4\n\t</page>", s)
            clean_string = handleText(new_string)
            z += 1
            print(z)
            writeOnFile(f, clean_string)

# Applique le filtrage sur la page
def handleText(page):
    external_link_section = re.sub(liens_externes_pattern, r"", page)
    clean_line_braces = re.sub(
        simple_double_one_line_braces, r"", external_link_section)
    clean_multiline_braces = re.sub(
        simple_double_multi_line_braces, r"", clean_line_braces)
    external_link = re.sub(external_link_pattern, r"", clean_multiline_braces)
    clean_text = re.sub(link_not_in_braces, r"", external_link)
    clean_sections = re.sub(sections_pattern, r"\1|\2", clean_text)
    clean_link = re.sub(double_dot_pattern, r"", clean_sections)

    return clean_link

# Récupére le texte d'une page

def handleContent(wiki_file):
    s = "  <page>\n"
    for line in wiki_file:
        s = s + "\t"*3+line
        if "</page>" in line:
            return s.lower()
    return s

# écrit dans f s

def writeOnFile(f, s):
    f.write(s)


# Main

def main():
    directory = r'maain/xmlfiles/'
    for filename in os.listdir(directory):
        if filename != "cleans":
            with open(directory+filename) as wiki_file:
                filename = filename[0:-4]
                f = open(directory+"cleans/"+filename + "_clean.xml", "a")
                parseFile(wiki_file, f)
                f.close()


if __name__ == "__main__":
    main()
