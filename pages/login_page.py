import flet as ft
import requests
import webbrowser
from oauthlib.oauth2 import WebApplicationClient
from dotenv import load_dotenv
import os

# Load var from .env
load_dotenv()

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
REDIRECT_URI = os.getenv('REDIRECT_URI')

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def login_page(page: ft.Page):
    def login(e):
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=REDIRECT_URI,
            scope=["openid", "email", "profile"],
        )
        webbrowser.open(request_uri)

    login_button = ft.ElevatedButton(text="Login with Google", on_click=login)
    page.add(ft.Column([login_button], alignment="center", expand=True))
