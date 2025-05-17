"""
RLG Projects Authentication Module
Version: 2.1.0
Features: JWT Auth, AI Threat Detection, Multi-language Support, GDPR Compliance
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re
from deepseek_api import DeepseekAI
from compliance_checker import AuthCompliance
from models import User, LoginHistory, db
from utilities import (
    send_verification_email,
    send_password_reset_email,
    log_security_event,
    rate_limit,
    validate_timezone,
    sanitize_input
)
import pytz
from flask_babel import gettext as _
import socket
import geoip2.database

auth = Blueprint('auth', __name__)
ai_auth = DeepseekAI()
geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
compliance = AuthCompliance()

# --------------------------
# CORE AUTHENTICATION ROUTES
# --------------------------
@auth.route('/register', methods=['POST'])
@rate_limit(limit=5, period=900)  # 5 attempts per 15 minutes
def register():
    data = request.get_json()
    sanitized_data = sanitize_input(data)
    
    # AI-Powered Validation
    validation_result = ai_auth.validate_registration(data)
    if not validation_result['valid']:
        return jsonify({'error': validation_result['message']}), 400

    # GDPR Compliance Check
    gdpd_errors = compliance.check_gdpd_compliance(data)
    if gdpd_errors:
        return jsonify({'gdpr_errors': gdpd_errors}), 400

    existing_user = User.query.filter_by(email=sanitized_data['email']).first()
    if existing_user:
        return jsonify({'error': _('Email already exists')}), 409

    # AI Password Strength Analysis
    password_analysis = ai_auth.analyze_password_strength(sanitized_data['password'])
    if password_analysis['score'] < 3:
        return jsonify({'password_issues': password_analysis['issues']}), 400

    hashed_password = generate_password_hash(
        sanitized_data['password'], 
        method='scrypt', 
        salt_length=16
    )

    new_user = User(
        email=sanitized_data['email'],
        password=hashed_password,
        timezone=validate_timezone(sanitized_data.get('timezone', 'UTC')),
        preferred_language=sanitized_data.get('language', 'en'),
        is_verified=False,
        consent_terms=data.get('consent_terms', False),
        consent_privacy=data.get('consent_privacy', False)
    )

    db.session.add(new_user)
    db.session.commit()

    # Send AI-Personalized Welcome Email
    ai_welcome_message = ai_auth.generate_welcome_email(new_user)
    send_verification_email(new_user, ai_welcome_message)

    # Log security event
    log_security_event(
        user_id=new_user.id,
        event_type='registration',
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        success=True
    )

    return jsonify({
        'message': _('Registration successful. Verification email sent.'),
        'ai_recommendations': password_analysis.get('recommendations', [])
    }), 201

@auth.route('/login', methods=['POST'])
@rate_limit(limit=5, period=300)  # 5 attempts per 5 minutes
def login():
    data = request.get_json()
    sanitized_data = sanitize_input(data)
    
    # AI Suspicious Activity Detection
    threat_level = ai_auth.detect_login_threat(
        request.remote_addr,
        sanitized_data['email']
    )
    if threat_level > 0.7:
        return jsonify({'error': _('Suspicious activity detected')}), 403

    user = User.query.filter_by(email=sanitized_data['email']).first()
    
    # AI-Powered Account Protection
    if user and user.failed_login_attempts >= 5:
        lock_duration = ai_auth.calculate_lock_duration(user)
        if datetime.utcnow() < user.last_failed_login + timedelta(minutes=lock_duration):
            return jsonify({'error': _('Account temporarily locked')}), 423

    if not user or not check_password_hash(user.password, sanitized_data['password']):
        if user:
            user.failed_login_attempts += 1
            user.last_failed_login = datetime.utcnow()
            db.session.commit()
            
            # AI Security Recommendation
            recommendation = ai_auth.generate_lock_recommendation(user)
            log_security_event(
                user_id=user.id,
                event_type='failed_login',
                recommendations=recommendation
            )
            
        return jsonify({'error': _('Invalid credentials')}), 401

    # Geographic Analysis
    try:
        geo_data = geoip_reader.city(request.remote_addr)
        country = geo_data.country.name
        city = geo_data.city.name
    except:
        country = city = "Unknown"

    # Store Login History
    login_record = LoginHistory(
        user_id=user.id,
        ip_address=request.remote_addr,
        location=f"{city}, {country}",
        device=ai_auth.identify_device(request.user_agent.string),
        threat_level=threat_level
    )
    db.session.add(login_record)
    
    # Reset failed attempts
    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Generate JWT with AI-Optimized Claims
    additional_claims = ai_auth.generate_jwt_claims(user)
    access_token = create_access_token(
        identity=user.id,
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=ai_auth.calculate_session_duration(user))
    )

    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'timezone': user.timezone,
            'language': user.preferred_language
        },
        'security_recommendations': ai_auth.generate_login_recommendations(user)
    }), 200

# --------------------------
# AI-ENHANCED SECURITY FEATURES
# --------------------------
@auth.route('/auth/risk-assessment', methods=['GET'])
@jwt_required()
def get_risk_assessment():
    user_id = get_jwt_identity()
    risk_report = ai_auth.generate_risk_report(user_id)
    return jsonify(risk_report)

@auth.route('/auth/activity-review', methods=['GET'])
@jwt_required()
def review_account_activity():
    user_id = get_jwt_identity()
    activities = LoginHistory.query.filter_by(user_id=user_id).all()
    ai_analysis = ai_auth.analyze_login_patterns(activities)
    return jsonify({
        'activities': [activity.serialize() for activity in activities],
        'ai_insights': ai_analysis
    })

# --------------------------
# PASSWORD MANAGEMENT
# --------------------------
@auth.route('/reset-password', methods=['POST'])
@rate_limit(limit=3, period=3600)
def request_password_reset():
    email = sanitize_input(request.json.get('email', ''))
    user = User.query.filter_by(email=email).first()
    
    if user:
        # AI-Powered Security Challenge
        challenge = ai_auth.generate_security_challenge(user)
        reset_token = ai_auth.generate_secure_token()
        
        user.reset_token = generate_password_hash(reset_token)
        user.reset_expires = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()
        
        # Send AI-Personalized Reset Email
        ai_email_content = ai_auth.generate_password_reset_email(user, challenge)
        send_password_reset_email(user, ai_email_content, reset_token)

    return jsonify({'message': _('If account exists, reset instructions sent')}), 200

@auth.route('/update-password', methods=['POST'])
@jwt_required()
def update_password():
    user_id = get_jwt_identity()
    data = sanitize_input(request.get_json())
    
    # AI Password Reuse Check
    if ai_auth.detect_password_reuse(user_id, data['new_password']):
        return jsonify({'error': _('Password matches previous versions')}), 400

    user = User.query.get(user_id)
    if not check_password_hash(user.password, data['current_password']):
        return jsonify({'error': _('Current password incorrect')}), 401

    user.password = generate_password_hash(data['new_password'])
    user.password_changed = datetime.utcnow()
    db.session.commit()

    # Force logout from all devices
    ai_auth.revoke_all_tokens(user_id)

    return jsonify({'message': _('Password updated successfully')}), 200

# --------------------------
# COMPLIANCE & DATA MANAGEMENT
# --------------------------
@auth.route('/export-data', methods=['GET'])
@jwt_required()
def export_user_data():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # GDPR-compliant data export
    export_data = compliance.generate_user_data_export(user)
    return jsonify(export_data)

@auth.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    compliance.process_account_deletion(user_id)
    return jsonify({'message': _('Account scheduled for deletion')}), 202

# --------------------------
# RLG AGENT INTEGRATION
# --------------------------
@auth.route('/auth/assistant', methods=['POST'])
@jwt_required()
def auth_assistant():
    user_id = get_jwt_identity()
    user_message = sanitize_input(request.json.get('message', ''))
    
    # Context-aware AI Assistant
    response = ai_auth.handle_auth_query(
        user_id=user_id,
        query=user_message,
        jwt_data=get_jwt()
    )
    
    return jsonify({
        'response': response['text'],
        'actions': response.get('actions', []),
        'security_check': response.get('security_level', 0)
    })

# --------------------------
# SECURITY MIDDLEWARE
# --------------------------
@auth.after_request
def add_security_headers(response):
    # AI-Optimized Security Headers
    headers = ai_auth.generate_security_headers(request)
    for key, value in headers.items():
        response.headers[key] = value
    return response