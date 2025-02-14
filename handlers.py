import datetime
from aiogram import Router, types, F
from db_utils import *

router = Router()

@router.message(F.text == "/start")
async def start(message: types.Message):
    
    await add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    welcome_text = (
        "👋 Привет! Я автоответчик.\n\n"
        "📌 Вот список доступных команд:\n"
        "➖ `/list` – Показать список команд\n"
        "➖ `/stats` – Показать количество пользователей\n"
        "➖ `/help` – Получить помощь\n\n"
        "💬 Вы можете задать мне вопросы, и я отвечу автоматически!"
    )
    await message.answer(welcome_text)

@router.message(F.text == "/list")
async def list_commands(message: types.Message):
    
    command_list = (
        "📋 **Список команд:**\n"
        "➖ `/start` – Начать работу с ботом\n"
        "➖ `/list` – Показать список команд\n"
        "➖ `/stats` – Показать количество пользователей\n"
        "➖ `/help` – Получить помощь\n"
        "➖ `/broadcast` – (Админ) Отправить сообщение всем пользователям. Используйте HH:MM (например, 14:30)\n\n"
        "🤖 **Автоответы:**\n"
        "🟢 *Если в вашем сообщении есть слова:*\n"
        "    🔹 `цена`, `price` → Я расскажу о наших ценах 💰\n"
        "    🔹 `поддержка`, `help`, `support` → Я помогу вам связаться с оператором 🆘\n"
        "    🔹 `контакты`, `contact`, `email` → Я подскажу, как нас найти 📞\n"
        "    🔹 `работа`, `vacancy`, `job` → Я расскажу про вакансии 👨‍💻\n"
        "    🔹 `отзывы`, `review`, `feedback` → Я покажу отзывы клиентов ⭐"
    )
    await message.answer(command_list, parse_mode="Markdown")

@router.message(F.text == "/help")
async def help_command(message: types.Message):
    
    help_text = (
        "🆘 **Помощь** 🆘\n\n"
        "🔹 *Как работает бот?*\n"
        "   Я автоматически отвечаю на часто задаваемые вопросы и помогаю вам найти нужную информацию.\n\n"
        "🔹 *Доступные команды:*\n"
        "   ➖ `/start` – Начать работу с ботом\n"
        "   ➖ `/list` – Список команд\n"
        "   ➖ `/stats` – Показать количество пользователей\n"
        "   ➖ `/help` – Получить помощь\n"
        "   ➖ `/broadcast` – (Админ) Отправить сообщение всем пользователям. Используйте HH:MM (например, 14:30)\n\n"
        "🔹 *Автоматические ответы на сообщения:*\n"
        "   - Если вы напишете `цена` или `price`, я расскажу о наших ценах 💰\n"
        "   - Если вы напишете `поддержка`, `help`, `support`, я подскажу контакты операторов 🆘\n"
        "   - Если вы напишете `контакты`, `contact`, `email`, я дам вам телефон 📞\n"
        "   - Если вы напишете `работа`, `vacancy`, `job`, я расскажу о вакансиях 👨‍💻\n"
        "   - Если вы напишете `отзывы`, `review`, `feedback`, я покажу отзывы клиентов ⭐\n\n"
        "🔹 *Как связаться с человеком?*\n"
        "   Напишите слово `поддержка`, и я подскажу контакты операторов."
    )
    await message.answer(help_text, parse_mode="Markdown")

@router.message(F.text == "/stats")
async def stats(message: types.Message):
    count = await get_user_count()
    await message.answer(f"📊 Общее количество зарегистрированных пользователей: {count}")

@router.message(F.text.startswith("/broadcast"))
async def schedule_broadcast(message: types.Message):
    
    args = message.text.split(" ", 2)
    
    if len(args) < 3:
        await message.answer("❌ Использование: `/broadcast HH:MM текст рассылки`")
        return
    
    try:
        time_str = args[1]
        text = args[2]
        broadcast_time = datetime.datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        await message.answer("❌ Неверный формат времени. Используйте HH:MM (например, 14:30)")
        return

    now = datetime.datetime.now()
    scheduled_time = datetime.datetime.combine(now.date(), broadcast_time)

    if scheduled_time < now:
        scheduled_time += datetime.timedelta(days=1)

    # Store in DB
    await add_scheduled_broadcast(text, scheduled_time)

    await message.answer(f"✅ Сообщение запланировано на {scheduled_time.strftime('%H:%M')}")

async def send_broadcast(bot, chat_ids, text):
    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id, text)
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")

async def process_scheduled_broadcasts(bot):
    while True:
        broadcasts = await get_scheduled_broadcasts()
        now = datetime.datetime.now()
        
        for broadcast in broadcasts:
            broadcast_id = broadcast["id"]
            message_text = broadcast["message"]
            scheduled_time = broadcast["scheduled_time"]

            if scheduled_time <= now:
                chat_ids = await get_all_users()
                await send_broadcast(bot, chat_ids, message_text)
                await mark_broadcast_as_sent(broadcast_id)
        
        await asyncio.sleep(0.5)

# Ключевые слова
@router.message(F.text.lower().contains("цена") |
                F.text.lower().contains("price"))
async def price_info(message: types.Message):
    await message.answer("💰 Наши услуги начинаются от $100. Свяжитесь с поддержкой для деталей.")

@router.message(F.text.lower().contains("поддержка") |
                F.text.lower().contains("help") |
                F.text.lower().contains("support"))
async def support_info(message: types.Message):
    await message.answer("🆘 Наша служба поддержки доступна 24/7. Напишите @support.")

@router.message(F.text.lower().contains("контакты") |
                F.text.lower().contains("contact") |
                F.text.lower().contains("email"))
async def contact_info(message: types.Message):
    await message.answer("📞 Наш телефон: +1 (234) 567-89-00\n📍 Адрес: Москва, ул. Полины Осипенко, 1")

@router.message(F.text.lower().contains("работа") |
                F.text.lower().contains("vacancy") |
                F.text.lower().contains("job"))
async def job_info(message: types.Message):
    await message.answer("👨‍💻 У нас есть открытые вакансии! Напишите @HR_manager.")

@router.message(F.text.lower().contains("отзывы") |
                F.text.lower().contains("review") |
                F.text.lower().contains("feedback"))
async def reviews_info(message: types.Message):
    await message.answer("⭐ Наши клиенты оставляют отзывы на сайте: https://example.com/reviews")
