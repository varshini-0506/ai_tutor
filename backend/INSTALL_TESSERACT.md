# Installing Tesseract OCR on Windows

## **Option 1: Using Chocolatey (Recommended)**

If you have Chocolatey installed:
```bash
choco install tesseract
```

## **Option 2: Manual Installation**

### **Step 1: Download Tesseract**
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer:
   - For 64-bit: `tesseract-ocr-w64-setup-5.3.1.20230401.exe`
   - For 32-bit: `tesseract-ocr-w32-setup-5.3.1.20230401.exe`

### **Step 2: Install Tesseract**
1. Run the downloaded installer
2. **Important Settings:**
   - Install to: `C:\Program Files\Tesseract-OCR\`
   - ✅ Check "Add to PATH" during installation
   - ✅ Check "Add to system PATH for all users"

### **Step 3: Verify Installation**
1. Open Command Prompt
2. Run: `tesseract --version`
3. You should see version information

## **Option 3: Using Winget**
```bash
winget install UB-Mannheim.TesseractOCR
```

## **Troubleshooting**

### **If Tesseract is not found:**
1. **Check PATH:**
   - Open System Properties → Advanced → Environment Variables
   - Add `C:\Program Files\Tesseract-OCR\` to PATH

2. **Restart Command Prompt:**
   - Close and reopen Command Prompt
   - Try `tesseract --version` again

3. **Manual PATH Addition:**
   ```bash
   setx PATH "%PATH%;C:\Program Files\Tesseract-OCR\"
   ```

### **If you get permission errors:**
1. Run Command Prompt as Administrator
2. Try the installation again

### **Alternative Installation Path:**
If you can't install to Program Files, install to:
```
C:\tesseract\
```
Then add `C:\tesseract\` to your PATH.

## **Testing the Installation**

After installation, test with:
```bash
# Test basic functionality
tesseract --version

# Test with a sample image (if you have one)
tesseract image.png output.txt
```

## **Python Integration**

The application will automatically detect Tesseract in these locations:
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
- `tesseract` (if in PATH)

## **Language Packs**

By default, Tesseract includes English. For other languages:
1. Download language packs from: https://github.com/tesseract-ocr/tessdata
2. Place `.traineddata` files in: `C:\Program Files\Tesseract-OCR\tessdata\`

## **Common Issues**

### **"tesseract is not recognized"**
- Add Tesseract to PATH
- Restart Command Prompt
- Check installation path

### **"Access denied"**
- Run as Administrator
- Check antivirus software
- Try different installation path

### **"DLL not found"**
- Install Visual C++ Redistributable
- Reinstall Tesseract

## **Verification**

After installation, the application will show:
```
✅ Tesseract found at: C:\Program Files\Tesseract-OCR\tesseract.exe
```

If you see:
```
❌ Tesseract OCR not found. OCR features will be disabled.
```

Then follow the troubleshooting steps above. 