import os
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


if __name__ == "__main__":
    from pathlib import Path
    root = Path("../examples/juditfischer")
    # root = root.relative_to(root)
    # create tree
    def criteria(path):
        if path.is_file() and path.stem != "index" and path.suffix in (".html", ".md", ".j2"):
            return True
        if not path.is_dir():
            return False
        if any(part.startswith("_") for part in path.relative_to(root).parts):
            return False
        return True

    tree = make_directory_tree(root, criteria=criteria)

    # print tree
    pprint_tree( (Path.cwd(), tree) )


    # create html
    import jinja2
    from jinja2 import Environment, FileSystemLoader, ChoiceLoader, DictLoader, select_autoescape

    env = Environment(
        loader=ChoiceLoader([FileSystemLoader('templates'),     DictLoader({'navigation':"""
        <ul>
            {%- for path, value in tree.items() recursive %}
                <li>
                    <a href="{{ path }}">{{ path.name }}</a>
                    {%- if value -%}
                        <ul>{{ loop(value.items()) }}</ul>
                    {%- endif %}
                </li>
            {%- endfor %}
        </ul>"""})]),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template("navigation")
    html = template.render(tree=tree)
    Path(Path.cwd(), "navigation.html").write_text(html)


