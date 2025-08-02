#!/usr/bin/env python3
"""
Test script for AI Tutor voice and image integration
"""

import requests
import base64
import json
import os

# Test configuration
BASE_URL = "http://127.0.0.1:5000"

def test_ocr_status():
    """Test if OCR is properly configured"""
    print("🔍 Testing OCR Status...")
    try:
        response = requests.get(f"{BASE_URL}/check-ocr")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OCR Status: {data['status']}")
            print(f"📝 Message: {data['message']}")
            if data.get('available'):
                print(f"🔧 Tesseract Version: {data.get('tesseract_version', 'Unknown')}")
            return data.get('available', False)
        else:
            print(f"❌ Failed to check OCR status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking OCR status: {e}")
        return False

def test_image_analysis():
    """Test image analysis functionality"""
    print("\n🖼️ Testing Image Analysis...")
    
    # Create a simple test image with text
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a test image with text
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        text = "Test OCR\nThis is a sample text\nfor testing purposes"
        draw.text((20, 20), text, fill='black', font=font)
        
        # Convert to base64
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Test the analyze-image endpoint
        response = requests.post(
            f"{BASE_URL}/analyze-image",
            json={
                "image": f"data:image/png;base64,{img_base64}",
                "analysis_type": "educational"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Image analysis successful")
            print(f"📊 Analysis length: {len(data.get('analysis', ''))} characters")
            return True
        else:
            print(f"❌ Image analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except ImportError:
        print("❌ PIL not available, skipping image test")
        return False
    except Exception as e:
        print(f"❌ Error testing image analysis: {e}")
        return False

def test_voice_endpoint():
    """Test voice-to-text endpoint"""
    print("\n🎤 Testing Voice-to-Text Endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/voice-to-text",
            json={"audio": "test_audio_data"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Voice endpoint responding")
            print(f"📝 Response: {data.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Voice endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing voice endpoint: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 AI Tutor Integration Test Suite")
    print("=" * 50)
    
    # Test OCR
    ocr_working = test_ocr_status()
    
    # Test image analysis
    image_working = test_image_analysis()
    
    # Test voice endpoint
    voice_working = test_voice_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"🔍 OCR Status: {'✅ Working' if ocr_working else '❌ Not Working'}")
    print(f"🖼️ Image Analysis: {'✅ Working' if image_working else '❌ Not Working'}")
    print(f"🎤 Voice Endpoint: {'✅ Working' if voice_working else '❌ Not Working'}")
    
    if not ocr_working:
        print("\n🔧 OCR Troubleshooting:")
        print("1. Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        print("2. Install pytesseract: pip install pytesseract")
        print("3. Ensure Tesseract is in your system PATH")
    
    if not image_working:
        print("\n🔧 Image Analysis Troubleshooting:")
        print("1. Check if PIL/Pillow is installed: pip install Pillow")
        print("2. Verify the analyze-image endpoint is accessible")
        print("3. Check server logs for detailed error messages")
    
    if not voice_working:
        print("\n🔧 Voice Troubleshooting:")
        print("1. Check if the voice-to-text endpoint is properly configured")
        print("2. Verify the server is running on the correct port")
        print("3. Check server logs for detailed error messages")

if __name__ == "__main__":
    main() 