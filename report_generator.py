import io
import json
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# Removed old translator import

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the report"""
        
        # Try to register Arabic font (fallback if not available)
        try:
            # Register Arabic font if available
            pdfmetrics.registerFont(TTFont('Arabic', 'NotoSansArabic-Regular.ttf'))
            arabic_font = 'Arabic'
        except:
            # Fallback to Helvetica which supports Unicode
            arabic_font = 'Helvetica'
        
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName=arabic_font
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
        """Generate PDF report from assessment data - Always in English for medical professionals"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Build report content
        story = []
        
        # Title - Always in English for EMR
        title_text = "Electronic Medical Record - Pregnancy Risk Assessment"
        
        # Add note if original was in Arabic
        if report_data.get('original_language') == 'ar':
            title_text += "\n(Translated from Arabic for Medical Documentation)"
        
        title = Paragraph(title_text, self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report metadata - Always in English
        timestamp = datetime.fromisoformat(report_data['timestamp'])
        metadata_text = f"Generated on: {timestamp.strftime('%B %d, %Y at %I:%M %p')}"
        metadata = Paragraph(metadata_text, self.styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Patient Information Section - Always in English
        patient_info_title = "Patient Information"
        story.append(Paragraph(patient_info_title, self.styles['SectionHeader']))
        
        patient_info = report_data.get('patient_info', {})
        patient_details = [
            f"Name: {patient_info.get('name', 'N/A')}",
            f"Age: {patient_info.get('age', 'N/A')} years",
            f"Gestational Age: {patient_info.get('pregnancy_week', 'N/A')} weeks"
        ]
        
        for detail in patient_details:
            story.append(Paragraph(detail, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Risk Assessment Summary
        risk_assessment = report_data['risk_assessment']
        
        # Risk level section
        risk_section_title = "Risk Assessment Summary"
        story.append(Paragraph(risk_section_title, self.styles['SectionHeader']))
        
        # Risk level with appropriate styling
        risk_level = risk_assessment['risk_level']
        risk_style_map = {
            'High': 'HighRisk',
            'Medium': 'MediumRisk', 
            'Low': 'LowRisk'
        }
        
        risk_level_text = f"Risk Level: {risk_level}"
        risk_level_para = Paragraph(risk_level_text, self.styles[risk_style_map[risk_level]])
        story.append(risk_level_para)
        story.append(Spacer(1, 12))
        
        # Explanation
        explanation_title = "Explanation:"
        story.append(Paragraph(explanation_title, self.styles['Heading3']))
        
        explanation_text = risk_assessment['explanation']
        story.append(Paragraph(explanation_text, self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Pregnancy Week Analysis
        if 'pregnancy_week_risks' in risk_assessment:
            week_analysis_title = "Pregnancy Week Analysis"
            story.append(Paragraph(week_analysis_title, self.styles['SectionHeader']))
            
            pregnancy_week = risk_assessment.get('pregnancy_week', 'N/A')
            week_text = f"Current Gestational Age: {pregnancy_week} weeks"
            story.append(Paragraph(week_text, self.styles['Normal']))
            
            for risk in risk_assessment['pregnancy_week_risks']:
                story.append(Paragraph(f"• {risk}", self.styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Medical Assessment Summary
        assessment_title = "Medical Assessment Summary"
        story.append(Paragraph(assessment_title, self.styles['SectionHeader']))
        
        # Patient responses
        responses_title = "Patient Responses:"
        story.append(Paragraph(responses_title, self.styles['Heading3']))
        
        questions = report_data.get('questions', [])
        responses = report_data.get('responses', [])
        
        for i, (question, response) in enumerate(zip(questions, responses), 1):
            if i > 1:  # Skip patient info context
                q_text = f"Q{i-1}: {question}"
                story.append(Paragraph(q_text, self.styles['Normal']))
                a_text = f"A{i-1}: {response}"
                story.append(Paragraph(a_text, self.styles['Normal']))
                story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 15))
        
        # Recommendations
        recommendations_title = "Clinical Recommendations:"
        story.append(Paragraph(recommendations_title, self.styles['Heading3']))
        
        recommendations_text = risk_assessment['recommendations']
        story.append(Paragraph(recommendations_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Next Steps
        next_steps_title = "Next Steps:"
        story.append(Paragraph(next_steps_title, self.styles['Heading3']))
        
        next_steps = self._get_next_steps(risk_assessment, 'en')  # Always get English next steps
        for step in next_steps:
            story.append(Paragraph(f"• {step}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Urgent care warning if needed
        if risk_assessment.get('urgent_care_needed', False):
            urgent_text = "⚠️ URGENT: This assessment indicates immediate medical attention is required."
            urgent_para = Paragraph(urgent_text, self.styles['HighRisk'])
            story.append(urgent_para)
            story.append(Spacer(1, 20))
        
        # Questions and Responses section
        qa_section_title = "Assessment Questions and Responses"
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
        disclaimer_title = "Important Disclaimer:"
        story.append(Paragraph(disclaimer_title, self.styles['Heading3']))
        
        disclaimer_text = """This assessment is for informational purposes only and should not replace professional medical advice. 
        Always consult with your healthcare provider for proper medical evaluation and treatment."""
        
        story.append(Paragraph(disclaimer_text, self.styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = "Generated by GraviLog Smart Risk Analysis Agent"
        footer = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        buffer.seek(0)
        pdf_data = buffer.read()
        buffer.close()
        
        return pdf_data
    
    def _get_next_steps(self, risk_assessment: Dict[str, Any], language: str) -> List[str]:
        """Generate next steps based on risk assessment - Always in English for EMR"""
        risk_level = risk_assessment.get('risk_level', 'Low')
        pregnancy_week = risk_assessment.get('pregnancy_week', 0)
        
        if risk_level == 'High':
            steps = [
                "Seek immediate medical attention - contact your doctor or go to emergency room",
                "Monitor symptoms closely",
                "Avoid strenuous physical activity until medical evaluation"
            ]
        elif risk_level == 'Medium':
            steps = [
                "Schedule appointment with OB/GYN within 24-48 hours",
                "Monitor symptoms and record any changes",
                "Rest and avoid stress"
            ]
        else:
            steps = [
                "Continue regular prenatal care appointments",
                "Maintain healthy lifestyle",
                "Monitor fetal movement regularly"
            ]
        
        # Add pregnancy week-specific steps
        if pregnancy_week > 0:
            if pregnancy_week <= 12:
                steps.append("Continue taking folic acid daily")
            elif pregnancy_week <= 28:
                steps.append("Complete gestational diabetes screening")
            else:
                steps.append("Watch for signs of preterm labor")
        
        return steps
    
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
