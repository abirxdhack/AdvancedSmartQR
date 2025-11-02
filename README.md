# 🎨 Advanced Smart QR Generator

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Telethon](https://img.shields.io/badge/Telethon-Latest-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**Ultimate QR Code Generator with Advanced Customization Features**

[Features](#-features) • [Installation](#-installation) • [Configuration](#-configuration) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Support](#-support)

</div>

---

## 📱 About

**Advanced Smart QR** is a powerful Telegram bot that generates highly customizable QR codes with advanced features. Built with **Telethon** and **uvloop** for maximum performance (20x faster than standard asyncio), this bot offers a complete QR code generation solution with an intuitive interface.

### 🌟 Key Highlights

- ⚡ **Ultra-Fast Performance** - Powered by uvloop for lightning-fast async operations
- 🎨 **5 Unique Styles** - Classic, Blue, Gradient, Dark, and Green themes
- 🖼️ **Logo Integration** - Add custom logos with shape options (Square, Circle, Rounded)
- 🏷️ **Text Labels** - Add custom text below QR codes
- 📐 **Multiple Sizes** - Small, Medium, Large, and Extra Large options
- 🔧 **Error Correction** - 4 levels of error correction (7%, 15%, 25%, 30%)
- 🌐 **Multi-Format Support** - URLs, WiFi, Phone, Email, SMS, vCard, and plain text

---

## ✨ Features

### 🎯 QR Code Generation
- Generate QR codes from various data types
- Support for up to **2953 characters**
- Real-time preview and settings adjustment
- Instant generation and download

### 🎨 Customization Options

#### **Styles**
- 🕷️ **Classic** - Traditional black squares
- 🕸️ **Blue** - Modern blue theme
- 🤖 **Gradient** - Purple gradient with rounded modules
- 🔍 **Dark** - Sleek dark gray
- 🙈 **Green** - Nature-inspired green circles

#### **Sizes**
- 🕷️ Small (10px boxes)
- 💫 Medium (15px boxes)
- 🙈 Large (20px boxes)
- 🙊 Extra Large (25px boxes)

#### **Error Correction Levels**
- 😔 Low (7% recovery)
- 👁️ Medium (15% recovery)
- 👀 High (30% recovery)
- 🫀 Max (25% recovery)

### 🖼️ Logo Features
- Upload custom logos
- Three shape options:
  - ⬜ Square
  - ⭕ Circle
  - ⏹️ Rounded
- Automatic logo sizing (25% of QR code)
- PNG transparency support

### 🏷️ Label Features
- Add custom text labels below QR codes
- Maximum 100 characters
- Bold, clear fonts
- Centered alignment

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token
- Telegram API ID and API Hash

### Step 1: Clone Repository
```bash
git clone https://github.com/abirxdhack/AdvancedSmartQR.git
cd AdvancedSmartQR
```

### Step 2: Install Dependencies
```bash
pip3 install -r requirements.txt
```

### Step 3: Configuration
Create a `config.py` file in the root directory:

```python
BOT_TOKEN = "your_bot_token_here"
UPDATE_URL = "https://t.me/your_channel"
API_ID = 12345678
API_HASH = "your_api_hash_here"
```

Create a `utils.py` file:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

LOGGER = logging.getLogger(__name__)
```

### Step 4: Run the Bot
```bash
python3 qr.py
```

---

## ⚙️ Configuration

### Getting Bot Token
1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token

### Getting API ID and API Hash
1. Visit [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Navigate to "API Development Tools"
4. Create a new application
5. Copy API ID and API Hash

---

## 📖 Usage

### Basic Commands

- `/start` - Welcome message with bot features
- `/qr` - Start QR code generation process

### Generation Process

1. **Send `/qr` command**
2. **Enter your data** (URL, text, WiFi credentials, etc.)
3. **Configure settings**:
   - Choose size
   - Select error correction level
   - Pick a style
   - Add logo (optional)
   - Add label (optional)
4. **Generate** - Click "Generate QR Code" button
5. **Download** - Receive your custom QR code

### Supported Data Formats

#### 📱 **URLs**
```
https://example.com
```

#### 📞 **Phone Numbers**
```
tel:+1234567890
```

#### 📧 **Email**
```
mailto:email@example.com
```

#### 📶 **WiFi Credentials**
```
WIFI:T:WPA;S:NetworkName;P:Password;;
```

#### 💬 **SMS**
```
smsto:+1234567890:Your message here
```

#### 👤 **vCard Contact**
```
BEGIN:VCARD
VERSION:3.0
FN:John Doe
TEL:+1234567890
EMAIL:john@example.com
END:VCARD
```

#### 📝 **Plain Text**
```
Any text up to 2953 characters
```

---

## 🖼️ Screenshots

### Main Interface
```
👋 Welcome to Ultimate QR Code Generator!

I can create customizable QR codes with features like:
📱 URLs | 📞 Phone | 📧 Email | 📶 WiFi | 💬 SMS | 👤 vCard

🎨 Features:
• Multiple styles and colors
• Custom logos in center
• Text labels below QR
• Error correction levels
• Adjustable sizes
```

### Settings Panel
```
⚙️ QR Code Settings

Data: https://example.com
Size: 📄 Medium
Error Correction: M (15%)
Style: ⬛ Classic

Configure your QR code and click 'Generate'!
```

---

## 🛠️ Technical Stack

- **Telethon** - Modern Telegram MTProto API framework
- **uvloop** - Ultra-fast asyncio event loop
- **qrcode** - QR code generation library
- **Pillow (PIL)** - Image processing and manipulation
- **Python 3.8+** - Programming language

---

## 📊 Performance

- **20x faster** than standard asyncio (thanks to uvloop)
- **Non-blocking I/O** - Handle multiple users simultaneously
- **Efficient memory usage** - Temporary file cleanup
- **Fast generation** - QR codes generated in milliseconds

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/abirxdhack/AdvancedSmartQR/issues)
- **Telegram**: Join our [Updates Channel](https://t.me/your_channel)
- **Email**: support@example.com

---

## 🙏 Acknowledgments

- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram client library
- [qrcode](https://github.com/lincolnloop/python-qrcode) - QR code generation
- [uvloop](https://github.com/MagicStack/uvloop) - Fast asyncio event loop
- [Pillow](https://github.com/python-pillow/Pillow) - Image processing

---

## 📈 Stats

![GitHub Stars](https://img.shields.io/github/stars/abirxdhack/AdvancedSmartQR?style=social)
![GitHub Forks](https://img.shields.io/github/forks/abirxdhack/AdvancedSmartQR?style=social)
![GitHub Issues](https://img.shields.io/github/issues/abirxdhack/AdvancedSmartQR)

---

<div align="center">

**Made with ❤️ by [AbirXDHack](https://github.com/abirxdhack)**

⭐ Star this repo if you find it useful!

</div>