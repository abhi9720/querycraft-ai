import json
from sqlglot import parse
from sqlglot.expressions import Create, ColumnDef, ForeignKey, Table, Schema, Identifier

OUTPUT_FILE = "schema_graph.json"

def parse_create_tables(sql_text):
    schema_graph = {}
    try:
        expressions = parse(sql_text)
    except Exception as e:
        print(f"Error parsing SQL: {e}")
        return schema_graph

    print(f"Parsing {len(expressions)} CREATE TABLE statements...")

    for create_expr in expressions:
        if not isinstance(create_expr, Create):
            continue

        table_expr = create_expr.this
        if isinstance(table_expr, Table):
            table_name = table_expr.name
        elif isinstance(table_expr, Schema):
            inner = table_expr.this
            if isinstance(inner, Table) or isinstance(inner, Identifier):
                table_name = inner.name
            else:
                table_name = str(inner)
        else:
            table_name = str(table_expr)

        if not table_name:
            print(f"⚠️ Skipping table because name could not be parsed: {create_expr}")
            continue

        print(f"✅ Parsed table name: {table_name}")

        columns = [col.name for col in create_expr.find_all(ColumnDef)]
        foreign_keys = []
        for fk in create_expr.find_all(ForeignKey):
            fk_columns = [col.name for col in fk.expressions]
            ref = fk.args.get("reference")
            if not ref:
                continue

            ref_schema = ref.this
            ref_table_name = None
            ref_columns = []
            if isinstance(ref_schema, Schema):
                if isinstance(ref_schema.this, Table):
                    ref_table_name = ref_schema.this.name
                elif hasattr(ref_schema.this, "this"):
                    ref_table_name = ref_schema.this.this.name if hasattr(ref_schema.this, "this") else str(ref_schema.this)

                ref_columns = [col.name for col in ref_schema.expressions]

            for i, col in enumerate(fk_columns):
                ref_col = ref_columns[i] if i < len(ref_columns) else (ref_columns[0] if ref_columns else None)
                foreign_keys.append({
                    "column": col,
                    "references": {"table": ref_table_name, "column": ref_col}
                })

        schema_graph[table_name] = {
            "columns": columns,
            "foreign_keys": foreign_keys
        }
    return schema_graph

def build_and_save_schema_graph(connector, output_file=OUTPUT_FILE):
    conn = None
    try:
        conn = connector.get_connection()
        cursor = conn.cursor()
        cursor.execute(connector.get_tables_query())
        tables = [row[0] for row in cursor.fetchall()]

        all_create_statements = ""
        for table_name in tables:
            create_statement = connector.get_create_table_statement(table_name, cursor)
            if create_statement:
                all_create_statements += create_statement + ";\n"

        schema_graph = parse_create_tables(all_create_statements)

        with open(output_file, "w") as f:
            json.dump(schema_graph, f, indent=4)

        print(f"✅ Schema graph saved to '{output_file}'")
    finally:
        if conn:
            connector.close_connection(conn)

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from database.factory import get_database_connector

    load_dotenv()
    db_type = os.getenv("DB_TYPE", "sqlite")
    db_name = os.getenv("DB_NAME", "Chinook_Sqlite.sqlite")

    connector = get_database_connector(db_type, db_name)
    build_and_save_schema_graph(connector, OUTPUT_FILE)
