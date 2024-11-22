from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin User ID (Replace with actual Telegram user ID)
ADMIN_ID = '7533233807'  # Replace with your actual Telegram user ID

# The path to the file where IDs and message links are stored
IDS_FILE = 'id.txt'

# Start command handler: Welcomes the user and shows the price ranges
def start(update: Update, context: CallbackContext):
    keyboard = []

    # Read the available price ranges from the ids file (this will dynamically build the list of ranges)
    try:
        with open(IDS_FILE, "r") as file:
            lines = file.readlines()
        
        # Extract unique price ranges from the file
        price_ranges = set()
        for line in lines:
            price_range = line.split("|")[0].strip()
            price_ranges.add(price_range)
        
        # Create the keyboard dynamically based on the extracted price ranges
        for price_range in price_ranges:
            keyboard.append([InlineKeyboardButton(price_range, callback_data=price_range)])
        
        # If no price ranges were found, provide a default set
        if not keyboard:
            keyboard = [
                [InlineKeyboardButton("₹100-₹500", callback_data='100-500')],
                [InlineKeyboardButton("₹500-₹1000", callback_data='500-1000')],
                [InlineKeyboardButton("₹1000-₹5000", callback_data='1000-5000')],
            ]

    except FileNotFoundError:
        # Default ranges if file is missing
        keyboard = [
            [InlineKeyboardButton("₹100-₹500", callback_data='100-500')],
            [InlineKeyboardButton("₹500-₹1000", callback_data='500-1000')],
            [InlineKeyboardButton("₹1000-₹5000", callback_data='1000-5000')],
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Welcome to the BGMI ID Store! Please select a price range:", 
        reply_markup=reply_markup
    )

# Callback function to handle the selected price range and forward the corresponding ID message
def send_ids(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    price_range = query.data

    try:
        # Open the ids_data.txt file and search for the price range
        with open(IDS_FILE, "r") as file:
            lines = file.readlines()

        found = False
        for line in lines:
            # Check if the line starts with the selected price range
            if line.startswith(price_range):
                parts = line.split("|")
                links = [link.strip() for link in parts[1:]]  # Extract all links

                # Forward each message based on the link
                for link in links:
                    # Extract message ID from the link (format: https://t.me/your_channel/message_id)
                    message_id = link.split("/")[-1]

                    try:
                        # Extract the channel or group username (e.g., your_channel)
                        chat_id = link.split("/")[3]  # The third part of the URL is the channel name

                        # Forward the message to the user
                        update.message.forward(chat_id=update.message.chat_id, from_chat_id=chat_id, message_id=message_id)
                    except Exception as e:
                        query.edit_message_text(text=f"Failed to forward the message from {link}. Error: {e}")
                        return
                
                query.edit_message_text(text=f"Here is the information for the ₹{price_range} range.")
                found = True
                break

        if not found:
            query.edit_message_text(text=f"No IDs found for the range ₹{price_range}.")

    except FileNotFoundError:
        query.edit_message_text(text="The ID data file is missing. Please contact the admin.")

# Admin command to add an ID and link
def add_id(update: Update, context: CallbackContext):
    # Check if the user is the admin
    if str(update.message.from_user.id) != ADMIN_ID:
        update.message.reply_text("You are not authorized to use this command.")
        return
    
    # Get the command arguments
    if len(context.args) < 2:
        update.message.reply_text("Please provide the price range and the link. Example: /add_id 100-500 https://t.me/your_channel/12345")
        return
    
    price_range = context.args[0]
    links = context.args[1:]

    # Validate price range (allow any range format)
    if not price_range:
        update.message.reply_text("Invalid price range. Please provide a valid range like ₹100-₹500, ₹500-₹15000.")
        return

    try:
        # Open the file and append the new ID and link
        with open(IDS_FILE, 'a') as file:
            for link in links:
                file.write(f"{price_range} | {link}\n")
        
        update.message.reply_text(f"ID links for the ₹{price_range} range have been added successfully!")

    except Exception as e:
        update.message.reply_text(f"An error occurred while adding the ID: {e}")

# Error handler for unexpected issues
def error(update: Update, context: CallbackContext):
    logger.warning(f'Update {update} caused error {context.error}')

def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
    updater = Updater("7847570111:AAEn7w5MaTCHkRwyObQwgZhsr-dbmekcRAQ", use_context=True)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Command handler for /start
    dispatcher.add_handler(CommandHandler("start", start))
    
    # Callback handler for inline button presses (price range selection)
    dispatcher.add_handler(CallbackQueryHandler(send_ids))
    
    # Command handler for /add_id (Admin adds new ID)
    dispatcher.add_handler(CommandHandler("add_id", add_id))
    
    # Error handler
    dispatcher.add_error_handler(error)
   
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    