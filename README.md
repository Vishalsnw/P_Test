# YouTube Limiter - Parental Control App

A Python-based Android app that limits children's YouTube usage by showing a "battery drained" overlay screen when the time limit is reached.

## Features

- **Time Limits**: Set daily YouTube usage limits (10-180 minutes)
- **Battery Drained Overlay**: Shows a convincing "battery drained" screen over YouTube when limit is reached
- **Device Admin Protection**: Prevents children from uninstalling the app
- **Parent PIN Protection**: Only parents can access settings
- **Automatic Daily Reset**: Usage counter resets each day
- **Background Monitoring**: Monitors YouTube usage even when app is in background

## How It Works

1. Parent installs the app and grants all permissions
2. Parent sets a PIN and daily time limit
3. App monitors YouTube usage in the background
4. When limit is reached, a full-screen "battery drained" overlay appears
5. Child cannot easily dismiss the overlay or uninstall the app

## Required Permissions

The parent must grant these permissions for full functionality:

1. **Overlay Permission**: To show the "battery drained" screen over other apps
2. **Usage Access**: To detect when YouTube is running
3. **Device Admin**: To prevent uninstallation without PIN

## Building the APK

### Prerequisites

1. Linux/Mac computer (or use WSL on Windows)
2. Python 3.8+
3. Android SDK and NDK

### Build Steps

```bash
# Install buildozer
pip install buildozer

# Install dependencies
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3 \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good

# Install Java
sudo apt-get install -y openjdk-17-jdk

# Build the APK (first build takes 20-40 minutes)
buildozer android debug

# The APK will be in: bin/youtubelimiter-1.0.0-arm64-v8a-debug.apk
```

### Install on Android Device

1. Transfer the APK to the Android device
2. Enable "Install from Unknown Sources" in Settings > Security
3. Open the APK file and install
4. Open the app and grant all requested permissions
5. Set your parent PIN and time limits

## Default Settings

- **Default PIN**: 1234 (change this immediately!)
- **Default Daily Limit**: 60 minutes
- **Blocked Hours**: 9 PM - 7 AM (optional feature)

## Tips for Parents

1. **Change the default PIN immediately** after first launch
2. **Grant all permissions** when prompted - this is required for the app to work
3. **Enable Device Admin** to prevent your child from uninstalling the app
4. The app works best when the child doesn't know about it

## Troubleshooting

### App doesn't detect YouTube
- Make sure "Usage Access" permission is granted
- Go to Settings > Apps > Special access > Usage access > YouTube Limiter

### Overlay doesn't appear
- Make sure "Display over other apps" permission is granted
- Go to Settings > Apps > Special access > Display over other apps > YouTube Limiter

### Child can uninstall the app
- Make sure Device Admin is enabled
- Go to Settings > Security > Device admin apps > YouTube Limiter

## Technical Notes

- Built with Python and Kivy framework
- Uses Buildozer to create Android APK
- Uses pyjnius for Android API access
- Targets Android API 33 (Android 13)
- Minimum supported: Android 5.0 (API 21)

## License

This project is for personal/educational use only.
