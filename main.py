"""
YouTube Parental Control App
Limits children's YouTube usage by showing a "battery drained" overlay screen.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.core.window import Window
from kivy.utils import platform
import json
import os
from datetime import datetime, timedelta

try:
    from android.permissions import request_permissions, Permission
    from android import mActivity
    from jnius import autoclass, cast
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False
    print("Running on desktop - Android features disabled")


class Config:
    """Manages app configuration and persistence"""
    CONFIG_FILE = "parental_config.json"
    
    DEFAULT_CONFIG = {
        "parent_pin": "1234",
        "daily_limit_minutes": 60,
        "is_enabled": True,
        "youtube_usage_today": 0,
        "last_reset_date": "",
        "blocked_hours_start": 21,
        "blocked_hours_end": 7,
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
    """Handles Android-specific functionality"""
    
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
    def request_usage_access():
        if not ANDROID_AVAILABLE:
            print("Usage access permission (simulated)")
            return
        
        try:
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            
            intent = Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)
            mActivity.startActivity(intent)
        except Exception as e:
            print(f"Error requesting usage access: {e}")
    
    @staticmethod
    def request_device_admin():
        if not ANDROID_AVAILABLE:
            print("Device admin permission (simulated)")
            return
        
        try:
            Intent = autoclass('android.content.Intent')
            DevicePolicyManager = autoclass('android.app.admin.DevicePolicyManager')
            ComponentName = autoclass('android.content.ComponentName')
            
            admin_component = ComponentName(
                mActivity,
                'org.parentalcontrol.youtubelimiter.MyDeviceAdminReceiver'
            )
            
            intent = Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN)
            intent.putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, admin_component)
            intent.putExtra(
                DevicePolicyManager.EXTRA_ADD_EXPLANATION,
                "Enable device admin to prevent children from uninstalling this parental control app."
            )
            mActivity.startActivity(intent)
        except Exception as e:
            print(f"Error requesting device admin: {e}")
    
    @staticmethod
    def is_youtube_running():
        if not ANDROID_AVAILABLE:
            return False
        
        try:
            UsageStatsManager = autoclass('android.app.usage.UsageStatsManager')
            UsageEvents = autoclass('android.app.usage.UsageEvents')
            System = autoclass('java.lang.System')
            
            context = mActivity
            usm = context.getSystemService(context.USAGE_STATS_SERVICE)
            
            end_time = System.currentTimeMillis()
            start_time = end_time - 5000
            
            events = usm.queryEvents(start_time, end_time)
            
            last_foreground_app = None
            while events.hasNextEvent():
                event = UsageEvents.Event()
                events.getNextEvent(event)
                
                if event.getEventType() == UsageEvents.Event.MOVE_TO_FOREGROUND:
                    last_foreground_app = event.getPackageName()
            
            if last_foreground_app:
                youtube_packages = [
                    'com.google.android.youtube',
                    'com.google.android.youtube.tv',
                    'com.google.android.youtube.music',
                    'com.google.android.apps.youtube.kids'
                ]
                if last_foreground_app in youtube_packages:
                    print(f"YouTube detected: {last_foreground_app}")
                    return True
                    
        except Exception as e:
            print(f"Error checking YouTube via UsageStats: {e}")
        return False
    
    @staticmethod
    def show_overlay_window():
        if not ANDROID_AVAILABLE:
            print("Would show overlay window on Android")
            return
        
        try:
            WindowManager = autoclass('android.view.WindowManager')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            View = autoclass('android.view.View')
            TextView = autoclass('android.widget.TextView')
            Color = autoclass('android.graphics.Color')
            Gravity = autoclass('android.view.Gravity')
            Build = autoclass('android.os.Build')
            
            context = mActivity
            wm = context.getSystemService(context.WINDOW_SERVICE)
            
            overlay_type = LayoutParams.TYPE_APPLICATION_OVERLAY if Build.VERSION.SDK_INT >= 26 else LayoutParams.TYPE_PHONE
            
            params = LayoutParams(
                LayoutParams.MATCH_PARENT,
                LayoutParams.MATCH_PARENT,
                overlay_type,
                LayoutParams.FLAG_NOT_FOCUSABLE | LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                -3  # PixelFormat.TRANSLUCENT
            )
            
            tv = TextView(context)
            tv.setText("Battery Drained\n\nPlease charge your device")
            tv.setTextColor(Color.WHITE)
            tv.setBackgroundColor(Color.BLACK)
            tv.setGravity(Gravity.CENTER)
            tv.setTextSize(32)
            
            wm.addView(tv, params)
        except Exception as e:
            print(f"Error showing overlay: {e}")


class LoginScreen(Screen):
    """Parent PIN entry screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(
            text='YouTube Limiter\nParental Control',
            font_size='24sp',
            halign='center',
            size_hint_y=0.3
        ))
        
        layout.add_widget(Label(text='Enter Parent PIN:', size_hint_y=0.1))
        
        self.pin_input = TextInput(
            multiline=False,
            password=True,
            font_size='24sp',
            size_hint_y=0.15,
            halign='center'
        )
        layout.add_widget(self.pin_input)
        
        login_btn = Button(
            text='Login',
            size_hint_y=0.15,
            background_color=(0.2, 0.6, 0.2, 1)
        )
        login_btn.bind(on_release=self.verify_pin)
        layout.add_widget(login_btn)
        
        self.status_label = Label(text='', size_hint_y=0.1, color=(1, 0, 0, 1))
        layout.add_widget(self.status_label)
        
        layout.add_widget(Label(text='', size_hint_y=0.2))
        
        self.add_widget(layout)
    
    def verify_pin(self, instance):
        config = Config.load()
        if self.pin_input.text == config['parent_pin']:
            self.pin_input.text = ''
            self.status_label.text = ''
            self.manager.current = 'settings'
        else:
            self.status_label.text = 'Incorrect PIN!'
            self.pin_input.text = ''


