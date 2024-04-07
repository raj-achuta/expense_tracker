import os.path
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import SPREADSHEET_ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

EXPENSE_SHEET_NAME = "Expense!A2:F"
DATA_SHEET_NAME = "Data!"


def get_creds():
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  return creds

def read(creds, range):
  try:
    service = build("sheets", "v4", credentials=creds)

    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=range)
        .execute()
    )
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return
    
    return values
  except HttpError as err:
    print(err)

def append(creds, data):
  try:
    service = build("sheets", "v4", credentials=creds)

    sheet = service.spreadsheets().values()
    result = (
        sheet.append(
          spreadsheetId=SPREADSHEET_ID, 
          range=EXPENSE_SHEET_NAME,
          body={'values': data},
          insertDataOption='INSERT_ROWS',
          valueInputOption='USER_ENTERED'
        )
        .execute()
    )
  except HttpError as err:
    raise err

def get_category():
  return read(get_creds(), f"{DATA_SHEET_NAME}A1:B")

def append_sheet(data):
  append(get_creds(), [data])

def start():
  read(get_creds())
  append(get_creds(), [["123","1234"]])