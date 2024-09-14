from time import sleep
import flet as ft
import threading

class ProgressRingComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.progress_ring = ft.ProgressRing(width=16, height=16, stroke_width=2)
    
    def run_progress(self):
        for i in range(0, 101):
            self.progress_ring.value = i * 0.01
            sleep(0.1)
            self.page.update()

    def start_progress(self):
        threading.Thread(target=self.run_progress).start()

    def build(self):
        return ft.Column(
            [
                ft.Text("Circular progress indicator", style="headlineSmall"),
                ft.Row([self.progress_ring, ft.Text("Wait for the completion...")]),
                ft.Text("Indeterminate circular progress", style="headlineSmall"),
                ft.Column(
                    [ft.ProgressRing(), ft.Text("I'm going to run for ages...")],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ]
        )