class SettingsScreen(Screen):
    """Parent settings screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config.load()
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        main_layout.add_widget(Label(
            text='Parental Control Settings',
            font_size='20sp',
            size_hint_y=0.1
        ))
        
        enable_layout = BoxLayout(size_hint_y=0.1)
        enable_layout.add_widget(Label(text='Enable YouTube Limiter:'))
        self.enable_switch = Switch(active=self.config['is_enabled'])
        enable_layout.add_widget(self.enable_switch)
        main_layout.add_widget(enable_layout)
        
        limit_layout = BoxLayout(orientation='vertical', size_hint_y=0.15)
        self.limit_label = Label(text=f"Daily Limit: {self.config['daily_limit_minutes']} minutes")
        limit_layout.add_widget(self.limit_label)
        self.limit_slider = Slider(min=10, max=180, value=self.config['daily_limit_minutes'])
        self.limit_slider.bind(value=self.on_limit_change)
        limit_layout.add_widget(self.limit_slider)
        main_layout.add_widget(limit_layout)
        
        usage_layout = BoxLayout(size_hint_y=0.1)
        usage_layout.add_widget(Label(text='Today\'s Usage:'))
        self.usage_label = Label(text=f"{self.config['youtube_usage_today']} minutes")
        usage_layout.add_widget(self.usage_label)
        main_layout.add_widget(usage_layout)
        
        reset_usage_btn = Button(
            text='Reset Today\'s Usage',
            size_hint_y=0.1,
            background_color=(0.6, 0.4, 0.2, 1)
        )
        reset_usage_btn.bind(on_release=self.reset_usage)
        main_layout.add_widget(reset_usage_btn)
        
        main_layout.add_widget(Label(text='--- Permissions ---', size_hint_y=0.08))
        
        perms_layout = BoxLayout(size_hint_y=0.12, spacing=5)
        
        overlay_btn = Button(text='Overlay', background_color=(0.3, 0.5, 0.7, 1))
        overlay_btn.bind(on_release=lambda x: AndroidHelper.request_overlay_permission())
        perms_layout.add_widget(overlay_btn)
        
        usage_btn = Button(text='Usage Access', background_color=(0.3, 0.5, 0.7, 1))
        usage_btn.bind(on_release=lambda x: AndroidHelper.request_usage_access())
        perms_layout.add_widget(usage_btn)
        
        admin_btn = Button(text='Device Admin', background_color=(0.3, 0.5, 0.7, 1))
        admin_btn.bind(on_release=lambda x: AndroidHelper.request_device_admin())
        perms_layout.add_widget(admin_btn)
        
        main_layout.add_widget(perms_layout)
        
        main_layout.add_widget(Label(text='--- Change PIN ---', size_hint_y=0.08))
        
        pin_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        pin_layout.add_widget(Label(text='New PIN:'))
        self.new_pin_input = TextInput(multiline=False, password=True)
        pin_layout.add_widget(self.new_pin_input)
        change_pin_btn = Button(text='Change', size_hint_x=0.3)
        change_pin_btn.bind(on_release=self.change_pin)
        pin_layout.add_widget(change_pin_btn)
        main_layout.add_widget(pin_layout)
        
        save_btn = Button(
            text='Save & Start Monitoring',
            size_hint_y=0.12,
            background_color=(0.2, 0.6, 0.2, 1)
        )
        save_btn.bind(on_release=self.save_and_start)
        main_layout.add_widget(save_btn)
        
        self.add_widget(main_layout)
    
    def on_limit_change(self, instance, value):
        self.limit_label.text = f"Daily Limit: {int(value)} minutes"
    
    def reset_usage(self, instance):
        self.config['youtube_usage_today'] = 0
        self.usage_label.text = "0 minutes"
        Config.save(self.config)
    
    def change_pin(self, instance):
        new_pin = self.new_pin_input.text
        if len(new_pin) >= 4:
            self.config['parent_pin'] = new_pin
            Config.save(self.config)
            self.new_pin_input.text = ''
            popup = Popup(
                title='Success',
                content=Label(text='PIN changed successfully!'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
        else:
            popup = Popup(
                title='Error',
                content=Label(text='PIN must be at least 4 characters'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
    
    def save_and_start(self, instance):
        self.config['is_enabled'] = self.enable_switch.active
        self.config['daily_limit_minutes'] = int(self.limit_slider.value)
        Config.save(self.config)
        
        self.manager.current = 'monitoring'


class MonitoringScreen(Screen):
    """Background monitoring display"""
    
    youtube_active = BooleanProperty(False)
    minutes_used = NumericProperty(0)
    minutes_remaining = NumericProperty(60)
    status_text = StringProperty("Monitoring...")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config.load()
        self.check_event = None
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(
            text='YouTube Monitor Active',
            font_size='22sp',
            size_hint_y=0.15
        ))
        
        self.status_display = Label(
            text=self.status_text,
            font_size='18sp',
            size_hint_y=0.15
        )
        layout.add_widget(self.status_display)
        
        self.usage_display = Label(
            text=f"Used: {self.minutes_used} min | Remaining: {self.minutes_remaining} min",
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.usage_display)
        
        self.youtube_status = Label(
            text="YouTube: Not Running",
            font_size='16sp',
            size_hint_y=0.1,
            color=(0, 1, 0, 1)
        )
        layout.add_widget(self.youtube_status)
        
        layout.add_widget(Label(text='', size_hint_y=0.3))
        
        settings_btn = Button(
            text='Parent Settings',
            size_hint_y=0.1,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        settings_btn.bind(on_release=self.goto_settings)
        layout.add_widget(settings_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.config = Config.load()
        self.minutes_used = self.config['youtube_usage_today']
        self.minutes_remaining = max(0, self.config['daily_limit_minutes'] - self.minutes_used)
        self.update_display()
        
        if self.check_event:
            self.check_event.cancel()
        self.check_event = Clock.schedule_interval(self.check_youtube, 5)
    
    def on_leave(self):
        if self.check_event:
            self.check_event.cancel()
            self.check_event = None
    
    def check_youtube(self, dt):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.config.get('last_reset_date') != today:
            self.config['youtube_usage_today'] = 0
            self.config['last_reset_date'] = today
            self.minutes_used = 0
            Config.save(self.config)
        
        if not self.config['is_enabled']:
            self.status_display.text = "Monitoring DISABLED"
            return
        
        youtube_running = AndroidHelper.is_youtube_running()
        
        if youtube_running:
            self.youtube_status.text = "YouTube: RUNNING"
            self.youtube_status.color = (1, 0.5, 0, 1)
            
            self.minutes_used += 1/12
            self.config['youtube_usage_today'] = int(self.minutes_used)
            Config.save(self.config)
            
            self.minutes_remaining = max(0, self.config['daily_limit_minutes'] - self.minutes_used)
            
            if self.minutes_remaining <= 0:
                self.show_block_screen()
        else:
            self.youtube_status.text = "YouTube: Not Running"
            self.youtube_status.color = (0, 1, 0, 1)
        
        self.update_display()
    
    def update_display(self):
        self.usage_display.text = f"Used: {int(self.minutes_used)} min | Remaining: {int(self.minutes_remaining)} min"
        if self.config['is_enabled']:
            self.status_display.text = "Monitoring Active"
        else:
            self.status_display.text = "Monitoring DISABLED"
    
    def show_block_screen(self):
        self.status_display.text = "TIME LIMIT REACHED!"
        self.youtube_status.color = (1, 0, 0, 1)
        AndroidHelper.show_overlay_window()
    
    def goto_settings(self, instance):
        self.manager.current = 'login'


class BatteryDrainedScreen(Screen):
    """Full screen 'battery drained' blocker"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=0)
        
        layout.add_widget(Label(text='', size_hint_y=0.3))
        
        layout.add_widget(Label(
            text='[size=48][b]Battery Drained[/b][/size]',
            markup=True,
            size_hint_y=0.2
        ))
        
        layout.add_widget(Label(
            text='[size=24]Please charge your device[/size]',
            markup=True,
            size_hint_y=0.1
        ))
        
        layout.add_widget(Label(
            text='[size=18]( 0% )[/size]',
            markup=True,
            size_hint_y=0.1
        ))
        
        layout.add_widget(Label(text='', size_hint_y=0.3))
        
        self.add_widget(layout)
        
        Window.clearcolor = (0, 0, 0, 1)


class YouTubeLimiterApp(App):
    """Main Application"""
    
    def build(self):
        AndroidHelper.request_all_permissions()
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(MonitoringScreen(name='monitoring'))
        sm.add_widget(BatteryDrainedScreen(name='blocked'))
        
        return sm
    
    def on_start(self):
        config = Config.load()
        if config['is_enabled']:
            print("YouTube Limiter is enabled and will start monitoring")


if __name__ == '__main__':
    YouTubeLimiterApp().run()
