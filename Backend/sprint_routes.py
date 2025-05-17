"""
RLG Sprint Management Core - AI-Optimized Sprint Workflows
Version: 16.0.0
Features: Smart Sprint Planning, Auto-Risk Mitigation, Cross-TimeZone Coordination
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from models import Sprint, Task, BacklogItem, Project, db
from deepseek_api import DeepseekAPI
from compliance_checker import ScrumGuideValidator
from report_generator import generate_sprint_report
from utilities import (
    validate_sprint_data,
    calculate_velocity,
    apply_timezone_to_dates,
    log_activity,
    handle_geo_distribution
)
from config import get_config
from datetime import datetime, timedelta
import pytz
import logging
from functools import lru_cache

sprints = Blueprint('sprints', __name__)
ai_engine = DeepseekAPI()
validator = ScrumGuideValidator()
config = get_config()
logger = logging.getLogger('RLG.Sprints')

@sprints.route('/sprints', methods=['POST'])
@jwt_required()
def create_sprint():
    """Create AI-optimized sprint with risk analysis"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate against Scrum Guide
        compliance_errors = validator.validate_sprint(data)
        if compliance_errors:
            return jsonify({"scrum_errors": compliance_errors}), 400
        
        # Generate AI recommendations
        ai_plan = ai_engine.generate_sprint_plan({
            'project_id': data['project_id'],
            'team_capacity': data.get('capacity'),
            'historical_data': get_historical_metrics(data['project_id'])
        })
        
        # Create sprint with localized dates
        tz = pytz.timezone(data.get('timezone', 'UTC'))
        sprint = Sprint(
            name=data['name'],
            start_date=apply_timezone_to_dates(data['start_date'], tz),
            end_date=apply_timezone_to_dates(data['end_date'], tz),
            project_id=data['project_id'],
            goals=data.get('goals', []),
            ai_recommendations=ai_plan
        )
        
        db.session.add(sprint)
        db.session.commit()
        
        # Auto-populate sprint backlog
        if data.get('auto_populate'):
            _populate_sprint_backlog(sprint.id, ai_plan['selected_items'])
        
        log_activity(user_id, 'sprint_create', sprint.id)
        
        return jsonify({
            "message": "Sprint created",
            "sprint": sprint.to_dict(),
            "warnings": ai_plan.get('risk_warnings')
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Sprint creation failed: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@sprints.route('/sprints/<int:sprint_id>', methods=['GET'])
@jwt_required()
def get_sprint(sprint_id):
    """Get sprint details with real-time AI insights"""
    try:
        sprint = Sprint.query.get_or_404(sprint_id)
        enhanced_data = ai_engine.enhance_sprint_data(sprint.to_dict())
        
        return jsonify({
            "sprint": enhanced_data,
            "analytics": get_live_metrics(sprint_id),
            "compliance": validator.check_sprint_compliance(sprint_id)
        })
        
    except Exception as e:
        logger.error(f"Sprint retrieval failed: {str(e)}")
        return jsonify({"error": "Sprint load error"}), 500

@sprints.route('/sprints/<int:sprint_id>/start', methods=['POST'])
@jwt_required()
def start_sprint(sprint_id):
    """Initiate sprint with team coordination"""
    try:
        sprint = Sprint.query.get_or_404(sprint_id)
        
        # Validate sprint start conditions
        if not validator.validate_sprint_start(sprint):
            return jsonify({"error": "Cannot start sprint"}), 400
            
        sprint.status = 'active'
        sprint.actual_start_date = datetime.utcnow()
        
        # Notify distributed teams
        handle_geo_distribution(sprint.project.team_members, 'sprint_start', sprint)
        
        db.session.commit()
        return jsonify({"message": "Sprint started", "status": sprint.status})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Sprint start failed: {str(e)}")
        return jsonify({"error": "Sprint start error"}), 500

@sprints.route('/sprints/<int:sprint_id>/complete', methods=['POST'])
@jwt_required()
def complete_sprint(sprint_id):
    """Complete sprint with automated wrap-up"""
    try:
        sprint = Sprint.query.get_or_404(sprint_id)
        sprint.status = 'completed'
        sprint.actual_end_date = datetime.utcnow()
        
        # Handle incomplete tasks
        if request.json.get('carry_over', True):
            _handle_unfinished_tasks(sprint_id)
        
        # Generate final report
        report = generate_sprint_report(sprint_id)
        
        db.session.commit()
        return jsonify({
            "message": "Sprint completed",
            "report": report,
            "retrospective": ai_engine.generate_retrospective(sprint_id)
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Sprint completion failed: {str(e)}")
        return jsonify({"error": "Sprint completion error"}), 500

@sprints.route('/sprints/<int:sprint_id>/tasks', methods=['GET'])
@jwt_required()
def get_sprint_tasks(sprint_id):
    """Get paginated tasks with AI prioritization"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        query = Task.query.filter_by(sprint_id=sprint_id)
        tasks = query.paginate(page=page, per_page=per_page)
        
        # Add AI insights
        enhanced_tasks = [ai_engine.analyze_task(t) for t in tasks.items]
        
        return jsonify({
            "tasks": enhanced_tasks,
            "pagination": {
                "total": tasks.total,
                "page": tasks.page,
                "per_page": tasks.per_page
            }
        })
        
    except Exception as e:
        logger.error(f"Task retrieval failed: {str(e)}")
        return jsonify({"error": "Task load error"}), 500

@sprints.route('/sprints/<int:sprint_id>/adjust', methods=['PATCH'])
@jwt_required()
def adjust_sprint(sprint_id):
    """AI-powered mid-sprint adjustments"""
    try:
        sprint = Sprint.query.get_or_404(sprint_id)
        adjustments = request.json
        
        # Get AI validation
        ai_validation = ai_engine.validate_sprint_changes(
            sprint.to_dict(),
            adjustments
        )
        
        if not ai_validation.get('valid', False):
            return jsonify({"errors": ai_validation.get('reasons')}), 400
            
        # Apply changes
        if 'end_date' in adjustments:
            sprint.end_date = apply_timezone_to_dates(
                adjustments['end_date'],
                pytz.timezone(adjustments.get('timezone', 'UTC'))
            )
            
        if 'goals' in adjustments:
            sprint.goals = ai_engine.refine_sprint_goals(
                sprint.goals,
                adjustments['goals']
            )
        
        db.session.commit()
        return jsonify({"message": "Sprint updated", "sprint": sprint.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Sprint adjustment failed: {str(e)}")
        return jsonify({"error": "Adjustment error"}), 500

# Helper functions
def _populate_sprint_backlog(sprint_id, items):
    """Add AI-selected items to sprint backlog"""
    try:
        for item in items:
            task = Task(
                title=item['title'],
                description=item.get('description'),
                sprint_id=sprint_id,
                story_points=item.get('points')
            )
            db.session.add(task)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Backlog population failed: {str(e)}")

def _handle_unfinished_tasks(sprint_id):
    """Automatically handle incomplete tasks"""
    unfinished = Task.query.filter(
        Task.sprint_id == sprint_id,
        Task.status != 'done'
    ).all()
    for task in unfinished:
        new_item = BacklogItem(
            title=f"Carryover: {task.title}",
            description=task.description,
            project_id=task.sprint.project_id,
            priority=task.priority
        )
        db.session.add(new_item)
    db.session.commit()

@lru_cache(maxsize=100)
def get_historical_metrics(project_id):
    """Get historical project data for AI planning"""
    return {
        'velocity': calculate_velocity(project_id),
        'risk_profile': ai_engine.get_project_risks(project_id),
        'team_performance': get_team_performance(project_id)
    }

def get_team_performance(project_id):
    """Dummy implementation for team performance; replace with real logic."""
    # Example: return average completion rate or other metric
    return {
        "average_completion_rate": 0.85,
        "team_mood": "stable"
    }

def calculate_burn_rate(sprint):
    """Calculate the sprint burn rate (dummy implementation)."""
    if not sprint or not sprint.tasks:
        return 0
    total_points = sum(task.story_points or 0 for task in sprint.tasks)
    completed_points = sum(task.story_points or 0 for task in sprint.tasks if task.status == 'done')
    if total_points == 0:
        return 0
    return completed_points / total_points

def calculate_focus_factor(sprint):
    """Calculate the sprint focus factor (dummy implementation)."""
    if not sprint or not sprint.tasks:
        return 0
    committed_points = sum(task.story_points or 0 for task in sprint.tasks)
    completed_points = sum(task.story_points or 0 for task in sprint.tasks if task.status == 'done')
    if committed_points == 0:
        return 0
    return completed_points / committed_points

def get_live_metrics(sprint_id):
    """Real-time sprint analytics"""
    sprint = Sprint.query.get(sprint_id)
    return {
        'burn_rate': calculate_burn_rate(sprint),
        'focus_factor': calculate_focus_factor(sprint),
        'risk_score': ai_engine.calculate_current_risk(sprint_id)
    }