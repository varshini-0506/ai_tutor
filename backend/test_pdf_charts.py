#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_generator import PDFReportGenerator
import json

def test_pdf_generation():
    """Test PDF generation with charts"""
    
    # Create test data
    test_data = {
        "subject_scores": {
            "Data Structures": 85,
            "Operating Systems": 78,
            "Database Management Systems": 92,
            "Computer Networks": 88
        },
        "topic_completion": {
            "Data Structures": 8,
            "Operating Systems": 6,
            "Database Management Systems": 10,
            "Computer Networks": 7
        },
        "activity_data": {
            "Mon": 5,
            "Tue": 3,
            "Wed": 7,
            "Thu": 4,
            "Fri": 6,
            "Sat": 2,
            "Sun": 1
        }
    }
    
    # Initialize PDF generator
    pdf_gen = PDFReportGenerator()
    
    # Generate test PDF
    output_path = "test_report_with_charts.pdf"
    
    try:
        pdf_gen.generate_report_pdf("Test Student", test_data, output_path, charts=None, remarks="Test report")
        print(f"✅ PDF generated successfully: {output_path}")
        print("📊 Charts should be included in the PDF")
        return True
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing PDF generation with charts...")
    success = test_pdf_generation()
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!") 