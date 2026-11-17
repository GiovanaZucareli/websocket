#Servidor de chat com WebSocket
import json
from datetime import datetime
from pathlib import Path
import tornado.web
import tornado.websocket
import tornado.ioloop

from tornado.options import define, options, parse_command_line
# Porta que o Servidor vai escutar
define("port", default=8887, help="run on the given port", type=int)

# Mensagens ja enviadas, para quem entrar no chat depois
historico = []
# Navegadores conectados
connections = set()

def transmitir(dados):
    # Um dicionario Python e enviado como JSON para todas as abas abertas.
    for con in list(connections):
        try:
            con.write_message(dados)
        except tornado.websocket.WebSocketClosedError:
            connections.discard(con)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("chat.html")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        # Cada aba possui sua propria conexao com o servidor.
        connections.add(self)
        # Envia as mensagens anteriores para quem acabou de entrar
        for msg in historico:
            self.write_message(msg)
        transmitir({"tipo": "participantes", "total": len(connections)})

    def on_message(self, message):
        # Valida os dados antes de usa-los: cada mensagem contem nome e texto.
        try:
            dados = json.loads(message)
            if not isinstance(dados, dict):
                raise ValueError()
            nome, texto = dados.get("nome"), dados.get("texto")
            if not isinstance(nome, str) or not isinstance(texto, str):
                raise ValueError()
            nome, texto = nome.strip(), texto.strip()
            if not nome or not texto or len(nome) > 40 or len(texto) > 1000:
                raise ValueError()
        except (ValueError, TypeError):
            self.write_message({"tipo": "erro", "texto": "Informe nome (até 40 caracteres) e mensagem (até 1000 caracteres)."})
            return

        # O horario e gerado pelo servidor, igual para todos os destinatarios.
        msg = {"tipo": "mensagem", "nome": nome, "texto": texto,
               "hora": datetime.now().strftime("%H:%M")}
        historico.append(msg)
        # Mantem as ultimas 100 mensagens em memoria, sem banco de dados.
        del historico[:-100]
        # Envia apenas a nova mensagem para todos os navegadores conectados
        transmitir(msg)

    def on_close(self):
        # Remove a aba desconectada da lista de destinatarios.
        connections.discard(self)
        transmitir({"tipo": "participantes", "total": len(connections)})

app = tornado.web.Application([
    (r"/", IndexHandler),
    (r"/websocket", WebSocketHandler),
], template_path=str(Path(__file__).resolve().parent))

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
