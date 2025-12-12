# Screen Time Limiter - Parental Control App

## Overview
A Python-based Android parental control app that limits children's screen time. When the timer expires, it displays a full-screen "battery drained" overlay that appears over any app currently in the foreground.

## Project Structure
```
├── main.py                  # Main Kivy application
├── buildozer.spec           # Android APK build configuration
├── requirements.txt         # Python dependencies
├── res/xml/device_admin.xml # Android Device Admin policies
├── java/                    # Java source for Device Admin
└── README.md                # User instructions
```

## Technology Stack
- **Python 3.11** - Main programming language
- **Kivy** - Cross-platform UI framework
- **Buildozer** - Android APK build tool
- **Pyjnius** - Python-Java bridge for Android APIs

## Key Features
1. Parent PIN protection (default: 1234)
2. Configurable timer (1-120 minutes)
3. Full-screen "battery drained" overlay when timer expires
4. Overlay appears over any app in foreground
5. PIN-protected unlock to dismiss overlay

## How It Works
1. Parent logs in with PIN
2. Sets desired time limit (e.g., 5 minutes)
3. Starts timer and gives device to child
4. When timer expires, "Battery Drained" overlay covers the entire screen
5. Only parent with PIN can dismiss the overlay

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
- 2025-12-12: Simplified to timer-based approach (overlay appears after set time)
- 2025-12-11: Initial project setup with Kivy application

## User Preferences
- Simple timer-based approach preferred over YouTube usage monitoring
