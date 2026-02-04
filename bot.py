import os
import random
import json
from datetime import date, timedelta
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

SPECIAL_QUOTE = "You stayed disciplined for 5 days straight. This is how champions are built. — CBUM"


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not found")

QUOTES = [
    "Discipline beats motivation. Show up every day. ",
    "Consistency is the real cheat code. ",
    "You don’t need motivation. You need standards. ",
    "Every rep is a vote for the person you want to become. ",
    "If it was easy, everyone would do it."
]
DATA_FILE = "users.json"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def update_streak(user_id):
    users = load_users()
    today = date.today().isoformat()

    user = users.get(user_id, {
        "last_date": None,
        "streak": 0
    })

    last_date = user["last_date"]
    streak = user["streak"]

    if last_date == today:
        pass
    elif last_date == (date.today() - timedelta(days=1)).isoformat():
        streak += 1
    else:
        streak = 1

    user["last_date"] = today
    user["streak"] = streak
    users[user_id] = user

    save_users(users)
    return streak

def get_random_quote(exclude=None):
    choices = [q for q in QUOTES if q != exclude]
    return random.choice(choices)

async def start(update, context):
    user_id = str(update.effective_user.id)
    streak = update_streak(user_id)

    if streak == 5:
        await update.message.reply_text(SPECIAL_QUOTE)
        return

    quote = get_random_quote()
    context.user_data["last_quote"] = quote

    keyboard = [
        [InlineKeyboardButton("Next quote 💪", callback_data="next")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        quote,
        reply_markup=reply_markup
    )


async def next_quote(update, context):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    streak = update_streak(user_id)

    if streak == 5:
        await query.edit_message_text(SPECIAL_QUOTE)
        return

    last_quote = context.user_data.get("last_quote")
    new_quote = get_random_quote(exclude=last_quote)
    context.user_data["last_quote"] = new_quote

    keyboard = [
        [InlineKeyboardButton("Next quote 💪", callback_data="next")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=new_quote,
        reply_markup=reply_markup
    )


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.add_handler(CallbackQueryHandler(next_quote, pattern="^next$"))

print("Bot is running...")
app.run_polling()