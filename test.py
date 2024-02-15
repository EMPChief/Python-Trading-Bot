import sqlite3

def all(db, query, params):
    cursor = db.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return rows

def keys(db, ts):
    for table in ts:
        fk = all(db, f"PRAGMA foreign_key_list('{table['name']}')", ())
        table['fk'] = fk
    return ts

def columns(db, ts):
    for table in ts:
        cs = all(db, f"PRAGMA table_info('{table['name']}')", ())
        table['columns'] = cs
    return ts

def tables(db):
    ts = all(db, "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT IN ('sqlite_sequence')", ())
    ts = columns(db, ts)
    ts = keys(db, ts)
    return ts

def quote(value):
    return f"'{value}'" if isinstance(value, str) else str(value)

def attr(attrs, sep=', ', indent=''):
    return sep.join(f"{indent}{prop}={quote(attrs[prop])}" for prop in attrs)

def tag(name, content, options=None):
    if options:
        attributes = attr(options, ' ')
        return f"<{name} {attributes}>{content}</{name}>"
    return f"<{name}>{content}</{name}>"

def font(content, options=None):
    return tag('font', content, options)

def b(content, options=None):
    return font(tag('b', content), options)

def td(content, options=None):
    options = options or {}
    options.setdefault('align', 'left')
    return tag('td', content, options)

def tr(tds):
    return tag('tr', ''.join(td(args[0], args[1]) for args in tds))

def tb(trs, options=None):
    options = options or {}
    options.setdefault('border', 0)
    options.setdefault('cellspacing', 0.5)
    return tag('table', ''.join(tr(args[0]) for args in trs), options)

def head(table):
    return tb([[[b(table['name'], {'point-size': 13}), {'height': 24, 'valign': 'bottom'}]]])

def type(column):
    return (column['type'] or '').lower()

def cols(column):
    return [[[f"{column['name']}{('* ' if column['pk'] else ' ')}{b(type(column))}"]]]

def body(table):
    return tb([cols(col) for col in table['columns']], {'width': 134})

def label(table):
    return f"{head(table)}|{body(table)}"

def edge(table, fk, options=None):
    labels = {'taillabel': fk.get('from', ''), 'headlabel': fk.get('to', '')} if options and options.get('edgeLabels') else {}
    return f"{table['name']} -> {fk['table']}[{attr(labels)}];"

def node(table):
    options = {'label': label(table)}
    return f"{table['name']} [{attr(options)}];"

def digraph(db, stream, options=None):
    options = options or {}
    stream.write(f"digraph {db['name']} {{\n{attr({'rankdir': options.get('direction', 'LR'), 'ranksep': '0.8', 'nodesep': '0.6', 'overlap': 'false', 'sep': '+16.0', 'splines': 'compound', 'concentrate': 'true', 'pad': '0.4,0.4', 'fontname': options.get('font', 'Helvetica'), 'fontsize': 12, 'label': b(options.get('title', db['filename']))}, ';\n', '  ')};\n")
    stream.write(f"  node[{attr({'shape': 'Mrecord', 'fontsize': 12, 'fontname': options.get('font', 'Helvetica'), 'margin': '0.07,0.04', 'penwidth': '1.0'})}];\n")
    stream.write(f"  edge[{attr({'arrowsize': '0.8', 'fontsize': 10, 'style': 'solid', 'penwidth': '0.9', 'fontname': options.get('font', 'Helvetica'), 'labelangle': 33, 'labeldistance': '2.0'})}];\n")

    ts = tables(db)
    nodes = []
    edges = []

    for table in ts:
        nodes.append(f"  {node(table)}\n")
        for fk in table['fk']:
            edges.append(f"  {edge(table, fk, options)}\n")

    stream.write(''.join(nodes) + ''.join(edges) + '}\n')

def sqleton(db, stream, options=None, cb=None):
    options = options or {}
    promise = digraph(db, stream, options)
    if cb:
        promise.then(cb).catch(cb)
    return promise

# Example usage:
db = sqlite3.connect('example.db')
with open('output.dot', 'w') as stream:
    sqleton({'name': 'ExampleDB', 'filename': 'example.db'}, stream)
