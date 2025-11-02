import io
import os
from typing import Dict

import uvloop
from telethon import TelegramClient, events, Button
from telethon.tl.custom import Message
import qrcode
from qrcode import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    RoundedModuleDrawer,
    CircleModuleDrawer,
)
from PIL import Image, ImageDraw, ImageFont

from config import BOT_TOKEN, UPDATE_URL, API_ID, API_HASH
from utils import LOGGER

uvloop.install()

bot = TelegramClient('qr_bot', API_ID, API_HASH)

user_states: Dict[int, Dict] = {}
user_data: Dict[int, Dict] = {}

SIZES = {"small": 10, "medium": 15, "large": 20, "xlarge": 25}
ERROR_LEVELS = {"low": ERROR_CORRECT_L, "medium": ERROR_CORRECT_M, "high": ERROR_CORRECT_Q, "max": ERROR_CORRECT_H}
STYLES = {
    "classic": {"drawer": SquareModuleDrawer(), "color": (0, 0, 0)},
    "blue": {"drawer": SquareModuleDrawer(), "color": (0, 0, 255)},
    "gradient": {"drawer": RoundedModuleDrawer(), "color": (100, 0, 200)},
    "dark": {"drawer": SquareModuleDrawer(), "color": (30, 30, 30)},
    "green": {"drawer": CircleModuleDrawer(), "color": (0, 128, 0)},
}
LOGO_SHAPES = {"square": "⬜ Square", "circle": "⭕ Circle", "rounded": "⏹ Rounded"}

START_MSG = """👋 <b>Welcome to Ultimate QR Code Generator!</b>

I can create <b>customizable QR codes</b> with features like:
<code>📱 URLs | 📞 Phone | 📧 Email | 📶 WiFi | 💬 SMS | 👤 vCard</code>

🎨 <b>Features:</b>
<code>• Multiple styles and colors</code>
<code>• Custom logos in center</code>
<code>• Text labels below QR</code>
<code>• Error correction levels</code>
<code>• Adjustable sizes</code>

📌 <b>How to use:</b>
<code>• Send /qr to start generating</code>
<code>• Configure your QR code settings</code>
<code>• Add optional logo & label</code>
<code>• Generate and download!</code>

🔒 Works in <b>Private, Groups & Supergroups</b>.
✨ Ready? Send <code>/qr</code> to begin!
"""


def get_state(user_id: int) -> str:
    return user_states.get(user_id, {}).get("state", "")


def set_state(user_id: int, state: str):
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]["state"] = state


def clear_state(user_id: int):
    user_states.pop(user_id, None)
    user_data.pop(user_id, None)


def get_data(user_id: int) -> Dict:
    return user_data.get(user_id, {})


def set_data(user_id: int, data: Dict):
    user_data[user_id] = data


def get_initial_message() -> str:
    return (
        "<b>📱 QR Code Generator</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "Send me the data you'd like to convert into a QR code.\n\n"
        "<b>✅ Supported Formats:</b>\n"
        "<code>• Plain text</code>\n"
        "<code>• Website URLs → https://example.com</code>\n"
        "<code>• Phone numbers → tel:+1234567890</code>\n"
        "<code>• Email addresses → mailto:email@example.com</code>\n"
        "<code>• WiFi credentials → WIFI:T:WPA;S:NetworkName;P:Password;;</code>\n"
        "<code>• SMS messages → smsto:+1234567890:Your message</code>\n"
        "<code>• vCard contact info</code>\n\n"
        "<b>🔢 Max Length:</b> <code>2953 characters</code>"
    )


