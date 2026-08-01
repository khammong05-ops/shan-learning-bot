import random
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ---------------------------------------------------------
# 1. Credentials (သႂ်ႇ Key ၸဝ်ႈၵဝ်ႇ တီႈၼႆႈ)
# ---------------------------------------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase Client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Wiktionary Shan Category URL
WIKTIONARY_CAT_URL = (
    "https://shn.wiktionary.org/w/index.php?title=ပိူင်ထၢၼ်ႈ:ၶေႃႈတေႃးတီး"
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


# ---------------------------------------------------------
# 2. Dynamic Scrapers (ဢဝ် dynamic data တီႈ ဝဵပ်ႉ Wiktionary)
# ---------------------------------------------------------
def fetch_words_from_wiktionary():
    """ ၵႂႃႇဢဝ် List ၶေႃႈၵႂၢမ်း တီႈ ဝဵပ်ႉ Wiktionary ၸဝ်ႈသြႃႇ Dynamic """
    words = []
    try:
        res = requests.get(WIKTIONARY_CAT_URL, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            category_div = soup.find("div", {"id": "mw-pages"})
            if category_div:
                links = category_div.find_all("a")
                for link in links:
                    w = link.text.strip()
                    if w and not w.startswith("ၼႃႈ"):
                        words.append(w)
    except Exception as e:
        print(f"❌ Scraper Warning: {e}")

    # Fallback list ပေႃး Net Connection မီး ပိူင်ႈ
    if not words:
        words = [
            "မႂ်ႇသုင်",
            "ၶိူဝ်းတႆး",
            "ႁၵ်ႉ",
            "ၼမ်ႉၸႂ်",
            "မိူင်းတႆး",
            "လိၼ်း",
            "ၵႃႈ",
        ]

    return words


def get_wiktionary_word_data(word):
    """ ႁႃ File သဵင် တီႈ ၼႃႈ Detail Wiktionary """
    url = f"https://shn.wiktionary.org/wiki/{word}"
    audio_url = None
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            audio_tag = soup.find("audio")
            if audio_tag:
                source = audio_tag.find("source")
                if source and source.get("src"):
                    src = source["src"]
                    audio_url = src if src.startswith("http") else f"https:{src}"
    except Exception as e:
        print(f"❌ Audio Scraper Warning: {e}")

    return {"text": word, "audio": audio_url}


# ---------------------------------------------------------
# 3. Telegram Bot Handlers
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "✨ **သွၼ်ႁဵၼ်းလိၵ်ႈတႆး ၸဵဝ်းမေႃဝႆး** ✨\n"
        "──────────────────────\n"
        "မႂ်ႇသုင်ၶႃႈ လုၵ်ႈႁဵၼ်းႁၵ်ႉတင်းမူတ်း! 🌸\n"
        "ยินดีต้อนรับเข้าสู่บทเรียนภาษาไทใหญ่\n"
        "လိူၵ်ႈ ၸၼ်ႉၵၢၼ်ႁဵၼ်း ဢၼ်ၶႂ်ႈလဵပ်ႈႁဵၼ်း တၢင်းလုမ်ႈၼႆႉ လႆႈၶႃႈ:"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🌱 ႁဵၼ်းၸၼ်ႉငဝ်ႈ", callback_data="level_under_dev"
            )
        ],
        [
            InlineKeyboardButton(
                "🌿 ႁဵၼ်းၸၼ်ႉၵၢင်", callback_data="level_under_dev"
            )
        ],
        [
            InlineKeyboardButton(
                "🌳 ႁဵၼ်းၸၼ်ႉသုင်", callback_data="menu_advanced"
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ ၽိုၵ်းတႅမ်ႈလိၵ်ႈတႆး", callback_data="menu_practice_write"
            )
        ],
        [
            InlineKeyboardButton(
                "🗣️ ၽိုၵ်းလၢတ်ႈၵႂၢမ်းတႆး", callback_data="menu_practice_speak"
            )
        ],
    ]

    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "level_under_dev":
        dev_text = (
            "🙏 **ယွၼ်းၼွမ်းယႂ်ႇၼမ် မေႃသွၼ်ပႆႇတၼ်းၶႃႈ!**\n\n"
            "မႃးလဵပ်ႈႁဵၼ်း တွၼ်ႈၼႆႉ ဢွၼ်တၢင်းၵွၼ်ႇၶႃႈ 👇"
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    "✏️ ၽိုၵ်းတႅမ်ႈလိၵ်ႈတႆး",
                    callback_data="menu_practice_write",
                )
            ],
            [
                InlineKeyboardButton(
                    "📖 ၽိုၵ်းဢၢၼ်ႇလိၵ်ႈတႆး",
                    callback_data="menu_practice_read",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 ၶိုၼ်းၵႂႃႇ ၼႃႈႁူဝ်ၶေႃႈ", callback_data="go_main_menu"
                )
            ],
        ]
        await query.message.edit_text(
            dev_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif data == "menu_practice_write":
        write_text = (
            "✏️ **တွၼ်ႈ ၽိုၵ်းတႅမ်ႈလိၵ်ႈတႆး**\n\n"
            "လိူၵ်ႈ မူတ်း ဢၼ်ၶႂ်ႈ ၽိုၵ်းတႅမ်ႈ:"
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    "1️⃣ တူၺ်းလိၵ်ႈသေၽိုၵ်းတႅမ်ႈ",
                    callback_data="mode_write_visual",
                )
            ],
            [
                InlineKeyboardButton(
                    "2️⃣ ထွမ်ႇသဵင်သေၽိုၵ်းတႅမ်ႈ",
                    callback_data="mode_write_audio",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 ၶိုၼ်းၵႂႃႇ ၼႃႈႁူဝ်ၶေႃႈ", callback_data="go_main_menu"
                )
            ],
        ]
        await query.message.edit_text(
            write_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif data == "mode_write_visual":
        online_words = fetch_words_from_wiktionary()
        target_word = random.choice(online_words)

        context.user_data["target_word"] = target_word
        context.user_data["current_mode"] = "visual_write"

        prompt_msg = (
            f"📝 **ၶေႃႈၽိုၵ်းတႅမ်ႈ ( တူၺ်းလိၵ်ႈသေတႅမ်ႈ ):**\n\n"
            f"👉   `{target_word}`   👈\n\n"
            f"တႅမ်ႈ ၶေႃႈၵႂၢမ်း ၼိူဝ်ၼႆႉ သေ သူင်ႇ တွပ်ႇမႃး လႆႈ ၵမ်းလဵဝ်ၶႃႈ!"
        )
        await query.message.reply_text(prompt_msg, parse_mode="Markdown")

    elif data == "mode_write_audio":
        online_words = fetch_words_from_wiktionary()
        target_word = random.choice(online_words)
        word_data = get_wiktionary_word_data(target_word)

        context.user_data["target_word"] = target_word
        context.user_data["current_mode"] = "audio_write"

        caption_msg = (
            "🎧 **ၶေႃႈၽိုၵ်းတႅမ်ႈ ( ထွမ်ႇသဵင်သေတႅမ်ႈ ):**\n\n"
            "ထွမ်ႇ သဵင် ဢၼ်သူင်ႇပၼ် ၼႆႉသေ တႅမ်ႈ ၶေႃႈၵႂၢမ်း ဢၼ်လႆႈထွမ်ႇ တွပ်ႇမႃးၶႃႈ!"
        )

        if word_data["audio"]:
            await query.message.reply_audio(
                audio=word_data["audio"],
                caption=caption_msg,
                parse_mode="Markdown",
            )
        else:
            await query.message.reply_text(
                f"🔊 သဵင်/လိၵ်ႈ: `{target_word}`\n\n{caption_msg}",
                parse_mode="Markdown",
            )

    elif data == "go_main_menu":
        await start(query, context)


async def check_student_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    student_text = update.message.text.strip()
    target_word = context.user_data.get("target_word")
    mode = context.user_data.get("current_mode", "general")
    user = update.effective_user

    if not target_word:
        await update.message.reply_text(
            "လိူၵ်ႈ ႁူဝ်ၶေႃႈ ၵၢၼ်ႁဵၼ်း တီႈ /start ဢွၼ်တၢင်းၶႃႈ!"
        )
        return

    # A. ပေႃး တွပ်ႇ ထုၵ်ႇမႅၼ်ႈ
    if student_text == target_word:
        celebration_effects = [
            "🎉✨💖 **ထုၵ်ႇမႅၼ်ႈယဝ်ႉၶႃႈ! ၵတ်ႉၶႅၼ်ႇလႅၼ်ႇလႅတ်း တႄႉတႄႉ!** ❤️💙",
            "🌟🥳 **မႅၼ်ႈဢမ်ႇမီးတီႈတီး! ၶႅမ်ႉလႅတ်းတႄႉတႄႉၶႃႈ!** 🎉✨",
        ]

        # 1. Direct Insert Data to Supabase
        try:
            supabase_data = {
    "author": user.full_name,
    "category": mode,
    "name_sci": target_word,
    "name_tai": student_text,
}

            supabase.table("student_responses").insert(
                supabase_data
            ).execute()
            print(f"✅ Supabase Direct Saved Success!")
        except Exception as e:
            print(f"❌ Supabase Insert Error: {e}")

        # 2. သူင်ႇ ႁူဝ်ၸႂ် / Confetti
        await update.message.reply_text(
            random.choice(celebration_effects), parse_mode="Markdown"
        )

        # 3. Dynamic Fetch ၶေႃႈမႂ်ႇ တီႈ ဝဵပ်ႉၸဝ်ႈသြႃႇ
        online_words = fetch_words_from_wiktionary()
        available_words = [w for w in online_words if w != target_word]
        next_word = random.choice(
            available_words if available_words else online_words
        )

        context.user_data["target_word"] = next_word

        next_msg = (
            f"🔄 **ၶေႃႈမႂ်ႇ ( တႃႇလဵပ်ႈႁဵၼ်းထႅင်ႈ ):**\n\n"
            f"👉   `{next_word}`   👈\n\n"
            f"တႅမ်ႈၸွမ်း ၶိုၼ်း လႆႈ ၵမ်းလဵဝ်ၶႃႈ!"
        )
        await update.message.reply_text(next_msg, parse_mode="Markdown")

    # B. ပေႃး တွပ်ႇ ၽိတ်း
    else:
        wrong_msg = (
            f"❌ **ပႆႇထုၵ်ႇမႅၼ်ႈၶႃႈ!**\n\n"
            f"ၶေႃႈတွပ်ႇ ဢၼ်တႅမ်ႈမႃး: `{student_text}`\n"
            f"ၶေႃႈထုၵ်ႇမႅၼ်ႈ တႄႉ ပဵၼ်: 👉 **`{target_word}`** 👈\n\n"
            f"💡 *မႄး တႅမ်ႈပၼ် ၶိုၼ်း ႁႂ်ႈထုၵ်ႇမႅၼ်ႈ ၵမ်းၼိုင်ႈၶႃႈ!*"
        )
        await update.message.reply_text(wrong_msg, parse_mode="Markdown")


from telegram.request import HTTPXRequest

# ---------------------------------------------------------
# 4. Main Runner ( Fixed HTTPXRequest Proxy Argument )
# ---------------------------------------------------------
if __name__ == "__main__":
    # Standard Proxy URL တီႈ PythonAnywhere
    PROXY_URL = "http://proxy.server:3128"

    # 💡 မႄး တီႈၼႆႈ: ၸႂ်ႉ proxy=PROXY_URL (ဢမ်ႇၸႂ်ႉ proxy_url)
    request_config = HTTPXRequest(
        proxy=PROXY_URL, connect_timeout=30.0, read_timeout=30.0
    )

    # သႂ်ႇ request configuration ၶဝ်ႈ တီႈ ApplicationBuilder
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .request(request_config)
        .get_updates_request(request_config)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND, check_student_answer
        )
    )

    print("🤖 Bot Fixed & Running Perfectly on PythonAnywhere...")
    app.run_polling()
