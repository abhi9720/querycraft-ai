import json
from collections import defaultdict

class SchemaGraph:
    def __init__(self):
        # Adjacency list: table -> list of related tables via foreign keys
        self.graph = defaultdict(list)

    def add_relation(self, table_from, table_to):
        self.graph[table_from].append(table_to)

    def get_related_tables(self, table_name):
        # Return all tables directly connected to this table
        return self.graph.get(table_name, [])

    @classmethod
    def load(cls, filepath):
        """
        Load schema graph from a JSON file.
        Example JSON format:
        {
            "users": ["orders"],
            "orders": ["users", "products"],
            "products": ["orders"]
        }
        """
        instance = cls()
        with open(filepath, "r") as f:
            data = json.load(f)
            for table, related in data.items():
                instance.graph[table] = related
        return instance