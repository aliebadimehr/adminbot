import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, CommandStart, BaseFilter

API_TOKEN = "8454313914:AAErG-SW2qWbqarlNouB5L6bsNwEHhdZUoM"
ADMIN_ID = 7947733356
CHANNEL_ID = -1003880102647

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
print("Bot is ready")  # پیام آماده بودن بات در ترمینال

class AdminFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id == ADMIN_ID

class PostStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_link = State()
    confirmation = State()

post_data = {}

@dp.message(CommandStart(), AdminFilter())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("سلام! لطفا متن پست را ارسال کنید.")
    await state.set_state(PostStates.waiting_for_text)

@dp.message(StateFilter(PostStates.waiting_for_text), AdminFilter())
async def process_text(message: types.Message, state: FSMContext):
    post_data['text'] = message.text
    await message.answer("متن دریافت شد. حالا عکس پست را ارسال کنید.")
    await state.set_state(PostStates.waiting_for_photo)

@dp.message(StateFilter(PostStates.waiting_for_photo), AdminFilter())
async def process_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("لطفا فقط عکس ارسال کنید.")
        return
    post_data['photo'] = message.photo[-1].file_id
    await message.answer("عکس دریافت شد. حالا لینک را ارسال کنید.")
    await state.set_state(PostStates.waiting_for_link)

@dp.message(StateFilter(PostStates.waiting_for_link), AdminFilter())
async def process_link(message: types.Message, state: FSMContext):
    post_data['link'] = message.text.strip()

    # ارسال پیش‌نمایش با دکمه دریافت فایل
    preview_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="دریافت فایل", url=post_data['link'])]])
    if 'photo' in post_data:
        sent_msg = await bot.send_photo(chat_id=ADMIN_ID, photo=post_data['photo'], caption=post_data['text'], reply_markup=preview_keyboard)
    else:
        sent_msg = await bot.send_message(chat_id=ADMIN_ID, text=post_data['text'], reply_markup=preview_keyboard)

    # دکمه تایید و لغو با inline_keyboard دو بعدی برای aiogram 3.x
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="تایید", callback_data="confirm"), InlineKeyboardButton(text="لغو", callback_data="cancel")]])
    await bot.send_message(chat_id=ADMIN_ID, text="آیا می‌خواهید این پست را ارسال کنید؟", reply_markup=confirm_keyboard)
    await state.set_state(PostStates.confirmation)

@dp.callback_query(AdminFilter())
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    print("CALLBACK RECEIVED:", callback_query.data)
    await callback_query.answer()

    current_state = await state.get_state()
    print("CURRENT STATE:", current_state)

    if current_state != PostStates.confirmation.state:
        print("IGNORED: Not in confirmation state")
        return

    if callback_query.data == 'cancel':
        await callback_query.message.edit_text("عملیات ارسال پست لغو شد.")
        await state.clear()
        post_data.clear()
        return

    if callback_query.data == 'confirm':
        post_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="دریافت فایل", url=post_data['link'])]]
        )

        if 'photo' in post_data:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=post_data['photo'],
                caption=post_data['text'],
                reply_markup=post_keyboard
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=post_data['text'],
                reply_markup=post_keyboard
            )

        await callback_query.message.edit_text("پست در کانال ارسال شد.")
        await state.clear()
        post_data.clear()

@dp.message(AdminFilter(), StateFilter(None))
async def debug_no_state(message: types.Message):
    print(f"Debug: Received message from admin without state: {message.text}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