def get_settings_message(data: Dict) -> str:
    size_map = {"small": "📄 Small", "medium": "📄 Medium", "large": "📄 Large", "xlarge": "📄 Extra Large"}
    err_map = {"low": "L (7%)", "medium": "M (15%)", "high": "H (30%)", "max": "Q (25%)"}
    style_map = {"classic": "⬛ Classic", "blue": "🔵 Blue", "gradient": "🌈 Gradient", "dark": "⚫ Dark", "green": "🟢 Green"}

    size_text = size_map[data["size"]]
    err_text = err_map[data["error"]]
    style_text = style_map[data["style"]]

    logo_part = f"<b>Logo:</b> <code>{data['logo_shape']}</code>\n" if data.get("has_logo") else ""
    label_part = f"<b>Label:</b> <code>{data['label']}</code>\n" if data.get("label") else ""

    return (
        "<b>⚙️ QR Code Settings</b>\n\n"
        f"<b>Data:</b> <code>{data['text'][:50]}{'...' if len(data['text']) > 50 else ''}</code>\n"
        f"<b>Size:</b> <code>{size_text}</code>\n"
        f"<b>Error Correction:</b> <code>{err_text}</code>\n"
        f"<b>Style:</b> <code>{style_text}</code>\n"
        f"{logo_part}{label_part}\n"
        "<b>Configure your QR code and click 'Generate'!</b>"
    )


def build_settings_keyboard(data: Dict):
    buttons = []
    
    size_buttons = [
        ("small", "🕷 Small"),
        ("medium", "💫 Medium"),
        ("large", "🙈 Large"),
        ("xlarge", "🙊 Extra Large")
    ]
    row1 = []
    row2 = []
    for key, label in size_buttons:
        text = f"✅ {label.split()[1]}" if key == data["size"] else label
        if key in ["small", "medium"]:
            row1.append(Button.inline(text, f"size_{key}"))
        else:
            row2.append(Button.inline(text, f"size_{key}"))
    buttons.append(row1)
    buttons.append(row2)

    err_buttons = [
        ("low", "😔 Low"),
        ("medium", "👁 Medium"),
        ("high", "👀 High"),
        ("max", "🫀 Max")
    ]
    row3 = []
    row4 = []
    for key, label in err_buttons:
        text = f"✅ {label.split()[1]}" if key == data["error"] else label
        if key in ["low", "medium"]:
            row3.append(Button.inline(text, f"error_{key}"))
        else:
            row4.append(Button.inline(text, f"error_{key}"))
    buttons.append(row3)
    buttons.append(row4)

    buttons.append([Button.inline("🧠 Change Style", "change_style")])

    logo_text = "✅ Add Logo" if data.get("has_logo") else "✍ Add Logo"
    label_text = "✅ Add Label" if data.get("label") else "🔥 Add Label"
    buttons.append([
        Button.inline(logo_text, "add_logo"),
        Button.inline(label_text, "add_label")
    ])

    buttons.append([Button.inline("💥 Generate QR Code", "generate")])
    
    return buttons


def build_style_keyboard(data: Dict):
    buttons = []
    style_options = [
        ("classic", "🕷 Classic"),
        ("blue", "🕸 Blue"),
        ("gradient", "🤖 Gradient"),
        ("dark", "🔍 Dark"),
        ("green", "🙈 Green")
    ]
    
    row1 = []
    row2 = []
    row3 = []
    
    for i, (key, label) in enumerate(style_options):
        text = f"✅ {label.split()[1]}" if key == data["style"] else label
        btn = Button.inline(text, f"style_{key}")
        if i < 2:
            row1.append(btn)
        elif i < 4:
            row2.append(btn)
        else:
            row3.append(btn)
    
    buttons.append(row1)
    buttons.append(row2)
    buttons.append(row3)
    buttons.append([Button.inline("⬅️ Back To Settings", "back_settings")])
    
    return buttons


def build_logo_shape_keyboard():
    return [
        [Button.inline("⬜️ Square", "logo_square"), Button.inline("⭕️ Circle", "logo_circle")],
        [Button.inline("⏹ Rounded", "logo_rounded")],
        [Button.inline("◀️ Back To Settings", "back_settings")]
    ]


