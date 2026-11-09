"""Exactly two read-only MCP tools. Service and actor validation on every HTTP request."""
from datetime import datetime, timezone
import hmac
import json
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
import uuid

from mcp.server.lowlevel import Server
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool
from pydantic import BaseModel, ConfigDict, StrictStr, ValidationError
from starlette.responses import JSONResponse
import uvicorn

from fixtures import EMPLOYEES, search, balance

SECRET = Path("/state/service_secret").read_text()
IDENTITIES = json.loads(Path("/state/test-identities.json").read_text())
AUDIT = Path("/audit/audit.jsonl")
handler = RotatingFileHandler(AUDIT, maxBytes=1048576, backupCount=4)
audit_logger = logging.getLogger("thiga.audit")
audit_logger.setLevel(logging.INFO)
audit_logger.propagate = False
audit_logger.addHandler(handler)


def audit(event: str, reason: str, actor: str | None = None, tool: str | None = None,
          correlation: str | None = None) -> None:
    # Fixed fields and controlled values only: no header, argument or exception dump.
    row = {"date_utc": datetime.now(timezone.utc).isoformat(), "event": event,
           "reason": reason, "actor": actor, "tool": tool, "correlation": correlation}
    line = json.dumps(row, ensure_ascii=False)
    audit_logger.info(line)
    print(line, flush=True)


class SearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    query: StrictStr


class BalanceArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    employee_id: StrictStr


MODELS = {"search_employee": SearchArgs, "get_leave_balance": BalanceArgs}


def result(value, error=False):
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(value, ensure_ascii=False))],
                          is_error=error)


async def list_tools(ctx, params):
    audit("tools_list", "allowed", ctx.request.scope["state"]["actor"],
          correlation=ctx.request.scope["state"]["correlation"])
    return ListToolsResult(tools=[Tool(name=name, description=description,
                                      input_schema=MODELS[name].model_json_schema())
        for name, description in [
            ("search_employee", "Recherche exacte normalisée dans l'annuaire professionnel fictif de votre entreprise."),
            ("get_leave_balance", "Solde fictif enregistré, personnel ou d'un subordonné direct autorisé.")]])


async def call_tool(ctx, params):
    state = ctx.request.scope["state"]
    actor_id = state["actor"]
    name = params.name
    if name not in MODELS:
        audit("tools_call", "unknown_tool", actor_id, correlation=state["correlation"])
        return result("unavailable", True)
    try:
        args = MODELS[name].model_validate(params.arguments or {})
    except ValidationError:
        audit("tools_call", "invalid_arguments", actor_id, name, state["correlation"])
        return result("invalid_arguments", True)
    actor = EMPLOYEES[actor_id]
    if name == "search_employee":
        value, reason = search(actor, args.query), "allowed"
    else:
        value, reason = balance(actor, args.employee_id)
    audit("tools_call", reason, actor_id, name, state["correlation"])
    return result(value)


server = Server("thiga-phase-a", version="0.1.0", on_list_tools=list_tools, on_call_tool=call_tool)
inner_app = server.streamable_http_app(stateless_http=True, json_response=True, host="0.0.0.0")


class ServiceIdentityGate:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = scope.get("headers", [])
        auth_values = [v for k, v in headers if k.lower() == b"authorization"]
        actor_values = [v for k, v in headers if k.lower() == b"x-openwebui-user-id"]
        correlation = str(uuid.uuid4())
        mids = [v for k,v in headers if k.lower() == b"x-thiga-message-id"]
        if len(mids) == 1:
            try: correlation = str(uuid.UUID(mids[0].decode()))
            except ValueError: pass
        if len(auth_values) != 1 or not hmac.compare_digest(auth_values[0], f"Bearer {SECRET}".encode()):
            audit("http_denied", "service_auth", correlation=correlation)
            return await JSONResponse({"error": "unavailable"}, status_code=401)(scope, receive, send)
        account = actor_values[0].decode("utf-8", errors="replace") if len(actor_values) == 1 else ""
        actor = IDENTITIES.get(account)
        if actor not in EMPLOYEES:
            audit("http_denied", "actor_unknown", correlation=correlation)
            return await JSONResponse({"error": "unavailable"}, status_code=403)(scope, receive, send)
        scope.setdefault("state", {}).update(actor=actor, correlation=correlation)
        return await self.app(scope, receive, send)


app = ServiceIdentityGate(inner_app)

if __name__ == "__main__":
    # SDK validation errors may contain user input: suppress framework diagnostics.
    logging.getLogger("uvicorn").setLevel(logging.CRITICAL)
    logging.getLogger("mcp").setLevel(logging.CRITICAL)
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False, log_config=None)
