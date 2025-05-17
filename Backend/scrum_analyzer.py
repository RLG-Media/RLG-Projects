"""
RLG Scrum Analytics Core - Advanced Process Intelligence
Version: 14.0.0
Features: AI-Powered Metrics, Cultural Process Adaptation, Real-Time Scrum Health Monitoring
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from models import Sprint, Task, BacklogItem, Project
from deepseek_api import DeepseekAPI
from geoip2.database import Reader
from config import get_config
import pytz
import logging
from functools import lru_cache
from collections import defaultdict
import matplotlib.pyplot as plt
from io import BytesIO
from flask_babel import gettext as _

logger = logging.getLogger('RLG.Scrum')
config = get_config()
ai_engine = DeepseekAPI()

class ScrumAnalyzer:
    """AI-enhanced Scrum process optimization engine"""
    
    def __init__(self, project_id: int):
        self.project_id = project_id
        self.project = Project.query.get_or_404(project_id)
        self.geo_reader = Reader('GeoLite2-City.mmdb')
        self.timezone = pytz.timezone(self.project.default_timezone)
        self._load_data()

    def _load_data(self):
        """Load and preprocess Scrum data"""
        self.sprints = Sprint.query.filter_by(project_id=self.project_id).all()
        self.tasks = Task.query.join(Sprint).filter(Sprint.project_id == self.project_id).all()
        self.backlog = BacklogItem.query.filter_by(project_id=self.project_id).all()
        
        # Convert to localized datetimes
        for sprint in self.sprints:
            sprint.start_date = sprint.start_date.astimezone(self.timezone)
            sprint.end_date = sprint.end_date.astimezone(self.timezone)

    @lru_cache(maxsize=100)
    def analyze_sprint(self, sprint_id: int) -> Dict:
        """Comprehensive sprint analysis with AI insights"""
        sprint = next(s for s in self.sprints if s.id == sprint_id)
        
        base_metrics = {
            'velocity': self._calculate_velocity(sprint),
            'burndown_rate': self._calculate_burndown(sprint),
            'process_adherence': self._check_process_compliance(sprint),
            'team_focus': self._calculate_focus_factor(sprint),
            'cultural_impact': self._analyze_cultural_factors(sprint)
        }
        
        ai_enhanced = ai_engine.enhance_metrics({
            'base_metrics': base_metrics,
            'historical_data': self._get_historical_context()
        })
        
        return {
            **base_metrics,
            'ai_recommendations': ai_enhanced.get('recommendations', []),
            'risk_predictions': ai_enhanced.get('risks', [])
        }

    def _calculate_velocity(self, sprint: Sprint) -> float:
        """Calculate normalized velocity"""
        committed = sprint.story_points_committed or 1  # Prevent division by zero
        return sprint.story_points_completed / committed

    def _calculate_burndown(self, sprint: Sprint) -> Dict:
        """Calculate real-time burndown trajectory"""
        time_elapsed = (datetime.now(self.timezone) - sprint.start_date).total_seconds()
        total_duration = (sprint.end_date - sprint.start_date).total_seconds()
        
        ideal = sprint.story_points_committed * (1 - (time_elapsed / total_duration))
        actual = sprint.story_points_remaining
        
        return {
            'ideal': ideal,
            'actual': actual,
            'variance': actual - ideal,
            'trend': self._calculate_burndown_trend(sprint)
        }

    def _check_process_compliance(self, sprint: Sprint) -> Dict:
        """Verify Scrum Guide adherence with cultural adaptations"""
        compliance = {
            'daily_scrums': len([e for e in sprint.events if e.type == 'daily']) >= 5,
            'review_held': any(e.type == 'review' for e in sprint.events),
            'retro_held': any(e.type == 'retrospective' for e in sprint.events),
            'artifact_completeness': self._check_artifacts(sprint)
        }
        
        # Cultural adaptations
        compliance.update(self._apply_cultural_rules(sprint))
        return compliance

    def _apply_cultural_rules(self, sprint: Sprint) -> Dict:
        """Apply region-specific Scrum adaptations"""
        cultural_rules = self._get_cultural_rules()
        return {
            'extended_planning': cultural_rules.get('extended_planning', False),
            'flexible_demos': cultural_rules.get('flexible_demos', True)
        }

    def _get_cultural_rules(self) -> Dict:
        """Get cultural working patterns from geo data"""
        if not self.project.team_members:
            return {}
            
        member_countries = {m.location.country for m in self.project.team_members}
        return ai_engine.get_cultural_rules(list(member_countries))

    def generate_team_analytics(self) -> Dict:
        """Cross-team performance analysis with geo insights"""
        analytics = defaultdict(list)
        
        for member in self.project.team_members:
            member_metrics = {
                'throughput': len([t for t in self.tasks if t.assignee_id == member.id]),
                'quality': self._calculate_quality(member),
                'cultural_factors': self._analyze_member_culture(member)
            }
            analytics[member.location.country].append(member_metrics)
        
        return self._enhance_with_ai(analytics)

    def _enhance_with_ai(self, data: Dict) -> Dict:
        """Add AI-powered insights to raw metrics"""
        return ai_engine.analyze_team_performance({
            'raw_data': data,
            'project_goals': self.project.goals,
            'historical_comparison': self._get_historical_team_data()
        })

    def generate_visual_report(self, sprint_id: int) -> BytesIO:
        """Generate visual Scrum health report"""
        buffer = BytesIO()
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        
        # Burndown Chart
        self._plot_burndown(axs[0, 0], sprint_id)
        
        # Velocity History
        self._plot_velocity(axs[0, 1])
        
        # Process Compliance
        self._plot_compliance(axs[1, 0], sprint_id)
        
        # Team Distribution
        self._plot_team_geo(axs[1, 1])
        
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        plt.close()
        return buffer

    def _plot_burndown(self, ax, sprint_id: int):
        """Generate burndown chart visualization"""
        sprint = next(s for s in self.sprints if s.id == sprint_id)
        ax.plot(sprint.burndown_dates, sprint.burndown_ideal, label=_("Ideal"))
        ax.plot(sprint.burndown_dates, sprint.burndown_actual, label=_("Actual"))
        ax.set_title(_("Burndown Progress"))

    # Compliance and Security
    def check_gdpr_compliance(self) -> Dict:
        """Verify GDPR compliance in Scrum processes"""
        return {
            'data_minimization': self._check_data_collection(),
            'right_to_erasure': self._verify_deletion_processes(),
            'consent_management': self._check_consent_records()
        }

    def check_ccpa_compliance(self) -> Dict:
        """Verify CCPA compliance for US-based teams"""
        return {
            'opt_out_mechanism': self._check_opt_out_system(),
            'data_sale_prevention': self._verify_no_data_sale(),
            'minor_protection': self._check_minor_safeguards()
        }

    # AI Integration
    def generate_ai_recommendations(self) -> List[Dict]:
        """Get real-time process improvement suggestions"""
        current_state = {
            'metrics': self._get_current_metrics(),
            'team_structure': self._get_team_composition(),
            'cultural_context': self._get_cultural_context()
        }
        return ai_engine.generate_scrum_recommendations(current_state)

    # Localization
    def localize_metrics(self, metrics: Dict, language: str) -> Dict:
        """Translate metrics and adapt to local context"""
        localized = {}
        for key, value in metrics.items():
            if isinstance(value, str):
                localized[key] = ai_engine.translate_text(value, language)
            elif isinstance(value, dict):
                localized[key] = self.localize_metrics(value, language)
            else:
                localized[key] = value
        return localized

    # Error Handling
    def handle_analysis_error(self, error: Exception) -> Dict:
        """Graceful error handling with AI diagnostics"""
        logger.error(f"Analysis failed: {str(error)}")
        return {
            'error': _("Analysis unavailable"),
            'diagnostics': ai_engine.suggest_error_recovery(str(error)),
            'reference_id': f"ERR-{datetime.now().timestamp()}"
        }

# Example usage:
# analyzer = ScrumAnalyzer(project_id=123)
# sprint_report = analyzer.analyze_sprint(sprint_id=456)
# visualization = analyzer.generate_visual_report(sprint_id=456)