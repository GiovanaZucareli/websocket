#Servidor WebSocket que repete as mensagens recebidas
import tornado.web
import tornado.websocket
import tornado.ioloop

from tornado.options import define, options, parse_command_line
# Porta que o Servidor vai escutar
define("port", default=8888, help="run on the given port", type=int)
 
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("repete.html")
 
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def on_message(self, message):
        texto = message.strip()
        if not texto:
            return
        # A contagem aparece na linha abaixo do texto transformado.
        resposta = "Texto em maiúsculas: " + texto.upper()
        resposta += "\nPalavras: " + str(len(texto.split()))
        self.write_message(resposta)
 
app = tornado.web.Application([
    (r"/", IndexHandler),
    (r"/websocket", WebSocketHandler),
])
 
if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
