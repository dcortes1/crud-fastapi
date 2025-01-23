from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase

app = FastAPI()

# Datos de conexión a Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

class Item(BaseModel):
    name: str
    description: str

def run_query(query, parameters=None):
    with driver.session() as session:
        result = session.run(query, parameters)
        return result.data()

@app.post("/items/")
async def create_item(item: Item):
    query = """
    CREATE (n:Item {name: $name, description: $description})
    RETURN n
    """
    run_query(query, parameters={"name": item.name, "description": item.description})
    return item

@app.get("/items/{name}", response_model=Item)
async def read_item(name: str):
    query = """
    MATCH (n:Item {name: $name})
    RETURN n.name as name, n.description as description
    """
    result = run_query(query, parameters={"name": name})
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    item = result[0]
    return Item(name=item["name"], description=item["description"])

@app.put("/items/{name}", response_model=Item)
async def update_item(name: str, item: Item):
    query = """
    MATCH (n:Item {name: $name})
    SET n.description = $description
    RETURN n
    """
    run_query(query, parameters={"name": name, "description": item.description})
    return item

@app.delete("/items/{name}")
async def delete_item(name: str):
    query = """
    MATCH (n:Item {name: $name})
    DELETE n
    RETURN n
    """
    result = run_query(query, parameters={"name": name})
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

@app.on_event("shutdown")
async def shutdown_event():
    driver.close()
