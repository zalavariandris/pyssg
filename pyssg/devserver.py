# from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer # python2
from http.server import BaseHTTPRequestHandler, HTTPServer # python3
from pyssg.staticsite import StaticSite

class SiteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        uri = self.path
        root_folder = Path.cwd()

        site = StaticSite(root_folder)
        print("""GET:
        root folder: {}
        uri: {}
        """.format(root_folder, uri))

        data, mime = site.serve(uri)
        
        self.send_response(200)
        self.send_header('Content-type', mime[0])
        self.end_headers()
        if isinstance(data, str):
            self.wfile.write(bytes(data, 'utf-8'))
        elif isinstance(data, bytes):
            self.wfile.write(data)

def serve():
    host = ''
    PORT = 8080
    server = HTTPServer((host, PORT), SiteHandler)
    print("server listening on port: localhost:{}".format(PORT))
    server.serve_forever()

if __name__ == "__main__":
    import sys
    from pathlib import Path
    print(sys.argv)
    print(Path.cwd())
    serve()
