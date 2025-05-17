"""
RLG Slack Integration Core - Smart Scrum Automation
Version: 15.0.0
Features: AI-Powered Standups, Cultural Adaptation, Compliance-Safe Messaging
"""

import os
import json
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models import Team, User, Sprint, Task
from deepseek_api import DeepseekAPI
from config import get_config
import pytz
import logging
import hashlib
from retry import retry
from functools import lru_cache
from geoip2.database import Reader

logger = logging.getLogger('RLG.Slack')
config = get_config()
ai_engine = DeepseekAPI()

class SlackBot:
    """AI-enhanced Slack integration for Scrum automation"""
    
    def __init__(self):
        self.client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
        self.socket_client = SocketModeClient(
            app_token=os.getenv('SLACK_APP_TOKEN'),
            web_client=self.client
        )
        self.geo_reader = Reader('GeoLite2-City.mmdb')
        self._register_handlers()
        self._setup_schedulers()

    def _register_handlers(self):
        """Register Slack event handlers"""
        self.socket_client.socket_mode_request_listeners.append(self.handle)
        self.handlers = {
            "standup_response": self._handle_standup_response,
            "task_update": self._handle_task_update,
            "retro_suggestion": self._handle_retro_suggestion
        }

    def _setup_schedulers(self):
        """Initialize scheduled Scrum events"""
        if config.ENVIRONMENT == 'production':
            self._schedule_daily_standups()
            self._schedule_sprint_reminders()

    @retry(tries=3, delay=2, backoff=2)
    def send_message(self, channel: str, message: str, attachments: List[Dict] = None) -> Dict:
        """Send localized, compliance-safe messages"""
        try:
            user_tz = self._get_user_timezone(channel)
            localized_msg = self._localize_message(message, channel)
            
            return self.client.chat_postMessage(
                channel=channel,
                text=localized_msg,
                attachments=attachments,
                blocks=self._build_ai_blocks(localized_msg),
                metadata=self._generate_metadata(channel)
            )
        except Exception as e:
            logger.error(f"Message failed: {str(e)}")
            raise

    def _localize_message(self, message: str, channel: str) -> str:
        """AI-powered message localization"""
        user = self._get_channel_user(channel)
        return ai_engine.translate_text(
            text=message,
            target_lang=user.preferred_language,
            context='scrum'
        )

    def _build_ai_blocks(self, message: str) -> List[Dict]:
        """Generate interactive Slack blocks with AI"""
        return ai_engine.generate_slack_blocks(message)

    def handle(self, client: SocketModeClient, req: SocketModeRequest):
        """Centralized event handler"""
        try:
            if req.type == "events_api":
                event_type = req.payload.get("event", {}).get("type")
                self.handlers.get(event_type, self._default_handler)(req.payload)
        except Exception as e:
            logger.error(f"Handler failed: {str(e)}")

    # Scrum-Specific Features
    def trigger_standup(self, sprint_id: int):
        """AI-powered daily standup automation"""
        sprint = Sprint.query.get_or_404(sprint_id)
        questions = ai_engine.generate_standup_questions(sprint)
        
        for member in sprint.team.members:
            tz = pytz.timezone(member.user.timezone)
            localized_time = datetime.now(tz).strftime('%H:%M')
            
            self.client.chat_postMessage(
                channel=member.user.slack_id,
                blocks=self._build_standup_blocks(questions, localized_time),
                metadata=self._standup_metadata(sprint_id)
            )

    def _build_standup_blocks(self, questions: List[str], time: str) -> List[Dict]:
        """Generate interactive standup form"""
        return [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{time} Standup Questions:*\n" + "\n".join(
                    [f"{i+1}. {q}" for i, q in enumerate(questions)]
                )
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Submit Update"},
                "action_id": "standup_response"
            }
        }]

    def _handle_standup_response(self, payload: Dict):
        """Process standup responses with AI analysis"""
        user_id = payload['user']['id']
        response = payload['actions'][0]['value']
        
        # Store response
        standup_log = {
            'user': self._hash_user_id(user_id),
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'sprint': payload['metadata']['sprint_id']
        }
        
        # Generate AI summary
        summary = ai_engine.analyze_standup_response(response)
        self._update_sprint_metrics(summary)
        
        # Send to channel
        self.client.chat_postMessage(
            channel=payload['channel']['id'],
            blocks=self._build_summary_blocks(summary)
        )

    # Compliance & Security
    def _hash_user_id(self, user_id: str) -> str:
        """GDPR-compliant user hashing"""
        return hashlib.sha256(user_id.encode() + config.SECRET_KEY.encode()).hexdigest()

    def _generate_metadata(self, channel: str) -> Dict:
        """Generate message metadata for auditing"""
        return {
            'source': 'rlg_bot',
            'channel': channel,
            'timestamp': datetime.now().isoformat(),
            'compliance_checksum': self._generate_compliance_hash()
        }

    # Schedulers
    def _schedule_daily_standups(self):
        """Schedule standups based on team timezones"""
        for team in Team.query.all():
            optimal_time = self._calculate_optimal_time(team.members)
            self._create_standup_schedule(team.channel_id, optimal_time)

    def _calculate_optimal_time(self, members: List[User]) -> datetime:
        """Calculate best standup time for distributed teams"""
        timezones = [m.timezone for m in members]
        return ai_engine.calculate_optimal_meeting_time(timezones)

    # Localization
    @lru_cache(maxsize=1000)
    def _get_user_timezone(self, channel: str) -> pytz.tzinfo:
        """Get user timezone with fallback"""
        try:
            user_id = self._get_channel_user_id(channel)
            user = User.query.filter_by(slack_id=user_id).first()
            return pytz.timezone(user.timezone)
        except:
            return pytz.utc

    # Error Handling
    def _default_handler(self, payload: Dict):
        """Handle unprocessed events"""
        logger.warning(f"Unhandled event: {json.dumps(payload)}")

    def _retry_policy(self, method: callable, *args, **kwargs):
        """Custom retry handler"""
        try:
            return method(*args, **kwargs)
        except Exception as e:
            logger.error(f"Retry failed: {str(e)}")
            self._log_compliance_issue()
            raise

    # Example usage
    def start(self):
        """Start listening for events"""
        self.socket_client.connect()
        logger.info("Slack bot listening for events...")

if __name__ == '__main__':
    bot = SlackBot()
    bot.start()