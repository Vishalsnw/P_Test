# Calculator App

## Overview
A Python calculator application built with Kivy framework. This app can run on desktop and be packaged as an Android APK using Buildozer.

## Project Structure
- `main.py` - Main calculator application with Kivy GUI
- `buildozer.spec` - Configuration for building Android APK
- `.github/workflows/build-apk.yml` - GitHub Actions workflow for automated APK builds

## Running the App
The app runs as a Kivy desktop application in the development environment. 

## Building Android APK
To build an APK, you have two options:

### Option 1: GitHub Actions (Recommended)
Push to GitHub and the workflow will automatically build the APK. Download it from the Actions artifacts.

### Option 2: Local Build (Linux/WSL required)
```bash
pip install buildozer
buildozer android debug
```
The APK will be in the `bin/` directory.

## Features
- Basic arithmetic operations (+, -, *, /)
- Parentheses support
- Clear (C) and Delete (DEL) buttons
- Clean, modern UI design
- Portrait orientation optimized for mobile

## Dependencies
- Python 3.11
- Kivy 2.3.1

## Recent Changes
- December 10, 2025: Initial project setup with calculator app and APK build configuration
