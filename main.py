import flet as ft
from pages.chat_page import chat_page

def main(page: ft.Page):
    page.title = "Chat con tus documentos"
    page.vertical_alignment = "stretch"
    page.horizontal_alignment = "stretch"

    chat_page(page)

ft.app(target=main)