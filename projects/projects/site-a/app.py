from flask import Flask, request, redirect, url_for, render_template_string
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path

# Path to the shared XML file (one level up)
DB_PATH = Path(__file__).resolve().parents[1] / "shared_db.xml"

app = Flask(__name__)

def pretty_xml(elem):
    rough = ET.tostring(elem, 'utf-8')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ")

def ensure_db():
    if not DB_PATH.exists():
        root = ET.Element("database")
        items = ET.SubElement(root, "items")
        DB_PATH.write_text(pretty_xml(root), encoding='utf-8')

def append_item(title, desc, author):
    ensure_db()
    tree = ET.parse(DB_PATH)
    root = tree.getroot()
    items = root.find("items")
    existing_ids = [int(i.attrib.get("id", "0")) for i in items.findall("item")]
    next_id = max(existing_ids, default=0) + 1
    item = ET.SubElement(items, "item", attrib={"id": str(next_id)})
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "desc").text = desc
    ET.SubElement(item, "author").text = author
    tree.write(DB_PATH, encoding='utf-8', xml_declaration=True)
    # rewrite prettified xml
    xml = ET.parse(DB_PATH).getroot()
    DB_PATH.write_text(pretty_xml(xml), encoding='utf-8')
    return next_id

def load_items():
    ensure_db()
    tree = ET.parse(DB_PATH)
    return tree.getroot().find("items").findall("item")

INDEX_HTML = """
<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Site A — Submit</title></head>
  <body>
    <h1>Site A — Add Item</h1>
    <form method="POST" action="{{ url_for('add') }}">
      <label>Title: <input name="title" required></label><br>
      <label>Description: <textarea name="desc" required></textarea></label><br>
      <label>Author: <input name="author" required></label><br>
      <button type="submit">Add</button>
    </form>

    <h2>Current items</h2>
    <ol>
    {% for item in items %}
      <li>{{ item.find('title').text }} <small>(id={{ item.attrib['id'] }})</small></li>
    {% endfor %}
    </ol>
  </body>
</html>
"""

@app.route("/")
def index():
    items = load_items()
    return render_template_string(INDEX_HTML, items=items)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title","").strip()
    desc = request.form.get("desc","").strip()
    author = request.form.get("author","").strip()
    if not title or not desc or not author:
        return "Missing fields", 400
    append_item(title, desc, author)
    return redirect(url_for("index"))

if __name__ == "__main__":
    ensure_db()
    app.run(port=5001, debug=True)
