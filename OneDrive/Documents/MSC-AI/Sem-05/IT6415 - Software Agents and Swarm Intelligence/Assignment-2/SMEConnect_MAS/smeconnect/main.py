from .simulation.engine import run_one_offer

def main():
    result = run_one_offer()
    print("SMEConnect AI starter")
    print("Agent instances:", len(result["agents"]))
    print("Messages:", len(result["messages"]))
    print("Seller decision:", result["decision"])
    print("Note: multi-round negotiation and full MAS not yet implemented")

if __name__ == "__main__":
    main()
