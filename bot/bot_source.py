
import logging
from datetime import datetime
from settings import TOKEN, TEXT
from data_base.db import get_or_create_user, update_user_status, user_subscribed
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          Updater)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

REG, PAY, LOCATION, BIO = range(4)


def start(update, context):
    user_id = update.message.from_user['id']
    user_name = update.message.from_user['first_name']
    language = update.message.from_user['language_code']

    user_status = get_or_create_user(user_id)

    if user_status['subscribed'] is not None:
        downloads = user_status['downloads']
        expired = user_status['subscription_expires']
        text = TEXT[language].START_SUBSCRIBED.format(user_name, downloads, expired)
    else:
        text = TEXT[language].START_UNSUBSCRIBED.format(user_name)

    update.message.reply_text(text)


def subscribe(update, context):
    print("subscribe")
    user_id = update.message.from_user['id']
    user_name = update.message.from_user['first_name']
    language = update.message.from_user['language_code']

    user_status = get_or_create_user(user_id)

    keyboard = [
        [InlineKeyboardButton("1 день", callback_data=str("day")),
         InlineKeyboardButton("1 месяц", callback_data=str("month")),
         InlineKeyboardButton("1 год", callback_data=str("year"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "На сколько подписаться",
        reply_markup=reply_markup
    )

    return REG


def registration(update, context):
    print("reg")
    print(update.callback_query.message.chat)
    user_id = update.callback_query.message.chat.id
    now_date = datetime.now()
    subscribe_data = update.callback_query.data

    user_status = update_user_status(user_id, now_date, subscribe_data)

    keyboard = [
        [InlineKeyboardButton("Оплатить", callback_data=str("pay"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.callback_query.message.reply_text(
        "Оплатить",
        reply_markup=reply_markup
    )

    return PAY


def pay(update, context):
    print("pay")
    user_id = update.callback_query.message.chat.id
    """check payment"""
    user_status = user_subscribed(user_id)
    sub_date_expires = user_status['subscription_expires']
    downloads_lim = user_status['downloads']
    update.callback_query.message.reply_text(
        f"Вы подписались до {sub_date_expires} "
        f"Осталось скачиваний сегодня {downloads_lim} "
        f"Что бы выбрать модель нажмите /getmodel",
    )


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    request_kwargs = {
        'proxy_url': 'https://167.172.140.184:3128',
    }
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True, request_kwargs=request_kwargs)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    subscribe_handler = ConversationHandler(
        entry_points=[CommandHandler('subscribe', subscribe)],
        states={
            REG: [CallbackQueryHandler(registration, pattern='(day|month|year)', pass_user_data=True)],
            PAY: [CallbackQueryHandler(pay, pattern='pay', pass_user_data=True)]
        },

        fallbacks=[CommandHandler('start', start)]
    )


    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(subscribe_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()