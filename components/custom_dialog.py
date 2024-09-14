import flet as ft

class DialogComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.dlg = ft.AlertDialog(
            title=ft.Text("Hello, you!"), 
            on_dismiss=lambda e: print("Dialog dismissed!")
        )
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("Do you really want to delete all those files?"),
            actions=[
                ft.TextButton("Yes", on_click=self.close_dlg_modal),
                ft.TextButton("No", on_click=self.close_dlg_modal),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

    async def close_dlg_modal(self, e):
        self.dlg_modal.open = False
        await self.page.update_async()

    async def open_dlg(self, e):
        self.page.dialog = self.dlg
        self.dlg.open = True
        await self.page.update_async()

    async def open_dlg_modal(self):
        self.page.dialog = self.dlg_modal
        self.dlg_modal.open = True
        await self.page.update_async()

    def build(self):
        return ft.Column(
            [
                ft.ElevatedButton("Open dialog", on_click=self.open_dlg),
                ft.ElevatedButton("Open modal dialog", on_click=self.open_dlg_modal),
            ]
        )
