import logging
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    Updater,
    CallbackContext,
)
import asyncio
import queue
import airtable
import traceback
import json

# Set up API credentials (replace with actual values)
api_key = "YOUR_API_KEY"
base_id = "YOUR_AIRTABLE_BASE_ID"
table_name = "YOUR_AIRTABLE_TABLE_NAME"

# Connect to Airtable API
client = airtable.Airtable(base_id, api_key)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = Bot(token="YOUR_BOT_TOKEN")

JOIN_GROUP = 0


# Command handler for /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Bot started. Send /join to join a group."
    )

    return JOIN_GROUP


# Command handler for /join command
async def join_group(update, context):
    chat_id = update.effective_chat.id

    # Inform user that joining via link is not possible
    await context.bot.send_message(chat_id=chat_id, text="Joining groups directly through links is not possible.")

    # Provide clear instructions
    instructions = (
        "To add me to a group, you (the group administrator) need to follow these steps:\n"
        "  1. Open the group you want to add me to.\n"
        "  2. Tap on the group's information panel (tap the group name at the top).\n"
        "  3. Tap on 'Add members' or 'Invite members'.\n"
        "  4. Search for my username (username_of_your_bot) and select me.\n"
        "  5. Confirm the addition."
    )
    await context.bot.send_message(chat_id=chat_id, text=instructions)

    # Optionally, provide a link to Telegram's documentation
    telegram_bot_docs = "https://core.telegram.org/bots#adding-a-bot-to-a-group"
    await context.bot.send_message(chat_id=chat_id, text=f"For more information, visit: {telegram_bot_docs}")


async def handle_message(update: Update, context: CallbackContext) -> None:
    try:
        message = update.message
        text = message.text
        chat_id = message.chat.id
        group_username = message.chat.username
        group_name = message.chat.title
        writer_username = message.from_user.username

        print(text)
        if "django" in text.lower():
            # Get the message link
            message_link = f"https://t.me/{group_username}/{message.message_id}"

            # Create a new record in the Airtable table
            try:
                record = {
                    "Contact": writer_username,
                    "Link": message_link
                }

                # Create record in Airtable
                response = client.create(table_name, record)
                logging.info("Airtable API response:")
                logging.info(json.dumps(response, indent=2))
            except Exception as e:
                logging.error(f"Error saving data to Airtable: {e}")
    except Exception as e:
        logging.error(f"Error in message handler: {e}")


def main() -> None:
    update_queue = queue.Queue()
    updater = Updater(bot=bot, update_queue=update_queue)

    start_handler = CommandHandler('start', start)
    join_group_handler = CommandHandler('join', join_group)
    message_handler = MessageHandler(
        filters.TEXT & ~(filters.COMMAND), handle_message)

    application = Application.builder().token(
        "6874916628:AAEM0-l6Y6lbEkDUBRk8Gwv7qk7ApMqRKzs").build()

    application.add_handler(start_handler)
    application.add_handler(join_group_handler)
    application.add_handler(message_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    asyncio.run(main())
