import httpx

from app.core.config import settings


class TelegramClient:
    """Klien tipis untuk Telegram Bot API (mode webhook, panggilan sinkron)."""

    def __init__(self, token: str | None = None) -> None:
        self.token = token or settings.telegram_bot_token
        self.base = f"https://api.telegram.org/bot{self.token}"

    def _call(self, method: str, payload: dict) -> dict:
        with httpx.Client(timeout=15) as client:
            resp = client.post(f"{self.base}/{method}", json=payload)
            return resp.json()

    def send_message(self, chat_id, text, reply_markup=None) -> dict:
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return self._call("sendMessage", payload)

    def edit_message_text(self, chat_id, message_id, text, reply_markup=None) -> dict:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return self._call("editMessageText", payload)

    def answer_callback_query(self, callback_query_id, text=None) -> dict:
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        return self._call("answerCallbackQuery", payload)

    def get_file(self, file_id) -> str:
        """Kembalikan file_path Telegram untuk file_id (langkah sebelum download)."""
        result = self._call("getFile", {"file_id": file_id})
        return result["result"]["file_path"]

    def download_file(self, file_path) -> bytes:
        url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        with httpx.Client(timeout=30) as client:
            return client.get(url).content

    def set_webhook(self, url, secret_token=None) -> dict:
        payload = {"url": url}
        if secret_token:
            payload["secret_token"] = secret_token
        return self._call("setWebhook", payload)

    def delete_webhook(self) -> dict:
        return self._call("deleteWebhook", {})

    def get_me(self) -> dict:
        return self._call("getMe", {})
