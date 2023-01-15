from telethon import TelegramClient, events
import fitz, sys
from io import BytesIO
from uuid import uuid4
import os
from PIL import Image, ImageDraw
#
buffer = BytesIO()
#
ID = os.environ['ID']
HASH = os.environ['HASH']
TOKEN = os.environ['TOKEN']
DPI = int(os.environ['DPI'])
#
bot = TelegramClient('bot', ID, HASH).start(bot_token=TOKEN)
print('Bot started...')


#
@bot.on(events.NewMessage())
async def my_handler(event):
  msg = event.message
  doc = msg.document
  id = msg.chat_id
  try:
    mime = doc.mime_type
  except:
    mime = None
  if msg.message == "ping":
    event.respond("pong")
  if mime == "application/pdf":
    save_name = "file" + str(uuid4()) + ".pdf"
    send_name = "converted.png"
    response = await event.respond("Downloading PDF...")
    await event.download_media(save_name)
    await response.edit("Converting...")
    #
    zoom_x = 6.0
    zoom_y = 6.0
    stroke_width = 3
    stroke_color = 'black'
    mat = fitz.Matrix(zoom_x, zoom_y)
    doc = fitz.open(save_name)
    #
    page = doc[0]
    #
    pix = page.get_pixmap(matrix=mat)
    #
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    #
    width, height = img.size
    # Define the crop amount variables
    crop_left = 265
    crop_top = 3950
    crop_right = 1780
    crop_bottom = 150
    #
    crop_right2 = 255
    crop_left2 = 1800
    # Calculate the coordinates for cropping the image
    x1 = crop_left
    y1 = crop_top
    x2 = width - crop_right
    y2 = height - crop_bottom
    x12 = crop_left2
    x22 = width - crop_right2
    #
    converter = (float(DPI) / 2.54)
    #
    width_pixels = int(9 * converter)
    height_pixels = int(6 * converter)
    #
    img.show()
    cropped_img = img.crop((x1, y1, x2, y2))
    cropped_img2 = img.crop((x12, y1, x22, y2))
    # Create a blank image of 6x9 inches
    blank_img = Image.new('RGB', (4 * DPI, 6 * DPI), "white")
    blank_img.info["dpi"] = (DPI, DPI)
    # Resize the image to 4x6 cm
    scaled_img = cropped_img.resize((width_pixels, height_pixels))
    scaled_img2 = cropped_img2.resize((width_pixels, height_pixels))
    #
    wd, ht = blank_img.size
    wsd, wsh = scaled_img.size
    wsd2, wsh2 = scaled_img2.size
    #
    x_fac = int((wd - wsd) / 2)
    x_fac2 = int(((wd - wsd2) / 2))
    y_fac = int(((ht / 2) - wsh) / 2)
    y_fac2 = int((ht / 2) + (((ht / 2) - wsh2)) / 2)
    #
    xx = int(x_fac)
    xx2 = int(x_fac2)
    yy = int(y_fac)
    yy2 = int(y_fac2)
    # Draw a border around the image
    draw = ImageDraw.Draw(scaled_img)
    draw2 = ImageDraw.Draw(scaled_img2)
    draw.rectangle([0, 0, wsd - 1, wsh - 1],
                   width=stroke_width,
                   outline=stroke_color)
    draw2.rectangle([0, 0, wsd2 - 1, wsh2 - 1],
                    width=stroke_width,
                    outline=stroke_color)
    # Paste the scaled image into the blank image
    blank_img.paste(scaled_img, (xx, yy))
    blank_img.paste(scaled_img2, (xx2, yy2))
    # Save the final image
    blank_img.save(buffer,
                   format="PNG",
                   optimize=True,
                   quality=95,
                   resolution=(DPI, DPI))
    #
    await response.edit("Done !")
    await response.edit("Uploading...")
    buffer.seek(0)
    buffer.name = send_name
    await bot.send_file(id, buffer, force_document=True)
    os.remove(save_name)
    await response.delete()


bot.run_until_disconnected()
