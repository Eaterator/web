import sys
import os
from sqlalchemy import MetaData
from sqlalchemy.orm import class_mapper
try:
    from sqlalchemy_schemadisplay import create_schema_graph, create_uml_graph
except ImportError:
    print("ERD diagrams require 'pip install sqlalchemy_schema_display' to run")
    sys.exit(1)
from application.config import SQLALCHEMY_DATABASE_URI
from application.app import db


output_dir = os.path.join(os.path.dirname(__file__), 'erd_diagrams')
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

graph = create_schema_graph(
    metadata=MetaData(SQLALCHEMY_DATABASE_URI),
    show_datatypes=True,
    show_indexes=True,
    rankdir='LR',
    concentrate=False
)

graph.write_png(os.path.join(output_dir, 'erd_diagram_eaterator.png'))

models = [m for m in [model for model in db.Model.__subclasses__()[0].__subclasses__()]]
print(models)
print(dir(models[0]))
mappers = []
for model in models:
    try:
        cls = model
        mappers.append(class_mapper(cls))
    except:
        import traceback
        print(traceback.format_exc())

graph = create_uml_graph(
    mappers,
    show_operations=False,
    show_multiplicity_one=True
)
graph.write_png(os.path.join(output_dir, 'class_diagram_eaterator.png'))
