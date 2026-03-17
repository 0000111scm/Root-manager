from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from threading import Thread

import root_cleaner_core as core


class RootCleanerUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=10, **kwargs)

        self.status_label = Label(text="Pronto", halign="center", valign="middle")
        self.status_label.bind(size=self.status_label.setter("text_size"))

        btn_fast = Button(text="Limpeza rápida", size_hint=(1, 0.2))
        btn_aggr = Button(text="Limpeza agressiva", size_hint=(1, 0.2))
        btn_analyze = Button(text="Somente análise", size_hint=(1, 0.2))

        btn_fast.bind(on_release=lambda *_: self.run_action("fast"))
        btn_aggr.bind(on_release=lambda *_: self.run_action("aggressive"))
        btn_analyze.bind(on_release=lambda *_: self.run_action("analyze"))

        self.add_widget(self.status_label)
        self.add_widget(btn_fast)
        self.add_widget(btn_aggr)
        self.add_widget(btn_analyze)

    def set_status(self, text):
        self.status_label.text = text

    def run_action(self, mode: str):
        self.set_status("Executando... aguarde (pode demorar)")

        def task():
            if not core.has_root():
                msg = "Sem acesso root (conceda permissão ao app)."
            else:
                if mode == "fast":
                    report = core.fast_clean()
                elif mode == "aggressive":
                    report = core.aggressive_clean()
                else:
                    report = core.analyze_only()

                msg = f"Concluído. Liberado ~{core.human_size(report.total_bytes_freed)}"

            Clock.schedule_once(lambda *_: self.set_status(msg), 0)

        Thread(target=task, daemon=True).start()


class RootCleanerApp(App):
    def build(self):
        self.title = "Root Cleaner"
        return RootCleanerUI()


if __name__ == "__main__":
    RootCleanerApp().run()
