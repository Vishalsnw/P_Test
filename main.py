"""
Screen Guardian - Advanced Parental Control App
Professional timer-based approach with multiple features and overlay screens.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ListProperty, BooleanProperty
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.animation import Animation
from kivy.metrics import dp, sp
from kivy.core.audio import SoundLoader
import json
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict

try:
    from android.permissions import request_permissions, Permission
    from android import mActivity
    from jnius import autoclass, cast
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False
    print("Running on desktop - Android features disabled")


COLORS_DARK = {
    'primary': (0.13, 0.59, 0.95, 1),
    'primary_dark': (0.08, 0.4, 0.75, 1),
    'secondary': (0.29, 0.69, 0.31, 1),
    'accent': (1, 0.34, 0.13, 1),
    'background': (0.12, 0.12, 0.15, 1),
    'surface': (0.18, 0.18, 0.22, 1),
    'surface_light': (0.24, 0.24, 0.28, 1),
    'text_primary': (1, 1, 1, 1),
    'text_secondary': (0.7, 0.7, 0.75, 1),
    'error': (0.96, 0.26, 0.21, 1),
    'warning': (1, 0.76, 0.03, 1),
    'success': (0.3, 0.69, 0.31, 1),
}

COLORS_LIGHT = {
    'primary': (0.13, 0.59, 0.95, 1),
    'primary_dark': (0.08, 0.4, 0.75, 1),
    'secondary': (0.29, 0.69, 0.31, 1),
    'accent': (1, 0.34, 0.13, 1),
    'background': (0.95, 0.95, 0.97, 1),
    'surface': (1, 1, 1, 1),
    'surface_light': (0.92, 0.92, 0.94, 1),
    'text_primary': (0.1, 0.1, 0.12, 1),
    'text_secondary': (0.4, 0.4, 0.45, 1),
    'error': (0.9, 0.2, 0.15, 1),
    'warning': (0.9, 0.65, 0.0, 1),
    'success': (0.2, 0.6, 0.25, 1),
}

COLORS = COLORS_DARK

OVERLAY_THEMES = {
    'battery_drained': {
        'bg_color': (0.05, 0.05, 0.08, 1),
        'accent_color': (0.8, 0.2, 0.2, 1),
        'icon': '',
        'title': 'Battery Critically Low',
        'subtitle': 'Connect charger to continue',
        'percent': '0%',
        'detail': 'Device shutting down to protect battery health'
    },
    'system_update': {
        'bg_color': (0.05, 0.12, 0.2, 1),
        'accent_color': (0.13, 0.59, 0.95, 1),
        'icon': '',
        'title': 'System Update Required',
        'subtitle': 'Installing critical security patches',
        'percent': 'Please wait...',
        'detail': 'Do not turn off your device'
    },
    'overheating': {
        'bg_color': (0.15, 0.05, 0.02, 1),
        'accent_color': (1, 0.4, 0.1, 1),
        'icon': '',
        'title': 'Device Overheating',
        'subtitle': 'Temperature: 48°C',
        'percent': 'COOLING DOWN',
        'detail': 'Device paused to prevent hardware damage'
    },
    'storage_full': {
        'bg_color': (0.1, 0.08, 0.15, 1),
        'accent_color': (0.61, 0.15, 0.69, 1),
        'icon': '',
        'title': 'Storage Full',
        'subtitle': 'No space available',
        'percent': '99.9% Used',
        'detail': 'Delete files to continue using device'
    },
    'network_error': {
        'bg_color': (0.08, 0.1, 0.12, 1),
        'accent_color': (0.55, 0.55, 0.6, 1),
        'icon': '',
        'title': 'Network Unavailable',
        'subtitle': 'Connection lost',
        'percent': 'OFFLINE',
        'detail': 'Check your internet connection'
    },
    'maintenance': {
        'bg_color': (0.1, 0.12, 0.08, 1),
        'accent_color': (0.85, 0.65, 0.13, 1),
        'icon': '',
        'title': 'System Maintenance',
        'subtitle': 'Optimizing device performance',
        'percent': 'In Progress...',
        'detail': 'This may take several minutes'
    }
}

TIME_PRESETS = [
    {'label': '15m', 'minutes': 15},
    {'label': '30m', 'minutes': 30},
    {'label': '1h', 'minutes': 60},
    {'label': '2h', 'minutes': 120},
]

DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


class Config:
    CONFIG_FILE = "parental_config.json"
    STATS_FILE = "usage_stats.json"
    
    DEFAULT_CONFIG = {
        "parent_pin": "1234",
        "timer_minutes": 5,
        "timer_end_timestamp": None,
        "is_timer_active": False,
        "selected_overlay": "random",
        "custom_overlay_message": "",
        "break_reminder_enabled": True,
        "break_reminder_interval": 30,
        "warning_before_end": 5,
        "sound_enabled": True,
        "dark_mode": True,
        "recovery_question": "What is your favorite color?",
        "recovery_answer": "blue",
        "profiles": {
            "default": {
                "name": "Child",
                "daily_limit": 120,
                "schedule": {}
            }
        },
        "active_profile": "default",
        "extension_requests_enabled": True,
        "max_extension_minutes": 10,
        "pending_extension_request": None,
    }
    
    @classmethod
    def load(cls):
        try:
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    for key in cls.DEFAULT_CONFIG:
                        if key not in config:
                            config[key] = cls.DEFAULT_CONFIG[key]
                    return config
        except Exception as e:
            print(f"Error loading config: {e}")
        return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save(cls, config):
        try:
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    @classmethod
    def load_stats(cls):
        try:
            if os.path.exists(cls.STATS_FILE):
                with open(cls.STATS_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading stats: {e}")
        return {"daily": {}, "sessions": []}
    
    @classmethod
    def save_stats(cls, stats):
        try:
            with open(cls.STATS_FILE, 'w') as f:
                json.dump(stats, f)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    @classmethod
    def record_usage(cls, minutes):
        stats = cls.load_stats()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in stats["daily"]:
            stats["daily"][today] = 0
        stats["daily"][today] += minutes
        
        stats["sessions"].append({
            "date": today,
            "time": datetime.now().strftime("%H:%M"),
            "duration": minutes
        })
        
        if len(stats["sessions"]) > 100:
            stats["sessions"] = stats["sessions"][-100:]
        
        old_dates = [d for d in stats["daily"].keys() 
                     if (datetime.now() - datetime.strptime(d, "%Y-%m-%d")).days > 30]
        for d in old_dates:
            del stats["daily"][d]
        
        cls.save_stats(stats)


class AndroidHelper:
    overlay_view = None
    window_manager = None
    service_running = False
    
    @staticmethod
    def request_all_permissions():
        if not ANDROID_AVAILABLE:
            return
        permissions = [Permission.INTERNET, Permission.ACCESS_NETWORK_STATE]
        request_permissions(permissions)
    
    @staticmethod
    def start_timer_service():
        if not ANDROID_AVAILABLE:
            print("Would start timer service on Android")
            return True
        try:
            from android import mActivity
            from jnius import autoclass
            service = autoclass('org.parentalcontrol.youtubelimiter.ServiceTimerservice')
            
            # For Android 14+ (API 34/35), we need to specify the service type
            # We use DATA_SYNC as it's the most appropriate standard type for a background timer
            # that syncs usage state.
            service.start(mActivity, 'DATA_SYNC')
            
            AndroidHelper.service_running = True
            print("Timer service started successfully!")
            return True
        except Exception as e:
            print(f"Error starting timer service: {e}")
            return False
    
    @staticmethod
    def stop_timer_service():
        if not ANDROID_AVAILABLE:
            print("Would stop timer service on Android")
            return True
        try:
            from android import mActivity
            from jnius import autoclass
            service = autoclass('org.parentalcontrol.youtubelimiter.ServiceTimerservice')
            service.stop(mActivity)
            AndroidHelper.service_running = False
            print("Timer service stopped!")
            return True
        except Exception as e:
            print(f"Error stopping timer service: {e}")
            return False
    
    @staticmethod
    def request_overlay_permission():
        if not ANDROID_AVAILABLE:
            print("Overlay permission (simulated)")
            return
        try:
            Settings = autoclass('android.provider.Settings')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            context = mActivity
            if not Settings.canDrawOverlays(context):
                intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
                intent.setData(Uri.parse("package:" + context.getPackageName()))
                mActivity.startActivity(intent)
        except Exception as e:
            print(f"Error requesting overlay permission: {e}")
    
    @staticmethod
    def has_overlay_permission():
        if not ANDROID_AVAILABLE:
            return True
        try:
            Settings = autoclass('android.provider.Settings')
            context = mActivity
            return Settings.canDrawOverlays(context)
        except Exception as e:
            print(f"Error checking overlay permission: {e}")
            return False
    
    @staticmethod
    def show_overlay_window():
        if not ANDROID_AVAILABLE:
            print("Would show overlay window on Android - SIMULATED")
            return True
        try:
            from android.runnable import run_on_ui_thread
            @run_on_ui_thread
            def create_overlay_ui():
                try:
                    WindowManager = autoclass('android.view.WindowManager')
                    LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
                    LinearLayout = autoclass('android.widget.LinearLayout')
                    TextView = autoclass('android.widget.TextView')
                    Color = autoclass('android.graphics.Color')
                    Gravity = autoclass('android.view.Gravity')
                    Build = autoclass('android.os.Build')
                    TypedValue = autoclass('android.util.TypedValue')
                    Context = autoclass('android.content.Context')
                    
                    context = mActivity
                    wm = context.getSystemService(Context.WINDOW_SERVICE)
                    
                    if Build.VERSION.SDK_INT >= 26:
                        overlay_type = LayoutParams.TYPE_APPLICATION_OVERLAY
                    else:
                        overlay_type = 2038
                    
                    params = LayoutParams(
                        LayoutParams.MATCH_PARENT,
                        LayoutParams.MATCH_PARENT,
                        overlay_type,
                        LayoutParams.FLAG_NOT_FOCUSABLE | 
                        LayoutParams.FLAG_NOT_TOUCH_MODAL |
                        LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                        -3
                    )
                    params.gravity = Gravity.TOP | Gravity.START
                    
                    layout = LinearLayout(context)
                    layout.setOrientation(LinearLayout.VERTICAL)
                    layout.setGravity(Gravity.CENTER)
                    layout.setBackgroundColor(Color.BLACK)
                    
                    title = TextView(context)
                    title.setText("Screen Time Ended")
                    title.setTextColor(Color.WHITE)
                    title.setTextSize(TypedValue.COMPLEX_UNIT_SP, 48)
                    title.setGravity(Gravity.CENTER)
                    layout.addView(title)
                    
                    wm.addView(layout, params)
                    AndroidHelper.overlay_view = layout
                    AndroidHelper.window_manager = wm
                    print("Overlay shown successfully!")
                except Exception as e:
                    print(f"Error creating overlay: {e}")
            create_overlay_ui()
            return True
        except Exception as e:
            print(f"Error showing overlay: {e}")
            return False
    
    @staticmethod
    def hide_overlay_window():
        if not ANDROID_AVAILABLE:
            print("Would hide overlay window on Android")
            return True
        try:
            if AndroidHelper.overlay_view and AndroidHelper.window_manager:
                try:
                    from android.runnable import run_on_ui_thread
                    @run_on_ui_thread
                    def remove_ui():
                        try:
                            AndroidHelper.window_manager.removeView(AndroidHelper.overlay_view)
                            AndroidHelper.overlay_view = None
                            AndroidHelper.window_manager = None
                        except Exception as e:
                            print(f"Error removing overlay: {e}")
                    remove_ui()
                except ImportError:
                    AndroidHelper.window_manager.removeView(AndroidHelper.overlay_view)
                    AndroidHelper.overlay_view = None
                    AndroidHelper.window_manager = None
                return True
        except Exception as e:
            print(f"Error hiding overlay: {e}")
        return False
    
    @staticmethod
    def start_lock_task():
        if not ANDROID_AVAILABLE:
            print("Would start lock task mode")
            return True
        try:
            activity = mActivity
            activity.startLockTask()
            return True
        except Exception as e:
            print(f"Error starting lock task: {e}")
            return False
    
    @staticmethod
    def stop_lock_task():
        if not ANDROID_AVAILABLE:
            print("Would stop lock task mode")
            return True
        try:
            activity = mActivity
            activity.stopLockTask()
            return True
        except Exception as e:
            print(f"Error stopping lock task: {e}")
            return False
    
    @staticmethod
    def keep_screen_on(enable):
        if not ANDROID_AVAILABLE:
            return True
        try:
            from jnius import autoclass
            activity = mActivity
            window = activity.getWindow()
            WindowManager = autoclass('android.view.WindowManager')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            if enable:
                window.addFlags(LayoutParams.FLAG_KEEP_SCREEN_ON)
            else:
                window.clearFlags(LayoutParams.FLAG_KEEP_SCREEN_ON)
            return True
        except Exception as e:
            print(f"Error setting screen on: {e}")
            return False


class SoundManager:
    sounds = {}
    
    @classmethod
    def init(cls):
        pass
    
    @classmethod
    def play_warning(cls):
        print("Playing warning sound")
    
    @classmethod
    def play_alert(cls):
        print("Playing alert sound")
    
    @classmethod
    def play_tick(cls):
        print("Playing tick sound")


class GradientBackground(Widget):
    def __init__(self, colors=None, **kwargs):
        super().__init__(**kwargs)
        self.colors = colors or [COLORS['background'], COLORS['surface']]
        self.bind(size=self._update, pos=self._update)
        self._update()
    
    def _update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.colors[0])
            Rectangle(pos=self.pos, size=self.size)
    
    def update_colors(self, colors):
        self.colors = colors
        self._update()


class StyledButton(Button):
    def __init__(self, btn_color=None, text_color=None, **kwargs):
        super().__init__(**kwargs)
        self.btn_color = btn_color or COLORS['primary']
        self.text_color = text_color or COLORS['text_primary']
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.color = self.text_color
        self.bold = True
        self.bind(size=self._update, pos=self._update)
        self._update()
    
    def _update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.btn_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
    
    def set_color(self, color):
        self.btn_color = color
        self._update()


class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLORS['surface_light']
        self.foreground_color = COLORS['text_primary']
        self.cursor_color = COLORS['primary']
        self.padding = [dp(15), dp(12)]
        self.font_size = sp(18)


class CircularProgress(Widget):
    progress = NumericProperty(0)
    color = ListProperty([0.13, 0.59, 0.95, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(progress=self._update, size=self._update, pos=self._update, color=self._update)
        self._update()
    
    def _update(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.2, 0.2, 0.25, 1)
            d = min(self.width, self.height) - dp(20)
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2
            Line(circle=(center_x, center_y, d / 2), width=dp(8))
            
            Color(*self.color)
            angle = self.progress * 360
            if angle > 0:
                Line(circle=(center_x, center_y, d / 2, 0, angle), width=dp(8), cap='round')


class AnimatedProgressBar(Widget):
    progress = NumericProperty(0)
    color = ListProperty([0.13, 0.59, 0.95, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anim_offset = 0
        self.bind(size=self._update, pos=self._update, progress=self._update)
        Clock.schedule_interval(self._animate, 0.05)
        self._update()
    
    def _animate(self, dt):
        self.anim_offset = (self.anim_offset + 2) % 20
        self._update()
    
    def _update(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.15, 0.15, 0.18, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(6)])
            
            Color(*self.color)
            progress_width = self.width * min(1, max(0, self.progress))
            if progress_width > 0:
                RoundedRectangle(
                    pos=self.pos,
                    size=(progress_width, self.height),
                    radius=[dp(6)]
                )


class PulsingDot(Widget):
    color = ListProperty([0.8, 0.2, 0.2, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update, pos=self._update)
        self._update()
        self._animate()
    
    def _update(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*self.color)
            d = min(self.width, self.height)
            Ellipse(pos=(self.center_x - d/2, self.center_y - d/2), size=(d, d))
    
    def _animate(self):
        anim = Animation(opacity=0.3, duration=0.8) + Animation(opacity=1, duration=0.8)
        anim.repeat = True
        anim.start(self)


class StatBar(Widget):
    value = NumericProperty(0)
    max_value = NumericProperty(100)
    bar_color = ListProperty([0.13, 0.59, 0.95, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update, pos=self._update, value=self._update, max_value=self._update)
        self._update()
    
    def _update(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.2, 0.2, 0.25, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])
            
            Color(*self.bar_color)
            ratio = min(1, self.value / self.max_value) if self.max_value > 0 else 0
            bar_width = self.width * ratio
            if bar_width > 0:
                RoundedRectangle(pos=self.pos, size=(bar_width, self.height), radius=[dp(4)])


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        self.bg = GradientBackground()
        layout.add_widget(self.bg)
        
        content = BoxLayout(
            orientation='vertical',
            padding=[dp(30), dp(50)],
            spacing=dp(20),
            size_hint=(0.85, 0.75),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        icon_label = Label(text='', font_size=sp(80), size_hint_y=0.2)
        content.add_widget(icon_label)
        
        title_label = Label(
            text='Screen Guardian',
            font_size=sp(32),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=0.1
        )
        content.add_widget(title_label)
        
        subtitle_label = Label(
            text='Advanced Parental Control',
            font_size=sp(16),
            color=COLORS['text_secondary'],
            size_hint_y=0.06
        )
        content.add_widget(subtitle_label)
        
        content.add_widget(Widget(size_hint_y=0.05))
        
        pin_label = Label(
            text='Enter Parent PIN',
            font_size=sp(14),
            color=COLORS['text_secondary'],
            size_hint_y=0.05
        )
        content.add_widget(pin_label)
        
        self.pin_input = StyledTextInput(
            multiline=False,
            password=True,
            hint_text='PIN Code',
            input_filter='int',
            size_hint_y=0.1,
            halign='center'
        )
        content.add_widget(self.pin_input)
        
        login_btn = StyledButton(
            text='UNLOCK',
            btn_color=COLORS['primary'],
            size_hint_y=0.1,
            font_size=sp(18)
        )
        login_btn.bind(on_release=self.verify_pin)
        content.add_widget(login_btn)
        
        self.status_label = Label(
            text='',
            font_size=sp(14),
            color=COLORS['error'],
            size_hint_y=0.06
        )
        content.add_widget(self.status_label)
        
        forgot_btn = Button(
            text='Forgot PIN?',
            font_size=sp(12),
            background_color=(0, 0, 0, 0),
            color=COLORS['text_secondary'],
            size_hint_y=0.06
        )
        forgot_btn.bind(on_release=self.show_recovery)
        content.add_widget(forgot_btn)
        
        hint_label = Label(
            text='Default PIN: 1234',
            font_size=sp(11),
            color=(0.35, 0.35, 0.4, 1),
            size_hint_y=0.05
        )
        content.add_widget(hint_label)
        
        layout.add_widget(content)
        self.add_widget(layout)
    
    def verify_pin(self, instance):
        config = Config.load()
        if self.pin_input.text == config['parent_pin']:
            self.pin_input.text = ''
            self.status_label.text = ''
            self.manager.current = 'main'
        else:
            self.status_label.text = 'Incorrect PIN!'
            self.pin_input.text = ''
    
    def show_recovery(self, instance):
        config = Config.load()
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        content.add_widget(Label(
            text=config.get('recovery_question', 'What is your favorite color?'),
            font_size=sp(14),
            color=COLORS['text_primary'],
            size_hint_y=0.3
        ))
        
        answer_input = TextInput(
            multiline=False,
            hint_text='Your answer',
            size_hint_y=0.25
        )
        content.add_widget(answer_input)
        
        result_label = Label(text='', font_size=sp(12), color=COLORS['error'], size_hint_y=0.2)
        content.add_widget(result_label)
        
        def check_answer(btn):
            if answer_input.text.lower().strip() == config.get('recovery_answer', 'blue').lower().strip():
                result_label.color = COLORS['success']
                result_label.text = f"Your PIN is: {config['parent_pin']}"
            else:
                result_label.color = COLORS['error']
                result_label.text = 'Incorrect answer'
        
        check_btn = StyledButton(text='Verify', btn_color=COLORS['primary'], size_hint_y=0.25)
        check_btn.bind(on_release=check_answer)
        content.add_widget(check_btn)
        
        popup = Popup(
            title='PIN Recovery',
            content=content,
            size_hint=(0.9, 0.5)
        )
        popup.open()
    
    def update_theme(self):
        self.bg.update_colors([COLORS['background'], COLORS['surface']])


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        self.bg = GradientBackground()
        layout.add_widget(self.bg)
        
        content = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(25)],
            spacing=dp(15),
            size_hint=(0.95, 0.95),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        header = BoxLayout(size_hint_y=0.08)
        header.add_widget(Label(
            text='Screen Guardian',
            font_size=sp(22),
            bold=True,
            color=COLORS['text_primary'],
            halign='left'
        ))
        content.add_widget(header)
        
        tabs = BoxLayout(size_hint_y=0.08, spacing=dp(5))
        
        self.tab_buttons = []
        tab_names = ['Timer', 'Schedule', 'Profiles', 'Stats', 'Settings']
        for i, name in enumerate(tab_names):
            btn = StyledButton(
                text=name,
                btn_color=COLORS['primary'] if i == 0 else COLORS['surface_light'],
                font_size=sp(12)
            )
            btn.tab_index = i
            btn.bind(on_release=self.switch_tab)
            self.tab_buttons.append(btn)
            tabs.add_widget(btn)
        
        content.add_widget(tabs)
        
        self.tab_content = BoxLayout(size_hint_y=0.84)
        content.add_widget(self.tab_content)
        
        layout.add_widget(content)
        self.add_widget(layout)
        
        self.current_tab = 0
        self.build_timer_tab()
    
    def switch_tab(self, instance):
        for btn in self.tab_buttons:
            btn.set_color(COLORS['surface_light'])
        instance.set_color(COLORS['primary'])
        
        self.current_tab = instance.tab_index
        self.tab_content.clear_widgets()
        
        if instance.tab_index == 0:
            self.build_timer_tab()
        elif instance.tab_index == 1:
            self.build_schedule_tab()
        elif instance.tab_index == 2:
            self.build_profiles_tab()
        elif instance.tab_index == 3:
            self.build_stats_tab()
        elif instance.tab_index == 4:
            self.build_settings_tab()
    
    def build_timer_tab(self):
        self.config = Config.load()
        
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        timer_section = BoxLayout(orientation='vertical', size_hint_y=0.35)
        
        self.progress_widget = CircularProgress(
            size_hint=(None, None),
            size=(dp(140), dp(140)),
            pos_hint={'center_x': 0.5}
        )
        timer_section.add_widget(self.progress_widget)
        
        self.time_display = Label(
            text='00:00',
            font_size=sp(44),
            bold=True,
            color=COLORS['text_primary']
        )
        timer_section.add_widget(self.time_display)
        
        status_row = BoxLayout(size_hint_y=0.15)
        self.status_indicator = PulsingDot(
            size_hint=(None, None),
            size=(dp(10), dp(10)),
            color=COLORS['text_secondary']
        )
        status_row.add_widget(Widget())
        status_row.add_widget(self.status_indicator)
        self.status_label = Label(
            text='Ready',
            font_size=sp(14),
            color=COLORS['text_secondary']
        )
        status_row.add_widget(self.status_label)
        status_row.add_widget(Widget())
        timer_section.add_widget(status_row)
        
        content.add_widget(timer_section)
        
        presets_label = Label(
            text='Quick Presets',
            font_size=sp(12),
            color=COLORS['text_secondary'],
            size_hint_y=0.05,
            halign='left'
        )
        content.add_widget(presets_label)
        
        presets_row = BoxLayout(size_hint_y=0.08, spacing=dp(10))
        for preset in TIME_PRESETS:
            btn = StyledButton(
                text=preset['label'],
                btn_color=COLORS['surface_light'],
                font_size=sp(14)
            )
            btn.preset_minutes = preset['minutes']
            btn.bind(on_release=self.apply_preset)
            presets_row.add_widget(btn)
        content.add_widget(presets_row)
        
        slider_section = BoxLayout(orientation='vertical', size_hint_y=0.1, spacing=dp(3))
        self.limit_label = Label(
            text=f"Custom: {self.config['timer_minutes']} min",
            font_size=sp(12),
            color=COLORS['text_secondary'],
            halign='left'
        )
        slider_section.add_widget(self.limit_label)
        
        self.limit_slider = Slider(
            min=1, max=120,
            value=self.config['timer_minutes'],
            cursor_size=(dp(20), dp(20))
        )
        self.limit_slider.bind(value=self.on_limit_change)
        slider_section.add_widget(self.limit_slider)
        content.add_widget(slider_section)
        
        btn_row = BoxLayout(size_hint_y=0.1, spacing=dp(15))
        self.start_btn = StyledButton(text='START', btn_color=COLORS['success'], font_size=sp(16))
        self.start_btn.bind(on_release=self.start_timer)
        btn_row.add_widget(self.start_btn)
        
        self.stop_btn = StyledButton(text='STOP', btn_color=COLORS['error'], font_size=sp(16))
        self.stop_btn.bind(on_release=self.stop_timer)
        btn_row.add_widget(self.stop_btn)
        content.add_widget(btn_row)
        
        overlay_section = BoxLayout(orientation='vertical', size_hint_y=0.18, spacing=dp(3))
        overlay_section.add_widget(Label(
            text='Overlay Style',
            font_size=sp(12),
            color=COLORS['text_secondary'],
            halign='left',
            size_hint_y=0.25
        ))
        
        overlay_names = ['Random'] + [k.replace('_', ' ').title() for k in OVERLAY_THEMES.keys()]
        
        overlay_row1 = BoxLayout(spacing=dp(5), size_hint_y=0.35)
        overlay_row2 = BoxLayout(spacing=dp(5), size_hint_y=0.35)
        
        self.overlay_buttons = []
        for i, name in enumerate(overlay_names[:4]):
            btn = StyledButton(
                text=name,
                btn_color=COLORS['primary'] if i == 0 else COLORS['surface_light'],
                font_size=sp(10)
            )
            btn.overlay_name = name.lower().replace(' ', '_')
            btn.bind(on_release=self.select_overlay)
            self.overlay_buttons.append(btn)
            overlay_row1.add_widget(btn)
        
        for name in overlay_names[4:]:
            btn = StyledButton(
                text=name,
                btn_color=COLORS['surface_light'],
                font_size=sp(10)
            )
            btn.overlay_name = name.lower().replace(' ', '_')
            btn.bind(on_release=self.select_overlay)
            self.overlay_buttons.append(btn)
            overlay_row2.add_widget(btn)
        
        overlay_section.add_widget(overlay_row1)
        overlay_section.add_widget(overlay_row2)
        content.add_widget(overlay_section)
        
        perm_row = BoxLayout(size_hint_y=0.08, spacing=dp(10))
        self.perm_status = Label(
            text='Checking...',
            font_size=sp(11),
            color=COLORS['warning'],
            size_hint_x=0.5
        )
        perm_row.add_widget(self.perm_status)
        
        perm_btn = StyledButton(
            text='Grant Permission',
            btn_color=COLORS['surface_light'],
            font_size=sp(11),
            size_hint_x=0.5
        )
        perm_btn.bind(on_release=lambda x: AndroidHelper.request_overlay_permission())
        perm_row.add_widget(perm_btn)
        content.add_widget(perm_row)
        
        self.tab_content.add_widget(content)
        self.check_permission()
        self.check_existing_timer()
    
    def apply_preset(self, instance):
        self.limit_slider.value = instance.preset_minutes
        self.config['timer_minutes'] = instance.preset_minutes
        Config.save(self.config)
    
    def select_overlay(self, instance):
        for btn in self.overlay_buttons:
            btn.set_color(COLORS['surface_light'])
        instance.set_color(COLORS['primary'])
        self.config['selected_overlay'] = instance.overlay_name
        Config.save(self.config)
    
    def check_permission(self):
        if AndroidHelper.has_overlay_permission():
            self.perm_status.text = "Permission: Granted"
            self.perm_status.color = COLORS['success']
        else:
            self.perm_status.text = "Permission: Required"
            self.perm_status.color = COLORS['error']
    
    def check_existing_timer(self):
        if self.config.get('is_timer_active') and self.config.get('timer_end_timestamp'):
            end_time = datetime.fromisoformat(self.config['timer_end_timestamp'])
            if datetime.now() < end_time:
                self.timer_end_time = end_time
                self.resume_countdown()
            elif datetime.now() >= end_time:
                self.trigger_overlay()
        else:
            self.timer_end_time = None
    
    def on_limit_change(self, instance, value):
        self.limit_label.text = f"Custom: {int(value)} min"
        self.config['timer_minutes'] = int(value)
        Config.save(self.config)
    
    def start_timer(self, instance):
        if not AndroidHelper.has_overlay_permission():
            popup = Popup(
                title='Permission Required',
                content=Label(text='Please grant Overlay\npermission first!'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return
        
        minutes = int(self.limit_slider.value)
        self.timer_end_time = datetime.now() + timedelta(minutes=minutes)
        self.timer_start_time = datetime.now()
        self.total_timer_minutes = minutes
        
        self.config['timer_end_timestamp'] = self.timer_end_time.isoformat()
        self.config['is_timer_active'] = True
        self.config['timer_minutes'] = minutes
        Config.save(self.config)
        
        AndroidHelper.start_timer_service()
        
        self.status_label.text = "Timer Active"
        self.status_label.color = COLORS['success']
        self.status_indicator.color = COLORS['success']
        
        self.warning_shown = False
        self.last_break_reminder = datetime.now()
        
        self.resume_countdown()
        
        if self.config.get('sound_enabled', True):
            SoundManager.play_tick()
        
        popup = Popup(
            title='Timer Started',
            content=Label(text=f'Limit: {minutes} min\n\nOverlay appears when done.', halign='center'),
            size_hint=(0.75, 0.35)
        )
        popup.open()
    
    def resume_countdown(self):
        if hasattr(self, 'countdown_event') and self.countdown_event:
            self.countdown_event.cancel()
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 0.5)
        self.status_label.text = "Timer Active"
        self.status_label.color = COLORS['success']
        self.status_indicator.color = COLORS['success']
    
    def update_countdown(self, dt):
        if not hasattr(self, 'timer_end_time') or not self.timer_end_time:
            return
        
        remaining = self.timer_end_time - datetime.now()
        total_minutes = self.config.get('timer_minutes', 5)
        
        if remaining.total_seconds() <= 0:
            self.time_display.text = "00:00"
            self.progress_widget.progress = 1
            self.trigger_overlay()
            return
        
        total_seconds = int(remaining.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.time_display.text = f"{minutes:02d}:{seconds:02d}"
        
        elapsed = (total_minutes * 60) - total_seconds
        progress = elapsed / (total_minutes * 60) if total_minutes > 0 else 0
        self.progress_widget.progress = min(1, max(0, progress))
        
        warning_time = self.config.get('warning_before_end', 5)
        if total_seconds <= warning_time * 60 and not getattr(self, 'warning_shown', False):
            self.warning_shown = True
            self.show_warning()
        
        if total_seconds <= 60:
            self.progress_widget.color = list(COLORS['error'])
        elif total_seconds <= warning_time * 60:
            self.progress_widget.color = list(COLORS['warning'])
        
        if self.config.get('break_reminder_enabled', True):
            break_interval = self.config.get('break_reminder_interval', 30) * 60
            if hasattr(self, 'last_break_reminder'):
                elapsed_since_break = (datetime.now() - self.last_break_reminder).total_seconds()
                if elapsed_since_break >= break_interval:
                    self.show_break_reminder()
                    self.last_break_reminder = datetime.now()
    
    def show_warning(self):
        warning_time = self.config.get('warning_before_end', 5)
        if self.config.get('sound_enabled', True):
            SoundManager.play_warning()
        
        popup = Popup(
            title='Time Warning',
            content=Label(text=f'Only {warning_time} minutes remaining!\n\nSave your work.', halign='center'),
            size_hint=(0.75, 0.35),
            auto_dismiss=True
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 5)
    
    def show_break_reminder(self):
        popup = Popup(
            title='Break Time',
            content=Label(text='Remember to take a break!\n\nStretch and rest your eyes.', halign='center'),
            size_hint=(0.75, 0.35),
            auto_dismiss=True
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 5)
    
    def trigger_overlay(self):
        if hasattr(self, 'countdown_event') and self.countdown_event:
            self.countdown_event.cancel()
            self.countdown_event = None
        
        elapsed_minutes = self.config.get('timer_minutes', 5)
        Config.record_usage(elapsed_minutes)
        
        self.status_label.text = "Time's Up!"
        self.status_label.color = COLORS['error']
        self.status_indicator.color = COLORS['error']
        self.time_display.text = "00:00"
        
        if self.config.get('sound_enabled', True):
            SoundManager.play_alert()
        
        success = AndroidHelper.show_overlay_window()
        
        if success:
            self.config['is_timer_active'] = False
            self.config['timer_end_timestamp'] = None
            Config.save(self.config)
            
            selected = self.config.get('selected_overlay', 'random')
            if selected == 'random':
                selected = random.choice(list(OVERLAY_THEMES.keys()))
            
            self.manager.get_screen('blocked').set_theme(selected)
            self.manager.get_screen('blocked').set_custom_message(
                self.config.get('custom_overlay_message', '')
            )
            self.manager.current = 'blocked'
    
    def stop_timer(self, instance):
        if hasattr(self, 'countdown_event') and self.countdown_event:
            self.countdown_event.cancel()
            self.countdown_event = None
        
        if hasattr(self, 'timer_start_time') and self.timer_start_time:
            elapsed = (datetime.now() - self.timer_start_time).total_seconds() / 60
            Config.record_usage(int(elapsed))
        
        self.timer_end_time = None
        self.config['is_timer_active'] = False
        self.config['timer_end_timestamp'] = None
        Config.save(self.config)
        
        AndroidHelper.stop_timer_service()
        AndroidHelper.hide_overlay_window()
        
        self.status_label.text = "Stopped"
        self.status_label.color = COLORS['text_secondary']
        self.status_indicator.color = COLORS['text_secondary']
        self.time_display.text = "00:00"
        self.progress_widget.progress = 0
        self.progress_widget.color = list(COLORS['primary'])
    
    def build_schedule_tab(self):
        self.config = Config.load()
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        title = Label(
            text='Weekly Schedule',
            font_size=sp(18),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        subtitle = Label(
            text='Set daily time limits for each day',
            font_size=sp(12),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(25)
        )
        content.add_widget(subtitle)
        
        profile = self.config['profiles'].get(self.config['active_profile'], {})
        schedule = profile.get('schedule', {})
        
        self.day_sliders = {}
        
        for day in DAYS_OF_WEEK:
            day_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70), spacing=dp(3))
            
            day_limit = schedule.get(day, 120)
            
            header = BoxLayout(size_hint_y=0.4)
            header.add_widget(Label(
                text=day,
                font_size=sp(14),
                color=COLORS['text_primary'],
                halign='left',
                size_hint_x=0.5
            ))
            limit_label = Label(
                text=f'{day_limit} min',
                font_size=sp(14),
                color=COLORS['primary'],
                halign='right',
                size_hint_x=0.5
            )
            header.add_widget(limit_label)
            day_box.add_widget(header)
            
            slider = Slider(min=0, max=240, value=day_limit, size_hint_y=0.6)
            slider.day = day
            slider.limit_label = limit_label
            slider.bind(value=self.on_schedule_change)
            self.day_sliders[day] = slider
            day_box.add_widget(slider)
            
            content.add_widget(day_box)
        
        save_btn = StyledButton(
            text='Save Schedule',
            btn_color=COLORS['success'],
            size_hint_y=None,
            height=dp(50),
            font_size=sp(16)
        )
        save_btn.bind(on_release=self.save_schedule)
        content.add_widget(save_btn)
        
        content.add_widget(Widget(size_hint_y=None, height=dp(20)))
        
        scroll.add_widget(content)
        self.tab_content.add_widget(scroll)
    
    def on_schedule_change(self, instance, value):
        instance.limit_label.text = f'{int(value)} min'
    
    def save_schedule(self, instance):
        profile_name = self.config['active_profile']
        schedule = {}
        for day, slider in self.day_sliders.items():
            schedule[day] = int(slider.value)
        
        self.config['profiles'][profile_name]['schedule'] = schedule
        Config.save(self.config)
        
        popup = Popup(
            title='Saved',
            content=Label(text='Schedule saved successfully!'),
            size_hint=(0.7, 0.25)
        )
        popup.open()
    
    def build_profiles_tab(self):
        self.config = Config.load()
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        title = Label(
            text='Child Profiles',
            font_size=sp(18),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        for profile_id, profile_data in self.config['profiles'].items():
            profile_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(100),
                padding=dp(10),
                spacing=dp(5)
            )
            
            with profile_box.canvas.before:
                Color(*COLORS['surface'])
                profile_box._rect = RoundedRectangle(pos=profile_box.pos, size=profile_box.size, radius=[dp(10)])
            profile_box.bind(pos=lambda w, p: setattr(w._rect, 'pos', p))
            profile_box.bind(size=lambda w, s: setattr(w._rect, 'size', s))
            
            header = BoxLayout(size_hint_y=0.4)
            header.add_widget(Label(
                text=f"  {profile_data.get('name', 'Child')}",
                font_size=sp(16),
                bold=True,
                color=COLORS['text_primary'],
                halign='left'
            ))
            
            if profile_id == self.config['active_profile']:
                active_label = Label(
                    text='ACTIVE',
                    font_size=sp(10),
                    color=COLORS['success'],
                    size_hint_x=0.3
                )
                header.add_widget(active_label)
            
            profile_box.add_widget(header)
            
            info = Label(
                text=f"Daily limit: {profile_data.get('daily_limit', 120)} min",
                font_size=sp(12),
                color=COLORS['text_secondary'],
                halign='left',
                size_hint_y=0.3
            )
            profile_box.add_widget(info)
            
            btn_row = BoxLayout(size_hint_y=0.3, spacing=dp(10))
            
            select_btn = StyledButton(
                text='Select',
                btn_color=COLORS['primary'],
                font_size=sp(11)
            )
            select_btn.profile_id = profile_id
            select_btn.bind(on_release=self.select_profile)
            btn_row.add_widget(select_btn)
            
            edit_btn = StyledButton(
                text='Edit',
                btn_color=COLORS['surface_light'],
                font_size=sp(11)
            )
            edit_btn.profile_id = profile_id
            edit_btn.bind(on_release=self.edit_profile)
            btn_row.add_widget(edit_btn)
            
            profile_box.add_widget(btn_row)
            content.add_widget(profile_box)
        
        add_btn = StyledButton(
            text='+ Add New Profile',
            btn_color=COLORS['secondary'],
            size_hint_y=None,
            height=dp(50),
            font_size=sp(16)
        )
        add_btn.bind(on_release=self.add_profile)
        content.add_widget(add_btn)
        
        content.add_widget(Widget(size_hint_y=None, height=dp(20)))
        
        scroll.add_widget(content)
        self.tab_content.add_widget(scroll)
    
    def select_profile(self, instance):
        self.config['active_profile'] = instance.profile_id
        Config.save(self.config)
        self.switch_tab(self.tab_buttons[2])
    
    def edit_profile(self, instance):
        profile_id = instance.profile_id
        profile = self.config['profiles'].get(profile_id, {})
        
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        content.add_widget(Label(text='Profile Name:', font_size=sp(12), size_hint_y=0.1))
        name_input = TextInput(text=profile.get('name', 'Child'), multiline=False, size_hint_y=0.15)
        content.add_widget(name_input)
        
        content.add_widget(Label(text='Daily Limit (minutes):', font_size=sp(12), size_hint_y=0.1))
        limit_input = TextInput(
            text=str(profile.get('daily_limit', 120)),
            multiline=False,
            input_filter='int',
            size_hint_y=0.15
        )
        content.add_widget(limit_input)
        
        def save_profile(btn):
            self.config['profiles'][profile_id]['name'] = name_input.text
            self.config['profiles'][profile_id]['daily_limit'] = int(limit_input.text or 120)
            Config.save(self.config)
            popup.dismiss()
            self.switch_tab(self.tab_buttons[2])
        
        save_btn = StyledButton(text='Save', btn_color=COLORS['success'], size_hint_y=0.15)
        save_btn.bind(on_release=save_profile)
        content.add_widget(save_btn)
        
        content.add_widget(Widget(size_hint_y=0.35))
        
        popup = Popup(title='Edit Profile', content=content, size_hint=(0.85, 0.55))
        popup.open()
    
    def add_profile(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        content.add_widget(Label(text='Profile Name:', font_size=sp(12), size_hint_y=0.1))
        name_input = TextInput(hint_text='Child name', multiline=False, size_hint_y=0.15)
        content.add_widget(name_input)
        
        content.add_widget(Label(text='Daily Limit (minutes):', font_size=sp(12), size_hint_y=0.1))
        limit_input = TextInput(text='120', multiline=False, input_filter='int', size_hint_y=0.15)
        content.add_widget(limit_input)
        
        def create_profile(btn):
            profile_id = f"profile_{len(self.config['profiles'])}"
            self.config['profiles'][profile_id] = {
                'name': name_input.text or 'Child',
                'daily_limit': int(limit_input.text or 120),
                'schedule': {}
            }
            Config.save(self.config)
            popup.dismiss()
            self.switch_tab(self.tab_buttons[2])
        
        create_btn = StyledButton(text='Create', btn_color=COLORS['success'], size_hint_y=0.15)
        create_btn.bind(on_release=create_profile)
        content.add_widget(create_btn)
        
        content.add_widget(Widget(size_hint_y=0.35))
        
        popup = Popup(title='New Profile', content=content, size_hint=(0.85, 0.55))
        popup.open()
    
    def build_stats_tab(self):
        stats = Config.load_stats()
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        title = Label(
            text='Usage Statistics',
            font_size=sp(18),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_usage = stats.get('daily', {}).get(today, 0)
        
        today_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        today_box.add_widget(Label(
            text='Today',
            font_size=sp(14),
            color=COLORS['text_secondary'],
            size_hint_y=0.3
        ))
        today_box.add_widget(Label(
            text=f'{today_usage} minutes',
            font_size=sp(28),
            bold=True,
            color=COLORS['primary'],
            size_hint_y=0.5
        ))
        today_bar = StatBar(
            value=today_usage,
            max_value=120,
            bar_color=COLORS['primary'],
            size_hint_y=None,
            height=dp(12)
        )
        today_box.add_widget(today_bar)
        content.add_widget(today_box)
        
        week_label = Label(
            text='Last 7 Days',
            font_size=sp(14),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(week_label)
        
        week_total = 0
        for i in range(7):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_name = (datetime.now() - timedelta(days=i)).strftime("%a")
            usage = stats.get('daily', {}).get(day, 0)
            week_total += usage
            
            day_row = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(10))
            day_row.add_widget(Label(
                text=day_name,
                font_size=sp(12),
                color=COLORS['text_secondary'],
                size_hint_x=0.2
            ))
            day_bar = StatBar(
                value=usage,
                max_value=180,
                bar_color=COLORS['secondary'] if i == 0 else COLORS['surface_light'],
                size_hint_x=0.6
            )
            day_row.add_widget(day_bar)
            day_row.add_widget(Label(
                text=f'{usage}m',
                font_size=sp(12),
                color=COLORS['text_primary'],
                size_hint_x=0.2
            ))
            content.add_widget(day_row)
        
        avg_daily = week_total // 7 if week_total > 0 else 0
        summary = Label(
            text=f'Weekly Total: {week_total} min  |  Daily Average: {avg_daily} min',
            font_size=sp(12),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(35)
        )
        content.add_widget(summary)
        
        content.add_widget(Widget(size_hint_y=None, height=dp(20)))
        
        scroll.add_widget(content)
        self.tab_content.add_widget(scroll)
    
    def build_settings_tab(self):
        self.config = Config.load()
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        title = Label(
            text='Settings',
            font_size=sp(18),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        def setting_row(label_text, widget):
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            row.add_widget(Label(
                text=label_text,
                font_size=sp(14),
                color=COLORS['text_primary'],
                halign='left',
                size_hint_x=0.6
            ))
            row.add_widget(widget)
            return row
        
        self.sound_switch = Switch(active=self.config.get('sound_enabled', True))
        self.sound_switch.bind(active=self.on_sound_toggle)
        content.add_widget(setting_row('Sound Effects', self.sound_switch))
        
        self.dark_switch = Switch(active=self.config.get('dark_mode', True))
        self.dark_switch.bind(active=self.on_theme_toggle)
        content.add_widget(setting_row('Dark Mode', self.dark_switch))
        
        self.break_switch = Switch(active=self.config.get('break_reminder_enabled', True))
        self.break_switch.bind(active=self.on_break_toggle)
        content.add_widget(setting_row('Break Reminders', self.break_switch))
        
        self.extension_switch = Switch(active=self.config.get('extension_requests_enabled', True))
        self.extension_switch.bind(active=self.on_extension_toggle)
        content.add_widget(setting_row('Allow Extension Requests', self.extension_switch))
        
        warning_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70))
        warning_section.add_widget(Label(
            text=f"Warning before end: {self.config.get('warning_before_end', 5)} min",
            font_size=sp(12),
            color=COLORS['text_secondary'],
            halign='left',
            size_hint_y=0.4
        ))
        self.warning_slider = Slider(min=1, max=15, value=self.config.get('warning_before_end', 5))
        self.warning_slider.bind(value=self.on_warning_change)
        warning_section.add_widget(self.warning_slider)
        content.add_widget(warning_section)
        
        divider = Widget(size_hint_y=None, height=dp(15))
        content.add_widget(divider)
        
        pin_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(90), spacing=dp(5))
        pin_section.add_widget(Label(
            text='Change PIN',
            font_size=sp(14),
            color=COLORS['text_primary'],
            halign='left',
            size_hint_y=0.25
        ))
        
        pin_row = BoxLayout(size_hint_y=0.4, spacing=dp(10))
        self.new_pin_input = StyledTextInput(
            multiline=False,
            password=True,
            hint_text='New PIN',
            input_filter='int',
            size_hint_x=0.6
        )
        pin_row.add_widget(self.new_pin_input)
        
        pin_btn = StyledButton(text='Update', btn_color=COLORS['primary'], font_size=sp(12), size_hint_x=0.4)
        pin_btn.bind(on_release=self.change_pin)
        pin_row.add_widget(pin_btn)
        pin_section.add_widget(pin_row)
        content.add_widget(pin_section)
        
        recovery_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(5))
        recovery_section.add_widget(Label(
            text='PIN Recovery Question',
            font_size=sp(14),
            color=COLORS['text_primary'],
            halign='left',
            size_hint_y=0.2
        ))
        
        self.question_input = StyledTextInput(
            text=self.config.get('recovery_question', 'What is your favorite color?'),
            multiline=False,
            hint_text='Recovery question',
            size_hint_y=0.35
        )
        recovery_section.add_widget(self.question_input)
        
        self.answer_input = StyledTextInput(
            text=self.config.get('recovery_answer', 'blue'),
            multiline=False,
            hint_text='Answer',
            size_hint_y=0.35
        )
        recovery_section.add_widget(self.answer_input)
        content.add_widget(recovery_section)
        
        save_recovery_btn = StyledButton(
            text='Save Recovery Settings',
            btn_color=COLORS['secondary'],
            size_hint_y=None,
            height=dp(45),
            font_size=sp(14)
        )
        save_recovery_btn.bind(on_release=self.save_recovery)
        content.add_widget(save_recovery_btn)
        
        overlay_msg_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(90), spacing=dp(5))
        overlay_msg_section.add_widget(Label(
            text='Custom Overlay Message',
            font_size=sp(14),
            color=COLORS['text_primary'],
            halign='left',
            size_hint_y=0.25
        ))
        self.custom_msg_input = StyledTextInput(
            text=self.config.get('custom_overlay_message', ''),
            hint_text='Optional custom message...',
            multiline=False,
            size_hint_y=0.4
        )
        overlay_msg_section.add_widget(self.custom_msg_input)
        
        save_msg_btn = StyledButton(text='Save Message', btn_color=COLORS['surface_light'], font_size=sp(12), size_hint_y=0.35)
        save_msg_btn.bind(on_release=self.save_custom_message)
        overlay_msg_section.add_widget(save_msg_btn)
        content.add_widget(overlay_msg_section)
        
        content.add_widget(Widget(size_hint_y=None, height=dp(30)))
        
        scroll.add_widget(content)
        self.tab_content.add_widget(scroll)
    
    def on_sound_toggle(self, instance, value):
        self.config['sound_enabled'] = value
        Config.save(self.config)
    
    def on_theme_toggle(self, instance, value):
        global COLORS
        self.config['dark_mode'] = value
        Config.save(self.config)
        COLORS = COLORS_DARK if value else COLORS_LIGHT
        Window.clearcolor = COLORS['background']
        self.bg.update_colors([COLORS['background'], COLORS['surface']])
    
    def on_break_toggle(self, instance, value):
        self.config['break_reminder_enabled'] = value
        Config.save(self.config)
    
    def on_extension_toggle(self, instance, value):
        self.config['extension_requests_enabled'] = value
        Config.save(self.config)
    
    def on_warning_change(self, instance, value):
        self.config['warning_before_end'] = int(value)
        Config.save(self.config)
    
    def change_pin(self, instance):
        new_pin = self.new_pin_input.text
        if len(new_pin) >= 4:
            self.config['parent_pin'] = new_pin
            Config.save(self.config)
            self.new_pin_input.text = ''
            popup = Popup(title='Success', content=Label(text='PIN updated!'), size_hint=(0.6, 0.2))
            popup.open()
        else:
            popup = Popup(title='Error', content=Label(text='PIN must be at least 4 digits'), size_hint=(0.7, 0.2))
            popup.open()
    
    def save_recovery(self, instance):
        self.config['recovery_question'] = self.question_input.text
        self.config['recovery_answer'] = self.answer_input.text
        Config.save(self.config)
        popup = Popup(title='Saved', content=Label(text='Recovery settings saved!'), size_hint=(0.6, 0.2))
        popup.open()
    
    def save_custom_message(self, instance):
        self.config['custom_overlay_message'] = self.custom_msg_input.text
        Config.save(self.config)
        popup = Popup(title='Saved', content=Label(text='Custom message saved!'), size_hint=(0.6, 0.2))
        popup.open()
    
    def on_enter(self):
        self.config = Config.load()
        if self.current_tab == 0:
            self.check_permission()
            self.check_existing_timer()
    
    def update_theme(self):
        self.bg.update_colors([COLORS['background'], COLORS['surface']])


class BlockedScreen(Screen):
    current_theme = StringProperty('battery_drained')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_data = OVERLAY_THEMES['battery_drained']
        self.custom_message = ''
        self.build_ui()
    
    def set_theme(self, theme_name):
        if theme_name in OVERLAY_THEMES:
            self.current_theme = theme_name
            self.theme_data = OVERLAY_THEMES[theme_name]
            self.update_ui()
    
    def set_custom_message(self, message):
        self.custom_message = message
    
    def build_ui(self):
        self.layout = FloatLayout()
        
        self.bg_widget = Widget()
        self.layout.add_widget(self.bg_widget)
        
        self.content = BoxLayout(
            orientation='vertical',
            padding=[dp(40), dp(50)],
            spacing=dp(12),
            size_hint=(1, 1)
        )
        
        self.content.add_widget(Widget(size_hint_y=0.08))
        
        self.icon_label = Label(
            text=self.theme_data['icon'],
            font_size=sp(90),
            size_hint_y=0.18
        )
        self.content.add_widget(self.icon_label)
        
        self.title_label = Label(
            text=self.theme_data['title'],
            font_size=sp(32),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=0.08,
            halign='center'
        )
        self.content.add_widget(self.title_label)
        
        self.subtitle_label = Label(
            text=self.theme_data['subtitle'],
            font_size=sp(16),
            color=COLORS['text_secondary'],
            size_hint_y=0.05
        )
        self.content.add_widget(self.subtitle_label)
        
        self.progress_bar = AnimatedProgressBar(
            progress=0.75,
            color=self.theme_data['accent_color'],
            size_hint=(0.7, None),
            height=dp(8),
            pos_hint={'center_x': 0.5}
        )
        self.content.add_widget(self.progress_bar)
        
        self.percent_label = Label(
            text=self.theme_data['percent'],
            font_size=sp(42),
            bold=True,
            size_hint_y=0.1
        )
        self.content.add_widget(self.percent_label)
        
        self.detail_label = Label(
            text=self.theme_data['detail'],
            font_size=sp(13),
            color=COLORS['text_secondary'],
            size_hint_y=0.06,
            halign='center',
            text_size=(Window.width - dp(80), None)
        )
        self.content.add_widget(self.detail_label)
        
        self.custom_msg_label = Label(
            text='',
            font_size=sp(12),
            color=(0.5, 0.5, 0.55, 1),
            size_hint_y=0.04
        )
        self.content.add_widget(self.custom_msg_label)
        
        self.content.add_widget(Widget(size_hint_y=0.06))
        
        extension_btn = Button(
            text='Request More Time',
            font_size=sp(12),
            background_color=(0.2, 0.2, 0.25, 1),
            size_hint=(0.6, 0.05),
            pos_hint={'center_x': 0.5}
        )
        extension_btn.bind(on_release=self.request_extension)
        self.content.add_widget(extension_btn)
        
        self.content.add_widget(Widget(size_hint_y=0.03))
        
        unlock_hint = Label(
            text='Parent: Enter PIN',
            font_size=sp(11),
            color=(0.3, 0.3, 0.35, 1),
            size_hint_y=0.03
        )
        self.content.add_widget(unlock_hint)
        
        pin_box = BoxLayout(
            size_hint=(0.75, 0.07),
            pos_hint={'center_x': 0.5},
            spacing=dp(10)
        )
        
        self.pin_input = TextInput(
            multiline=False,
            password=True,
            hint_text='PIN',
            input_filter='int',
            font_size=sp(18),
            halign='center',
            background_color=(0.12, 0.12, 0.15, 1),
            foreground_color=COLORS['text_primary'],
            cursor_color=COLORS['primary'],
            size_hint_x=0.6
        )
        pin_box.add_widget(self.pin_input)
        
        unlock_btn = Button(
            text='Unlock',
            font_size=sp(13),
            background_color=(0.2, 0.2, 0.25, 1),
            size_hint_x=0.4
        )
        unlock_btn.bind(on_release=self.try_unlock)
        pin_box.add_widget(unlock_btn)
        
        self.content.add_widget(pin_box)
        
        self.status_label = Label(
            text='',
            font_size=sp(11),
            color=COLORS['error'],
            size_hint_y=0.03
        )
        self.content.add_widget(self.status_label)
        
        self.content.add_widget(Widget(size_hint_y=0.03))
        
        self.layout.add_widget(self.content)
        self.add_widget(self.layout)
    
    def update_ui(self):
        self.icon_label.text = self.theme_data['icon']
        self.title_label.text = self.theme_data['title']
        self.subtitle_label.text = self.theme_data['subtitle']
        self.percent_label.text = self.theme_data['percent']
        self.percent_label.color = self.theme_data['accent_color']
        self.detail_label.text = self.theme_data['detail']
        self.progress_bar.color = list(self.theme_data['accent_color'])
        
        if self.custom_message:
            self.custom_msg_label.text = self.custom_message
        
        self.bg_widget.canvas.clear()
        with self.bg_widget.canvas:
            Color(*self.theme_data['bg_color'])
            Rectangle(pos=(0, 0), size=Window.size)
    
    def request_extension(self, instance):
        config = Config.load()
        if not config.get('extension_requests_enabled', True):
            self.status_label.text = 'Extension requests disabled'
            return
        
        config['pending_extension_request'] = {
            'time': datetime.now().isoformat(),
            'minutes': config.get('max_extension_minutes', 10)
        }
        Config.save(config)
        
        self.status_label.color = COLORS['warning']
        self.status_label.text = 'Extension request sent to parent'
    
    def on_enter(self):
        self.update_ui()
        AndroidHelper.start_lock_task()
        AndroidHelper.keep_screen_on(True)
    
    def on_leave(self):
        AndroidHelper.stop_lock_task()
        AndroidHelper.keep_screen_on(False)
    
    def try_unlock(self, instance):
        config = Config.load()
        if self.pin_input.text == config['parent_pin']:
            if config.get('pending_extension_request'):
                self.show_extension_popup(config)
            else:
                self.dismiss_overlay()
        else:
            self.status_label.color = COLORS['error']
            self.status_label.text = 'Incorrect PIN'
            self.pin_input.text = ''
    
    def show_extension_popup(self, config):
        ext_req = config['pending_extension_request']
        minutes = ext_req.get('minutes', 10)
        
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        content.add_widget(Label(
            text=f'Child requested {minutes} more minutes.\n\nGrant extension?',
            font_size=sp(14),
            halign='center',
            size_hint_y=0.4
        ))
        
        btn_row = BoxLayout(size_hint_y=0.3, spacing=dp(15))
        
        def grant_extension(btn):
            self.grant_extension(minutes)
            popup.dismiss()
        
        def deny_extension(btn):
            config['pending_extension_request'] = None
            Config.save(config)
            popup.dismiss()
            self.dismiss_overlay()
        
        grant_btn = StyledButton(text=f'Grant {minutes}m', btn_color=COLORS['success'])
        grant_btn.bind(on_release=grant_extension)
        btn_row.add_widget(grant_btn)
        
        deny_btn = StyledButton(text='Deny', btn_color=COLORS['error'])
        deny_btn.bind(on_release=deny_extension)
        btn_row.add_widget(deny_btn)
        
        content.add_widget(btn_row)
        content.add_widget(Widget(size_hint_y=0.3))
        
        popup = Popup(title='Extension Request', content=content, size_hint=(0.85, 0.4))
        popup.open()
    
    def grant_extension(self, minutes):
        config = Config.load()
        config['pending_extension_request'] = None
        config['is_timer_active'] = True
        config['timer_minutes'] = minutes
        config['timer_end_timestamp'] = (datetime.now() + timedelta(minutes=minutes)).isoformat()
        Config.save(config)
        
        AndroidHelper.hide_overlay_window()
        AndroidHelper.stop_lock_task()
        self.pin_input.text = ''
        self.status_label.text = ''
        self.manager.current = 'main'
    
    def dismiss_overlay(self):
        AndroidHelper.hide_overlay_window()
        AndroidHelper.stop_lock_task()
        self.pin_input.text = ''
        self.status_label.text = ''
        self.manager.current = 'main'


class ScreenGuardianApp(App):
    def build(self):
        global COLORS
        config = Config.load()
        COLORS = COLORS_DARK if config.get('dark_mode', True) else COLORS_LIGHT
        
        Window.clearcolor = COLORS['background']
        Window.bind(on_keyboard=self.on_keyboard)
        AndroidHelper.request_all_permissions()
        SoundManager.init()
        
        self.sm = ScreenManager(transition=FadeTransition(duration=0.25))
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(BlockedScreen(name='blocked'))
        
        return self.sm
    
    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            if self.sm.current == 'blocked':
                print("Back button blocked!")
                return True
        return False
    
    def on_start(self):
        should_block = False
        
        if ANDROID_AVAILABLE:
            try:
                intent = mActivity.getIntent()
                if intent and intent.getBooleanExtra("show_block_screen", False):
                    should_block = True
            except Exception as e:
                print(f"Error checking intent: {e}")
        
        config = Config.load()
        if config.get('is_timer_active') and config.get('timer_end_timestamp'):
            try:
                end_time = datetime.fromisoformat(config['timer_end_timestamp'])
                if datetime.now() >= end_time:
                    should_block = True
                    config['is_timer_active'] = False
                    config['timer_end_timestamp'] = None
                    Config.save(config)
            except Exception as e:
                print(f"Error checking timer: {e}")
        
        if should_block:
            selected = config.get('selected_overlay', 'random')
            if selected == 'random':
                selected = random.choice(list(OVERLAY_THEMES.keys()))
            Clock.schedule_once(lambda dt: self.show_block_screen(selected), 0.5)
    
    def show_block_screen(self, theme='battery_drained'):
        self.sm.get_screen('blocked').set_theme(theme)
        self.sm.current = 'blocked'
        Window.clearcolor = OVERLAY_THEMES.get(theme, OVERLAY_THEMES['battery_drained'])['bg_color']


if __name__ == '__main__':
    ScreenGuardianApp().run()
