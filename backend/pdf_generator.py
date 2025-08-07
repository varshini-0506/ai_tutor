from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json
import os
from datetime import datetime
import base64
import io

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6
        )
    
    def generate_report_pdf(self, student_name, report_data, output_path, charts=None, remarks=None):
        """Generate a complete PDF report with embedded chart images"""
        print(f"Starting PDF generation for {student_name}")
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph(f"📈 Progress Report - {student_name}", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report date
        date_para = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.normal_style)
        story.append(date_para)
        story.append(Spacer(1, 30))
        
        # Summary section
        summary_heading = Paragraph("📊 Learning Summary", self.heading_style)
        story.append(summary_heading)
        
        # Subject Mastery Chart
        if charts and charts.get('bar'):
            story.append(Paragraph("Subject Mastery", self.styles['h3']))
            bar_img_data = base64.b64decode(charts['bar'].split(',')[1])
            bar_img = Image(io.BytesIO(bar_img_data), width=5*inch, height=2.5*inch)
            story.append(bar_img)
            story.append(Spacer(1, 20))

        # Topic Completion Chart
        if charts and charts.get('doughnut'):
            story.append(Paragraph("Topic Completion", self.styles['h3']))
            doughnut_img_data = base64.b64decode(charts['doughnut'].split(',')[1])
            doughnut_img = Image(io.BytesIO(doughnut_img_data), width=3*inch, height=3*inch)
            story.append(doughnut_img)
            story.append(Spacer(1, 20))

        # Weekly Activity Chart
        if charts and charts.get('line'):
            story.append(Paragraph("Weekly Activity", self.styles['h3']))
            line_img_data = base64.b64decode(charts['line'].split(',')[1])
            line_img = Image(io.BytesIO(line_img_data), width=5*inch, height=2.5*inch)
            story.append(line_img)
            story.append(Spacer(1, 20))
        
        # Extract data from report_data
        try:
            # Handle both cases: report_data could be a dict or JSON string
            if isinstance(report_data, str):
                data = json.loads(report_data)
            else:
                data = report_data
            
            # Subject scores table
            if 'subject_scores' in data and data['subject_scores']:
                scores_heading = Paragraph("📚 Subject Performance", self.heading_style)
                story.append(scores_heading)
                
                # Subject scores table
                table_data = [['Subject', 'Score (%)']]
                for subject, score in data['subject_scores'].items():
                    table_data.append([subject, str(score)])
                
                subject_table = Table(table_data, colWidths=[3*inch, 1*inch])
                subject_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(subject_table)
                story.append(Spacer(1, 20))
            
            # Topic completion section
            if 'topic_completion' in data and data['topic_completion']:
                completion_heading = Paragraph("📖 Topic Completion Progress", self.heading_style)
                story.append(completion_heading)
                
                # Topic completion table
                table_data = [['Subject', 'Topics Completed']]
                for subject, completed_count in data['topic_completion'].items():
                    table_data.append([subject, str(completed_count)])
                
                completion_table = Table(table_data, colWidths=[3*inch, 1*inch])
                completion_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(completion_table)
                story.append(Spacer(1, 20))
            
            # Activity section
            if 'activity_data' in data and data['activity_data']:
                activity_heading = Paragraph("📈 Weekly Activity", self.heading_style)
                story.append(activity_heading)
                
                # Activity table
                table_data = [['Day', 'Activities']]
                for day, count in data['activity_data'].items():
                    table_data.append([day, str(count)])
                
                activity_table = Table(table_data, colWidths=[1*inch, 1*inch])
                activity_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(activity_table)
                story.append(Spacer(1, 20))
            
            # Overall statistics
            if 'total_views' in data:
                stats_heading = Paragraph("📊 Overall Statistics", self.heading_style)
                story.append(stats_heading)
                
                stats_text = f"Total learning sessions: {data['total_views']}"
                stats_para = Paragraph(stats_text, self.normal_style)
                story.append(stats_para)
                story.append(Spacer(1, 20))
            
        except Exception as e:
            error_para = Paragraph(f"Error processing report data: {str(e)}", self.normal_style)
            story.append(error_para)
        
        # Teacher Remarks Section
        if remarks:
            remarks_heading = Paragraph("📝 Teacher's Remarks", self.heading_style)
            story.append(remarks_heading)
            
            remarks_para = Paragraph(remarks, self.normal_style)
            story.append(remarks_para)
            story.append(Spacer(1, 20))
        
        # Conclusion
        conclusion_heading = Paragraph("🎯 Recommendations", self.heading_style)
        story.append(conclusion_heading)
        
        conclusion_text = """
        • Continue practicing subjects with lower scores
        • Complete remaining topics in each subject
        • Maintain consistent daily learning activity
        • Review completed topics regularly for retention
        """
        conclusion_para = Paragraph(conclusion_text, self.normal_style)
        story.append(conclusion_para)
        
        # Build PDF
        print(f"Building PDF for {student_name}")
        doc.build(story)
        print(f"PDF generated successfully: {output_path}")
        return output_path
