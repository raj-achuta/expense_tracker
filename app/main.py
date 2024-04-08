from dotenv import load_dotenv
load_dotenv()

from app.telegram import start_telegram

def main():
    start_telegram()