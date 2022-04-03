from http.server import HTTPServer, BaseHTTPRequestHandler
from cli import bfs_deserialization
import cgi
import wand
# import algo_simple
# import tf_idf


base_url = "https://fr.wikipedia.org/?curid="


class web_server(BaseHTTPRequestHandler):
    # https://fr.wikipedia.org/?curid=13574496

    # Permet de récupérer un fichier à partir de l'url
    def getFile(self):
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
            return file_to_open
        except:
            self.send_response(404)
            return "File not found"

    # Renvoie index.html
    def getIndex(self):
        if self.path == '/':
            self.path = '/index.html'
            file_to_open = self.getFile()
            self.sendFile(file_to_open)
        else:
            file_to_open = self.getFile()
            self.sendFile(file_to_open)
    # Renvoie un réponse un fichier
    def sendFile(self, file_to_open):
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

    # Gére les requests GET
    def do_GET(self):
        self.getIndex()
    # Gére les requests POST et donc les requêtes
    def do_POST(self):
        if self.path.endswith('/search'):
            ctype, pdic = cgi.parse_header(self.headers.get('content-type'))
            pdic['boundary'] = bytes(pdic['boundary'], "utf-8")
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdic)
                request = fields.get('request')
                self.send_response(200)
                self.send_header('content-type', 'text/html;charset=utf-8')
                self.end_headers()
                if len(request) == 0:
                    self.wfile.write("Error page")
                else:
                    html_file = self.handleRequest(request[0])
                    liste_titre = list(
                        map(lambda index: dic_index_to_line_number.get(index)[0], html_file))
                    liste_titre_id = list(
                        map(lambda title: (getIdByTitle(title), title), liste_titre))
                    s = '<a href="/">Home</a><br>'+buildReponse(liste_titre_id)
                    self.wfile.write(bytes(s, 'utf-8'))
    
    # Traitement de la requête
    def handleRequest(self, request):
        request_list = request.split()
        l = wand.wand_with_init(request_list)
        #l = algo_simple.init(request_list)
        return l

# Crée la réponse d'une requête
def buildReponse(liste_titre_id):
    s = ""
    for (page_id, title) in liste_titre_id:
        page_url = base_url + page_id
        s += '<a href="{0}">{1}</a><br>'.format(page_url, title)
    return s

# Inverse le dictionnaire titre -> (numéro ligne, indice bfs)
def reverseDic(bfs_dic):
    d = {}
    for (titre, v) in bfs_dic.items():
        line_number, index_parcours = v
        d[int(index_parcours)] = (titre, int(line_number))
    return d


corpus_file = open("corpus.xml", "r", encoding="utf-8")
# dictionnaire titre -> (numéro ligne, indice bfs)
bfs_dic = bfs_deserialization()
# dictionnaire index_bfs -> (titre , num de ligne)
dic_index_to_line_number = reverseDic(bfs_dic)

# Récupére la ligne dans le corpus de la page t
def getLineIndex(t):
    return int(bfs_dic.get(t)[0])

# Renvoie l'id d'une page à la ligne i
def jumpToLine(i):
    corpus_file.seek(i)
    ids = "<id>"
    for s in corpus_file:
        if ids in s:
            return s.strip()[4:-5]

# Récupére l'id de la page ç partir du titre
def getIdByTitle(t):
    line = getLineIndex(t)
    s = jumpToLine(line)
    return s


if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 8000), web_server)
    try:
        print("SERVER UP")
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")
