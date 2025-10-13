from pydantic import BaseModel
from typing import List

class PrunedTable(BaseModel):
    table_name: str
    used_columns: List[str]

class PrunedSchema(BaseModel):
    schema_pruned: List[PrunedTable]
