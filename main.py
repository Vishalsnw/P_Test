"""
YouTube Parental Control App
Simple timer-based approach: After set time elapses, shows a "battery drained" overlay.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.core.window import Window
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
        "timer_minutes": 5,
        "timer_end_timestamp": None,
        "is_timer_active": False,
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
    
    overlay_view = None
    window_manager = None
    
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
    def has_overlay_permission():
        """Check if overlay permission is granted"""
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
        """Show full-screen battery drained overlay"""
        if not ANDROID_AVAILABLE:
            print("Would show overlay window on Android")
            return True
        
        try:
            WindowManager = autoclass('android.view.WindowManager')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
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
                LayoutParams.FLAG_NOT_FOCUSABLE | LayoutParams.FLAG_LAYOUT_IN_SCREEN | LayoutParams.FLAG_FULLSCREEN,
                -3
            )
            
            tv = TextView(context)
            tv.setText("\n\n\n\nBattery Drained\n\nPlease charge your device\n\n0%")
            tv.setTextColor(Color.WHITE)
            tv.setBackgroundColor(Color.BLACK)
            tv.setGravity(Gravity.CENTER)
            tv.setTextSize(32)
            
            wm.addView(tv, params)
            
            AndroidHelper.overlay_view = tv
            AndroidHelper.window_manager = wm
            
            print("Overlay shown successfully")
            return True
        except Exception as e:
            print(f"Error showing overlay: {e}")
            return False
    
    @staticmethod
    def hide_overlay_window():
        """Remove the overlay window"""
        if not ANDROID_AVAILABLE:
            print("Would hide overlay window on Android")
            return True
        
        try:
            if AndroidHelper.overlay_view and AndroidHelper.window_manager:
                AndroidHelper.window_manager.removeView(AndroidHelper.overlay_view)
                AndroidHelper.overlay_view = None
                AndroidHelper.window_manager = None
                print("Overlay hidden successfully")
                return True
        except Exception as e:
            print(f"Error hiding overlay: {e}")
        return False


class LoginScreen(Screen):
    """Parent PIN entry screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(
            text='Screen Time Limiter\nParental Control',
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
            halign='center',
            input_filter='int'
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
        
        layout.add_widget(Label(text='Default PIN: 1234', size_hint_y=0.2, color=(0.5, 0.5, 0.5, 1)))
        
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
    """Timer configuration and control screen"""
    
    time_remaining = StringProperty("00:00")
    timer_status = StringProperty("Timer Not Active")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config.load()
        self.countdown_event = None
        self.timer_end_time = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        main_layout.add_widget(Label(
            text='Screen Time Limiter',
            font_size='22sp',
            size_hint_y=0.1
        ))
        
        self.status_label = Label(
            text=self.timer_status,
            font_size='18sp',
            size_hint_y=0.1,
            color=(1, 1, 0, 1)
        )
        main_layout.add_widget(self.status_label)
        
        self.time_display = Label(
            text=self.time_remaining,
            font_size='48sp',
            size_hint_y=0.15
        )
        main_layout.add_widget(self.time_display)
        
        limit_layout = BoxLayout(orientation='vertical', size_hint_y=0.15)
        self.limit_label = Label(text=f"Set Timer: {self.config['timer_minutes']} minutes")
        limit_layout.add_widget(self.limit_label)
        self.limit_slider = Slider(min=1, max=120, value=self.config['timer_minutes'])
        self.limit_slider.bind(value=self.on_limit_change)
        limit_layout.add_widget(self.limit_slider)
        main_layout.add_widget(limit_layout)
        
        self.start_btn = Button(
            text='START TIMER',
            size_hint_y=0.12,
            background_color=(0.2, 0.6, 0.2, 1),
            font_size='20sp'
        )
        self.start_btn.bind(on_release=self.start_timer)
        main_layout.add_widget(self.start_btn)
        
        self.stop_btn = Button(
            text='STOP TIMER',
            size_hint_y=0.12,
            background_color=(0.6, 0.2, 0.2, 1),
            font_size='20sp'
        )
        self.stop_btn.bind(on_release=self.stop_timer)
        main_layout.add_widget(self.stop_btn)
        
        main_layout.add_widget(Label(text='--- Permissions ---', size_hint_y=0.05))
        
        self.perm_status = Label(
            text='Checking overlay permission...',
            size_hint_y=0.06,
            color=(1, 1, 0, 1)
        )
        main_layout.add_widget(self.perm_status)
        
        perm_btn = Button(
            text='Grant Overlay Permission',
            size_hint_y=0.08,
            background_color=(0.3, 0.5, 0.7, 1)
        )
        perm_btn.bind(on_release=lambda x: AndroidHelper.request_overlay_permission())
        main_layout.add_widget(perm_btn)
        
        main_layout.add_widget(Label(text='--- Change PIN ---', size_hint_y=0.05))
        
        pin_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        pin_layout.add_widget(Label(text='New PIN:'))
        self.new_pin_input = TextInput(multiline=False, password=True, input_filter='int')
        pin_layout.add_widget(self.new_pin_input)
        change_pin_btn = Button(text='Change', size_hint_x=0.3)
        change_pin_btn.bind(on_release=self.change_pin)
        pin_layout.add_widget(change_pin_btn)
        main_layout.add_widget(pin_layout)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Called when screen is shown"""
        self.config = Config.load()
        self.check_permission()
        self.check_existing_timer()
    
    def check_permission(self):
        if AndroidHelper.has_overlay_permission():
            self.perm_status.text = "Overlay Permission: GRANTED"
            self.perm_status.color = (0, 1, 0, 1)
        else:
            self.perm_status.text = "Overlay Permission: NOT GRANTED"
            self.perm_status.color = (1, 0, 0, 1)
    
    def check_existing_timer(self):
        """Check if there's an active timer from before"""
        if self.config.get('is_timer_active') and self.config.get('timer_end_timestamp'):
            end_time = datetime.fromisoformat(self.config['timer_end_timestamp'])
            if datetime.now() < end_time:
                self.timer_end_time = end_time
                self.resume_countdown()
            elif datetime.now() >= end_time:
                self.trigger_overlay()
    
    def on_limit_change(self, instance, value):
        self.limit_label.text = f"Set Timer: {int(value)} minutes"
        self.config['timer_minutes'] = int(value)
        Config.save(self.config)
    
    def start_timer(self, instance):
        if not AndroidHelper.has_overlay_permission():
            popup = Popup(
                title='Permission Required',
                content=Label(text='Please grant Overlay permission first!\nTap "Grant Overlay Permission" button.'),
                size_hint=(0.9, 0.4)
            )
            popup.open()
            return
        
        minutes = int(self.limit_slider.value)
        self.timer_end_time = datetime.now() + timedelta(minutes=minutes)
        
        self.config['timer_end_timestamp'] = self.timer_end_time.isoformat()
        self.config['is_timer_active'] = True
        self.config['timer_minutes'] = minutes
        Config.save(self.config)
        
        self.status_label.text = "Timer ACTIVE"
        self.status_label.color = (0, 1, 0, 1)
        
        self.resume_countdown()
        
        popup = Popup(
            title='Timer Started',
            content=Label(text=f'Timer set for {minutes} minutes.\nOverlay will appear when time is up.'),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def resume_countdown(self):
        """Start or resume the countdown display"""
        if self.countdown_event:
            self.countdown_event.cancel()
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)
        self.status_label.text = "Timer ACTIVE"
        self.status_label.color = (0, 1, 0, 1)
    
    def update_countdown(self, dt):
        if not self.timer_end_time:
            return
        
        remaining = self.timer_end_time - datetime.now()
        
        if remaining.total_seconds() <= 0:
            self.time_display.text = "00:00"
            self.trigger_overlay()
            return
        
        total_seconds = int(remaining.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.time_display.text = f"{minutes:02d}:{seconds:02d}"
    
    def trigger_overlay(self):
        """Time's up - show the overlay"""
        if self.countdown_event:
            self.countdown_event.cancel()
            self.countdown_event = None
        
        self.status_label.text = "TIME'S UP! Overlay Shown"
        self.status_label.color = (1, 0, 0, 1)
        self.time_display.text = "00:00"
        
        success = AndroidHelper.show_overlay_window()
        
        if success:
            self.config['is_timer_active'] = False
            self.config['timer_end_timestamp'] = None
            Config.save(self.config)
            
            self.manager.current = 'blocked'
    
    def stop_timer(self, instance):
        """Stop the timer and hide overlay if shown"""
        if self.countdown_event:
            self.countdown_event.cancel()
            self.countdown_event = None
        
        self.timer_end_time = None
        self.config['is_timer_active'] = False
        self.config['timer_end_timestamp'] = None
        Config.save(self.config)
        
        AndroidHelper.hide_overlay_window()
        
        self.status_label.text = "Timer Stopped"
        self.status_label.color = (1, 1, 0, 1)
        self.time_display.text = "00:00"
    
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
                content=Label(text='PIN must be at least 4 digits'),
                size_hint=(0.8, 0.3)
            )
            popup.open()


class BlockedScreen(Screen):
    """Full screen 'battery drained' blocker - shows when timer expires"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20)
        
        layout.add_widget(Label(text='', size_hint_y=0.2))
        
        layout.add_widget(Label(
            text='Battery Drained',
            font_size='48sp',
            size_hint_y=0.15
        ))
        
        layout.add_widget(Label(
            text='Please charge your device',
            font_size='24sp',
            size_hint_y=0.1
        ))
        
        layout.add_widget(Label(
            text='0%',
            font_size='36sp',
            size_hint_y=0.1
        ))
        
        layout.add_widget(Label(text='', size_hint_y=0.2))
        
        layout.add_widget(Label(
            text='Parent: Enter PIN to unlock',
            font_size='16sp',
            size_hint_y=0.05,
            color=(0.5, 0.5, 0.5, 1)
        ))
        
        pin_layout = BoxLayout(size_hint_y=0.1, spacing=10, padding=[50, 0, 50, 0])
        self.pin_input = TextInput(
            multiline=False,
            password=True,
            font_size='24sp',
            halign='center',
            input_filter='int'
        )
        pin_layout.add_widget(self.pin_input)
        
        unlock_btn = Button(
            text='Unlock',
            size_hint_x=0.4,
            background_color=(0.3, 0.3, 0.3, 1)
        )
        unlock_btn.bind(on_release=self.try_unlock)
        pin_layout.add_widget(unlock_btn)
        layout.add_widget(pin_layout)
        
        self.status_label = Label(text='', size_hint_y=0.05, color=(1, 0, 0, 1))
        layout.add_widget(self.status_label)
        
        layout.add_widget(Label(text='', size_hint_y=0.05))
        
        self.add_widget(layout)
    
    def on_enter(self):
        Window.clearcolor = (0, 0, 0, 1)
    
    def try_unlock(self, instance):
        config = Config.load()
        if self.pin_input.text == config['parent_pin']:
            AndroidHelper.hide_overlay_window()
            self.pin_input.text = ''
            self.status_label.text = ''
            self.manager.current = 'timer'
        else:
            self.status_label.text = 'Incorrect PIN!'
            self.pin_input.text = ''


class ScreenTimeLimiterApp(App):
    """Main Application"""
    
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        AndroidHelper.request_all_permissions()
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(TimerScreen(name='timer'))
        sm.add_widget(BlockedScreen(name='blocked'))
        
        return sm
    
    def on_start(self):
        config = Config.load()
        if config.get('is_timer_active') and config.get('timer_end_timestamp'):
            end_time = datetime.fromisoformat(config['timer_end_timestamp'])
            if datetime.now() >= end_time:
                print("Timer expired while app was closed - showing overlay")


if __name__ == '__main__':
    ScreenTimeLimiterApp().run()
