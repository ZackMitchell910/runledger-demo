"""Tiny refund/support agent under test.

Speaks RunLedger's stdio JSON protocol: reads task_start / tool_result
messages on stdin, writes tool_call / final_output messages on stdout.
Human-readable logs go to stderr only.

Policy: an agent must look up the order (to confirm it exists, is refundable,
and get the real charged amount) BEFORE it issues a refund.
"""
import json
import sys


def send(payload):
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def recv():
    for line in sys.stdin:
        line = line.strip()
        if line:
            return json.loads(line)
    raise SystemExit(1)


def call_tool(name, call_id, args):
    send({"type": "tool_call", "name": name, "call_id": call_id, "args": args})
    msg = recv()
    if msg.get("type") != "tool_result" or not msg.get("ok"):
        raise RuntimeError(f"tool {name} failed: {msg.get('error')}")
    return msg["result"]


def main():
    task = recv()
    ticket = task.get("input", {})
    order_id = ticket["order_id"]

    # "Speed-up": the customer already told us the amount, so refund right
    # away and look the order up afterwards just to fill in the reply.
    refund = call_tool(
        "issue_refund", "c1",
        {"order_id": order_id, "amount_usd": ticket["claimed_amount_usd"]},
    )
    order = call_tool("lookup_order", "c2", {"order_id": order_id})

    send({"type": "final_output", "output": {
        "decision": "refund",
        "order_id": order_id,
        "refund_id": refund["refund_id"],
        "reply": f"Refunded ${order['amount_usd']:.2f} for order {order_id}.",
    }})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
