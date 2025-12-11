# YouTube Limiter - Parental Control App

## Overview
A Python-based Android parental control app that limits children's YouTube usage. When the time limit is reached, it displays a full-screen "battery drained" overlay to discourage further use.

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
1. Parent PIN protection
2. Configurable daily time limits (10-180 minutes)
3. YouTube detection and monitoring
4. Full-screen "battery drained" overlay
5. Device Admin protection against uninstallation

## Running on Desktop (Preview)
The app can run on desktop for testing, but Android-specific features (overlay, usage detection, device admin) are simulated.

```bash
python main.py
```

## Building APK
Requires Linux/Mac with Android SDK:
```bash
pip install buildozer
buildozer android debug
```

## Recent Changes
- 2025-12-11: Initial project setup with Kivy application

## User Preferences
- None recorded yet
