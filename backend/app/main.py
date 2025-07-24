from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.asgi import GraphQL
import app.db
from app.gql_api.schema import schema

app = FastAPI(title="KPI Dashboard GraphQL")

# 1) CORS: allow your front-end origin (or '*' for all during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # adjust if your React app runs elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2) Mount GraphQL
graphql_app = GraphQL(schema, graphiql=True)
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
