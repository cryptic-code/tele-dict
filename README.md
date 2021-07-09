## 📖 Bring Dictionary to Your Telegram 🤖

A afternoon-project born out of boredom. Yet, fully functional and deployable with Flask.

The code isn't totally bullet-proof, though.

## Configuration ⚙

#### Dependencies
Simply run the following command in a virtual environment:
```sh
pip install -r requirements.txt
```

#### Environment Variables

- Your Telegram bot's access token should be set as `TELEGRAM-TOKEN` environment variable.
- As well as, your app's base url should be set as `APP_URL` environment variable.

Put it in a `.env` file for local development:

```
TELEGRAM_TOKEN=< your-token-here >
APP_URL=< your-url-here >
```

#### Webhook Registration

While running first time, just hit the index of your app's url to register the webhook with telegram.