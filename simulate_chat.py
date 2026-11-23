
from agent import process_message, reset_customer_session


def main():
    print("=" * 50)
    print("E-Commerce WhatsApp AI Agent - Chat Simulator")
    print("=" * 50)
    print("Type 'exit' to quit.")
    print("Type 'reset' to reset the conversation.\n")

    customer_name = input("Enter your name: ").strip()

    if not customer_name:
        print("Customer name is required.")
        return

    phone = input("Enter your phone number: ").strip()

    if not phone:
        print("Phone number is required.")
        return

    print("\nChat started. You can now send messages.\n")

    while True:
        message = input("You: ").strip()

        if not message:
            continue

        if message.lower() == "exit":
            print("Chat ended.")
            break

        if message.lower() == "reset":
            reset_customer_session(phone)
            print("Conversation history has been reset.\n")
            continue

        response = process_message(message, phone)
        print(f"\nAssistant: {response}\n")


if __name__ == "__main__":
    main()
