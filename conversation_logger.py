"""
Conversation Logger Module
Logs the conversation to a file if enabled in config
"""

import datetime
from config import Config

class ConversationLogger:
    def __init__(self):
        self.enabled = Config.ENABLE_CONVERSATION_LOGGING
        self.log_file = Config.LOG_FILE_PATH
        if self.enabled:
            with open(self.log_file, 'a') as f:
                f.write(f"\n--- New Conversation Session: {datetime.datetime.now()} ---\n")

    def log(self, speaker: str, text: str):
        if not self.enabled:
            return
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {speaker}: {text}\n") 