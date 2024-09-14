import flet as ft

class Data:
    def __init__(self) -> None:
        self.counter = 0

class SnackBarComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.data = Data()

    def on_click(self, e):
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Hello {self.data.counter}"))
        self.page.snack_bar.open = True
        self.data.counter += 1
        self.page.update()

    def build(self):
        return ft.ElevatedButton("Open SnackBar", on_click=self.on_click)