def build_logo_upload_keyboard():
    return [
        [Button.inline("✅ Choose Shape", "choose_logo_shape")],
        [Button.inline("🔍 Skip Logo", "skip_logo")]
    ]


def build_logo_photo_keyboard():
    return [[Button.inline("◀️ Skip Logo", "skip_logo")]]


def build_label_keyboard():
    return [[Button.inline("◀️ Skip Label", "skip_label")]]


@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event: Message):
    user_id = event.sender_id
    LOGGER.info(f"User {user_id} started bot")
    
    buttons = [[Button.url("📢 Updates Channel", UPDATE_URL)]]
    
    await bot.send_message(event.chat_id, START_MSG, buttons=buttons, parse_mode='html')
    print(f"Start message sent to {user_id}")


@bot.on(events.NewMessage(pattern='/qr'))
async def qr_handler(event: Message):
    user_id = event.sender_id
    LOGGER.info(f"User {user_id} started /qr")
    
    buttons = [[Button.inline("❌ Cancel", "cancel")]]
    await bot.send_message(event.chat_id, get_initial_message(), buttons=buttons, parse_mode='html')
    set_state(user_id, "waiting_data")
    print(f"QR prompt sent to {user_id}")


@bot.on(events.CallbackQuery(pattern=b'cancel'))
async def cancel_callback(event):
    user_id = event.sender_id
    LOGGER.info(f"User {user_id} cancelled")
    
    await event.edit("<b>❌ QR code generation cancelled.</b>", parse_mode='html')
    clear_state(user_id)
    await event.answer()
    print(f"Cancelled: {user_id}")


@bot.on(events.NewMessage())
async def message_handler(event: Message):
    if event.text and (event.text.startswith('/start') or event.text.startswith('/qr')):
        return
    
    user_id = event.sender_id
    state = get_state(user_id)
    
    if state == "waiting_data":
        text = event.text.strip()
        sender = await event.get_sender()
        full_name = sender.first_name or "User"
        
        print(f"Processing {full_name} Inputs")
        
        if len(text) > 2953:
            await bot.send_message(event.chat_id, "<b>❌ Text too long! Max 2953 characters.</b>", parse_mode='html')
            LOGGER.warning(f"Too long: {len(text)} from {user_id}")
            return
        if not text:
            await bot.send_message(event.chat_id, "<b>⚠️ Please send valid data.</b>", parse_mode='html')
            return

        print(f"Validating All Received Databases")
        
        data = {
            "text": text,
            "size": "medium",
            "error": "medium",
            "style": "classic",
            "has_logo": False,
            "logo_shape": None,
            "logo_image": None,
            "label": None,
        }
        set_data(user_id, data)
        set_state(user_id, "settings")

        buttons = build_settings_keyboard(data)
        await bot.send_message(event.chat_id, get_settings_message(data), buttons=buttons, parse_mode='html')
        await event.delete()
        LOGGER.info(f"Data received from {user_id}")
        
    elif state == "waiting_logo_photo":
        if event.photo:
            photo = await event.download_media(bytes)
            img = Image.open(io.BytesIO(photo))

            data = get_data(user_id)
            data["has_logo"] = True
            data["logo_image"] = img
            set_data(user_id, data)
            set_state(user_id, "settings")

            msg_text = (
                f"<b>✅ Logo uploaded!</b>\n"
                f"<b>Shape:</b> <code>{data['logo_shape']}</code>\n\n"
                f"<b>⚙️ QR Code Settings</b>\n\n"
                "<b>Ready to generate!</b>"
            )
            
            await bot.send_message(event.chat_id, msg_text, buttons=build_settings_keyboard(data), parse_mode='html')
            await event.delete()
            print("Logo received")
            
    elif state == "add_label":
        label = event.text.strip()
        if len(label) > 100:
            await bot.send_message(event.chat_id, "<b>❌ Label too long! Max 100 characters.</b>", parse_mode='html')
            return

        data = get_data(user_id)
        data["label"] = label
        set_data(user_id, data)
        set_state(user_id, "settings")

        logo_part = f"<b>✅ Logo uploaded!</b>\n<b>Shape:</b> <code>{data['logo_shape']}</code>\n\n" if data.get("has_logo") else ""
        msg_text = (
            f"{logo_part}"
            f"<b>✅ Label added!</b>\n\n"
            f"<b>⚙️ QR Code Settings</b>\n\n"
            "<b>Ready to generate!</b>"
        )
        
        await bot.send_message(event.chat_id, msg_text, buttons=build_settings_keyboard(data), parse_mode='html')
        await event.delete()
        print(f"Label: {label}")


