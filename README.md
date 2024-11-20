# 🤖 Telegram Image Compressor Bot

> A powerful Telegram bot for smart image compression and format conversion using TinyPNG API.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/TelegramBotFather/Image-Compressor)

## ✨ Features

- 🖼️ **Smart Compression**
  - Maintain quality while reducing size
  - Support for files up to 5MB
  - Multiple format support (JPEG, PNG, WebP)

- 🔄 **Format Conversion**
  - Convert between popular formats
  - Preserve image quality
  - Smart format recommendations

- 📊 **Usage Tracking**
  - Personal statistics
  - Compression history
  - Data savings metrics

- 👮 **Admin Features**
  - User management system
  - Broadcast messages
  - Usage statistics
  - Ban/Unban users

## 🛠️ Technical Stack

- **Python 3.9+**
- **Pyrogram** - Telegram MTProto API framework
- **TinyPNG API** - Image compression
- **MongoDB** - Data storage
- **Python-dotenv** - Environment management

## 📝 Usage Examples

1. **Direct File Compression**
   - Send an image file to the bot
   - Receive compressed version instantly

2. **URL Compression**
   - Send an image URL
   - Bot downloads, compresses, and returns the image

3. **Format Conversion**
   - Use `/convert` command
   - Select target format
   - Send image for conversion

## ⚙️ Advanced Configuration

```python
# Configurable Parameters
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
SUPPORTED_FORMATS = {'.webp', '.jpeg', '.jpg', '.png'}
RATE_LIMIT_SECONDS = 5
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔐 Security

- All files are processed securely
- Temporary files are automatically cleaned up
- Rate limiting prevents abuse
- User data is handled with care

## 📞 Support

For support, please open an issue or contact [@YourUsername](https://t.me/YourUsername) on Telegram.
