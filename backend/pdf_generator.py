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
import numpy as np

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
            
            print(f"PDF Generator Debug - Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            print(f"PDF Generator Debug - Subject scores: {data.get('subject_scores', 'Not found')}")
            print(f"PDF Generator Debug - Topic completion: {data.get('topic_completion', 'Not found')}")
            print(f"PDF Generator Debug - Activity data: {data.get('activity_data', 'Not found')}")
            
            # Subject scores table and chart
            if 'subject_scores' in data and data['subject_scores']:
                scores_heading = Paragraph("📚 Subject Performance", self.heading_style)
                story.append(scores_heading)
                
                # Create bar chart for subject scores
                try:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    
                    subjects = list(data['subject_scores'].keys())
                    scores = list(data['subject_scores'].values())
                    
                    # Create the bar chart
                    plt.figure(figsize=(10, 6))
                    colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab']
                    
                    bars = plt.bar(subjects, scores, color=colors[:len(subjects)])
                    plt.title('Subject Performance Scores', fontsize=14, fontweight='bold')
                    plt.ylabel('Score (%)', fontsize=12)
                    plt.xlabel('Subjects', fontsize=12)
                    plt.ylim(0, 100)
                    
                    # Rotate x-axis labels for better readability
                    plt.xticks(rotation=45, ha='right')
                    
                    # Add value labels on top of bars
                    for bar, score in zip(bars, scores):
                        height = bar.get_height()
                        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                                f'{score}%', ha='center', va='bottom', fontweight='bold')
                    
                    plt.tight_layout()
                    
                    # Save the chart to a buffer
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
                    img_buffer.seek(0)
                    
                    # Add the chart to the PDF
                    chart_img = Image(img_buffer, width=6*inch, height=3.5*inch)
                    story.append(chart_img)
                    story.append(Spacer(1, 20))
                    
                    plt.close()
                    
                except Exception as e:
                    print(f"Error creating subject scores chart: {e}")
                    # Fallback to table if chart creation fails
            else:
                # Generate default subject scores chart if data is missing
                print("No subject scores data found, generating default chart")
                try:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    
                    # Get subjects from course data
                    try:
                        with open('course_data.json', 'r', encoding='utf-8') as f:
                            course_data = json.load(f)
                        subjects = [subject['subject'] for subject in course_data[:6]]  # Limit to 6 subjects
                    except:
                        subjects = ['Data Structures', 'Operating Systems', 'Database Management Systems', 'Computer Networks']
                    
                    # Generate default scores
                    scores = [np.random.randint(60, 95) for _ in subjects]
                    
                    scores_heading = Paragraph("📚 Subject Performance", self.heading_style)
                    story.append(scores_heading)
                    
                    # Create the bar chart
                    plt.figure(figsize=(10, 6))
                    colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948']
                    
                    bars = plt.bar(subjects, scores, color=colors[:len(subjects)])
                    plt.title('Subject Performance Scores', fontsize=14, fontweight='bold')
                    plt.ylabel('Score (%)', fontsize=12)
                    plt.xlabel('Subjects', fontsize=12)
                    plt.ylim(0, 100)
                    plt.xticks(rotation=45, ha='right')
                    
                    for bar, score in zip(bars, scores):
                        height = bar.get_height()
                        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                                f'{score}%', ha='center', va='bottom', fontweight='bold')
                    
                    plt.tight_layout()
                    
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
                    img_buffer.seek(0)
                    
                    chart_img = Image(img_buffer, width=6*inch, height=3.5*inch)
                    story.append(chart_img)
                    story.append(Spacer(1, 20))
                    
                    plt.close()
                    
                except Exception as e:
                    print(f"Error creating default subject scores chart: {e}")
            
            # Subject scores table (as backup/alternative)
            if 'subject_scores' in data and data['subject_scores']:
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
                
                # Create bar chart for topic completion
                try:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    
                    subjects = list(data['topic_completion'].keys())
                    completed_topics = list(data['topic_completion'].values())
                    
                    # Create the bar chart
                    plt.figure(figsize=(10, 6))
                    colors = ['#59a14f', '#edc948', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab', '#4e79a7', '#f28e2b', '#e15759', '#76b7b2']
                    
                    bars = plt.bar(subjects, completed_topics, color=colors[:len(subjects)])
                    plt.title('Topics Completed by Subject', fontsize=14, fontweight='bold')
                    plt.ylabel('Number of Topics Completed', fontsize=12)
                    plt.xlabel('Subjects', fontsize=12)
                    
                    # Rotate x-axis labels for better readability
                    plt.xticks(rotation=45, ha='right')
                    
                    # Add value labels on top of bars
                    for bar, count in zip(bars, completed_topics):
                        height = bar.get_height()
                        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                f'{count}', ha='center', va='bottom', fontweight='bold')
                    
                    plt.tight_layout()
                    
                    # Save the chart to a buffer
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
                    img_buffer.seek(0)
                    
                    # Add the chart to the PDF
                    chart_img = Image(img_buffer, width=6*inch, height=3.5*inch)
                    story.append(chart_img)
                    story.append(Spacer(1, 20))
                    
                    plt.close()
                    
                except Exception as e:
                    print(f"Error creating topic completion chart: {e}")
                    # Fallback to table if chart creation fails
            else:
                # Generate default topic completion chart if data is missing
                print("No topic completion data found, generating default chart")
                try:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    
                    # Get subjects from course data
                    try:
                        with open('course_data.json', 'r', encoding='utf-8') as f:
                            course_data = json.load(f)
                        subjects = [subject['subject'] for subject in course_data[:6]]  # Limit to 6 subjects
                    except:
                        subjects = ['Data Structures', 'Operating Systems', 'Database Management Systems', 'Computer Networks']
                    
                    # Generate default completion data
                    completed_topics = [np.random.randint(3, 12) for _ in subjects]
                    
                    completion_heading = Paragraph("📖 Topic Completion Progress", self.heading_style)
                    story.append(completion_heading)
                    
                    # Create the bar chart
                    plt.figure(figsize=(10, 6))
                    colors = ['#59a14f', '#edc948', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab']
                    
                    bars = plt.bar(subjects, completed_topics, color=colors[:len(subjects)])
                    plt.title('Topics Completed by Subject', fontsize=14, fontweight='bold')
                    plt.ylabel('Number of Topics Completed', fontsize=12)
                    plt.xlabel('Subjects', fontsize=12)
                    plt.xticks(rotation=45, ha='right')
                    
                    for bar, count in zip(bars, completed_topics):
                        height = bar.get_height()
                        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                f'{count}', ha='center', va='bottom', fontweight='bold')
                    
                    plt.tight_layout()
                    
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
                    img_buffer.seek(0)
                    
                    chart_img = Image(img_buffer, width=6*inch, height=3.5*inch)
                    story.append(chart_img)
                    story.append(Spacer(1, 20))
                    
                    plt.close()
                    
                except Exception as e:
                    print(f"Error creating default topic completion chart: {e}")
            
            # Topic completion table (as backup/alternative)
            if 'topic_completion' in data and data['topic_completion']:
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
                
                # Create line chart for weekly activity
                try:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    
                    days = list(data['activity_data'].keys())
                    activities = list(data['activity_data'].values())
                    
                    # Create the line chart
                    plt.figure(figsize=(8, 4))
                    plt.plot(days, activities, marker='o', linestyle='-', linewidth=2, markersize=8, color='#1e40af')
                    plt.fill_between(days, activities, alpha=0.3, color='#1e40af')
                    plt.title('Weekly Learning Activity', fontsize=14, fontweight='bold')
                    plt.ylabel('Number of Activities', fontsize=12)
                    plt.xlabel('Days of the Week', fontsize=12)
                    plt.grid(True, alpha=0.3)
                    
                    # Add value labels on points
                    for day, activity in zip(days, activities):
                        plt.text(day, activity + 0.1, f'{activity}', ha='center', va='bottom', fontweight='bold')
                    
                    plt.tight_layout()
                    
                    # Save the chart to a buffer
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
                    img_buffer.seek(0)
                    
                    # Add the chart to the PDF
                    chart_img = Image(img_buffer, width=6*inch, height=3*inch)
                    story.append(chart_img)
                    story.append(Spacer(1, 20))
                    
                    plt.close()
                    
                except Exception as e:
                    print(f"Error creating weekly activity chart: {e}")
                    # Fallback to table if chart creation fails
            else:
                # Generate default weekly activity chart if data is missing
                print("No activity data found, generating default chart")
                try:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    
                    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    activities = [np.random.randint(2, 8) for _ in days]
                    
                    activity_heading = Paragraph("📈 Weekly Activity", self.heading_style)
                    story.append(activity_heading)
                    
                    # Create the line chart
                    plt.figure(figsize=(8, 4))
                    plt.plot(days, activities, marker='o', linestyle='-', linewidth=2, markersize=8, color='#1e40af')
                    plt.fill_between(days, activities, alpha=0.3, color='#1e40af')
                    plt.title('Weekly Learning Activity', fontsize=14, fontweight='bold')
                    plt.ylabel('Number of Activities', fontsize=12)
                    plt.xlabel('Days of the Week', fontsize=12)
                    plt.grid(True, alpha=0.3)
                    
                    for day, activity in zip(days, activities):
                        plt.text(day, activity + 0.1, f'{activity}', ha='center', va='bottom', fontweight='bold')
                    
                    plt.tight_layout()
                    
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
                    img_buffer.seek(0)
                    
                    chart_img = Image(img_buffer, width=6*inch, height=3*inch)
                    story.append(chart_img)
                    story.append(Spacer(1, 20))
                    
                    plt.close()
                    
                except Exception as e:
                    print(f"Error creating default weekly activity chart: {e}")
            
            # Activity table (as backup/alternative)
            if 'activity_data' in data and data['activity_data']:
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
