from dotenv import load_dotenv
load_dotenv()

# from app.example import main1
from app.telegram import start_telegram

def main():
    start_telegram()