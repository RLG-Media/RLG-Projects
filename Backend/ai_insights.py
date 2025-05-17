"""
RLG AI Insights Engine - Scrum Optimization Core
Version: 3.2.0
Features: Predictive Analytics, NLP Processing, Risk Detection, Auto-Optimization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from deepseek_api import DeepseekAPI
from scrum_analyzer import ScrumPatternRecognizer
from geo_analyzer import TeamLocationOptimizer
from slack_integration import SlackAlerter
from transformers import pipeline
from sklearn.ensemble import IsolationForest
from sentence_transformers import SentenceTransformer
import pytz
import logging

class AIInsightsEngine:
    def __init__(self):
        self.ai_core = DeepseekAPI()
        self.nlp = pipeline("text2text-generation", model="facebook/bart-base")
        self.embeddings = SentenceTransformer('all-MiniLM-L6-v2')
        self.scrum_validator = ScrumPatternRecognizer()
        self.geo_optimizer = TeamLocationOptimizer()
        self.slack_alerter = SlackAlerter()
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.logger = logging.getLogger('RLG_AI')

    # --------------------------
    # CORE SCRUM ANALYTICS
    # --------------------------
    def analyze_sprint_health(self, sprint_data):
        """Comprehensive sprint analysis with multi-factor scoring"""
        try:
            # Temporal analysis
            time_features = self._extract_time_features(sprint_data)
            
            # Textual analysis
            text_features = self.embeddings.encode([
                sprint_data['goal'],
                sprint_data['retro_notes'],
                sprint_data['daily_standups']
            ])
            
            # Numerical metrics
            metrics = self._calculate_metrics(sprint_data)
            
            # Geographic optimization
            geo_score = self.geo_optimizer.calculate_team_synergy(
                sprint_data['team_locations']
            )
            
            # Combine features
            features = np.concatenate([
                time_features,
                text_features.mean(axis=0),
                np.array([metrics['velocity'], metrics['risk_score'], geo_score])
            ])
            
            # Predict anomalies
            anomaly_score = self.anomaly_detector.decision_function([features])[0]
            health_score = self._normalize_score(1 - anomaly_score)
            
            return {
                'health_score': health_score,
                'time_analysis': time_features,
                'text_analysis': text_features.tolist(),
                'geo_optimization': geo_score,
                'key_metrics': metrics
            }
            
        except Exception as e:
            self.logger.error(f"Sprint analysis failed: {str(e)}")
            return {'error': 'Analysis failed'}

    # --------------------------
    # PREDICTIVE MODELING
    # --------------------------
    def predict_sprint_risks(self, historical_data, current_sprint):
        """Predict risks using ensemble AI approach"""
        try:
            # Data preparation
            df = self._create_temporal_dataframe(historical_data)
            current_features = self._extract_prediction_features(current_sprint)
            
            # Deepseek prediction
            deepseek_pred = self.ai_core.predict('sprint_risk', {
                'history': df.to_dict(),
                'current': current_features
            })
            
            # Statistical analysis
            stat_risk = self._calculate_statistical_risk(df, current_features)
            
            # NLP analysis
            text_risk = self._analyze_textual_risk(current_sprint['goal'], current_sprint['backlog_items'])
            
            # Combine predictions
            combined_risk = 0.6*deepseek_pred['risk_score'] + 0.3*stat_risk + 0.1*text_risk
            
            # Generate mitigation strategies
            mitigation = self.ai_core.generate(
                f"Generate risk mitigation strategies for: {current_sprint['goal']} "
                f"with risk score {combined_risk:.2f}. Focus on Scrum best practices."
            )
            
            return {
                'risk_score': combined_risk,
                'factors': {
                    'historical_patterns': deepseek_pred['patterns'],
                    'statistical_analysis': stat_risk,
                    'goal_complexity': text_risk
                },
                'mitigation_strategies': mitigation,
                'alert_level': 'high' if combined_risk > 0.7 else 'medium' if combined_risk > 0.4 else 'low'
            }
            
        except Exception as e:
            self.logger.error(f"Risk prediction failed: {str(e)}")
            return {'error': 'Risk prediction unavailable'}

    # --------------------------
    # NLP & TEXT PROCESSING
    # --------------------------
    def analyze_team_communication(self, messages):
        """Analyze team chat/standup messages for sentiment and insights"""
        try:
            # Sentiment analysis
            sentiment = self.nlp(
                f"summarize sentiment: {' '.join(messages)}",
                max_length=50,
                do_sample=False
            )[0]['generated_text']
            
            # Key theme extraction
            themes = self.ai_core.extract_themes(messages)
            
            # Action item detection
            actions = self.ai_core.generate(
                f"Extract action items from these messages: {messages}"
            )
            
            # Scrum compliance check
            compliance_report = self.scrum_validator.validate_communication(messages)
            
            return {
                'sentiment': sentiment,
                'key_themes': themes,
                'action_items': actions,
                'compliance_issues': compliance_report
            }
            
        except Exception as e:
            self.logger.error(f"Communication analysis failed: {str(e)}")
            return {'error': 'Text analysis failed'}

    # --------------------------
    # AUTOMATED OPTIMIZATION
    # --------------------------
    def optimize_team_workflow(self, team_data):
        """AI-driven workflow optimization with geographic awareness"""
        try:
            # Timezone optimization
            schedule_rec = self.geo_optimizer.optimal_meeting_times(
                team_data['locations'],
                team_data['working_hours']
            )
            
            # Skill gap analysis
            skill_gap = self.ai_core.analyze_skills(
                team_data['members'],
                team_data['backlog_items']
            )
            
            # Workload balancing
            workload_dist = self._balance_workload(
                team_data['capacity'],
                team_data['backlog_complexity']
            )
            
            # Generate Jira-like automation rules
            automation_rules = self.ai_core.generate(
                f"Create workflow automation rules for: {team_data['tools']} "
                "following Scrum best practices"
            )
            
            return {
                'schedule_optimization': schedule_rec,
                'skill_gap_analysis': skill_gap,
                'workload_distribution': workload_dist,
                'automation_rules': automation_rules
            }
            
        except Exception as e:
            self.logger.error(f"Workflow optimization failed: {str(e)}")
            return {'error': 'Optimization unavailable'}

    # --------------------------
    # REPORTING & VISUALIZATION
    # --------------------------
    def generate_ai_report(self, sprint_id, report_type='executive'):
        """Generate multi-format reports with AI insights"""
        try:
            # Retrieve data from database
            sprint_data = self._get_sprint_data(sprint_id)
            historical_data = self._get_historical_data(sprint_data['project_id'])
            
            # Base metrics
            report = {
                'sprint_metrics': self._calculate_base_metrics(sprint_data),
                'predictive_insights': self.predict_sprint_risks(historical_data, sprint_data),
                'team_analysis': self.analyze_team_communication(sprint_data['messages'])
            }
            
            # Add visualizations
            report['visualizations'] = {
                'burndown': self._generate_burndown_data(sprint_data),
                'velocity_trend': self._calculate_velocity_trend(historical_data),
                'risk_evolution': self._track_risk_history(sprint_data)
            }
            
            # Format based on report type
            if report_type == 'executive':
                return self._format_executive_report(report)
            elif report_type == 'technical':
                return self._format_technical_report(report)
            else:
                return self._format_developer_report(report)
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            return {'error': 'Report generation failed'}

    # --------------------------
    # PRIVATE UTILITY METHODS
    # --------------------------
    def _calculate_velocity(self, historical_data):
        """Calculate team velocity with anomaly detection"""
        velocities = [s['points_completed'] / s['duration_days'] for s in historical_data]
        return np.mean(velocities[-3:]) if len(velocities) >=3 else np.mean(velocities)

    def _normalize_score(self, score):
        """Convert anomaly score to 0-100 scale"""
        return max(0, min(100, int(score * 100)))

    def _extract_time_features(self, sprint_data):
        """Create temporal features for ML models"""
        start = pd.to_datetime(sprint_data['start_date'])
        end = pd.to_datetime(sprint_data['end_date'])
        return np.array([
            (end - start).days,
            start.hour,
            start.weekday(),
            pd.Timestamp.now().tz_localize('UTC').tz_convert(sprint_data['timezone']).hour
        ])

    def _balance_workload(self, capacities, complexities):
        """AI-driven workload distribution using knapsack algorithm"""
        # Implementation of optimized workload distribution
        pass

# --------------------------
# SUPPORTING FUNCTIONS
# --------------------------
def create_geo_aware_dataset(team_data):
    """Create location-enhanced dataset for analysis"""
    df = pd.DataFrame(team_data)
    df = pd.concat([df, pd.json_normalize(df['locations'])], axis=1)
    df['time_diff'] = df['timezone'].apply(lambda x: pytz.timezone(x).utcoffset(datetime.now()).total_seconds()/3600)
    return df

def detect_cultural_factors(messages):
    """Identify cultural considerations in team communication"""
    # Implementation using NLP models
    pass