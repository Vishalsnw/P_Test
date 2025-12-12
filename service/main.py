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

def show_overlay():
    """Show the battery drained overlay over all apps"""
    try:
        from jnius import autoclass, PythonJavaClass, java_method
        
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        
        WindowManager = autoclass('android.view.WindowManager')
        LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        LinearLayout = autoclass('android.widget.LinearLayout')
        TextView = autoclass('android.widget.TextView')
        Color = autoclass('android.graphics.Color')
        Gravity = autoclass('android.view.Gravity')
        Build = autoclass('android.os.Build')
        TypedValue = autoclass('android.util.TypedValue')
        Context = autoclass('android.content.Context')
        Handler = autoclass('android.os.Handler')
        Looper = autoclass('android.os.Looper')
        
        context = service.getApplicationContext()
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
            LayoutParams.FLAG_LAYOUT_IN_SCREEN |
            LayoutParams.FLAG_LAYOUT_NO_LIMITS |
            LayoutParams.FLAG_SHOW_WHEN_LOCKED |
            LayoutParams.FLAG_TURN_SCREEN_ON,
            -3
        )
        params.gravity = Gravity.TOP | Gravity.START
        
        class AddViewRunnable(PythonJavaClass):
            __javainterfaces__ = ['java/lang/Runnable']
            
            def __init__(self, wm, layout, params):
                super().__init__()
                self.wm = wm
                self.layout = layout
                self.params = params
            
            @java_method('()V')
            def run(self):
                try:
                    self.wm.addView(self.layout, self.params)
                    print("SERVICE: Overlay added to WindowManager!")
                except Exception as e:
                    print(f"SERVICE: Error adding view: {e}")
        
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
        
        handler = Handler(Looper.getMainLooper())
        runnable = AddViewRunnable(wm, layout, params)
        handler.post(runnable)
        
        print("SERVICE: Overlay posted to main thread handler!")
        return True
    except Exception as e:
        print(f"SERVICE ERROR showing overlay: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main service loop - checks timer and shows overlay when expired"""
    print("SERVICE: Timer monitoring service started!")
    
    while True:
        try:
            config = load_config()
            
            if config and config.get('is_timer_active') and config.get('timer_end_timestamp'):
                end_time = datetime.fromisoformat(config['timer_end_timestamp'])
                now = datetime.now()
                
                if now >= end_time:
                    print("SERVICE: Timer expired! Showing overlay...")
                    show_overlay()
                    
                    config['is_timer_active'] = False
                    config['timer_end_timestamp'] = None
                    
                    for path in [CONFIG_FILE, ALT_CONFIG_FILE]:
                        try:
                            with open(path, 'w') as f:
                                json.dump(config, f)
                            break
                        except:
                            pass
                    
                    while True:
                        time.sleep(60)
                else:
                    remaining = (end_time - now).total_seconds()
                    print(f"SERVICE: Timer active, {int(remaining)} seconds remaining")
            
            time.sleep(5)
            
        except Exception as e:
            print(f"SERVICE ERROR: {e}")
            time.sleep(5)


if __name__ == '__main__':
    main()
