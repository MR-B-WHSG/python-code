# main.py

from game import run_one_round

def main():
    scores = {}  # We'll only store scores["You"] in practice
    round_count = 1

    while True:
        print(f"\n=== Starting Round #{round_count} ===")
        run_one_round(scores, round_count)

        # Show player's current total
        you_score = scores.get("You", 0)
        print(f"\nYour total score so far: {you_score} points\n")

        ans = input("Play another round? (y/n) ").lower()
        if ans != 'y':
            break
        round_count += 1

    print("\n=== Final Score ===")
    print(f"You: {scores.get('You', 0)} points\n")

if __name__ == "__main__":
    main()
