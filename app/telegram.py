import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from app.config import TELEGRAM_TOKEN
from app.error_handler import error_handler
from app.cache import get_cache_category, get_cache_sub_category, contains_category, invalidate_cahce, contains_sub_category
from datetime import datetime, timedelta
from app.sheets import append_sheet

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

DESCRIPTION, CATEGORY, SUB_CATEGORY, DATE, PRICE, COMMENT = range(6)
data = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please enter description of your purchase"
    )
    return DESCRIPTION

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Description of purchase by %s: %s", user.first_name, update.message.text)
    
    cat = update.message.text
    
    data.append(cat)
    
    reply_keyboard = get_cache_category()
    
    await update.message.reply_text(
        "Description Noted! Please choose category",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )
    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("category of purchase by %s: %s", user.first_name, update.message.text)
    cat = update.message.text
    data.append(cat)
    
    text = "category Noted! please choose sub category"
    markup = None
    if(contains_category(cat)):
        reply_keyboard = get_cache_sub_category(cat)
        markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    
    await update.message.reply_text(
        text,
        reply_markup=markup
    )
    return SUB_CATEGORY

async def sub_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("sub_category of purchase by %s: %s", user.first_name, update.message.text)
    
    sub_cat = update.message.text
    data.append(sub_cat)
    
    current_date = datetime.now()
    
    if(not contains_sub_category(data[-2],sub_cat)):
        invalidate_cahce()
    
    reply_keyboard = [[
        (current_date - timedelta(days=1)).strftime('%m/%d/%Y'),
        current_date.strftime('%m/%d/%Y'),
        (current_date + timedelta(days=1)).strftime('%m/%d/%Y')
    ]]
    await update.message.reply_text(
        "sub_category Noted! enter date",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    )
    return DATE

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("date of purchase by %s: %s", user.first_name, update.message.text)
    data.append(update.message.text)
    
    await update.message.reply_text("date Noted! please enter price")
    return PRICE

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Description of purchase by %s: %s", user.first_name, update.message.text)
    data.append(update.message.text)
    await update.message.reply_text("Description Noted! please enter an comment or send /skip if you don't want to enter an comment")
    return COMMENT

async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("comment of purchase by %s: %s", user.first_name, update.message.text)
    data.append(update.message.text)
    text = "comment Noted! purchase updated in google sheet, use /start to add new purchase"
    try:
        append_sheet(data)
    except:
        text = "unabled to update google sheets, please try again later"
    data.clear()
    await update.message.reply_text(text)
    return ConversationHandler.END

async def skip_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "comment skipped! purchase updated in google sheet, use /start to add new purchase"
    try:
        append_sheet(data)
    except:
        text = "unabled to update google sheets, please try again later"
    data.clear()
    await update.message.reply_text(text)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data.clear()
    await update.message.reply_text("purchase info is cleared, use /start to add new purchase")
    return ConversationHandler.END

def start_telegram():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DESCRIPTION:[MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
            CATEGORY:[MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
            SUB_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, sub_category)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
            COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, comment),
                CommandHandler("skip",  skip_comment)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(conv_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)