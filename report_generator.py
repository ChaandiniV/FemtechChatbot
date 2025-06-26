import io
import json
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.colors import HexColor

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the report"""
        
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Risk level styles
        self.styles.add(ParagraphStyle(
            name='HighRisk',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.red,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='MediumRisk',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.orange,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='LowRisk',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.green,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.darkblue
        ))
    
    def generate_pdf_report(self, report_data: Dict[str, Any]) -> bytes:
        """Generate PDF report from assessment data"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Build report content
        story = []
        
        # Title
        title_text = "Pregnancy Risk Assessment Report" if report_data['language'] == 'en' else "تقرير تقييم مخاطر الحمل"
        title = Paragraph(title_text, self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report metadata
        timestamp = datetime.fromisoformat(report_data['timestamp'])
        metadata_text = f"Generated on: {timestamp.strftime('%B %d, %Y at %I:%M %p')}" if report_data['language'] == 'en' else f"تم إنشاؤه في: {timestamp.strftime('%d %B %Y في %I:%M %p')}"
        metadata = Paragraph(metadata_text, self.styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Risk Assessment Summary
        risk_assessment = report_data['risk_assessment']
        
        # Risk level section
        risk_section_title = "Risk Assessment Summary" if report_data['language'] == 'en' else "ملخص تقييم المخاطر"
        story.append(Paragraph(risk_section_title, self.styles['SectionHeader']))
        
        # Risk level with appropriate styling
        risk_level = risk_assessment['risk_level']
        risk_style_map = {
            'High': 'HighRisk',
            'Medium': 'MediumRisk', 
            'Low': 'LowRisk'
        }
        
        risk_level_text = f"Risk Level: {risk_level}" if report_data['language'] == 'en' else f"مستوى الخطورة: {risk_level}"
        risk_level_para = Paragraph(risk_level_text, self.styles[risk_style_map[risk_level]])
        story.append(risk_level_para)
        story.append(Spacer(1, 12))
        
        # Explanation
        explanation_title = "Explanation:" if report_data['language'] == 'en' else "التفسير:"
        story.append(Paragraph(explanation_title, self.styles['Heading3']))
        story.append(Paragraph(risk_assessment['explanation'], self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Recommendations
        recommendations_title = "Recommendations:" if report_data['language'] == 'en' else "التوصيات:"
        story.append(Paragraph(recommendations_title, self.styles['Heading3']))
        story.append(Paragraph(risk_assessment['recommendations'], self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Urgent care warning if needed
        if risk_assessment.get('urgent_care_needed', False):
            urgent_text = "⚠️ URGENT: This assessment indicates you should seek immediate medical attention." if report_data['language'] == 'en' else "⚠️ عاجل: يشير هذا التقييم إلى ضرورة طلب العناية الطبية الفورية."
            urgent_para = Paragraph(urgent_text, self.styles['HighRisk'])
            story.append(urgent_para)
            story.append(Spacer(1, 20))
        
        # Questions and Responses section
        qa_section_title = "Assessment Questions and Responses" if report_data['language'] == 'en' else "أسئلة التقييم والإجابات"
        story.append(Paragraph(qa_section_title, self.styles['SectionHeader']))
        
        # Create Q&A table
        qa_data = []
        for i, (question, response) in enumerate(zip(report_data['questions'], report_data['responses'])):
            qa_data.append([f"Q{i+1}:", question])
            qa_data.append(["A:", response])
            qa_data.append(["", ""])  # Empty row for spacing
        
        if qa_data:
            qa_table = Table(qa_data, colWidths=[1*inch, 5*inch])
            qa_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(qa_table)
        
        story.append(Spacer(1, 30))
        
        # Disclaimer
        disclaimer_title = "Important Disclaimer:" if report_data['language'] == 'en' else "إخلاء مسؤولية مهم:"
        story.append(Paragraph(disclaimer_title, self.styles['Heading3']))
        
        disclaimer_text = """This assessment is for informational purposes only and should not replace professional medical advice. 
        Always consult with your healthcare provider for proper medical evaluation and treatment.""" if report_data['language'] == 'en' else """هذا التقييم لأغراض إعلامية فقط ولا يجب أن يحل محل المشورة الطبية المهنية.
        استشيري دائماً مقدم الرعاية الصحية للحصول على تقييم وعلاج طبي مناسب."""
        
        story.append(Paragraph(disclaimer_text, self.styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = "Generated by GraviLog Smart Risk Analysis Agent" if report_data['language'] == 'en' else "تم إنشاؤه بواسطة وكيل تحليل المخاطر الذكي GraviLog"
        footer = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        buffer.seek(0)
        pdf_data = buffer.read()
        buffer.close()
        
        return pdf_data
    
    def generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """Generate JSON report for API consumption"""
        
        json_report = {
            'report_id': f"risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': report_data['timestamp'],
            'language': report_data['language'],
            'assessment': {
                'risk_level': report_data['risk_assessment']['risk_level'],
                'explanation': report_data['risk_assessment']['explanation'],
                'recommendations': report_data['risk_assessment']['recommendations'],
                'urgent_care_needed': report_data['risk_assessment'].get('urgent_care_needed', False)
            },
            'questions_and_responses': [
                {
                    'question': q,
                    'response': r
                }
                for q, r in zip(report_data['questions'], report_data['responses'])
            ],
            'metadata': {
                'total_questions': len(report_data['questions']),
                'assessment_duration': 'N/A',  # Could be calculated if timestamps were tracked
                'system_version': '1.0'
            }
        }
        
        return json.dumps(json_report, indent=2, ensure_ascii=False)
