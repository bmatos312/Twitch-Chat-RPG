from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    with open('schema.sql', 'w') as f:
        for table in db.metadata.sorted_tables:
            f.write(f"CREATE TABLE {table.name} (\n")
            for column in table.columns:
                f.write(f"    {column.name} {column.type},\n")
            f.write(");\n\n")

print("SQL script generated successfully.")

