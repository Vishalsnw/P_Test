"""
Background service that monitors timer and shows overlay when time expires.
This runs even when the main app is in background.
"""
import os
import json
import time
from datetime import datetime

CONFIG_FILE = "/data/data/org.parentalcontrol.youtubelimiter/files/app/parental_config.json"
ALT_CONFIG_FILE = "parental_config.json"

overlay_shown = False

def load_config():
    """Load configuration from file"""
    for path in [CONFIG_FILE, ALT_CONFIG_FILE]:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
        except:
            pass
    return None

def save_config(config):
    """Save configuration to file"""
    for path in [CONFIG_FILE, ALT_CONFIG_FILE]:
        try:
            with open(path, 'w') as f:
                json.dump(config, f)
            print(f"SERVICE: Config saved to {path}")
            return True
        except Exception as e:
            print(f"SERVICE: Failed to save config to {path}: {e}")
    return False

def check_overlay_permission():
    """Check if overlay permission is granted"""
    try:
        from jnius import autoclass
        
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        Settings = autoclass('android.provider.Settings')
        
        context = service.getApplicationContext()
        can_draw = Settings.canDrawOverlays(context)
        print(f"SERVICE: Overlay permission granted: {can_draw}")
        return can_draw
    except Exception as e:
        print(f"SERVICE: Error checking overlay permission: {e}")
        return False

def launch_blocking_activity():
    """Launch the main app in blocking mode - this shows a fullscreen activity"""
    try:
        from jnius import autoclass
        
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        
        Intent = autoclass('android.content.Intent')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        
        context = service.getApplicationContext()
        
        intent = Intent(context, PythonActivity)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
        intent.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
        intent.putExtra("show_block_screen", True)
        
        context.startActivity(intent)
        print("SERVICE: Launched blocking activity!")
        return True
    except Exception as e:
        print(f"SERVICE: Error launching activity: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_overlay():
    """Show the battery drained overlay over all apps"""
    global overlay_shown
    
    if not check_overlay_permission():
        print("SERVICE: Cannot show overlay - permission not granted!")
        print("SERVICE: Falling back to launching blocking activity...")
        return launch_blocking_activity()
    
    try:
        from jnius import autoclass
        
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        
        WindowManager = autoclass('android.view.WindowManager')
        LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        FrameLayout = autoclass('android.widget.FrameLayout')
        TextView = autoclass('android.widget.TextView')
        Color = autoclass('android.graphics.Color')
        Gravity = autoclass('android.view.Gravity')
        Build = autoclass('android.os.Build')
        TypedValue = autoclass('android.util.TypedValue')
        Context = autoclass('android.content.Context')
        PixelFormat = autoclass('android.graphics.PixelFormat')
        
        context = service.getApplicationContext()
        wm = context.getSystemService(Context.WINDOW_SERVICE)
        
        print(f"SERVICE: Android SDK version: {Build.VERSION.SDK_INT}")
        
        if Build.VERSION.SDK_INT >= 26:
            overlay_type = LayoutParams.TYPE_APPLICATION_OVERLAY
        else:
            overlay_type = LayoutParams.TYPE_SYSTEM_ALERT
        
        print(f"SERVICE: Using overlay type: {overlay_type}")
        
        flags = (LayoutParams.FLAG_NOT_FOCUSABLE |
                 LayoutParams.FLAG_NOT_TOUCH_MODAL |
                 LayoutParams.FLAG_LAYOUT_IN_SCREEN |
                 LayoutParams.FLAG_FULLSCREEN |
                 LayoutParams.FLAG_SHOW_WHEN_LOCKED |
                 LayoutParams.FLAG_DISMISS_KEYGUARD |
                 LayoutParams.FLAG_TURN_SCREEN_ON)
        
        params = LayoutParams(
            LayoutParams.MATCH_PARENT,
            LayoutParams.MATCH_PARENT,
            overlay_type,
            flags,
            PixelFormat.TRANSLUCENT
        )
        
        layout = FrameLayout(context)
        layout.setBackgroundColor(Color.BLACK)
        
        title = TextView(context)
        title.setText("Battery Drained\n\nPlease charge your device\n\n0%")
        title.setTextColor(Color.WHITE)
        title.setTextSize(TypedValue.COMPLEX_UNIT_SP, 36)
        title.setGravity(Gravity.CENTER)
        
        frame_params = FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT
        )
        frame_params.gravity = Gravity.CENTER
        layout.addView(title, frame_params)
        
        try:
            wm.addView(layout, params)
            overlay_shown = True
            print("SERVICE: OVERLAY SHOWN SUCCESSFULLY!")
            return True
        except Exception as e:
            print(f"SERVICE: Failed to add view to WindowManager: {e}")
            print("SERVICE: Falling back to launching blocking activity...")
            import traceback
            traceback.print_exc()
            return launch_blocking_activity()
            
    except Exception as e:
        print(f"SERVICE ERROR showing overlay: {e}")
        import traceback
        traceback.print_exc()
        print("SERVICE: Falling back to launching blocking activity...")
        return launch_blocking_activity()


def main():
    """Main service loop - checks timer and shows overlay when expired"""
    global overlay_shown
    
    print("=" * 50)
    print("SERVICE: Timer monitoring service started!")
    print("=" * 50)
    
    has_permission = check_overlay_permission()
    print(f"SERVICE: Overlay permission status: {has_permission}")
    
    if not has_permission:
        print("SERVICE WARNING: Overlay permission not granted!")
        print("SERVICE WARNING: Will use activity fallback when timer expires")
    
    while True:
        try:
            config = load_config()
            
            if config:
                is_active = config.get('is_timer_active', False)
                end_timestamp = config.get('timer_end_timestamp')
                
                if is_active and end_timestamp:
                    end_time = datetime.fromisoformat(end_timestamp)
                    now = datetime.now()
                    remaining = (end_time - now).total_seconds()
                    
                    if remaining <= 0 and not overlay_shown:
                        print("=" * 50)
                        print("SERVICE: TIMER EXPIRED!")
                        print("=" * 50)
                        
                        success = show_overlay()
                        
                        if success:
                            overlay_shown = True
                            config['is_timer_active'] = False
                            config['timer_end_timestamp'] = None
                            save_config(config)
                            print("SERVICE: Block screen activated!")
                        else:
                            print("SERVICE: Failed to show block screen!")
                            
                    elif remaining > 0:
                        mins = int(remaining // 60)
                        secs = int(remaining % 60)
                        print(f"SERVICE: Timer active - {mins}m {secs}s remaining")
            
            time.sleep(5)
            
        except Exception as e:
            print(f"SERVICE ERROR in main loop: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)


if __name__ == '__main__':
    main()
