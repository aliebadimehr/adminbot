import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, CommandStart

API_TOKEN = "8454313914:AAErG-SW2qWbqarlNouB5L6bsNwEHhdZUoM"
ADMIN_ID = 7947733356
CHANNEL_ID = -1003880102647

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
print("Bot is ready")  # پیام آماده بودن بات در ترمینال

class PostStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_link = State()
    confirmation = State()

post_data = {}

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("سلام! لطفا متن پست را ارسال کنید.")
    await state.set_state(PostStates.waiting_for_text)

@dp.message(StateFilter(PostStates.waiting_for_text))
async def process_text(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    post_data['text'] = message.text
    await message.answer("متن دریافت شد. حالا عکس پست را ارسال کنید.")
    await state.set_state(PostStates.waiting_for_photo)

@dp.message(StateFilter(PostStates.waiting_for_photo))
async def process_photo(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.photo:
        await message.answer("لطفا فقط عکس ارسال کنید.")
        return
    post_data['photo'] = message.photo[-1].file_id
    await message.answer("عکس دریافت شد. حالا لینک را ارسال کنید.")
    await state.set_state(PostStates.waiting_for_link)

@dp.message(StateFilter(PostStates.waiting_for_link))
async def process_link(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
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

@dp.callback_query(StateFilter(PostStates.confirmation))
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id != ADMIN_ID:
        return

    if callback_query.data not in ['confirm', 'cancel']:
        return

    if callback_query.data == 'cancel':
        await callback_query.message.edit_text("عملیات ارسال پست لغو شد.")
        await state.clear()
        post_data.clear()
        return

    # اگر تایید شد، ارسال به کانال
    elif callback_query.data == 'confirm':
        post_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="دریافت فایل", url=post_data['link'])]])
        if 'photo' in post_data:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=post_data['photo'], caption=post_data['text'], reply_markup=post_keyboard)
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=post_data['text'], reply_markup=post_keyboard)

        await callback_query.message.edit_text("پست در کانال ارسال شد.")
        await state.clear()
        post_data.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
