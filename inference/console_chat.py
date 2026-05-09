from inference.chat_engine import answer_question

print("\nBaiuGPT Production Console Chat")
print("Type 'exit' to quit\n")

while True:
    user = input("You: ").strip()

    if user.lower() == "exit":
        break

    answer = answer_question(user)

    print("\nBaiuGPT:")
    print(answer)
    print()