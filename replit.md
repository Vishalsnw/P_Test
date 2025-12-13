# Screen Time Limiter - Parental Control App

## Overview
A Python-based Android parental control app that limits children's screen time. When the timer expires, it displays a full-screen overlay (with multiple convincing designs) that appears over any app currently in the foreground.

## Project Structure
```
├── main.py                  # Main Kivy application with professional UI
├── buildozer.spec           # Android APK build configuration
├── requirements.txt         # Python dependencies
├── res/xml/device_admin.xml # Android Device Admin policies
├── java/                    # Java source for Device Admin
└── README.md                # User instructions
```

## Technology Stack
- **Python 3.11** - Main programming language
- **Kivy** - Cross-platform UI framework with custom styled components
- **Buildozer** - Android APK build tool
- **Pyjnius** - Python-Java bridge for Android APIs

## Key Features
1. Parent PIN protection (default: 1234)
2. Configurable timer (1-120 minutes)
3. **6 Different Overlay Screens** with convincing designs:
   - Battery Drained - Low battery warning
   - System Update - Security patches installing
   - Device Overheating - Temperature warning
   - Storage Full - No space available
   - Network Error - Connection lost
   - Maintenance Mode - System optimization
4. Random or selectable overlay themes
5. PIN-protected unlock to dismiss overlay
6. Professional, polished UI design

## UI Components
- **GradientBackground** - Smooth color gradients
- **StyledButton** - Rounded, colored buttons
- **CircularProgress** - Animated countdown progress ring
- **PulsingDot** - Status indicator with animation

## How It Works
1. Parent logs in with PIN
2. Sets desired time limit (e.g., 5 minutes)
3. Optionally selects overlay style (or use Random)
4. Starts timer and gives device to child
5. When timer expires, selected overlay covers the entire screen
6. Only parent with PIN can dismiss the overlay

## Running on Desktop (Preview)
The app can run on desktop for testing, but Android-specific overlay features are simulated.

```bash
python main.py
```

## Building APK
Requires Linux/Mac with Android SDK:
```bash
pip install buildozer
buildozer android debug
```

## Android Permissions Required
- SYSTEM_ALERT_WINDOW - For displaying overlay over other apps

## Recent Changes
- 2025-12-13: Complete UI redesign with professional styling and 6 overlay screen themes
- 2025-12-12: Simplified to timer-based approach (overlay appears after set time)
- 2025-12-11: Initial project setup with Kivy application

## User Preferences
- Simple timer-based approach preferred over YouTube usage monitoring
- Professional, attractive UI design
- Multiple convincing overlay screens
