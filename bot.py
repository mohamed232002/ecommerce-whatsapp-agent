
import os
import segno

from neonize import extract_text
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv, PairStatusEv

from agent import process_message


client = NewClient("whatsapp_session.db")


# Display only the latest QR code.
@client.event.qr
def on_qr(client: NewClient, data_qr: bytes) -> None:
    os.system("cls")
    print("=" * 45)
    print("WhatsApp - Scan QR Code")
    print("=" * 45)
    print("Open WhatsApp > Linked Devices > Link a Device\n")

    qr = segno.make_qr(data_qr)
    qr.terminal(compact=True, border=1)

    print("\nWaiting for QR scan...")


@client.event(ConnectedEv)
def on_connected(client: NewClient, event: ConnectedEv) -> None:
    print("\nWhatsApp connected successfully.")


@client.event(PairStatusEv)
def on_pair_status(client: NewClient, event: PairStatusEv) -> None:
    print(f"\nWhatsApp paired successfully: {event.ID.User}")




@client.event(MessageEv)
def on_message(client: NewClient, event: MessageEv) -> None:
    try:
        source = event.Info.MessageSource
        chat = source.Chat

        if getattr(source, "IsFromMe", False):
            return

        server = str(chat.Server)

        # Ignore WhatsApp Status updates.
        if server == "broadcast" or str(chat.User) == "status":
            return

        # Ignore group messages.
        if server == "g.us":
            return

        message_text = extract_text(event.Message)

        if not message_text or not message_text.strip():
            return

        phone = str(chat.User)

        if not phone:
            return

        print(f"\nCustomer ({phone}): {message_text}")

        response = process_message(message_text, phone)

        client.send_message(chat, str(response))

        print(f"Agent: {response}")

    except Exception as error:
        print(f"Error handling WhatsApp message: {error}")


if __name__ == "__main__":
    print("Starting E-Commerce WhatsApp AI Agent...")
    print("Waiting for WhatsApp connection...")

    client.connect()