@bot.on(events.CallbackQuery(pattern=b'size_'))
async def size_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "settings":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        size = event.data.decode().split("_")[1]
        data = get_data(user_id)
        
        size_names = {"small": "Small", "medium": "Medium", "large": "Large", "xlarge": "Extra Large"}
        
        if data["size"] == size:
            await event.answer(f"You Already Chosen {size_names[size]} As Size 🙄", alert=True)
            return
        
        data["size"] = size
        set_data(user_id, data)
        await event.edit(get_settings_message(data), buttons=build_settings_keyboard(data), parse_mode='html')
        await event.answer(f"QR Code Size Updated To {size_names[size]} Size")
        print(f"Size: {size}")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in size_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'error_'))
async def error_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "settings":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        error = event.data.decode().split("_")[1]
        data = get_data(user_id)
        
        error_percent = {"low": "7", "medium": "15", "high": "30", "max": "25"}
        error_names = {"low": "Low", "medium": "Medium", "high": "High", "max": "Max"}
        
        if data["error"] == error:
            await event.answer(f"You Already Chosen {error_names[error]} As Error Correction 🙄", alert=True)
            return
        
        data["error"] = error
        set_data(user_id, data)
        await event.edit(get_settings_message(data), buttons=build_settings_keyboard(data), parse_mode='html')
        await event.answer(f"Error Correction Updated To {error_percent[error]} Percent")
        print(f"Error: {error}")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in error_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'change_style'))
async def change_style_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "settings":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        data = get_data(user_id)
        set_state(user_id, "choose_style")
        buttons = build_style_keyboard(data)
        await event.edit(
            "<b>🎨 Select QR Code Style</b>\n\n<b>Choose a color scheme for your QR code:</b>",
            buttons=buttons,
            parse_mode='html'
        )
        await event.answer()
        print("Style menu")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in change_style_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'style_'))
async def style_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "choose_style":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        style = event.data.decode().split("_")[1]
        data = get_data(user_id)
        data["style"] = style
        set_data(user_id, data)
        set_state(user_id, "settings")
        await event.edit(get_settings_message(data), buttons=build_settings_keyboard(data), parse_mode='html')
        await event.answer()
        print(f"Style: {style}")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in style_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'back_settings'))
async def back_settings_callback(event):
    try:
        user_id = event.sender_id
        data = get_data(user_id)
        set_state(user_id, "settings")
        await event.edit(get_settings_message(data), buttons=build_settings_keyboard(data), parse_mode='html')
        await event.answer()
        print("Back")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in back_settings_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'add_logo'))
async def add_logo_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "settings":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        await event.edit(
            "<b>🖼️ Upload Logo Image</b>\n\n"
            "Send me an image to use as logo in QR code center.\n\n"
            "<b>✅ Best practices:</b>\n"
            "<code>• Use square or circular logos</code>\n"
            "<code>• High contrast with background</code>\n"
            "<code>• Simple designs work best</code>\n"
            "<code>• PNG with transparency recommended</code>\n"
            "<code>• Logo will be 25% of QR code size</code>\n\n"
            "<b>Choose shape or skip to continue without logo.</b>",
            buttons=build_logo_upload_keyboard(),
            parse_mode='html'
        )
        set_state(user_id, "upload_logo")
        await event.answer()
        print("Logo start")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in add_logo_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'choose_logo_shape'))
