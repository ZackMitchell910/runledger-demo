"""Fake order backend used ONLY to record cassettes (runledger --mode record).

CI never calls these: it replays the recorded results from cassettes/*.jsonl.
"""
ORDERS = {
    "A-1001": {"order_id": "A-1001", "status": "delivered", "amount_usd": 49.0, "refundable": True},
}


def lookup_order(args):
    order = ORDERS.get(args["order_id"])
    if order is None:
        raise KeyError(f"order not found: {args['order_id']}")
    return dict(order)


def issue_refund(args):
    return {"refund_id": f"R-{args['order_id']}", "amount_usd": args["amount_usd"], "status": "issued"}


TOOLS = {"lookup_order": lookup_order, "issue_refund": issue_refund}
