from flask import Flask, render_template_string
import xml.etree.ElementTree as ET
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "shared_db.xml"

app = Flask(__name__)

def ensure_db():
    if not DB_PATH.exists():
        root = ET.Element("database")
        items = ET.SubElement(root, "items")
        ET.ElementTree(root).write(DB_PATH, encoding='utf-8', xml_declaration=True)

def load_items():
    ensure_db()
    tree = ET.parse(DB_PATH)
    items = tree.getroot().find("items")
    result = []
    for it in items.findall("item"):
        result.append({
            "id": it.attrib.get("id"),
            "title": it.findtext("title","(no title)"),
            "desc": it.findtext("desc",""),
            "author": it.findtext("author","")
        })
    return result

FEED_HTML = """
<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Site B — Shared Feed</title></head>
  <body>
    <h1>Shared Feed (Site B)</h1>
    <ul>
    {% for it in items %}
      <li id="item-{{ it.id }}">
        <strong>{{ it.title }}</strong> by <em>{{ it.author }}</em><br>
        {{ it.desc }}
      </li>
    {% endfor %}
    </ul>
  </body>
</html>
"""

@app.route("/")
def feed():
    items = load_items()
    return render_template_string(FEED_HTML, items=items)

if __name__ == "__main__":
    ensure_db()
    app.run(port=5002, debug=True)
