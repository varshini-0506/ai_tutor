import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pdf_generator import PDFReportGenerator
    print("✅ PDF generator imported successfully")
    
    # Create test data
    test_data = {
        "subject_scores": {
            "Data Structures": 85,
            "Operating Systems": 78
        },
        "topic_completion": {
            "Data Structures": 8,
            "Operating Systems": 6
        },
        "activity_data": {
            "Mon": 5,
            "Tue": 3,
            "Wed": 7
        }
    }
    
    # Test PDF generation
    pdf_gen = PDFReportGenerator()
    result = pdf_gen.generate_report_pdf("Test Student", test_data, "test_output.pdf")
    print(f"✅ PDF generated: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 