from pathlib import Path
import shutil
from jinja2 import Template, Environment, ChoiceLoader, FileSystemLoader, DictLoader,  select_autoescape
import mimetypes

class Page:
    def __init__(self, name, uri, children=[]):
        self.name, self.uri = name, uri
        self.children = children

class StaticSite:
    def __init__(self, root):
        assert Path(root).exists(), "provided root path: '{}', does not exists!".format(root)
        self.root = Path(root)

        # Create Jinja envionment
        theme = Path(self.root, "_theme")

        def make_directory_tree(root, criteria=None):
            root = Path(root)
            tree = {}
            for path in root.glob("*"):
                if criteria is None or criteria(path):
                    tree[path] = make_directory_tree(path, criteria)
            return tree

        def pprint_tree(node, file=None, _prefix="", _last=True):
            # print(_prefix, "└─ " if _last else "├─ ", node[0].name, sep="", file=file)
            print(_prefix, "`- " if _last else "+  ", node[0].stem, sep="", file=file)
            _prefix += "   " if _last else "|  "
            child_count = len(node[1])
            for i, child in enumerate(node[1].items()):
                _last = i == (child_count - 1)
                pprint_tree(child, file, _prefix, _last)

        def criteria(path):
            if path.is_file() and path.stem != "index" and path.suffix in (".html", ".md", ".j2"):
                return True
            if not path.is_dir():
                return False
            if any(part.startswith("_") for part in path.relative_to(root).parts):
                return False
            return True



        navigation_source = """
        <ul>
            {%- for page in tree recursive %}
                <li>
                    <a href="{{ page.uri }}">{{ page.name }}</a>
                    {%- if page.children -%}
                        <ul>{{ loop(page.children) }}</ul>
                    {%- endif %}
                </li>
            {%- endfor %}
        </ul>"""

        self.env = Environment(
            loader=ChoiceLoader([FileSystemLoader(str(theme)), DictLoader({'navigation':navigation_source})]),
            autoescape=select_autoescape(['html', 'xml']),
        )

        folder_tree = make_directory_tree(self.root, criteria=criteria)

        def pathtree_to_pagetree(compact):
            return [Page(name=path.stem, uri="/"+str(path.relative_to(self.root)), children=pathtree_to_pagetree(children)) for path, children in compact.items()]

        self.tree = pathtree_to_pagetree(folder_tree)

        for page in self.tree:
            print(page.name, page.uri, len(page.children))


    def build(self, watch=True):
        # clean _site folder
        if Path(self.root, "_site").exists():
            shutil.rmtree(Path(self.root, "_site"))

        # generate static files for routes
        for route in self.routes():
            data, mime = self.serve(route)
            if isinstance(data, str):
                folder = Path(self.root, "_site", route[1:])
                folder.mkdir(parents=True, exist_ok=True)
                file = Path(folder, "index.html")
                file.write_text(data)
            elif isinstance(data, bytes):
                file = Path(self.root, "_site", route[1:])
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(data)

    def files(self):
        """return all files, but the exceptions"""
        for file in self.root.rglob("*.*"):
            if file.name.startswith("."):
                pass
            elif file.is_file and any(part.startswith("_") for part in file.parent.parts):
                pass
            elif file.suffix == ".meta":
                pass
            else:
                yield file

    def routes(self):
        """return all valid routes on website, including the pages and assets"""
        for file in self.files():
            if file.suffix in [".html", ".j2", ".md"]:
                # process page
                if file.stem == "index":
                    if file.parent == self.root:
                        yield "/"
                    else:
                        yield "/"+str(file.parent.relative_to(self.root))
                else:
                    yield "/"+str(file.relative_to(self.root).with_suffix(""))
            else:
                # process assets
                yield "/"+str(file.relative_to(self.root))

    def process(self, file):
        file = Path(file)
        if file.suffix == ".html":
            # process html
            return file.read_text(), ('text/html', None)
        elif file.suffix == ".j2":
            # process jinja2 template
            t = self.env.from_string(file.read_text(), globals={'tree': self.tree})
            return t.render(), ('text/html', None)
        elif file.suffix == ".md":
            # process markdown as jinja2 template
            t = self.env.from_string(file.read_text(), globals={'tree': self.tree})
            return t.render(), ('text/html', None)
        else:
            # process assets, potentially rescale file
            mime = mimetypes.guess_type(str(file))
            return file.read_bytes(), mime

    def serve(self, route)->"HTML string":
        """get content for route, if valid"""

        # Get file for route
        path = Path(self.root, route[1:])
        if path.is_dir():
            # if the path is a dir then get the first index.* file
            path=list(path.glob("index.*") )[0]

        if path.suffix == "":
            # if path has no suffix, find the first matching file
            path = list(path.parent.glob(path.name+".*"))[0]

        if not path.is_file():
            return """
            <html>devserv
                <head></head>
                <body>404</body>
            </html>
            """, ('text/html', None)
        else:
            return self.process(path)

    def open(self):
        import webbrowser
        url = Path("file:///", self.root, "_site_", "index.html").absolute()
        webbrowser.register('chrome',
            None,
            webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
        webbrowser.get('chrome').open(str(url))



if __name__ == "__main__":
    import logging
    from pathlib import Path
    logging.basicConfig(level=logging.DEBUG)

    # build portfolio
    root = Path("../examples/juditfischer")
    site = StaticSite(root)
    site.build()
    # site.open()


