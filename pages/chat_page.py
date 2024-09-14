import flet as ft
from utils.chat_with_doc import ChatWithDocs
import os
import shutil
import threading

EMB_PATH = "assets/model/all-MiniLM-L6-v2-F16.gguf"
MODEL_PATHS = {
    'qwen05b': 'assets/model/qwen2-0_5b-instruct-q8_0.gguf'
}

def chat_page(page: ft.Page):
    chat_with_docs = ChatWithDocs(EMB_PATH, MODEL_PATHS)
    # Lista de conversaciones
    conversation_list = ft.Column(scroll="auto", expand=True)
    selected_conversation = None
    page.vectors = None

    def load_conversations():
        files = os.listdir("assets/docs/")
        for file in files:
            if file.endswith(".pdf"):
                add_conversation(file)

    def add_conversation(file_name):
        def on_select(e):
            nonlocal selected_conversation
            if selected_conversation:
                selected_conversation.bgcolor = None
                selected_conversation.update()
            selected_conversation = e.control
            selected_conversation.bgcolor = ft.colors.GREY_100
            selected_conversation.update()
            start_load_document(file_name)
        
        def on_delete(e):
            file_path = os.path.join("assets", "docs", file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                conversation_list.controls.remove(conversation_button)
                page.update()
        
        conversation_button = ft.Container(
            content=ft.Row(
                [
                    ft.Text("  "+file_name, expand=True),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        on_click=on_delete,
                        style=ft.ButtonStyle(
                            color={ft.MaterialState.DEFAULT: ft.colors.GREY_600}
                        )
                    )
                ],
                alignment="spaceBetween"
            ),
            on_click=on_select,
            padding=0,
            border_radius=3
        )
        conversation_list.controls.append(conversation_button)
        page.update()

    def load_document(file_name):
        file_path = os.path.join("assets", "docs", file_name)
        text = chat_with_docs.load_pdf(file_path)
        texts = chat_with_docs.process_text(text)
        vectorstore = chat_with_docs.create_vector_store(texts)
        return vectorstore

    def start_load_document(file_name):
        threading.Thread(target=async_load_document, args=(file_name,)).start()

    def async_load_document(file_name):
        # Mostrar mensaje de carga
        processing_message.visible = True
        page.update()
        page.vectors = load_document(file_name)
        processing_message.visible = False
        page.snack_bar = ft.SnackBar(
            ft.Text("Documento procesado y listo para el chat."),
            action="Ok",
            open=True
        )
        page.update()

    def on_file_picked(e):
        if e.files:
            source_path = e.files[0].path
            file_name = os.path.basename(source_path)
            dest_path = os.path.join("assets", "docs", file_name)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy(source_path, dest_path)
            add_conversation(file_name)
    
    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    btn_add_conversation = ft.ElevatedButton(
        icon=ft.icons.FILE_UPLOAD,
        icon_color= ft.colors.GREY_700,
        text="Subir PDF",
        color=ft.colors.GREY_700,
        on_click=lambda _: file_picker.pick_files(),
        bgcolor=ft.colors.GREY_100
    )

    # SideBar
    sidebar = ft.Container(
        content=ft.Column(
            [
                conversation_list,
                btn_add_conversation
            ],
            spacing=0
        ),
        width=200,
        padding=10,
        border_radius=0,
        border=ft.Border(right=ft.BorderSide(1, ft.colors.GREY_600)),
        expand=False
    )

    # Área de chat
    chat_log = ft.Column(scroll="auto", expand=True)

    processing_message = ft.Text("Procesando documento...", visible=False)

    txt_input = ft.TextField(
        hint_text="Escribe tu mensaje...",
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=5
    )

    def send_message(e):
        user_message = txt_input.value
        if user_message:
            chat_log.controls.append(
                ft.Container(
                    content=ft.Text(f"Tú:\n {user_message}"),
                    padding=10,
                    bgcolor=ft.colors.BLUE_GREY_100,
                    border_radius=5
                )
            )
            page.update()
            txt_input.value = ""
            page.update()

            # Mostrar un indicador de carga
            loading_indicator = ft.ProgressRing(
                color=ft.colors.BLUE_GREY_400
            )
            
            chat_log.controls.append(loading_indicator)
            page.update()

            if selected_conversation:
                response = chat_with_docs.request_model(user_message, page.vectors, 50, 1000, 'qwen05b')
                chat_log.controls.remove(loading_indicator)
                chat_log.controls.append(
                    ft.Container(
                        content=ft.Text(f"Doc:\n {response}"),
                        padding=10,
                        bgcolor=ft.colors.GREY_300,
                        border_radius=5
                    )
                )
                page.update()

    btn_send = ft.IconButton(
        icon=ft.icons.SEND,
        on_click=send_message,
        style=ft.ButtonStyle(
            bgcolor={ft.MaterialState.DEFAULT: ft.colors.GREY_800},
            color={ft.MaterialState.DEFAULT: ft.colors.GREY_100},
            shape=ft.RoundedRectangleBorder(radius=5)
        )
    )

    input_row = ft.Row(
        [txt_input, btn_send],
        alignment="end",
        spacing=10
    )

    chat_area = ft.Column(
        [chat_log, input_row],
        spacing=10,
        expand=True
    )

    page.controls.clear()
    page.add(
        ft.Row(
            [
                sidebar,
                ft.Column(
                    [
                        ft.Container(content=processing_message, alignment=ft.alignment.center),
                        chat_area,
                    ],
                    expand=True
                )
            ],
            spacing=10,
            expand=True
        )
    )

    load_conversations()
    page.update()

ft.app(target=chat_page)
