"""
RLG Project Management API Core - Scrum Automation Endpoints
Version: 12.0.0
Features: Full Scrum Workflow, AI Recommendations, Multi-Team Support
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from models import Project, Sprint, BacklogItem, Team, db
from deepseek_api import DeepseekAPI
from compliance_checker import ScrumGuideValidator
from report_generator import generate_project_report
from utilities import (
    validate_project_data,
    calculate_velocity,
    apply_timezone_to_dates,
    log_activity
)
from config import get_config
from datetime import datetime
import pytz
import logging
from compliance_checker import ComplianceHandler

compliance_handler = ComplianceHandler()
projects = Blueprint('projects', __name__)
ai_engine = DeepseekAPI()
validator = ScrumGuideValidator()
config = get_config()
logger = logging.getLogger('RLG.Projects')

@projects.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    """Create new project with AI-optimized defaults"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate and enhance with AI
        errors = validate_project_data(data)
        if errors:
            return jsonify({"errors": errors}), 400
            
        ai_recommendations = ai_engine.generate_project_recommendations(data)
        
        # Create project with localized settings
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            owner_id=user_id,
            default_language=data.get('language', 'en'),
            supported_timezones=data.get('timezones', ['UTC']),
            ai_settings=ai_recommendations['settings']
        )
        
        db.session.add(project)
        db.session.commit()
        
        # Initial AI setup
        ai_engine.initialize_project_ai(project.id)
        
        log_activity(user_id, 'project_create', project.id)
        
        return jsonify({
            "message": "Project created",
            "project": project.to_dict(),
            "ai_recommendations": ai_recommendations
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Project creation failed: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@projects.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """Get paginated projects with AI-enhanced insights"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Project.query.filter_by(owner_id=user_id)
        projects = query.paginate(page=page, per_page=per_page)
        
        # Add AI insights
        enhanced_projects = []
        for project in projects.items:
            project_data = project.to_dict()
            project_data['ai_health_check'] = ai_engine.analyze_project_health(project.id)
            enhanced_projects.append(project_data)
        
        return jsonify({
            "projects": enhanced_projects,
            "total": projects.total,
            "page": projects.page,
            "per_page": projects.per_page
        })
        
    except Exception as e:
        logger.error(f"Project retrieval error: {str(e)}")
        return jsonify({"error": "Project loading failed"}), 500

@projects.route('/projects/<int:project_id>/sprints', methods=['POST'])
@jwt_required()
def create_sprint(project_id):
    """Create Scrum-compliant sprint with AI planning"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate against Scrum Guide
        compliance_errors = validator.validate_sprint(data)
        if compliance_errors:
            return jsonify({"scrum_errors": compliance_errors}), 400
        
        # Calculate dates with timezone
        tz = pytz.timezone(data['timezone'])
        start_date = apply_timezone_to_dates(data['start_date'], tz)
        end_date = apply_timezone_to_dates(data['end_date'], tz)
        
        # Create sprint
        sprint = Sprint(
            name=data['name'],
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            ai_recommendations=ai_engine.generate_sprint_plan(data)
        )
        
        db.session.add(sprint)
        db.session.commit()
        
        # Auto-generate initial backlog
        if data.get('generate_backlog'):
            ai_backlog = ai_engine.generate_initial_backlog(project_id)
            create_backlog_items(project_id, ai_backlog)
        
        log_activity(user_id, 'sprint_create', sprint.id)
        
        return jsonify({
            "message": "Sprint created",
            "sprint": sprint.to_dict(),
            "ai_warnings": ai_engine.check_sprint_risks(sprint.id)
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Sprint creation failed: {str(e)}")
        return jsonify({"error": "Sprint setup error"}), 500

@projects.route('/projects/<int:project_id>/backlog', methods=['POST'])
@jwt_required()
def create_backlog_item(project_id):
    """Add prioritized backlog item with AI scoring"""
    try:
        data = request.get_json()
        
        # Calculate priority score
        priority_score = ai_engine.calculate_priority(
            data['business_value'],
            data['technical_complexity']
        )
        
        item = BacklogItem(
            title=data['title'],
            description=data['description'],
            project_id=project_id,
            business_value=data['business_value'],
            technical_complexity=data['technical_complexity'],
            ai_priority_score=priority_score
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            "message": "Backlog item added",
            "item": item.to_dict(),
            "ai_recommendation": ai_engine.suggest_item_refinement(item.id)
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Backlog creation failed: {str(e)}")
        return jsonify({"error": "Backlog item error"}), 500

@projects.route('/projects/<int:project_id>/reports', methods=['GET'])
@jwt_required()
def generate_project_report(project_id):
    """Generate comprehensive project report with AI insights"""
    try:
        report_type = request.args.get('type', 'executive')
        
        # Generate base report
        report = generate_project_report(project_id, report_type)
        
        # Enhance with AI analysis
        ai_analysis = ai_engine.analyze_project_report(report)
        report['ai_insights'] = ai_analysis
        
        # Add compliance status
        report['compliance'] = validator.check_project_compliance(project_id)
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return jsonify({"error": "Report generation error"}), 500

@projects.route('/projects/<int:project_id>/ai-recommendations', methods=['GET'])
@jwt_required()
def get_ai_recommendations(project_id):
    """Get real-time AI optimization suggestions"""
    try:
        recommendations = ai_engine.generate_project_recommendations(project_id)
        return jsonify({
            "automation_ideas": recommendations['automation'],
            "risk_mitigations": recommendations['risks'],
            "team_optimization": recommendations['team'],
            "compliance_suggestions": recommendations['compliance']
        })
        
    except Exception as e:
        logger.error(f"AI recommendations failed: {str(e)}")
        return jsonify({"error": "AI service error"}), 500

@projects.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """GDPR-compliant project deletion"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Compliance checks
        if not validator.validate_deletion(project):
            return jsonify({"error": "Active sprints exist"}), 400
            
        # Anonymize data
        compliance_handler.anonymize_project_data(project_id)
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({"message": "Project deleted"}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Project deletion failed: {str(e)}")
        return jsonify({"error": "Deletion error"}), 500

# Helper functions
def create_backlog_items(project_id, items):
    """Batch create AI-generated backlog items"""
    try:
        for item in items:
            backlog_item = BacklogItem(
                title=item['title'],
                description=item['description'],
                project_id=project_id,
                ai_priority_score=item['priority_score']
            )
            db.session.add(backlog_item)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Batch backlog creation failed: {str(e)}")