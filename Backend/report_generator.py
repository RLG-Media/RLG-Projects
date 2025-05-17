"""
RLG Report Engine - Smart Analytics & Visualization Core
Version: 13.0.0
Features: AI-Enhanced Insights, Multi-Format Export, Localized Reporting
"""

import pandas as pd
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from models import Project, Sprint, Task, BacklogItem
from deepseek_api import DeepseekAPI
from config import get_config
import pytz
import matplotlib.pyplot as plt
import geoip2.database
import logging
from functools import lru_cache
import json
from flask_babel import gettext as _

logger = logging.getLogger('RLG.Reports')
config = get_config()
ai_engine = DeepseekAPI()

class ReportGenerator:
    """AI-driven reporting engine with Scrum-specific analytics"""
    
    def __init__(self):
        self.geo_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        self.styles = getSampleStyleSheet()
        self.formats = {
            'pdf': self._generate_pdf,
            'excel': self._generate_excel,
            'json': self._generate_json
        }

    def generate_project_report(self, project_id: int, report_type: str = 'executive', 
                               language: str = 'en', timezone: str = 'UTC') -> BytesIO:
        """Main report generation entry point"""
        try:
            project = self._get_project_data(project_id)
            localized_data = self._localize_data(project, language, timezone)
            ai_insights = ai_engine.analyze_project_data(project_id)
            
            buffer = BytesIO()
            report_format = report_type.split('_')[-1]
            self.formats[report_format](buffer, localized_data, ai_insights, report_type)
            
            self._save_report(project_id, buffer, report_type)
            return buffer
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise

    def _generate_pdf(self, buffer, data, insights, report_type):
        """Generate PDF reports with visualizations"""
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Header
        elements.append(Paragraph(_("Project Report"), self.styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Summary Section
        elements += self._pdf_summary_section(data, insights)
        
        # AI Insights
        elements += self._pdf_ai_section(insights)
        
        # Visualizations
        elements += self._pdf_visualizations(data)
        
        # Compliance Footer
        elements.append(self._pdf_compliance_footer())
        
        doc.build(elements)

    def _pdf_visualizations(self, data):
        """Generate report visualizations"""
        visuals = []
        
        # Burndown Chart
        burndown_img = self._create_burndown_chart(data['sprints'])
        visuals.append(Image(burndown_img, width=400, height=300))
        
        # Velocity Trend
        velocity_img = self._create_velocity_chart(data['velocity_history'])
        visuals.append(Image(velocity_img, width=400, height=300))
        
        return visuals

    def _generate_excel(self, buffer, data, insights, report_type):
        """Generate Excel reports with interactive elements"""
        with pd.ExcelWriter(buffer) as writer:
            # Raw Data Sheet
            pd.DataFrame(data['raw_metrics']).to_excel(writer, sheet_name='Metrics')
            
            # AI Insights Sheet
            insights_df = pd.DataFrame(insights['recommendations'])
            insights_df.to_excel(writer, sheet_name='AI Recommendations')
            
            # Charts Sheet
            self._excel_charts(writer, data)

    def _generate_json(self, buffer, data, insights, report_type):
        """Generate JSON report with embedded analytics"""
        report_data = {
            'metadata': data['metadata'],
            'metrics': data['processed_metrics'],
            'ai_insights': insights,
            'compliance_status': self._check_compliance(data)
        }
        buffer.write(json.dumps(report_data).encode())

    @lru_cache(maxsize=100)
    def _get_project_data(self, project_id: int) -> dict:
        """Retrieve and cache project data"""
        project = Project.query.get_or_404(project_id)
        return {
            'metadata': project.to_dict(),
            'sprints': [s.to_dict() for s in project.sprints],
            'backlog': [b.to_dict() for b in project.backlog],
            'team': self._get_team_data(project.team_id),
            'velocity_history': self._calculate_velocity_history(project_id)
        }

    def _localize_data(self, data: dict, language: str, timezone: str) -> dict:
        """Localize report content"""
        localized = {}
        tz = pytz.timezone(timezone)
        
        # Localize dates
        for sprint in data['sprints']:
            sprint['start_date'] = self._convert_timezone(sprint['start_date'], tz)
            sprint['end_date'] = self._convert_timezone(sprint['end_date'], tz)
        
        # Translate content
        localized['metadata'] = self._translate_content(data['metadata'], language)
        localized['metrics'] = self._localize_metrics(data['metrics'], language)
        
        return {**data, **localized}

    def _translate_content(self, content: dict, language: str) -> dict:
        """AI-powered content translation"""
        translated = {}
        for key, value in content.items():
            if isinstance(value, str):
                translated[key] = ai_engine.translate_text(value, language)
            else:
                translated[key] = value
        return translated

    def _create_burndown_chart(self, sprints: list) -> BytesIO:
        """Generate burndown visualization"""
        buffer = BytesIO()
        plt.figure()
        
        dates = []
        remaining = []
        for sprint in sprints:
            dates.append(sprint['start_date'])
            remaining.append(sprint['story_points_committed'])
            dates.append(sprint['end_date'])
            remaining.append(sprint['story_points_completed'])
            
        plt.plot(dates, remaining, marker='o')
        plt.title(_("Burndown Chart"))
        plt.savefig(buffer, format='png')
        plt.close()
        return buffer

    def _create_velocity_chart(self, velocity_data: list) -> BytesIO:
        """Generate velocity trend visualization"""
        buffer = BytesIO()
        plt.figure()
        
        sprints = [f"Sprint {i+1}" for i in range(len(velocity_data))]
        plt.bar(sprints, velocity_data)
        plt.title(_("Velocity Trend"))
        plt.savefig(buffer, format='png')
        plt.close()
        return buffer

    def _check_compliance(self, data: dict) -> dict:
        """Ensure report compliance with regulations"""
        return {
            'gdpr': ai_engine.check_gdpr_compliance(data),
            'ccpa': ai_engine.check_ccpa_compliance(data),
            'data_retention': self._validate_retention_policies(data)
        }

    def _save_report(self, project_id: int, buffer: BytesIO, report_type: str):
        """Store report in data lake"""
        path = f"{config.DATA_LAKE_PATH}/{project_id}/reports/{datetime.now().isoformat()}_{report_type}"
        with open(path, 'wb') as f:
            f.write(buffer.getvalue())

    # Additional utility methods
    def _calculate_velocity_history(self, project_id: int) -> list:
        """Calculate historical velocity data"""
        sprints = Sprint.query.filter_by(project_id=project_id).all()
        return [s.story_points_completed / s.duration_days for s in sprints]

    def _convert_timezone(self, dt: datetime, tz: pytz.tzinfo) -> datetime:
        """Convert datetime to target timezone"""
        return dt.astimezone(tz).strftime('%Y-%m-%d %H:%M %Z')

    def _excel_charts(self, writer, data):
        """Add Excel-native charts"""
        from openpyxl import Workbook
        from openpyxl.chart import LineChart, Reference
        
        workbook = writer.book
        worksheet = workbook.create_sheet('Charts')
        
        # Velocity Chart
        chart = LineChart()
        data_ref = Reference(workbook['Metrics'], min_col=5, min_row=2, max_row=len(data['velocity_history'])+1)
        chart.add_data(data_ref, titles_from_data=True)
        worksheet.add_chart(chart, "A1")

    def _pdf_ai_section(self, insights: dict) -> list:
        """Generate AI insights section"""
        elements = []
        elements.append(Paragraph(_("AI Recommendations"), self.styles['Heading2']))
        
        for rec in insights.get('recommendations', []):
            elements.append(Paragraph(f"• {rec['description']}", self.styles['Normal']))
            
        return elements

    def _pdf_compliance_footer(self) -> Paragraph:
        """Generate compliance footer"""
        text = _("Generated by RLG Projects | Compliant with GDPR and CCPA regulations")
        return Paragraph(text, self.styles['Footnote'])

# Example usage:
# generator = ReportGenerator()
# pdf_report = generator.generate_project_report(123, 'executive_pdf', 'es', 'Europe/Madrid')