async def choose_logo_shape_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "upload_logo":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        set_state(user_id, "choose_logo_shape")
        await event.edit(
            "<b>🔲 Select Logo Shape</b>\n\n<b>Choose how your logo should appear:</b>",
            buttons=build_logo_shape_keyboard(),
            parse_mode='html'
        )
        await event.answer()
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in choose_logo_shape_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'logo_square'))
async def logo_square_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "choose_logo_shape":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        shape_text = LOGO_SHAPES["square"]
        data = get_data(user_id)
        data["logo_shape"] = shape_text
        set_data(user_id, data)
        set_state(user_id, "waiting_logo_photo")
        buttons = build_logo_photo_keyboard()
        await event.edit(
            f"<b>🖼️ Upload Logo Image</b>\n\n<b>Selected shape:</b> <code>{shape_text}</code>\n\n<b>Now send me the logo image.</b>",
            buttons=buttons,
            parse_mode='html'
        )
        await event.answer()
        print(f"Shape: {shape_text}")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in logo_square_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'logo_circle'))
async def logo_circle_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "choose_logo_shape":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        shape_text = LOGO_SHAPES["circle"]
        data = get_data(user_id)
        data["logo_shape"] = shape_text
        set_data(user_id, data)
        set_state(user_id, "waiting_logo_photo")
        buttons = build_logo_photo_keyboard()
        await event.edit(
            f"<b>🖼️ Upload Logo Image</b>\n\n<b>Selected shape:</b> <code>{shape_text}</code>\n\n<b>Now send me the logo image.</b>",
            buttons=buttons,
            parse_mode='html'
        )
        await event.answer()
        print(f"Shape: {shape_text}")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in logo_circle_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'logo_rounded'))
async def logo_rounded_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "choose_logo_shape":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        shape_text = LOGO_SHAPES["rounded"]
        data = get_data(user_id)
        data["logo_shape"] = shape_text
        set_data(user_id, data)
        set_state(user_id, "waiting_logo_photo")
        buttons = build_logo_photo_keyboard()
        await event.edit(
            f"<b>🖼️ Upload Logo Image</b>\n\n<b>Selected shape:</b> <code>{shape_text}</code>\n\n<b>Now send me the logo image.</b>",
            buttons=buttons,
            parse_mode='html'
        )
        await event.answer()
        print(f"Shape: {shape_text}")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in logo_rounded_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'skip_logo'))
async def skip_logo_callback(event):
    try:
        user_id = event.sender_id
        data = get_data(user_id)
        data["has_logo"] = False
        data.pop("logo_shape", None)
        data.pop("logo_image", None)
        set_data(user_id, data)
        set_state(user_id, "settings")
        await event.edit(get_settings_message(data), buttons=build_settings_keyboard(data), parse_mode='html')
        await event.answer()
        print("Logo skipped")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in skip_logo_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'add_label'))
async def add_label_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "settings":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        set_state(user_id, "add_label")
        await event.edit(
            "<b>🏷️ Label Text</b>\n\n"
            "Send me the text to display below QR code.\n"
            "<b>Example:</b> <code>Scan Me, My Website, etc.</code>\n\n"
            "<b>Click 'Skip Label' to continue without label.</b>",
            buttons=build_label_keyboard(),
            parse_mode='html'
        )
        await event.answer()
        print("Label start")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in add_label_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'skip_label'))
async def skip_label_callback(event):
    try:
        user_id = event.sender_id
        data = get_data(user_id)
        data.pop("label", None)
        set_data(user_id, data)
        set_state(user_id, "settings")
        await event.edit(get_settings_message(data), buttons=build_settings_keyboard(data), parse_mode='html')
        await event.answer()
        print("Label skipped")
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in skip_label_callback: {e}")


