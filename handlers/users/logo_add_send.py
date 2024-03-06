import json
from aiogram import types
from loader import dp, bot,db  # Assuming dp is your Dispatcher instance
from aiogram_media_group import MediaGroupFilter, media_group_handler
from aiogram.types import ContentType
from typing import List
import os
from aiogram.types import InputFile
from PIL import Image
from states.stateone import generateImage
from aiogram.dispatcher import FSMContext
from io import BytesIO
import aiohttp
from aiogram import types
import requests
import io
async def photo_link(photo: types.photo_size.PhotoSize) -> str:
    with await photo.download(BytesIO()) as file:
        form = aiohttp.FormData()
        form.add_field(
            name='file',
            value=file,
        )
        async with bot.session.post('https://telegra.ph/upload', data=form) as response:
            img_src = await response.json()

    link = 'http://telegra.ph/' + img_src[0]["src"]
    return link


@dp.message_handler(commands='logo',state=None)
async def get_photo(message: types.Message):
    await bot.send_photo(message.from_user.id,photo=InputFile('example_image.jpg'),caption='Iltimos rasmlarni shunaqa qilib logoni qo\'yishimiz uchun logotifingizni yuboring✅\n\n1)Logo png formatda bo\'lishi.\n2)Orqa foni qora bo\'lishi kerak!')
    await generateImage.logo.set()



@dp.message_handler(content_types=types.ContentType.PHOTO,state=generateImage.logo)
async def get_logo(message: types.Message,state: FSMContext):
    photo = message.photo[-1]
    id = message.from_user.id
    # stiker = await message.answer('⏳')
    link = await photo_link(photo)
    await message.answer(link)
    # await generateImage.send_images.set()
    await db.update_user_logo(link,id)
    await message.reply('Logo muvaffaqiyatli qo\'shildi\n\nRasmlaringizni yuborishingiz mumkin.')
    await state.finish()



@dp.message_handler(MediaGroupFilter(), content_types=ContentType.PHOTO)
@media_group_handler()
async def album_handler(messages: List[types.Message]):
    saved_file_paths = []
    captions = []

    for message in messages:
        data = message.to_python()
        photo_file_ids = [photo["file_id"] for photo in data.get("photo", [])]
        caption = message.caption
        captions.append(caption)

        # Download and save each photo
        photo_file = await bot.download_file_by_id(photo_file_ids[-1])
        file_path = f"{photo_file_ids[-1]}.png"  # Set your desired file path
        saved_file_paths.append(file_path)

        with open(file_path, 'wb') as photo_file_local:
            photo_file_local.write(photo_file.read())

        background = Image.open(file_path).convert("RGBA")
        user = await db.select_user(telegram_id=message.from_user.id)
        logo=user['logo']
        # Open foreground image (logo) and resize it to the same size as the background
        foreground_url = logo
        response = requests.get(foreground_url, stream=True)
        response.raise_for_status()

        foreground = Image.open(io.BytesIO(response.content)).convert("RGBA")
        foreground = foreground.resize(background.size)
        alpha = 0.6
        blended_image = Image.blend(background, foreground, alpha)

        blended_image_path = file_path
        os.remove(file_path)
        blended_image.save(blended_image_path)

    album = types.MediaGroup()

    for i, saved_file_path in enumerate(saved_file_paths):
        # Attach each photo with its corresponding caption
        album.attach_photo(InputFile(path_or_bytesio=f"{saved_file_path}"), caption=captions[i])

    await message.reply_media_group(media=album)

    # Optionally, you can clean up the saved files after sending them
    for saved_file_path in saved_file_paths:
        os.remove(saved_file_path)


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def process_photo(message: types.Message):
    rasm_file_id = message.photo[-1].file_id
    caption = message.caption
    rasm_path = f"{rasm_file_id}.png"

    await bot.download_file_by_id(rasm_file_id, rasm_path)

    background = Image.open(rasm_path).convert("RGBA")
    user = await db.select_user(telegram_id=message.from_user.id)
    logo=user['logo']
    # Open foreground image (logo) and resize it to the same size as the background
    foreground_url = logo
    response = requests.get(foreground_url, stream=True)
    response.raise_for_status()

    foreground = Image.open(io.BytesIO(response.content)).convert("RGBA")
    foreground = foreground.resize(background.size)


    alpha = 0.6
    blended_image = Image.blend(background, foreground, alpha)

    # Save the blended image to a temporary file
    blended_image_path = rasm_path
    os.remove(rasm_path)
    blended_image.save(blended_image_path)

    # Send the saved image
    with open(blended_image_path, "rb") as photo:
        await bot.send_photo(message.chat.id, photo,caption=caption)

    # Remove the temporary files
    os.remove(blended_image_path)
