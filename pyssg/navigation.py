import os
def make_directory_tree(root, criteria=None):
    root = Path(root)
    tree = {}
    for path in root.glob("*"):
        if criteria is None or criteria(path):
            tree[path] = make_directory_tree(path, criteria)
    return tree


def pprint_tree(node, file=None, _prefix="", _last=True):
    print(_prefix, "└─ " if _last else "├─ ", node[0].name, sep="", file=file)
    _prefix += "   " if _last else "│  "
    child_count = len(node[1])
    for i, child in enumerate(node[1].items()):
        _last = i == (child_count - 1)
        pprint_tree(child, file, _prefix, _last)
        

if __name__ == "__main__":
    from pathlib import Path
    root = Path(".")
    # root = root.relative_to(root)
    # create tree
    tree = make_directory_tree(root, criteria=Path.is_dir)

    # print tree
    pprint_tree( (Path.cwd(), tree) )


    # create html
    import jinja2
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

   template = env.from_string("""
        <ul>
            {%- for path, value in tree.items() recursive %}
                <li>
                    <a href="{{ path }}">{{ path.name }}</a>
                    {%- if value -%}
                        <ul>{{ loop(value.items()) }}</ul>
                    {%- endif %}
                </li>
            {%- endfor %}
        </ul>""")
    template = env.get_template("navigation.j2")
    html = template.render(tree=tree)
    Path(Path.cwd(), "navigation.html").write_text(html)


