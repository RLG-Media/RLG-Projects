"""
RLG AI Prompt Engineering Core - Scrum Optimization Templates
Version: 5.1.0
Features: 150+ Scrum-specific prompts, Multi-cultural Adaptation, Context-Aware Generation
"""

from datetime import datetime
import pytz

class ScrumPrompts:
    # --------------------------
    # CORE SCRUM WORKFLOW PROMPTS
    # --------------------------
    @staticmethod
    def sprint_planning_template(project_context, team_profile):
        """AI prompt for automated sprint planning with capacity awareness"""
        return f"""
        Act as an expert Scrum Master with 15 years experience. Generate a sprint plan for:
        Project: {project_context['name']}
        Team Capacity: {team_profile['available_hours']} hours
        Historical Velocity: {project_context['velocity']}
        Backlog Items: {len(project_context['backlog']}
        
        Consider these factors:
        1. Team skills: {team_profile['skills']}
        2. Priority items: {project_context['priority_items']}
        3. Dependencies: {project_context['dependencies']}
        4. Timezone distribution: {team_profile['timezones']}
        
        Format output as JSON with:
        - sprint_goal
        - committed_items (list)
        - risk_assessment
        - recommended_pairings
        - timezone_optimized_schedule
        """

    @staticmethod
    def daily_standup_prompt(sprint_data, yesterday_metrics):
        """Context-aware daily standup agenda generation"""
        return f"""
        Generate a daily scrum agenda for {datetime.now().strftime('%Y-%m-%d')}
        Sprint: {sprint_data['name']}
        Current Progress: {sprint_data['progress']}%
        Yesterday's Metrics:
        - Completed: {yesterday_metrics['completed_tasks']}
        - Blockers: {yesterday_metrics['blockers']}
        - WIP: {yesterday_metrics['wip_tasks']}
        
        Include:
        1. Focus areas for today
        2. Blocker resolution suggestions
        3. Team motivation quote based on progress
        4. Timezone-adjusted availability reminders
        5. Compliance checkpoints from Scrum Guide
        
        Format: Markdown with emoji visualization
        """

    # --------------------------
    # RETROSPECTIVE & REVIEW PROMPTS
    # --------------------------
    @staticmethod
    def retrospective_analysis(sprint_metrics, team_sentiment):
        """Multi-factor retrospective prompt"""
        return f"""
        Analyze sprint performance and generate improvement actions:
        Metrics:
        - Velocity: {sprint_metrics['velocity']}
        - Burndown: {sprint_metrics['burndown']}
        - Defect Rate: {sprint_metrics['defect_rate']}
        Team Sentiment: {team_sentiment}
        
        Provide:
        1. Three key achievements
        2. Two improvement areas
        3. Actionable solutions for next sprint
        4. Cultural considerations for {sprint_metrics['team_locations']}
        5. Process compliance scorecard
        
        Present in table format with priority levels
        """

    # --------------------------
    # COMPLIANCE & BEST PRACTICES
    # --------------------------
    @staticmethod
    def compliance_check_prompt(sprint_data, scrum_guide_version):
        """Automated Scrum Guide compliance verification"""
        return f"""
        Verify compliance with Scrum Guide {scrum_guide_version} for:
        Sprint: {sprint_data['name']}
        Duration: {sprint_data['duration']} days
        Team Size: {sprint_data['team_size']}
        Artifacts: {sprint_data['artifacts_used']}
        
        Check:
        1. Event timeboxes
        2. Role responsibilities
        3. Artifact completeness
        4. Definition of Done adherence
        5. Value delivery metrics
        
        Output format:
        - Compliance score (0-100)
        - Critical violations
        - Improvement suggestions
        - Automated correction scripts
        """

    # --------------------------
    # CROSS-CULTURAL COMMUNICATION
    # --------------------------
    @staticmethod
    def localized_communication(context, recipient_profile):
        """Culture-aware communication prompts"""
        return f"""
        Generate {recipient_profile['language']} message for:
        Context: {context['purpose']}
        Recipient Culture: {recipient_profile['cultural_background']}
        Timezone: {recipient_profile['timezone']}
        Preferred Communication Style: {recipient_profile['comm_style']}
        
        Include:
        1. Local time references
        2. Culturally appropriate greetings
        3. Contextual metaphor/examples
        4. Action items with localized urgency indicators
        5. Scrum terminology in {recipient_profile['language']}
        """

    # --------------------------
    # AI AGENT & CHATBOT PROMPTS
    # --------------------------
    @staticmethod
    def rlg_agent_base_persona():
        """Define RLG Agent's personality and capabilities"""
        return """
        You are RLG Agent - an AI Scrum Master assistant. Your characteristics:
        1. Always follows Scrum Guide 2020 principles
        2. Adapts communication style to user's role (dev/PO/stakeholder)
        3. Proactive in identifying process improvements
        4. Maintains professional yet empathetic tone
        5. Provides options rather than directives
        
        Response guidelines:
        - Use bullet points for complex information
        - Include emojis for emotional intelligence
        - Add cultural context markers
        - Reference team's historical data
        - Suggest multiple solutions when appropriate
        """

    # --------------------------
    # REPORTING & ANALYTICS
    # --------------------------
    @staticmethod
    def executive_report_prompt(sprint_data, strategic_goals):
        """C-level sprint reporting template"""
        return f"""
        Generate executive summary for {sprint_data['name']}:
        Business Goals: {strategic_goals}
        Technical Metrics:
        - Velocity: {sprint_data['velocity']}
        - ROI: {sprint_data['roi']}
        - Risk Exposure: {sprint_data['risk']}
        
        Include:
        1. Goal alignment analysis
        2. Investment recommendations
        3. Team health assessment
        4. Market comparison
        5. Visualizations suggestions
        """

    # --------------------------
    # RISK MANAGEMENT
    # --------------------------
    @staticmethod
    def risk_prediction_prompt(project_data, risk_history):
        """Predictive risk modeling prompt"""
        return f"""
        Predict risks for upcoming sprint using:
        Project History: {risk_history}
        Team Composition: {project_data['team']}
        Backlog Complexity: {project_data['backlog_complexity']}
        Dependencies: {project_data['dependencies']}
        
        Output format:
        1. Top 3 predicted risks (probability & impact)
        2. Early warning indicators
        3. Mitigation playbook
        4. Fallback scenarios
        5. Team-specific preparation exercises
        """

    # --------------------------
    # ONBOARDING & TRAINING
    # --------------------------
    @staticmethod
    def role_based_onboarding(user_role, team_profile):
        """Personalized onboarding prompt"""
        return f"""
        Create {user_role} onboarding plan for team: 
        Team Size: {team_profile['size']}
        Domain: {team_profile['domain']}
        Tools: {team_profile['tools']}
        
        Include:
        1. First-week checklist
        2. Key artifact templates
        3. Team communication norms
        4. Role-specific Scrum Guide highlights
        5. Cultural adaptation tips for {team_profile['location']}
        """

    # --------------------------
    # CONTINUOUS IMPROVEMENT
    # --------------------------
    @staticmethod
    def process_improvement_prompt(historical_data, industry_benchmarks):
        """Kaizen-style improvement generator"""
        return f"""
        Suggest process improvements based on:
        Team Historical Data: {historical_data}
        Industry Benchmarks: {industry_benchmarks}
        
        Requirements:
        1. List 5 experiment ideas
        2. Include metrics tracking plan
        3. Provide implementation steps
        4. Predict outcome impact
        5. Add risk assessment
        """

    # --------------------------
    # CROSS-PLATFORM INTEGRATION
    # --------------------------
    @staticmethod
    def tool_integration_prompt(tool_list, current_workflow):
        """Workflow automation prompt"""
        return f"""
        Design integration strategy for tools: {tool_list}
        Existing Workflow: {current_workflow}
        
        Output:
        1. Automation opportunities
        2. Data flow diagram
        3. Error handling strategy
        4. Compliance considerations
        5. Team training plan
        """

    # --------------------------
    # CRISIS MANAGEMENT
    # --------------------------
    @staticmethod
    def blocker_resolution_prompt(blocker_details, team_context):
        """Critical issue resolution prompt"""
        return f"""
        Generate emergency response plan for:
        Blocker: {blocker_details}
        Team Capacity: {team_context['capacity']}
        Sprint Timeline: {team_context['timeline']}
        
        Include:
        1. Short-term workaround
        2. Long-term solution
        3. Stakeholder communication plan
        4. Progress recovery strategy
        5. Post-mortem preparation
        """