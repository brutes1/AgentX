import ast
import json
import operator
from datetime import datetime

from openai import OpenAI

MODEL = "system"

client = OpenAI(
    base_url="http://127.0.0.1:1976/v1",
    api_key="fm",
)

SYSTEM_PROMPT = "You are AgentX, a capable and direct assistant. Use tools when they help answer accurately."

# --- Tools ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current local date and time.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluates a safe arithmetic expression and returns the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A math expression, e.g. '(3 + 5) * 2'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]


def _get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Safe AST-based math evaluator — no use of Python's built-in eval()
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _compute_node(node) -> float:
    if isinstance(node, ast.Constant):
        return node.n
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_compute_node(node.left), _compute_node(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_compute_node(node.operand))
    raise ValueError(f"Unsupported operation: {type(node).__name__}")


def _calculate(expression: str) -> str:
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_compute_node(tree.body))
    except Exception as e:
        return f"Error: {e}"


def _dispatch_tool(name: str, args: dict) -> str:
    if name == "get_current_time":
        return _get_current_time()
    if name == "calculate":
        return _calculate(**args)
    return f"Unknown tool: {name}"


# --- Agent loop ---

def run(user_message: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for _ in range(10):  # cap iterations to prevent runaway loops
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            stream=True,
        )

        content = ""
        tool_calls: dict[int, dict] = {}

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                content += delta.content
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    entry = tool_calls.setdefault(tc.index, {"id": "", "name": "", "arguments": ""})
                    if tc.id:
                        entry["id"] = tc.id
                    if tc.function.name:
                        entry["name"] += tc.function.name
                    if tc.function.arguments:
                        entry["arguments"] += tc.function.arguments

        if not tool_calls:
            return content

        # Reconstruct assistant message with tool calls
        assembled = [
            {"index": i, "id": v["id"], "type": "function",
             "function": {"name": v["name"], "arguments": v["arguments"]}}
            for i, v in tool_calls.items()
        ]
        messages.append({"role": "assistant", "content": content, "tool_calls": assembled})

        for call in assembled:
            result = _dispatch_tool(call["function"]["name"], json.loads(call["function"]["arguments"]))
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result,
            })

    return "Max iterations reached without a final response."


if __name__ == "__main__":
    print(f"AgentX online (model: {MODEL}). Type 'exit' to quit.\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break
        print(f"\nAgentX: {run(user_input)}\n")
