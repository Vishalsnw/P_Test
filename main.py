from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.utils import platform

if platform != 'android':
    from kivy.core.window import Window
    Window.size = (360, 640)


class CalculatorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 5

        self.display = TextInput(
            multiline=False,
            readonly=True,
            halign='right',
            font_size=48,
            size_hint=(1, 0.2),
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        self.add_widget(self.display)

        buttons_layout = GridLayout(cols=4, spacing=5, size_hint=(1, 0.8))

        buttons = [
            ('C', 'operator'), ('(', 'operator'), (')', 'operator'), ('/', 'operator'),
            ('7', 'number'), ('8', 'number'), ('9', 'number'), ('*', 'operator'),
            ('4', 'number'), ('5', 'number'), ('6', 'number'), ('-', 'operator'),
            ('1', 'number'), ('2', 'number'), ('3', 'number'), ('+', 'operator'),
            ('0', 'number'), ('.', 'number'), ('DEL', 'operator'), ('=', 'equals'),
        ]

        for btn_text, btn_type in buttons:
            btn = Button(
                text=btn_text,
                font_size=32,
                bold=True
            )

            if btn_type == 'number':
                btn.background_color = (0.3, 0.3, 0.3, 1)
            elif btn_type == 'operator':
                btn.background_color = (0.5, 0.5, 0.5, 1)
            elif btn_type == 'equals':
                btn.background_color = (0.2, 0.6, 0.9, 1)

            btn.bind(on_press=self.on_button_press)
            buttons_layout.add_widget(btn)

        self.add_widget(buttons_layout)

    def on_button_press(self, instance):
        current = self.display.text
        button_text = instance.text

        if button_text == 'C':
            self.display.text = ''
        elif button_text == 'DEL':
            self.display.text = current[:-1]
        elif button_text == '=':
            try:
                result = eval(current)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                self.display.text = str(result)
            except Exception:
                self.display.text = 'Error'
        else:
            self.display.text = current + button_text


class CalculatorApp(App):
    def build(self):
        self.title = 'Calculator'
        return CalculatorLayout()


if __name__ == '__main__':
    CalculatorApp().run()
