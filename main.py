"""
YouTube Parental Control App
Professional timer-based approach with multiple attractive overlay screens.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.animation import Animation
from kivy.metrics import dp, sp
import json
import os
import random
from datetime import datetime, timedelta

try:
    from android.permissions import request_permissions, Permission
    from android import mActivity
    from jnius import autoclass, cast
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False
    print("Running on desktop - Android features disabled")


COLORS = {
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


class Config:
    CONFIG_FILE = "parental_config.json"
    
    DEFAULT_CONFIG = {
        "parent_pin": "1234",
        "timer_minutes": 5,
        "timer_end_timestamp": None,
        "is_timer_active": False,
        "selected_overlay": "random",
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


class AndroidHelper:
    overlay_view = None
    window_manager = None
    service_running = False
    
    @staticmethod
    def request_all_permissions():
        if not ANDROID_AVAILABLE:
            return
        
        permissions = [
            Permission.INTERNET,
            Permission.ACCESS_NETWORK_STATE,
        ]
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
            service.start(mActivity, '')
            
            AndroidHelper.service_running = True
            print("Timer service started successfully!")
            return True
        except Exception as e:
            print(f"Error starting timer service: {e}")
            import traceback
            traceback.print_exc()
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
                    title.setText("Battery Drained")
                    title.setTextColor(Color.WHITE)
                    title.setTextSize(TypedValue.COMPLEX_UNIT_SP, 48)
                    title.setGravity(Gravity.CENTER)
                    layout.addView(title)
                    
                    subtitle = TextView(context)
                    subtitle.setText("\n\nPlease charge your device\n\n")
                    subtitle.setTextColor(Color.WHITE)
                    subtitle.setTextSize(TypedValue.COMPLEX_UNIT_SP, 24)
                    subtitle.setGravity(Gravity.CENTER)
                    layout.addView(subtitle)
                    
                    percent = TextView(context)
                    percent.setText("0%")
                    percent.setTextColor(Color.WHITE)
                    percent.setTextSize(TypedValue.COMPLEX_UNIT_SP, 36)
                    percent.setGravity(Gravity.CENTER)
                    layout.addView(percent)
                    
                    wm.addView(layout, params)
                    
                    AndroidHelper.overlay_view = layout
                    AndroidHelper.window_manager = wm
                    
                    print("Overlay shown successfully on Android!")
                except Exception as e:
                    print(f"Error creating overlay: {e}")
                    import traceback
                    traceback.print_exc()
            
            create_overlay_ui()
            return True
        except ImportError:
            print("android.runnable not available, trying direct method")
            try:
                WindowManager = autoclass('android.view.WindowManager')
                LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
                TextView = autoclass('android.widget.TextView')
                Color = autoclass('android.graphics.Color')
                Gravity = autoclass('android.view.Gravity')
                Build = autoclass('android.os.Build')
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
                    LayoutParams.FLAG_NOT_FOCUSABLE | LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                    -3
                )
                
                tv = TextView(context)
                tv.setText("\n\n\nBattery Drained\n\nPlease charge your device\n\n0%")
                tv.setTextColor(Color.WHITE)
                tv.setBackgroundColor(Color.BLACK)
                tv.setGravity(Gravity.CENTER)
                tv.setTextSize(32)
                
                wm.addView(tv, params)
                
                AndroidHelper.overlay_view = tv
                AndroidHelper.window_manager = wm
                
                print("Overlay shown (direct method)!")
                return True
            except Exception as e:
                print(f"Error showing overlay (direct): {e}")
                import traceback
                traceback.print_exc()
                return False
        except Exception as e:
            print(f"Error showing overlay: {e}")
            import traceback
            traceback.print_exc()
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
                            print("Overlay hidden successfully")
                        except Exception as e:
                            print(f"Error removing overlay: {e}")
                    
                    remove_ui()
                except ImportError:
                    AndroidHelper.window_manager.removeView(AndroidHelper.overlay_view)
                    AndroidHelper.overlay_view = None
                    AndroidHelper.window_manager = None
                    print("Overlay hidden (direct)")
                return True
        except Exception as e:
            print(f"Error hiding overlay: {e}")
        return False
    
    @staticmethod
    def start_lock_task():
        if not ANDROID_AVAILABLE:
            print("Would start lock task mode on Android")
            return True
        
        try:
            from jnius import autoclass
            
            activity = mActivity
            activity.startLockTask()
            print("Lock task mode started - home/back buttons disabled!")
            return True
        except Exception as e:
            print(f"Error starting lock task: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def stop_lock_task():
        if not ANDROID_AVAILABLE:
            print("Would stop lock task mode on Android")
            return True
        
        try:
            activity = mActivity
            activity.stopLockTask()
            print("Lock task mode stopped!")
            return True
        except Exception as e:
            print(f"Error stopping lock task: {e}")
            return False
    
    @staticmethod
    def keep_screen_on(enable):
        if not ANDROID_AVAILABLE:
            print(f"Would set keep screen on: {enable}")
            return True
        
        try:
            from jnius import autoclass
            
            activity = mActivity
            window = activity.getWindow()
            WindowManager = autoclass('android.view.WindowManager')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            
            if enable:
                window.addFlags(LayoutParams.FLAG_KEEP_SCREEN_ON)
                print("Screen will stay on")
            else:
                window.clearFlags(LayoutParams.FLAG_KEEP_SCREEN_ON)
                print("Screen can sleep now")
            return True
        except Exception as e:
            print(f"Error setting screen on: {e}")
            return False
    
    @staticmethod
    def hide_navigation_bar():
        if not ANDROID_AVAILABLE:
            return True
        
        try:
            from jnius import autoclass
            
            View = autoclass('android.view.View')
            activity = mActivity
            
            decor_view = activity.getWindow().getDecorView()
            flags = (View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                     View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
                     View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                     View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                     View.SYSTEM_UI_FLAG_FULLSCREEN |
                     View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY)
            
            decor_view.setSystemUiVisibility(flags)
            print("Navigation bar hidden!")
            return True
        except Exception as e:
            print(f"Error hiding navigation: {e}")
            return False


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


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        
        bg = GradientBackground()
        layout.add_widget(bg)
        
        content = BoxLayout(
            orientation='vertical',
            padding=[dp(30), dp(50)],
            spacing=dp(20),
            size_hint=(0.85, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        icon_label = Label(
            text='',
            font_size=sp(80),
            size_hint_y=0.25
        )
        content.add_widget(icon_label)
        
        title_label = Label(
            text='Screen Guardian',
            font_size=sp(32),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=0.12
        )
        content.add_widget(title_label)
        
        subtitle_label = Label(
            text='Parental Control System',
            font_size=sp(16),
            color=COLORS['text_secondary'],
            size_hint_y=0.08
        )
        content.add_widget(subtitle_label)
        
        content.add_widget(Widget(size_hint_y=0.05))
        
        pin_label = Label(
            text='Enter Parent PIN',
            font_size=sp(14),
            color=COLORS['text_secondary'],
            size_hint_y=0.06,
            halign='left'
        )
        content.add_widget(pin_label)
        
        self.pin_input = StyledTextInput(
            multiline=False,
            password=True,
            hint_text='PIN Code',
            input_filter='int',
            size_hint_y=0.12,
            halign='center'
        )
        content.add_widget(self.pin_input)
        
        content.add_widget(Widget(size_hint_y=0.03))
        
        login_btn = StyledButton(
            text='UNLOCK',
            btn_color=COLORS['primary'],
            size_hint_y=0.12,
            font_size=sp(18)
        )
        login_btn.bind(on_release=self.verify_pin)
        content.add_widget(login_btn)
        
        self.status_label = Label(
            text='',
            font_size=sp(14),
            color=COLORS['error'],
            size_hint_y=0.08
        )
        content.add_widget(self.status_label)
        
        hint_label = Label(
            text='Default PIN: 1234',
            font_size=sp(12),
            color=(0.4, 0.4, 0.45, 1),
            size_hint_y=0.06
        )
        content.add_widget(hint_label)
        
        layout.add_widget(content)
        self.add_widget(layout)
    
    def verify_pin(self, instance):
        config = Config.load()
        if self.pin_input.text == config['parent_pin']:
            self.pin_input.text = ''
            self.status_label.text = ''
            self.manager.current = 'timer'
        else:
            self.status_label.text = 'Incorrect PIN!'
            self.pin_input.text = ''


class TimerScreen(Screen):
    time_remaining = StringProperty("00:00")
    timer_status = StringProperty("Ready")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config.load()
        self.countdown_event = None
        self.timer_end_time = None
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        
        bg = GradientBackground()
        layout.add_widget(bg)
        
        content = BoxLayout(
            orientation='vertical',
            padding=[dp(25), dp(30)],
            spacing=dp(12),
            size_hint=(0.9, 0.95),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        header = BoxLayout(size_hint_y=0.08, spacing=dp(10))
        header.add_widget(Label(
            text='Screen Guardian',
            font_size=sp(22),
            bold=True,
            color=COLORS['text_primary'],
            halign='left',
            size_hint_x=0.7
        ))
        self.status_indicator = PulsingDot(
            size_hint=(None, None),
            size=(dp(12), dp(12)),
            color=COLORS['text_secondary']
        )
        header.add_widget(self.status_indicator)
        content.add_widget(header)
        
        timer_box = BoxLayout(orientation='vertical', size_hint_y=0.28)
        
        self.progress_widget = CircularProgress(
            size_hint=(None, None),
            size=(dp(180), dp(180)),
            pos_hint={'center_x': 0.5}
        )
        timer_box.add_widget(self.progress_widget)
        
        self.time_display = Label(
            text=self.time_remaining,
            font_size=sp(52),
            bold=True,
            color=COLORS['text_primary']
        )
        timer_box.add_widget(self.time_display)
        
        self.status_label = Label(
            text=self.timer_status,
            font_size=sp(16),
            color=COLORS['text_secondary']
        )
        timer_box.add_widget(self.status_label)
        content.add_widget(timer_box)
        
        slider_box = BoxLayout(orientation='vertical', size_hint_y=0.12, spacing=dp(5))
        self.limit_label = Label(
            text=f"Timer Duration: {self.config['timer_minutes']} min",
            font_size=sp(14),
            color=COLORS['text_secondary'],
            halign='left'
        )
        slider_box.add_widget(self.limit_label)
        
        self.limit_slider = Slider(
            min=1, max=120,
            value=self.config['timer_minutes'],
            cursor_size=(dp(24), dp(24)),
            value_track=True,
            value_track_color=COLORS['primary'],
            cursor_image='',
            background_width=dp(4)
        )
        self.limit_slider.bind(value=self.on_limit_change)
        slider_box.add_widget(self.limit_slider)
        content.add_widget(slider_box)
        
        btn_box = BoxLayout(spacing=dp(15), size_hint_y=0.1)
        
        self.start_btn = StyledButton(
            text='START',
            btn_color=COLORS['success'],
            font_size=sp(16)
        )
        self.start_btn.bind(on_release=self.start_timer)
        btn_box.add_widget(self.start_btn)
        
        self.stop_btn = StyledButton(
            text='STOP',
            btn_color=COLORS['error'],
            font_size=sp(16)
        )
        self.stop_btn.bind(on_release=self.stop_timer)
        btn_box.add_widget(self.stop_btn)
        content.add_widget(btn_box)
        
        content.add_widget(Widget(size_hint_y=0.02))
        
        overlay_section = BoxLayout(orientation='vertical', size_hint_y=0.15, spacing=dp(5))
        overlay_section.add_widget(Label(
            text='Overlay Style',
            font_size=sp(14),
            color=COLORS['text_secondary'],
            halign='left'
        ))
        
        overlay_names = ['Random'] + [k.replace('_', ' ').title() for k in OVERLAY_THEMES.keys()]
        overlay_row = BoxLayout(spacing=dp(8))
        self.overlay_buttons = []
        
        for i, name in enumerate(overlay_names[:4]):
            btn = StyledButton(
                text=name,
                btn_color=COLORS['primary'] if i == 0 else COLORS['surface_light'],
                font_size=sp(11)
            )
            btn.name = name.lower().replace(' ', '_')
            btn.bind(on_release=self.select_overlay)
            self.overlay_buttons.append(btn)
            overlay_row.add_widget(btn)
        
        overlay_section.add_widget(overlay_row)
        
        overlay_row2 = BoxLayout(spacing=dp(8))
        for i, name in enumerate(overlay_names[4:]):
            btn = StyledButton(
                text=name,
                btn_color=COLORS['surface_light'],
                font_size=sp(11)
            )
            btn.name = name.lower().replace(' ', '_')
            btn.bind(on_release=self.select_overlay)
            self.overlay_buttons.append(btn)
            overlay_row2.add_widget(btn)
        
        overlay_section.add_widget(overlay_row2)
        content.add_widget(overlay_section)
        
        perm_section = BoxLayout(orientation='vertical', size_hint_y=0.12, spacing=dp(5))
        
        self.perm_status = Label(
            text='Checking permissions...',
            font_size=sp(12),
            color=COLORS['warning'],
            halign='left'
        )
        perm_section.add_widget(self.perm_status)
        
        perm_btn = StyledButton(
            text='Grant Overlay Permission',
            btn_color=COLORS['surface_light'],
            font_size=sp(12)
        )
        perm_btn.bind(on_release=lambda x: AndroidHelper.request_overlay_permission())
        perm_section.add_widget(perm_btn)
        content.add_widget(perm_section)
        
        pin_section = BoxLayout(size_hint_y=0.08, spacing=dp(10))
        pin_section.add_widget(Label(
            text='New PIN:',
            font_size=sp(12),
            color=COLORS['text_secondary'],
            size_hint_x=0.25
        ))
        self.new_pin_input = StyledTextInput(
            multiline=False,
            password=True,
            input_filter='int',
            hint_text='****',
            size_hint_x=0.45
        )
        pin_section.add_widget(self.new_pin_input)
        change_btn = StyledButton(
            text='Change',
            btn_color=COLORS['surface_light'],
            font_size=sp(12),
            size_hint_x=0.3
        )
        change_btn.bind(on_release=self.change_pin)
        pin_section.add_widget(change_btn)
        content.add_widget(pin_section)
        
        layout.add_widget(content)
        self.add_widget(layout)
    
    def select_overlay(self, instance):
        for btn in self.overlay_buttons:
            btn.btn_color = COLORS['surface_light']
            btn._update()
        instance.btn_color = COLORS['primary']
        instance._update()
        
        self.config['selected_overlay'] = instance.name
        Config.save(self.config)
    
    def on_enter(self):
        self.config = Config.load()
        self.check_permission()
        self.check_existing_timer()
    
    def check_permission(self):
        if AndroidHelper.has_overlay_permission():
            self.perm_status.text = "Overlay Permission: Granted"
            self.perm_status.color = COLORS['success']
        else:
            self.perm_status.text = "Overlay Permission: Required"
            self.perm_status.color = COLORS['error']
    
    def check_existing_timer(self):
        if self.config.get('is_timer_active') and self.config.get('timer_end_timestamp'):
            end_time = datetime.fromisoformat(self.config['timer_end_timestamp'])
            if datetime.now() < end_time:
                self.timer_end_time = end_time
                self.resume_countdown()
            elif datetime.now() >= end_time:
                self.trigger_overlay()
    
    def on_limit_change(self, instance, value):
        self.limit_label.text = f"Timer Duration: {int(value)} min"
        self.config['timer_minutes'] = int(value)
        Config.save(self.config)
    
    def start_timer(self, instance):
        if not AndroidHelper.has_overlay_permission():
            popup = Popup(
                title='Permission Required',
                content=Label(text='Please grant Overlay\npermission first!'),
                size_hint=(0.8, 0.35),
                background_color=COLORS['surface']
            )
            popup.open()
            return
        
        minutes = int(self.limit_slider.value)
        self.timer_end_time = datetime.now() + timedelta(minutes=minutes)
        
        self.config['timer_end_timestamp'] = self.timer_end_time.isoformat()
        self.config['is_timer_active'] = True
        self.config['timer_minutes'] = minutes
        Config.save(self.config)
        
        AndroidHelper.start_timer_service()
        
        self.status_label.text = "Timer Active"
        self.status_label.color = COLORS['success']
        self.status_indicator.color = COLORS['success']
        
        self.resume_countdown()
        
        popup = Popup(
            title='Timer Started',
            content=Label(
                text=f'Screen limit: {minutes} min\n\nYou can close this app.\nOverlay appears when time expires.',
                halign='center'
            ),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def resume_countdown(self):
        if self.countdown_event:
            self.countdown_event.cancel()
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 0.5)
        self.status_label.text = "Timer Active"
        self.status_label.color = COLORS['success']
        self.status_indicator.color = COLORS['success']
    
    def update_countdown(self, dt):
        if not self.timer_end_time:
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
        
        if remaining.total_seconds() < 60:
            self.progress_widget.color = list(COLORS['error'])
    
    def trigger_overlay(self):
        if self.countdown_event:
            self.countdown_event.cancel()
            self.countdown_event = None
        
        self.status_label.text = "Time's Up!"
        self.status_label.color = COLORS['error']
        self.status_indicator.color = COLORS['error']
        self.time_display.text = "00:00"
        
        success = AndroidHelper.show_overlay_window()
        
        if success:
            self.config['is_timer_active'] = False
            self.config['timer_end_timestamp'] = None
            Config.save(self.config)
            
            selected = self.config.get('selected_overlay', 'random')
            if selected == 'random':
                selected = random.choice(list(OVERLAY_THEMES.keys()))
            
            self.manager.get_screen('blocked').set_theme(selected)
            self.manager.current = 'blocked'
    
    def stop_timer(self, instance):
        if self.countdown_event:
            self.countdown_event.cancel()
            self.countdown_event = None
        
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
    
    def change_pin(self, instance):
        new_pin = self.new_pin_input.text
        if len(new_pin) >= 4:
            self.config['parent_pin'] = new_pin
            Config.save(self.config)
            self.new_pin_input.text = ''
            popup = Popup(
                title='Success',
                content=Label(text='PIN updated successfully!'),
                size_hint=(0.7, 0.25)
            )
            popup.open()
        else:
            popup = Popup(
                title='Error',
                content=Label(text='PIN must be at least 4 digits'),
                size_hint=(0.7, 0.25)
            )
            popup.open()


class BlockedScreen(Screen):
    current_theme = StringProperty('battery_drained')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_data = OVERLAY_THEMES['battery_drained']
        self.build_ui()
    
    def set_theme(self, theme_name):
        if theme_name in OVERLAY_THEMES:
            self.current_theme = theme_name
            self.theme_data = OVERLAY_THEMES[theme_name]
            self.update_ui()
    
    def build_ui(self):
        self.layout = FloatLayout()
        
        self.bg_widget = Widget()
        self.layout.add_widget(self.bg_widget)
        
        self.content = BoxLayout(
            orientation='vertical',
            padding=[dp(40), dp(60)],
            spacing=dp(15),
            size_hint=(1, 1)
        )
        
        self.content.add_widget(Widget(size_hint_y=0.1))
        
        self.icon_label = Label(
            text=self.theme_data['icon'],
            font_size=sp(100),
            size_hint_y=0.2
        )
        self.content.add_widget(self.icon_label)
        
        self.title_label = Label(
            text=self.theme_data['title'],
            font_size=sp(36),
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=0.1,
            halign='center'
        )
        self.content.add_widget(self.title_label)
        
        self.subtitle_label = Label(
            text=self.theme_data['subtitle'],
            font_size=sp(18),
            color=COLORS['text_secondary'],
            size_hint_y=0.06
        )
        self.content.add_widget(self.subtitle_label)
        
        self.content.add_widget(Widget(size_hint_y=0.05))
        
        self.percent_label = Label(
            text=self.theme_data['percent'],
            font_size=sp(48),
            bold=True,
            size_hint_y=0.12
        )
        self.content.add_widget(self.percent_label)
        
        self.detail_label = Label(
            text=self.theme_data['detail'],
            font_size=sp(14),
            color=COLORS['text_secondary'],
            size_hint_y=0.08,
            halign='center',
            text_size=(Window.width - dp(80), None)
        )
        self.content.add_widget(self.detail_label)
        
        self.content.add_widget(Widget(size_hint_y=0.1))
        
        unlock_hint = Label(
            text='Parent: Enter PIN below',
            font_size=sp(12),
            color=(0.35, 0.35, 0.4, 1),
            size_hint_y=0.04
        )
        self.content.add_widget(unlock_hint)
        
        pin_box = BoxLayout(
            size_hint=(0.8, 0.08),
            pos_hint={'center_x': 0.5},
            spacing=dp(10)
        )
        
        self.pin_input = TextInput(
            multiline=False,
            password=True,
            hint_text='PIN',
            input_filter='int',
            font_size=sp(20),
            halign='center',
            background_color=(0.15, 0.15, 0.18, 1),
            foreground_color=COLORS['text_primary'],
            cursor_color=COLORS['primary'],
            size_hint_x=0.65
        )
        pin_box.add_widget(self.pin_input)
        
        unlock_btn = Button(
            text='Unlock',
            font_size=sp(14),
            background_color=(0.25, 0.25, 0.3, 1),
            size_hint_x=0.35
        )
        unlock_btn.bind(on_release=self.try_unlock)
        pin_box.add_widget(unlock_btn)
        
        self.content.add_widget(pin_box)
        
        self.status_label = Label(
            text='',
            font_size=sp(12),
            color=COLORS['error'],
            size_hint_y=0.04
        )
        self.content.add_widget(self.status_label)
        
        self.content.add_widget(Widget(size_hint_y=0.05))
        
        self.layout.add_widget(self.content)
        self.add_widget(self.layout)
    
    def update_ui(self):
        self.icon_label.text = self.theme_data['icon']
        self.title_label.text = self.theme_data['title']
        self.subtitle_label.text = self.theme_data['subtitle']
        self.percent_label.text = self.theme_data['percent']
        self.percent_label.color = self.theme_data['accent_color']
        self.detail_label.text = self.theme_data['detail']
        
        self.bg_widget.canvas.clear()
        with self.bg_widget.canvas:
            Color(*self.theme_data['bg_color'])
            Rectangle(pos=(0, 0), size=Window.size)
    
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
            AndroidHelper.hide_overlay_window()
            AndroidHelper.stop_lock_task()
            self.pin_input.text = ''
            self.status_label.text = ''
            self.manager.current = 'timer'
        else:
            self.status_label.text = 'Incorrect PIN'
            self.pin_input.text = ''


class ScreenTimeLimiterApp(App):
    def build(self):
        Window.clearcolor = COLORS['background']
        Window.bind(on_keyboard=self.on_keyboard)
        AndroidHelper.request_all_permissions()
        
        self.sm = ScreenManager(transition=FadeTransition(duration=0.3))
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(TimerScreen(name='timer'))
        self.sm.add_widget(BlockedScreen(name='blocked'))
        
        return self.sm
    
    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            if self.sm.current == 'blocked':
                print("Back button blocked on blocked screen!")
                return True
        return False
    
    def on_start(self):
        should_block = False
        
        if ANDROID_AVAILABLE:
            try:
                intent = mActivity.getIntent()
                if intent and intent.getBooleanExtra("show_block_screen", False):
                    print("App launched by service in block mode")
                    should_block = True
            except Exception as e:
                print(f"Error checking intent: {e}")
        
        config = Config.load()
        if config.get('is_timer_active') and config.get('timer_end_timestamp'):
            try:
                end_time = datetime.fromisoformat(config['timer_end_timestamp'])
                if datetime.now() >= end_time:
                    print("Timer expired - showing block screen")
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
        print(f"Block screen displayed with theme: {theme}")


if __name__ == '__main__':
    ScreenTimeLimiterApp().run()
