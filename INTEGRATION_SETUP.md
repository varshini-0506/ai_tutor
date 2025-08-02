# AI Tutor Voice & Image Integration Setup Guide

## Overview
This guide covers the setup and troubleshooting of voice recognition and image-to-text (OCR) functionality in the AI Tutor application.

## Voice Integration

### How It Works
- Uses the Web Speech API (SpeechRecognition) for browser-based voice recognition
- Converts speech to text in real-time
- Supports multiple languages (currently set to English-US)

### Browser Compatibility
- ✅ Chrome/Chromium (recommended)
- ✅ Edge
- ✅ Safari (limited support)
- ❌ Firefox (not supported)

### Setup Requirements
1. **HTTPS Required**: Speech recognition requires a secure context (HTTPS or localhost)
2. **Microphone Permission**: Users must grant microphone access
3. **Modern Browser**: Chrome 25+ or equivalent

### Troubleshooting Voice Issues

#### "Speech recognition error: aborted"
**Causes:**
- Multiple recognition instances running simultaneously
- Browser security restrictions
- Microphone permission denied

**Solutions:**
1. Refresh the page and try again
2. Check microphone permissions in browser settings
3. Ensure only one voice session is active
4. Use Chrome browser for best compatibility

#### "Voice not supported"
**Causes:**
- Browser doesn't support Web Speech API
- Running on non-secure context

**Solutions:**
1. Use Chrome or Edge browser
2. Ensure you're on localhost or HTTPS
3. Update browser to latest version

#### No Audio Input Detected
**Causes:**
- Microphone not connected or disabled
- Wrong microphone selected
- System audio settings

**Solutions:**
1. Check microphone connection
2. Verify microphone is selected in browser settings
3. Test microphone in other applications
4. Check system audio settings

## Image-to-Text (OCR) Integration

### How It Works
- Uses Tesseract OCR engine via pytesseract
- Extracts text from uploaded images
- Provides educational analysis of extracted content
- Supports multiple image formats (PNG, JPG, JPEG, etc.)

### Setup Requirements

#### 1. Install Tesseract OCR
**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract

# Add to PATH: C:\Program Files\Tesseract-OCR
```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-eng  # English language pack
```

#### 2. Install Python Dependencies
```bash
cd backend
pip install pytesseract Pillow
```

#### 3. Verify Installation
```bash
python -c "import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())"
```

### Troubleshooting OCR Issues

#### "OCR library not available"
**Causes:**
- pytesseract not installed
- Tesseract not installed or not in PATH

**Solutions:**
1. Install pytesseract: `pip install pytesseract`
2. Install Tesseract OCR (see setup requirements)
3. Add Tesseract to system PATH
4. Restart your terminal/IDE

#### "Could not extract text from image"
**Causes:**
- Poor image quality
- Unsupported text format
- Image doesn't contain readable text
- OCR engine issues

**Solutions:**
1. Use high-resolution images (300+ DPI)
2. Ensure good lighting and contrast
3. Use clear, readable fonts
4. Avoid handwritten text (unless using specialized models)
5. Check image format (PNG, JPG supported)

#### "Tesseract not properly configured"
**Causes:**
- Tesseract not found in PATH
- Wrong Tesseract installation
- Permission issues

**Solutions:**
1. Verify Tesseract installation: `tesseract --version`
2. Add Tesseract to system PATH
3. Restart application after PATH changes
4. Check file permissions

## Testing Integration

### Run the Test Suite
```bash
python test_integration.py
```

This will test:
- ✅ OCR status and configuration
- ✅ Image analysis functionality
- ✅ Voice endpoint availability

### Manual Testing

#### Test Voice Integration
1. Open AI Tutor in Chrome
2. Click "Voice Input" button
3. Grant microphone permission
4. Speak clearly into microphone
5. Verify text appears in input field

#### Test Image Integration
1. Upload an image with clear text
2. Select "Image" action type
3. Submit the image
4. Verify OCR analysis appears

## Common Issues & Solutions

### Frontend Issues
- **CORS Errors**: Ensure backend is running on correct port
- **Network Errors**: Check if backend server is running
- **Permission Errors**: Grant microphone access in browser

### Backend Issues
- **Import Errors**: Install missing Python packages
- **Path Errors**: Ensure Tesseract is in system PATH
- **Port Conflicts**: Check if port 5000 is available

### Performance Issues
- **Slow OCR**: Use smaller images or reduce resolution
- **Voice Lag**: Check microphone quality and internet connection
- **Memory Issues**: Restart application periodically

## Development Notes

### Voice Recognition Configuration
- `continuous: false` - Prevents multiple sessions
- `interimResults: false` - Better stability
- `lang: 'en-US'` - English language support

### OCR Configuration
- Uses default Tesseract settings
- Supports multiple languages (configure in Tesseract)
- Processes images in memory (no file storage)

### Error Handling
- Comprehensive error logging
- User-friendly error messages
- Graceful degradation for unsupported features

## Support

If you encounter issues not covered in this guide:
1. Check browser console for error messages
2. Review backend server logs
3. Run the test suite for diagnostics
4. Verify all dependencies are installed correctly 