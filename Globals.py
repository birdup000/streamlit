import os
from dotenv import load_dotenv

load_dotenv()


def getenv(var_name: str):
    default_values = {
        "APP_NAME": "AGiXT",
        "AGIXT_URI": "http://agixt:7437",
        "AUTH_PROVIDER": "magicalauth",
        "APP_URI": "http://localhost:8501",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "%(asctime)s | %(levelname)s | %(message)s",
        "PRIMARY_COLOR": "#1E90FF",
        "BACKGROUND_COLOR": "#FFFFFF",
        "SECONDARY_BACKGROUND_COLOR": "#F8F8F8",
        "TEXT_COLOR": "#000000",
        "FONT": "Arial"
    }
    default_value = default_values[var_name] if var_name in default_values else ""
    return os.getenv(var_name, default_value)
