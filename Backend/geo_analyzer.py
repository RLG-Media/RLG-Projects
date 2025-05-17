"""
RLG Geo-Analytics Core - Distributed Team Optimization Engine
Version: 10.0.0
Features: Timezone Intelligence, Cultural Adaptation, Geographic Risk Analysis
"""

import json
import pytz
from datetime import datetime, time
import numpy as np
from typing import List, Dict
from geoip2.database import Reader
from deepseek_api import DeepseekAPI
from dateutil import tz
import logging
from retry import retry
import matplotlib.pyplot as plt
from config import get_config
from collections import defaultdict
import hashlib

class TeamLocationOptimizer:
    """AI-powered geographic analysis engine for distributed Scrum teams"""
    
    def __init__(self):
        self.config = get_config()
        self.geo_reader = Reader('GeoLite2-City.mmdb')
        self.ai = DeepseekAPI()
        self.logger = logging.getLogger('RLG.Geo')
        self._init_cultural_data()
        self.cache = {}
        
    def _init_cultural_data(self):
        """Load cultural and regional working patterns"""
        with open('cultural_work_patterns.json') as f:
            self.cultural_norms = json.load(f)
            
        self.holidays = self._load_holiday_calendar()

    def _load_holiday_calendar(self) -> Dict:
        """Load regional holiday data"""
        # Implementation for fetching holidays from public API
        return defaultdict(list)

    @retry(tries=3, delay=2)
    def get_location_metadata(self, ip_address: str) -> Dict:
        """Get comprehensive geographic metadata for an IP"""
        try:
            geo = self.geo_reader.city(ip_address)
            return {
                'country': geo.country.name,
                'country_code': geo.country.iso_code,
                'city': geo.city.name,
                'timezone': geo.location.time_zone,
                'coordinates': (geo.location.latitude, geo.location.longitude),
                'working_hours': self._get_cultural_working_hours(geo.country.iso_code),
                'risk_factors': self._calculate_geo_risk(geo)
            }
        except Exception as e:
            self.logger.error(f"Geo lookup failed: {str(e)}")
            return self._fallback_location_data()

    def _get_cultural_working_hours(self, country_code: str) -> Dict:
        """Get cultural working patterns with AI enhancements"""
        cache_key = f"work_hours_{country_code}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        base_hours = self.cultural_norms.get(country_code, {})
        ai_adjusted = self.ai.adjust_working_hours(base_hours)
        
        self.cache[cache_key] = ai_adjusted
        return ai_adjusted

    def _calculate_geo_risk(self, geo_data) -> Dict:
        """Calculate geographic risk factors for planning"""
        risks = {
            'timezone_risk': self._timezone_risk_score(geo_data.location.time_zone),
            'political_risk': self.ai.predict_political_risk(geo_data.country.iso_code),
            'connectivity_risk': self._internet_quality_score(geo_data.country.iso_code)
        }
        risks['overall_risk'] = np.mean(list(risks.values()))
        return risks

    def _timezone_risk_score(self, timezone: str) -> float:
        """Calculate timezone alignment risk (0-1 scale)"""
        team_zones = [tz for tz in self.config.TIMEZONE_MAP if tz in pytz.all_timezones]
        offsets = [self._tz_to_offset(tz) for tz in team_zones]
        target_offset = self._tz_to_offset(timezone)
        return abs(target_offset - np.mean(offsets)) / 24

    def optimal_meeting_times(self, timezones: List[str], duration: int = 2) -> List[Dict]:
        """Find optimal meeting times across multiple timezones"""
        time_windows = []
        for hour in range(0, 24):
            coverage = self._calculate_time_coverage(hour, duration, timezones)
            if coverage['score'] > 0.7:
                time_windows.append({
                    'utc_start': hour,
                    'local_times': self._convert_to_local_times(hour, timezones),
                    'coverage_score': coverage['score'],
                    'cultural_acceptance': coverage['cultural']
                })
        return sorted(time_windows, key=lambda x: (-x['coverage_score'], x['utc_start']))

    def _calculate_time_coverage(self, start_hour: int, duration: int, timezones: List[str]) -> Dict:
        """Calculate coverage quality score for a time window"""
        scores = []
        for tz in timezones:
            local_start = self._utc_to_local(start_hour, tz)
            score = self._time_suitability(local_start, duration, tz)
            scores.append(score)
        return {
            'score': np.mean(scores),
            'cultural': self._cultural_acceptance_score(start_hour, timezones)
        }

    def _time_suitability(self, local_time: time, duration: int, timezone: str) -> float:
        """Calculate suitability score (0-1) for a local time window"""
        work_hours = self._get_cultural_working_hours(self._tz_to_country(timezone))
        start = local_time.hour
        end = (start + duration) % 24
        
        if work_hours['overnight_shift']:
            return 1.0  # 24/7 operations
            
        if start >= work_hours['work_start'] and end <= work_hours['work_end']:
            return 1.0
        elif start >= work_hours['core_hours_start'] and end <= work_hours['core_hours_end']:
            return 0.9
        else:
            overlap = self._calculate_overlap(start, end, work_hours)
            return overlap / duration

    def generate_distributed_team_report(self, team_ips: List[str]) -> Dict:
        """Comprehensive geographic analysis report for leadership"""
        locations = [self.get_location_metadata(ip) for ip in team_ips]
        
        return {
            'timezone_analysis': self._analyze_timezones(locations),
            'risk_assessment': self._team_risk_profile(locations),
            'recommendations': self.ai.generate_geo_recommendations(locations),
            'visualization': self._generate_geo_visualization(locations)
        }

    def _analyze_timezones(self, locations: List[Dict]) -> Dict:
        """Deep analysis of team timezone distribution"""
        timezones = [loc['timezone'] for loc in locations]
        return {
            'span_hours': self._calculate_timezone_span(timezones),
            'optimal_windows': self.optimal_meeting_times(timezones),
            'core_overlap': self._calculate_core_overlap(timezones)
        }

    def _generate_geo_visualization(self, locations: List[Dict]):
        """Generate team distribution map visualization"""
        # Implementation using matplotlib or external mapping service
        return "https://example.com/team_map.png"

    def _fallback_location_data(self) -> Dict:
        """Safe default when geo lookup fails"""
        return {
            'country': 'Unknown',
            'timezone': 'UTC',
            'working_hours': {'work_start': 9, 'work_end': 17},
            'risk_factors': {'overall_risk': 0.5}
        }

    # --------------------------
    # HELPER FUNCTIONS
    # --------------------------
    def _tz_to_offset(self, timezone: str) -> float:
        """Convert timezone to UTC offset in hours"""
        now = datetime.now(pytz.timezone(timezone))
        return now.utcoffset().total_seconds() / 3600

    def _utc_to_local(self, utc_hour: int, timezone: str) -> time:
        """Convert UTC hour to local time object"""
        utc_time = datetime.utcnow().replace(hour=utc_hour, minute=0)
        local_time = utc_time.astimezone(pytz.timezone(timezone))
        return local_time.time()

    def _hash_ip(self, ip: str) -> str:
        """GDPR-compliant IP hashing"""
        return hashlib.sha256(ip.encode()).hexdigest()

if __name__ == '__main__':
    analyzer = TeamLocationOptimizer()
    
    # Example analysis for a distributed team
    team_ips = ['203.0.113.1', '198.51.100.42', '192.0.2.255']
    report = analyzer.generate_distributed_team_report(team_ips)
    
    print("Optimal Meeting Times:")
    for window in report['timezone_analysis']['optimal_windows'][:3]:
        print(f"UTC {window['utc_start']:02}:00 - Score: {window['coverage_score']:.2f}")
        
    print(f"\nTeam Risk Profile: {report['risk_assessment']['overall_risk']:.2f}")