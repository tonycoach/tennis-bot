import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart
from aiogram import Router
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

class Order(StatesGroup):
    waiting_for_request = State()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Оставить заказ")],
        [KeyboardButton(text="ℹ️ О нас")],
        [KeyboardButton(text="🚚 Доставка и оплата")],
        [KeyboardButton(text="📞 Контакты")],
    ],
    resize_keyboard=True
)

back_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Назад")]],
    resize_keyboard=True
)

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🎾 Добро пожаловать!\n\n"
        "Здесь вы можете заказать теннисный инвентарь с доставкой из Европы в Россию.\n\n"
        "📦 Самые лучшие цены, помощь в подборе и простой способ оставить заявку прямо в чате.\n"
        "Выберите нужный раздел ниже 👇",
        reply_markup=main_menu
    )

@router.message(F.text == "📝 Оставить заказ")
async def handle_request(message: Message, state: FSMContext):
    await message.answer(
        "✏️ Опишите, что вам нужно. Укажите как можно больше параметров:\n\n"
        "🎾 Ракетки — бренд, модель, вес, размер головы, ручка\n"
        "👟 Кроссовки — бренд, модель, размер, грунт/хард, муж/жен\n"
        "🧵 Струны — бренд, название, толщина, комплект/бобина\n"
        "🩹 Намотки — бренд, цвет, количество\n\n"
        "📌 Пример:\n"
        "Wilson Blade 98, 305g, L2, 98 sq.in, 1 шт\n\n"
        "📬 После отправки заявки ожидайте ответ в личных сообщениях — "
        "мы напишем вам по наличию, цене и срокам доставки.",
        reply_markup=back_button
    )
    await state.set_state(Order.waiting_for_request)

@router.message(Order.waiting_for_request)
async def forward_request_to_admin(message: Message, state: FSMContext):
    text = message.text.strip()

    if not text or text == "🔙 Назад":
        await message.answer("❌ Заявка не отправлена. Вы ничего не ввели.", reply_markup=main_menu)
        await state.clear()
        return

    await message.answer("✅ Ваша заявка отправлена. Мы скоро свяжемся с вами.", reply_markup=main_menu)

    admin_text = (
        f"📥 Новая заявка от @{message.from_user.username or 'без ника'}:\n\n"
        f"{text}\n\n"
        f"Telegram ID: <code>{message.from_user.id}</code>"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=admin_text)
    await state.clear()

@router.message(F.text == "ℹ️ О нас")
async def about_us(message: Message):
    text = (
        "Мы доставляем теннисный инвентарь из Европы в Россию.\n\n"
        "Работаем с проверенными магазинами — предлагаем отличные цены, "
        "часто значительно ниже, чем в популярных онлайн-магазинах.\n\n"
        "💰 Примеры:\n\n"
        "Wilson Pro Staff 97 v14\n"
        "• Racketlon: 40 000 ₽\n"
        "• Tennispro: 40 000 ₽\n"
        "• У НАС: 23 000 ₽ *\n\n"
        "Luxilon BB Alu Power (бобина, 220 м)\n"
        "• Racketlon: 38 000 ₽\n"
        "• Tennispro: 40 000 ₽\n"
        "• У НАС: 24 000 ₽ *\n\n"
        "Nike Air Zoom Vapor 11 (кроссовки)\n"
        "• Racketlon: 31 900 ₽\n"
        "• Tennispro: 30 000 ₽\n"
        "• У НАС: 22 500 ₽ *\n\n"
        "* Цены ориентировочные. Зависит от курса и наличия в магазинах."
    )
    await message.answer(text, reply_markup=back_button)

@router.message(F.text == "🚚 Доставка и оплата")
async def delivery_info(message: Message):
    text = (
        "📦 Доставка:\n"
        "• Срок: от 7 до 30 дней\n"
        "• Способы: почта или с попутчиком\n"
        "• Мы сами надёжно упакуем товар\n\n"
        "💳 Оплата:\n"
        "• После подтверждения наличия и цены\n"
        "• Переводом на банковскую карту\n\n"
        "📬 Подтверждение перевода можно отправить прямо в бот (фото или скрин)"
    )
    await message.answer(text, reply_markup=back_button)

@router.message(F.text == "📞 Контакты")
async def contacts(message: Message):
    text = (
        "Вы можете связаться с нами, отправить ваш заказ или задать вопрос напрямую по любому из этих контактов:\n\n"
        "📱 Telegram: @antonbelikov\n"
        "📧 Email: anbelmax@gmail.com\n"
        "📞 WhatsApp: +7 918 568 09 20\n\n"
        "Будем рады помочь и ответить на любые вопросы!"
    )
    await message.answer(text, reply_markup=back_button)

@router.message(F.text == "🔙 Назад")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