@bot.on(events.CallbackQuery(pattern=b'generate'))
async def generate_callback(event):
    try:
        user_id = event.sender_id
        state = get_state(user_id)
        
        if state != "settings":
            await event.answer("Session Expired Please Try Again", alert=True)
            return
            
        data = get_data(user_id)
        sender = await event.get_sender()
        full_name = sender.first_name or "User"
        temp_path = f"downloads/{user_id}.png"
        
        os.makedirs("downloads", exist_ok=True)
        
        print(f"Processing {full_name} Inputs")
        print(f"Validating All Received Databases")
        
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_LEVELS[data["error"]],
            box_size=SIZES[data["size"]],
            border=4,
        )
        qr.add_data(data["text"])
        qr.make(fit=True)

        style = STYLES[data["style"]]
        img = qr.make_image(
            fill_color=style["color"],
            back_color=(255, 255, 255),
            module_drawer=style["drawer"],
        )
        
        img = img.convert("RGB")

        if data.get("has_logo") and data.get("logo_image"):
            logo = data["logo_image"].copy()
            logo_size = img.size[0] // 4
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            
            if logo.mode != "RGBA":
                logo = logo.convert("RGBA")
            
            img_with_logo = Image.new("RGB", img.size, (255, 255, 255))
            img_with_logo.paste(img, (0, 0))
            
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            
            if logo.mode == "RGBA":
                img_with_logo.paste(logo, pos, logo)
            else:
                img_with_logo.paste(logo, pos)
            
            img = img_with_logo

        if data.get("label"):
            label_text = data["label"]
            label_height = 100
            new_img = Image.new("RGB", (img.size[0], img.size[1] + label_height), (255, 255, 255))
            new_img.paste(img, (0, 0))
            
            draw = ImageDraw.Draw(new_img)
            
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", 40)
                except:
                    font = ImageFont.load_default()
            
            try:
                bbox = font.getbbox(label_text)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(label_text) * 20
            
            text_x = (new_img.size[0] - text_width) // 2
            text_y = img.size[1] + 30
            
            draw.text((text_x, text_y), label_text, fill=(0, 0, 0), font=font)
            img = new_img

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        print(f"Generating Image -> /{temp_path}")
        
        with open(temp_path, "wb") as f:
            f.write(buf.getvalue())

        size_map = {"small": "Small", "medium": "Medium", "large": "Large", "xlarge": "Extra Large"}
        err_map = {"low": "L (7%)", "medium": "M (15%)", "high": "H (30%)", "max": "Q (25%)"}
        style_map = {"classic": "⬛ Classic", "blue": "🔵 Blue", "gradient": "🌈 Gradient", "dark": "⚫ Dark", "green": "🟢 Green"}

        size_text = size_map[data["size"]]
        err_text = err_map[data["error"]]
        style_text = style_map[data["style"]]

        caption = (
            "<b>✅ QR Code Generated</b>\n\n"
            f"<b>Size:</b> <code>📄 {size_text}</code>\n"
            f"<b>Style:</b> <code>{style_text}</code>\n"
            f"<b>Error Correction:</b> <code>{err_text}</code>"
        )

        await event.delete()
        await bot.send_file(
            event.chat_id,
            temp_path,
            caption=caption,
            parse_mode='html'
        )
        clear_state(user_id)
        await event.answer()
        LOGGER.info(f"QR sent to {user_id}")

        print(f"Cleaning Download -> /{temp_path}")
        try:
            os.remove(temp_path)
        except:
            pass
    except Exception as e:
        await event.answer("Session Expired Please Try Again", alert=True)
        LOGGER.error(f"Error in generate_callback: {e}")


async def main():
    print("Creating Bot Client From BOT_TOKEN")
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot Client Created Successfully!")
    LOGGER.info("Bot started successfully")
    print("Bot is running...")
    await bot.run_until_disconnected()


if __name__ == "__main__":
    uvloop.run(main())