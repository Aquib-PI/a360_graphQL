import json
import strawberry
from typing import Any
from graphql.language import ast

@strawberry.scalar(
    name="JSON",
    description="The `JSON` scalar type represents arbitrary JSON values"
)
def JSONScalar(value: Any) -> Any:
    """Pass-through for JSON values in GraphQL requests/responses."""
    return value

@JSONScalar.serializer
def serialize_json(value: Any) -> Any:
    # Ensure the value is JSON serializable
    return value

@JSONScalar.parser
def parse_json_literal(ast_node: ast.Node) -> Any:
    # Parse JSON literal values in GraphQL AST
    if isinstance(ast_node, ast.StringValue):
        return json.loads(ast_node.value)
    if isinstance(ast_node, ast.BooleanValue):
        return ast_node.value
    if isinstance(ast_node, ast.IntValue):
        return int(ast_node.value)
    if isinstance(ast_node, ast.FloatValue):
        return float(ast_node.value)
    if isinstance(ast_node, ast.ObjectValue):
        obj = {}
        for field in ast_node.fields:
            obj[field.name.value] = parse_json_literal(field.value)
        return obj
    if isinstance(ast_node, ast.ListValue):
        return [parse_json_literal(item) for item in ast_node.values]
    return None 