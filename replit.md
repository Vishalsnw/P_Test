# Screen Guardian - Advanced Parental Control App

## Overview
A feature-rich Python-based Android parental control app that limits children's screen time. Includes multiple overlay designs, usage statistics, scheduling, profiles, and more.

## Project Structure
```
├── main.py                  # Main Kivy application with all features
├── buildozer.spec           # Android APK build configuration
├── requirements.txt         # Python dependencies
├── parental_config.json     # App configuration (auto-generated)
├── usage_stats.json         # Usage statistics (auto-generated)
├── res/xml/device_admin.xml # Android Device Admin policies
├── java/                    # Java source for Device Admin
└── README.md                # User instructions
```

## Technology Stack
- **Python 3.11** - Main programming language
- **Kivy** - Cross-platform UI framework with custom components
- **Buildozer** - Android APK build tool
- **Pyjnius** - Python-Java bridge for Android APIs

## Key Features

### Timer & Control
1. **Time Presets** - Quick buttons for 15min, 30min, 1hr, 2hr
2. **Custom Timer** - Slider for 1-120 minutes
3. **5-Minute Warning** - Configurable alert before time expires
4. **Break Reminders** - Periodic reminders during screen time
5. **Extension Requests** - Child can request more time (parent approves)

### Overlay Screens (6 Designs)
- **Battery Drained** - Low battery warning with 0%
- **System Update** - Security patches installing
- **Device Overheating** - Temperature warning (48°C)
- **Storage Full** - 99.9% storage used
- **Network Error** - Connection lost/offline
- **Maintenance Mode** - System optimization in progress

### Profiles & Scheduling
- **Multiple Child Profiles** - Different settings per child
- **Weekly Schedule** - Set daily limits for each day
- **Profile Switching** - Easy switch between profiles

### Statistics
- **Daily Usage Tracking** - Minutes used today
- **Weekly Charts** - Last 7 days with visual bars
- **Usage History** - Stored for 30 days

### Settings
- **Sound Effects** - Toggle warning sounds
- **Dark/Light Mode** - Theme toggle
- **PIN Recovery** - Secret question to recover PIN
- **Custom Overlay Message** - Parent-defined message
- **Configurable Warning Time** - 1-15 minutes before end

## UI Components
- **GradientBackground** - Smooth color gradients
- **StyledButton** - Rounded, colored buttons
- **CircularProgress** - Animated countdown ring
- **AnimatedProgressBar** - Overlay loading bars
- **PulsingDot** - Status indicator
- **StatBar** - Usage statistics bars
- **Tabbed Interface** - Timer, Schedule, Profiles, Stats, Settings

## How It Works
1. Parent logs in with PIN (default: 1234)
2. Navigate tabs to configure timer, schedule, profiles
3. Set time limit using presets or slider
4. Select overlay style (or Random)
5. Start timer and give device to child
6. 5-minute warning appears before time ends
7. When timer expires, convincing overlay blocks screen
8. Child can request extension (parent approves via PIN)
9. Parent unlocks with PIN

## Running on Desktop
```bash
python main.py
```

## Building APK
```bash
pip install buildozer
buildozer android debug
```

## Recent Changes
- 2025-12-13: Added all advanced features (presets, scheduling, profiles, stats, settings, extensions, warnings, themes)
- 2025-12-13: Complete UI redesign with professional styling
- 2025-12-12: Timer-based approach implemented
- 2025-12-11: Initial project setup

## User Preferences
- Professional, attractive UI design
- Multiple convincing overlay screens
- Comprehensive parental control features
