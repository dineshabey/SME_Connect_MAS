from smeconnect.graphs.seller_graph import build_seller_graph

def test_counter_offer():
    result = build_seller_graph().invoke({"minimum_price":150.0,"target_price":170.0,"stock":500,"offered_price":160.0,"requested_quantity":200,"decision":""})
    assert result["decision"] == "COUNTER_OFFER"

def test_reject_overstock():
    result = build_seller_graph().invoke({"minimum_price":150.0,"target_price":170.0,"stock":100,"offered_price":200.0,"requested_quantity":200,"decision":""})
    assert result["decision"] == "REJECT"
