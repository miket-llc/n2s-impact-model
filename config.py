"""
Configuration file for N2S Efficiency Modeling Application
Contains defaults, constants, and helper functions
"""

from typing import Dict, Tuple

# =============================================================================
# PROJECT DEFAULTS
# =============================================================================

# Version tracking for deployment verification
APP_VERSION = "v4.2.0 - Final: 25% Target with Operational Efficiency Component (Oct 17, 2025)"

# Default project parameters
DEFAULT_TOTAL_HOURS = 17054
DEFAULT_BLENDED_RATE = 100  # $/hour

# Default phase allocation percentages (must sum to 100)
DEFAULT_PHASE_ALLOCATION = {
    'Discover': 5,
    'Plan': 10, 
    'Design': 15,
    'Build': 25,
    'Test': 20,
    'Deploy': 10,
    'Post Go-Live': 15
}

# Phase order for consistent display
PHASE_ORDER = [
    'Discover', 'Plan', 'Design', 'Build', 
    'Test', 'Deploy', 'Post Go-Live'
]

# Default risk weight multipliers per phase
DEFAULT_RISK_WEIGHTS = {
    'Discover': 1,
    'Plan': 2,
    'Design': 3,
    'Build': 4,
    'Test': 5,
    'Deploy': 6,
    'Post Go-Live': 7
}

# Risk level definitions and guidelines
RISK_LEVEL_DEFINITIONS = {
    "general": {
        "description": (
            "Risk weights multiply your modeled hours to account for project "
            "complexity, team experience, and potential issues. Higher weights "
            "= more conservative estimates."
        ),
        "0.5": "Very low risk - Simple, well-understood work",
        "1.0": "Low risk - Standard complexity, experienced team",
        "2.0": "Moderate risk - Some complexity or unknowns",
        "3.0": "Medium-high risk - Significant complexity",
        "5.0": "High risk - Major complexity, new technology",
        "7.0": "Very high risk - Critical path, many unknowns",
        "10.0": "Maximum risk - Experimental, high uncertainty"
    },
    "phases": {
        "Discover": {
            "description": (
                "Requirements gathering, stakeholder alignment, scope definition"
            ),
            "typical_risks": [
                "Unclear or changing requirements",
                "Stakeholder availability and alignment", 
                "Scope creep potential",
                "Business process complexity"
            ],
            "low_risk": "Well-defined project with clear requirements",
            "high_risk": (
                "Complex business transformation with unclear scope"
            )
        },
        "Plan": {
            "description": (
                "Project planning, resource allocation, timeline development"
            ),
            "typical_risks": [
                "Resource availability constraints",
                "Dependency management complexity",
                "Timeline optimization challenges", 
                "Cross-team coordination needs"
            ],
            "low_risk": "Standard project with available resources",
            "high_risk": "Multi-team project with resource constraints"
        },
        "Design": {
            "description": (
                "Architecture design, technical specifications, UI/UX design"
            ),
            "typical_risks": [
                "Technical architecture complexity",
                "Integration design challenges",
                "Performance requirements",
                "Scalability considerations"
            ],
            "low_risk": "Standard design patterns and proven architecture",
            "high_risk": (
                "New architecture or complex integration requirements"
            )
        },
        "Build": {
            "description": (
                "Code development, component creation, feature implementation"
            ),
            "typical_risks": [
                "Technical implementation complexity",
                "Third-party integration challenges",
                "Code quality and maintainability",
                "Team skill gaps"
            ],
            "low_risk": "Standard development with experienced team",
            "high_risk": "Complex features with new technology stack"
        },
        "Test": {
            "description": (
                "Testing execution, defect resolution, quality assurance"
            ),
            "typical_risks": [
                "Test environment stability",
                "Complex test scenario coverage",
                "Integration testing challenges",
                "Performance testing complexity"
            ],
            "low_risk": "Well-automated testing with stable environments",
            "high_risk": "Complex integration testing with manual processes"
        },
        "Deploy": {
            "description": (
                "Production deployment, release management, go-live activities"
            ),
            "typical_risks": [
                "Production environment issues",
                "Data migration complexity",
                "Rollback procedure needs",
                "User training and adoption"
            ],
            "low_risk": "Standard deployment with proven processes",
            "high_risk": "Complex migration with high business impact"
        },
        "Post Go-Live": {
            "description": (
                "Production support, issue resolution, user adoption"
            ),
            "typical_risks": [
                "Production support complexity",
                "User adoption challenges",
                "Performance optimization needs",
                "Ongoing maintenance requirements"
            ],
            "low_risk": "Standard support for familiar system",
            "high_risk": "Complex system with high support demands"
        }
    }
}

def get_risk_level_description(weight: float) -> str:
    """Get description for a specific risk weight level"""
    definitions = RISK_LEVEL_DEFINITIONS["general"]
    
    if weight <= 0.7:
        return definitions["0.5"]
    elif weight <= 1.2:
        return definitions["1.0"]
    elif weight <= 2.5:
        return definitions["2.0"]
    elif weight <= 4.0:
        return definitions["3.0"]
    elif weight <= 6.0:
        return definitions["5.0"]
    elif weight <= 8.0:
        return definitions["7.0"]
    else:
        return definitions["10.0"]

def get_phase_risk_info(phase: str) -> dict:
    """Get risk information for a specific phase"""
    if phase in RISK_LEVEL_DEFINITIONS["phases"]:
        return RISK_LEVEL_DEFINITIONS["phases"][phase]
    return {
        "description": f"Risk factors for {phase} phase",
        "typical_risks": [],
        "low_risk": "Standard complexity",
        "high_risk": "High complexity"
    }

# =============================================================================
# MATURITY ASSESSMENT FRAMEWORK (CMMI-inspired)
# =============================================================================

MATURITY_LEVELS = {
    1: {
        "name": "Ad-hoc/Manual",
        "description": "Processes are unpredictable, poorly controlled, and reactive",
        "automation_characteristics": {
            "test_automation": "0-20%",
            "ci_cd": "Manual deployments",
            "code_reuse": "0-10%", 
            "documentation": "Manual/inconsistent",
            "environment_management": "Manual setup"
        },
        "savings_potential_range": [5, 8],
        "typical_savings": 6.5
    },
    2: {
        "name": "Repeatable", 
        "description": "Processes are characterized for projects and often reactive",
        "automation_characteristics": {
            "test_automation": "20-40%",
            "ci_cd": "Basic automated builds",
            "code_reuse": "10-25%",
            "documentation": "Templates used",
            "environment_management": "Some standardization"
        },
        "savings_potential_range": [8, 12],
        "typical_savings": 10
    },
    3: {
        "name": "Defined",
        "description": "Processes are characterized for organization and proactive", 
        "automation_characteristics": {
            "test_automation": "40-65%",
            "ci_cd": "Automated testing in pipeline",
            "code_reuse": "25-40%",
            "documentation": "Standardized and automated",
            "environment_management": "Standardized environments"
        },
        "savings_potential_range": [12, 18],
        "typical_savings": 15
    },
    4: {
        "name": "Managed",
        "description": "Processes are measured and controlled",
        "automation_characteristics": {
            "test_automation": "65-85%", 
            "ci_cd": "Full deployment automation",
            "code_reuse": "40-60%",
            "documentation": "Generated and maintained",
            "environment_management": "Infrastructure as Code"
        },
        "savings_potential_range": [18, 25],
        "typical_savings": 21.5
    },
    5: {
        "name": "Optimizing",
        "description": "Focus on continuous process improvement",
        "automation_characteristics": {
            "test_automation": "85%+",
            "ci_cd": "Self-healing pipelines",
            "code_reuse": "60%+",
            "documentation": "AI-assisted and self-updating",
            "environment_management": "Fully automated and optimized"
        },
        "savings_potential_range": [25, 30],
        "typical_savings": 27.5
    }
}

# Automation Assessment Questions
AUTOMATION_ASSESSMENT = {
    "test_automation_coverage": {
        "question": "What percentage of your testing is currently automated?",
        "type": "slider",
        "min_value": 0,
        "max_value": 100,
        "default": 30,
        "weight": 0.3,
        "help": "Include unit tests, integration tests, and regression testing"
    },
    "ci_cd_maturity": {
        "question": "Current CI/CD automation level:",
        "type": "selectbox",
        "options": [
            "Manual deployments",
            "Basic build automation", 
            "Automated testing in pipeline",
            "Full deployment automation",
            "Self-healing pipelines"
        ],
        "default": 1,
        "weight": 0.25,
        "help": "How automated is your build and deployment process?"
    },
    "code_reuse_level": {
        "question": "What percentage of code/components do you typically reuse across projects?",
        "type": "slider", 
        "min_value": 0,
        "max_value": 80,
        "default": 20,
        "weight": 0.2,
        "help": "Shared libraries, components, APIs, and integration patterns"
    },
    "environment_automation": {
        "question": "Environment management maturity:",
        "type": "selectbox",
        "options": [
            "Manual environment setup",
            "Some scripted setup",
            "Standardized environments", 
            "Infrastructure as Code",
            "Fully automated and optimized"
        ],
        "default": 1,
        "weight": 0.15,
        "help": "How are development, test, and production environments managed?"
    },
    "documentation_automation": {
        "question": "Documentation and knowledge management:",
        "type": "selectbox",
        "options": [
            "Manual documentation",
            "Template-based documentation",
            "Some automated generation",
            "Mostly automated documentation",
            "AI-assisted and self-updating"
        ],
        "default": 1,
        "weight": 0.1,
        "help": "How is project documentation created and maintained?"
    }
}

def assess_current_maturity(assessment_responses: dict) -> dict:
    """
    Calculate current maturity level based on assessment responses
    
    Args:
        assessment_responses: Dict with user responses to assessment questions
        
    Returns:
        Dict with maturity analysis and savings potential
    """
    total_score = 0.0
    max_score = 0.0
    
    for question_key, response in assessment_responses.items():
        if question_key in AUTOMATION_ASSESSMENT:
            question_config = AUTOMATION_ASSESSMENT[question_key]
            weight = question_config['weight']
            
            if question_config['type'] == 'slider':
                # Normalize slider values to 0-1 scale
                score = response / 100.0
            elif question_config['type'] == 'selectbox':
                # Convert selectbox value to index, then to 0-1 scale
                options = question_config['options']
                if response in options:
                    response_index = options.index(response)
                    max_options = len(options) - 1
                    score = response_index / max_options if max_options > 0 else 0
                else:
                    score = 0
            
            total_score += score * weight
            max_score += weight
    
    # Calculate maturity level (1-5 scale)
    normalized_score = total_score / max_score if max_score > 0 else 0
    maturity_level = min(5, max(1, int(normalized_score * 4) + 1))
    
    # Get maturity level details
    level_info = MATURITY_LEVELS[maturity_level]
    
    # Calculate realistic savings potential based on current state
    min_savings, max_savings = level_info['savings_potential_range']
    
    # Fine-tune based on specific automation scores
    test_auto_boost = (assessment_responses.get('test_automation_coverage', 30) - 30) * 0.1
    
    # Convert CI/CD response to index for boost calculation
    cicd_response = assessment_responses.get('ci_cd_maturity', 'Basic build automation')
    cicd_options = AUTOMATION_ASSESSMENT['ci_cd_maturity']['options']
    if cicd_response in cicd_options:
        cicd_index = cicd_options.index(cicd_response)
    else:
        cicd_index = 1  # Default to basic level
    cicd_boost = (cicd_index - 1) * 0.5
    
    adjusted_savings = level_info['typical_savings'] + test_auto_boost + cicd_boost
    realistic_max = min(max_savings, max(min_savings, adjusted_savings))
    
    return {
        'maturity_level': maturity_level,
        'maturity_name': level_info['name'],
        'maturity_description': level_info['description'],
        'automation_characteristics': level_info['automation_characteristics'],
        'current_savings_potential': realistic_max,
        'savings_range': [min_savings, max_savings],
        'assessment_score': normalized_score,
        'improvement_areas': _identify_improvement_areas(assessment_responses)
    }

def _identify_improvement_areas(responses: dict) -> list:
    """Identify areas with lowest scores for improvement recommendations"""
    areas = []
    for question_key, response in responses.items():
        if question_key in AUTOMATION_ASSESSMENT:
            question_config = AUTOMATION_ASSESSMENT[question_key]
            if question_config['type'] == 'slider' and response < 50:
                areas.append(question_key)
            elif question_config['type'] == 'selectbox':
                # Convert string response to index for comparison
                options = question_config['options']
                if response in options:
                    response_index = options.index(response)
                    if response_index < 2:  # First 2 levels are low
                        areas.append(question_key)
    return areas

def calculate_target_feasibility(current_maturity: dict, target_savings: float, 
                               selected_initiatives: list) -> dict:
    """
    Determine if target savings is feasible given current state and initiatives
    
    Args:
        current_maturity: Output from assess_current_maturity()
        target_savings: Desired savings percentage
        selected_initiatives: List of selected N2S initiatives
        
    Returns:
        Dict with feasibility analysis and recommendations
    """
    current_potential = current_maturity['current_savings_potential']
    
    # Calculate initiative boost potential
    initiative_boost = len(selected_initiatives) * 1.5  # Rough estimate: 1.5% per initiative
    
    # Calculate total potential with initiatives
    total_potential = current_potential + initiative_boost
    
    feasible = target_savings <= total_potential
    
    if not feasible:
        # Find what maturity level would be needed
        required_level = 5
        for level in range(1, 6):
            level_max = MATURITY_LEVELS[level]['savings_potential_range'][1]
            if target_savings <= level_max + initiative_boost:
                required_level = level
                break
    else:
        required_level = current_maturity['maturity_level']
    
    return {
        'feasible': feasible,
        'current_potential': current_potential,
        'total_potential_with_initiatives': total_potential,
        'gap': max(0, target_savings - total_potential),
        'required_maturity_level': required_level,
        'required_maturity_name': MATURITY_LEVELS[required_level]['name'],
        'recommendations': _generate_recommendations(current_maturity, required_level)
    }

def _generate_recommendations(current_maturity: dict, target_level: int) -> list:
    """Generate specific recommendations to reach target maturity level"""
    recommendations = []
    current_level = current_maturity['maturity_level']
    
    if target_level <= current_level:
        return ["Your current maturity level is sufficient for this target"]
    
    improvement_areas = current_maturity['improvement_areas']
    
    if 'test_automation_coverage' in improvement_areas:
        recommendations.append("Increase automated test coverage to 60%+ (current focus area)")
    
    if 'ci_cd_maturity' in improvement_areas:
        recommendations.append("Implement full CI/CD pipeline with automated deployments")
    
    if 'code_reuse_level' in improvement_areas:
        recommendations.append("Develop reusable component library (target 40%+ reuse)")
    
    if target_level >= 4:
        recommendations.append("Implement Infrastructure as Code for environment management")
        recommendations.append("Add comprehensive monitoring and measurement systems")
    
    if target_level >= 5:
        recommendations.append("Focus on continuous optimization and AI-assisted processes")
    
    return recommendations

# Remove old hardcoded SCENARIOS - keeping for reference only
SCENARIOS_LEGACY = {
    'Target: ~10% Savings': {
        'base_factor': 1.0,
        'description': (
            'Conservative improvements with proven, low-risk approaches. '
            'Light automation enhancements to achieve ~10% total project savings '
            '(without cost avoidance)'
        )
    },
    'Target: ~20% Savings': {
        'base_factor': 1.0,
        'additional_factor': 1.0,
        'description': ('Moderate automation improvements with enhanced testing '
                        'and quality practices to achieve ~20% total project savings '
                        '(without cost avoidance)')
    },
    'Target: ~30% Savings': {
        'base_factor': 1.0,
        'additional_factor': 1.5,
        'max_savings_caps': {
            'Discover': 0.50,
            'Plan': 0.55,
            'Design': 0.60,
            'Build': 0.65,
            'Test': 0.80,
            'Deploy': 0.60,
            'Post Go-Live': 0.85
        },
        'description': ('Aggressive automation transformation with comprehensive '
                        'N2S implementation to achieve ~30% total project savings '
                        '(without cost avoidance)')
    }
}

# Cost avoidance multiplier options based on industry research
COST_AVOIDANCE_OPTIONS = {
    'None (0x)': {
        'multiplier': 0.0,
        'ongoing_factor': 0.0,
        'description': 'No cost avoidance - development savings only'
    },
    'Minimal (0.5x)': {
        'multiplier': 0.5,
        'ongoing_factor': 0.25,  # 25% of dev savings as ongoing avoidance
        'description': 'Very conservative long-term benefits'
    },
    'Conservative (1.5x)': {
        'multiplier': 1.5,
        'ongoing_factor': 0.5,  # 50% of dev savings as ongoing avoidance
        'description': 'Minimal long-term benefits, risk-averse estimate'
    },
    'Moderate (2.5x)': {
        'multiplier': 2.5,
        'ongoing_factor': 0.8,  # 80% of dev savings as ongoing avoidance  
        'description': 'Typical shift-left benefits, industry average'
    },
    'Aggressive (4x)': {
        'multiplier': 4.0,
        'ongoing_factor': 1.2,  # 120% of dev savings as ongoing avoidance
        'description': 'High-maturity organization with strong processes'
    },
    'Maximum (6x)': {
        'multiplier': 6.0,
        'ongoing_factor': 1.5,  # 150% of dev savings as ongoing avoidance
        'description': 'Best-case scenario with full DevOps maturity'
    }
}

# =============================================================================
# INDUSTRY BENCHMARK CONSTANTS
# =============================================================================

# Research-based improvement factors for validation
INDUSTRY_BENCHMARKS = {
    'test_automation_cost_reduction': 0.15,  # 15% from Gartner/Forrester
    'quality_improvement': 0.20,  # 20% quality improvement
    'post_release_defect_reduction': 0.25,  # 25% from McKinsey
    'testing_phase_reduction': 0.45,  # 30-50% from Perfecto/Testlio (increased)
    'manual_testing_reduction': 0.40,  # 35-45% manual testing reduction (increased)
    'defect_fix_cost_multipliers': {
        'unit_test': 10,
        'system_test': 40, 
        'production': 70
    }
}

# Maximum credible total cost reduction (updated for N2S reality)
MAX_TOTAL_COST_REDUCTION = 0.50  # 50% for aggressive N2S implementations

# =============================================================================
# INITIATIVE DEFINITIONS
# =============================================================================

# Authoritative initiative list from Excel Sheet: 10pct_Savings
INITIATIVE_FALLBACK = [
    "Modernization Studio",
    "AI/Automation", 
    "N2S CARM",
    "Preconfigured Envs",
    "Automated Testing",
    "EDCC",
    "Integration Code Reuse",
    "Agile + DevOps Practices"  # NEW: Operational efficiency lever
]

# Maturity level definitions for each initiative
INITIATIVE_MATURITY_DEFINITIONS = {
    "Modernization Studio": {
        "description": "Ellucian's modern development platform and tooling",
        "0%": "No use of Modernization Studio tools",
        "25%": "Basic setup, occasional use for simple tasks",
        "50%": "Regular use for standard development, some team training",
        "75%": "Well-integrated into workflow, most developers proficient",
        "100%": "Fully adopted, optimized workflows, advanced features used"
    },
    "AI/Automation": {
        "description": "AI-powered code generation, automated workflows, and intelligent tooling",
        "0%": "No AI/automation tools in development process",
        "25%": "Basic AI code suggestions, simple automation scripts",
        "50%": "Regular use of AI coding assistants, some automated workflows",
        "75%": "Advanced AI integration, automated testing/deployment pipelines",
        "100%": "Full AI-driven development, comprehensive automation ecosystem"
    },
    "N2S CARM": {
        "description": "Navigate-to-SaaS Change and Release Management processes", 
        "0%": "Traditional manual change management",
        "25%": "Basic N2S processes documented, limited adoption", 
        "50%": "Standard N2S workflows in place, team partially trained",
        "75%": "Well-established processes, good compliance and metrics",
        "100%": "Optimized N2S CARM, full automation, continuous improvement"
    },
    "Preconfigured Envs": {
        "description": "Pre-built development, testing, and deployment environments",
        "0%": "Manual environment setup for each project",
        "25%": "Some standardized environments, mostly manual setup",
        "50%": "Standard pre-configured environments available and used",
        "75%": "Comprehensive environment library, automated provisioning",
        "100%": "Fully automated, optimized environments with instant deployment"
    },
    "Automated Testing": {
        "description": "Automated unit, integration, and end-to-end testing frameworks",
        "0%": "Primarily manual testing processes",
        "25%": "Basic unit tests, some automation for critical paths",
        "50%": "Good test coverage, automated regression testing",
        "75%": "Comprehensive test automation, CI/CD integration",
        "100%": "Full test automation, AI-driven testing, performance optimization"
    },
    "EDCC": {
        "description": "Ellucian Data Center Cloud infrastructure and services",
        "0%": "On-premise infrastructure, manual deployments",
        "25%": "Basic cloud migration, some EDCC services adopted",
        "50%": "Standard EDCC deployment, cloud-native development",
        "75%": "Advanced EDCC features, optimized cloud architecture",
        "100%": "Full EDCC optimization, serverless, auto-scaling"
    },
    "Integration Code Reuse": {
        "description": "Standardized integration patterns, reusable components and APIs",
        "0%": "Custom integrations built from scratch each time",
        "25%": "Some common patterns documented, limited reuse",
        "50%": "Standard integration library, moderate component reuse",
        "75%": "Comprehensive reusable component library, good adoption",
        "100%": "Fully optimized integration platform, API-first, maximum reuse"
    },
    "Agile + DevOps Practices": {
        "description": "Agile ceremonies, DevOps culture, continuous improvement, collaboration tools",
        "0%": "Waterfall-style delivery, siloed teams, infrequent releases",
        "25%": "Basic Agile adoption, some DevOps practices, improving collaboration",
        "50%": "Mature Agile/Scrum, good DevOps practices, automated pipelines",
        "75%": "Advanced Agile at scale, strong DevOps culture, continuous delivery",
        "100%": "Optimized flow, blameless culture, continuous deployment, data-driven improvement"
    }
}

# Helper function to get maturity level description
def get_maturity_description(initiative: str, level: int) -> str:
    """Get description for a specific maturity level of an initiative"""
    if initiative not in INITIATIVE_MATURITY_DEFINITIONS:
        return f"{level}% maturity"
    
    definitions = INITIATIVE_MATURITY_DEFINITIONS[initiative]
    
    # Find the closest defined level
    if level == 0:
        return definitions["0%"]
    elif level <= 25:
        return definitions["25%"]
    elif level <= 50:
        return definitions["50%"]
    elif level <= 75:
        return definitions["75%"]
    else:
        return definitions["100%"]

def get_initiative_description(initiative: str) -> str:
    """Get the main description of an initiative"""
    if initiative in INITIATIVE_MATURITY_DEFINITIONS:
        return INITIATIVE_MATURITY_DEFINITIONS[initiative]["description"]
    return f"Efficiency initiative: {initiative}"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def validate_phase_allocation(allocation: Dict[str, float]) -> bool:
    """Validate that phase allocation percentages sum to 100"""
    total = sum(allocation.values())
    return abs(total - 100.0) < 0.01  # Allow small floating point errors

def get_phase_colors() -> Dict[str, str]:
    """Return consistent color scheme for phases"""
    colors = [
        '#FF6B6B',  # Discover - Red
        '#4ECDC4',  # Plan - Teal  
        '#45B7D1',  # Design - Blue
        '#96CEB4',  # Build - Green
        '#FFEAA7',  # Test - Yellow
        '#DDA0DD',  # Deploy - Purple
        '#98D8C8'   # Post Go-Live - Mint
    ]
    return dict(zip(PHASE_ORDER, colors))

def calculate_baseline_hours(total_hours: float, allocation: Dict[str, float]) -> Dict[str, float]:
    """Calculate baseline hours for each phase"""
    return {phase: total_hours * (pct / 100.0) for phase, pct in allocation.items()}

def format_currency(amount: float) -> str:
    """Format currency with appropriate thousands separators"""
    return f"${amount:,.0f}"

def format_hours(hours: float) -> str:
    """Format hours with appropriate precision"""
    return f"{hours:,.0f}"

def format_percentage(value: float) -> str:
    """Format percentage with one decimal place"""
    return f"{value:.1f}%"

# =============================================================================
# DATA VALIDATION
# =============================================================================

def validate_scenario_results(baseline_cost: float, modeled_cost: float) -> Tuple[bool, str]:
    """
    Validate that calculated improvements are within credible industry bounds
    
    Returns:
        Tuple of (is_valid, warning_message)
    """
    if modeled_cost >= baseline_cost:
        return True, ""
    
    cost_reduction = (baseline_cost - modeled_cost) / baseline_cost
    
    if cost_reduction > MAX_TOTAL_COST_REDUCTION:
        warning = (f"Total cost reduction of {format_percentage(cost_reduction * 100)} "
                  f"exceeds maximum credible limit of {format_percentage(MAX_TOTAL_COST_REDUCTION * 100)}. "
                  "Consider reducing maturity levels or choosing a more conservative scenario.")
        return False, warning
    
    return True, ""

# =============================================================================
# EXPORT CONFIGURATIONS
# =============================================================================

EXPORT_COLUMNS = [
    'Phase',
    'Baseline Hours', 
    'Modeled Hours',
    'Hour Variance',
    'Hour Variance %',
    'Baseline Cost',
    'Modeled Cost', 
    'Cost Variance',
    'Cost Variance %',
    'Risk-Adjusted Hours'
]

# Excel styling for exports
EXCEL_STYLES = {
    'header': {
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white'
    },
    'currency': {'num_format': '$#,##0'},
    'percentage': {'num_format': '0.0%'},
    'hours': {'num_format': '#,##0'}
}

# =============================================================================
# ROLE-BASED MODELING
# =============================================================================

# Role definitions with descriptions and hourly rates
ROLE_DEFINITIONS = {
    # Pod Roles (Core delivery team)
    'Project Manager': {
        'type': 'Pod',
        'base_hours': 1600,
        'hourly_rate': 135,
        'description': 'Overall project leadership, planning, coordination, and stakeholder management'
    },
    'Solutions Architect': {
        'type': 'Pod',
        'base_hours': 780,
        'hourly_rate': 155,
        'description': 'Enterprise architecture, solution design, technical strategy, and system integration oversight'
    },
    'Technical Architect': {
        'type': 'Pod',
        'base_hours': 468,
        'hourly_rate': 145,
        'description': 'Platform extensions, custom development, extensibility framework, and technical integrations'
    },
    'Integration Lead': {
        'type': 'Pod',
        'base_hours': 936,
        'hourly_rate': 140,
        'description': 'Integration architecture, data flow design, API coordination, and integration testing oversight'
    },
    'Platform Lead': {
        'type': 'Pod',
        'base_hours': 468,
        'hourly_rate': 145,
        'description': 'Banner platform configuration, extensibility setup, and platform-level customizations'
    },
    'Student AR Consultant': {
        'type': 'Pod',
        'base_hours': 936,
        'hourly_rate': 125,
        'description': 'Student accounts receivable module configuration, business process design, and testing'
    },
    
    # Specialized Functional Consultants
    'Fin Aid Consultant': {
        'type': 'Pooled',
        'base_hours': 137,
        'hourly_rate': 125,
        'description': 'Financial aid module configuration and COD integration'
    },
    'Finance Consultant': {
        'type': 'Pooled',
        'base_hours': 137,
        'hourly_rate': 125,
        'description': 'Finance module configuration and general ledger setup'
    },
    'HR Consultant': {
        'type': 'Pooled',
        'base_hours': 137,
        'hourly_rate': 125,
        'description': 'HR/Payroll module configuration and integration'
    },
    
    # Technical Implementation Team
    'Integration Engineer': {
        'type': 'Pooled',
        'base_hours': 951,
        'hourly_rate': 110,
        'description': 'Integration development, API implementation, data mapping, and Banner Experience card development'
    },
    'Degree Works Consultant': {
        'type': 'Pooled',
        'base_hours': 92,
        'hourly_rate': 110,
        'description': 'Degree audit system configuration and workflow setup'
    },
    'Degree Works Scribe': {
        'type': 'Pooled',
        'base_hours': 46,
        'hourly_rate': 95,
        'description': 'Degree audit block coding and program configuration'
    },
    'Reporting Consultant': {
        'type': 'Pooled',
        'base_hours': 166,
        'hourly_rate': 115,
        'description': 'Operational reporting, analytics, and dashboard development'
    },
    'Experience Consultant': {
        'type': 'Pooled',
        'base_hours': 166,
        'hourly_rate': 120,
        'description': 'Banner Experience UI/UX design, card development, and front-end customization'
    },
    
    # Support Functions
    'Change Management': {
        'type': 'Pooled',
        'base_hours': 320,
        'hourly_rate': 115,
        'description': 'User adoption strategy, training, communications, and organizational change support'
    },
    'Other & Contingency': {
        'type': 'Pooled',
        'base_hours': 100,
        'hourly_rate': 100,
        'description': 'Buffer for unforeseen needs and additional support'
    }
}

# Phase allocation percentages by role
# Based on typical Banner migration/modernization activities
# Percentages represent % of total role hours allocated to each phase
ROLE_PHASE_ALLOCATION = {
    # Project Manager - Heavy in Discover/Plan/Deploy, coordinates throughout
    'Project Manager': {
        'Discover': 15,
        'Plan': 20,
        'Design': 10,
        'Build': 15,
        'Test': 15,
        'Deploy': 15,
        'Post Go-Live': 10
    },
    
    # Solutions Architect - Heavy in early phases for architecture/design
    'Solutions Architect': {
        'Discover': 20,
        'Plan': 15,
        'Design': 25,
        'Build': 15,
        'Test': 10,
        'Deploy': 10,
        'Post Go-Live': 5
    },
    
    # Technical Architect - Design-heavy, builds extensions
    'Technical Architect': {
        'Discover': 10,
        'Plan': 10,
        'Design': 25,
        'Build': 30,
        'Test': 15,
        'Deploy': 5,
        'Post Go-Live': 5
    },
    
    # Integration Lead - Design/Build/Test focus
    'Integration Lead': {
        'Discover': 10,
        'Plan': 15,
        'Design': 20,
        'Build': 25,
        'Test': 20,
        'Deploy': 5,
        'Post Go-Live': 5
    },
    
    # Platform Lead - Similar to Technical Architect
    'Platform Lead': {
        'Discover': 10,
        'Plan': 10,
        'Design': 25,
        'Build': 30,
        'Test': 15,
        'Deploy': 5,
        'Post Go-Live': 5
    },
    
    # Student AR Consultant - Requirements through testing
    'Student AR Consultant': {
        'Discover': 15,
        'Plan': 10,
        'Design': 20,
        'Build': 25,
        'Test': 20,
        'Deploy': 5,
        'Post Go-Live': 5
    },
    
    # Functional Consultants - Requirements and configuration
    'Fin Aid Consultant': {
        'Discover': 20,
        'Plan': 10,
        'Design': 15,
        'Build': 30,
        'Test': 20,
        'Deploy': 3,
        'Post Go-Live': 2
    },
    
    'Finance Consultant': {
        'Discover': 20,
        'Plan': 10,
        'Design': 15,
        'Build': 30,
        'Test': 20,
        'Deploy': 3,
        'Post Go-Live': 2
    },
    
    'HR Consultant': {
        'Discover': 20,
        'Plan': 10,
        'Design': 15,
        'Build': 30,
        'Test': 20,
        'Deploy': 3,
        'Post Go-Live': 2
    },
    
    # Integration Engineer - Heavy Build/Test focus
    'Integration Engineer': {
        'Discover': 5,
        'Plan': 5,
        'Design': 15,
        'Build': 40,
        'Test': 25,
        'Deploy': 5,
        'Post Go-Live': 5
    },
    
    # Degree Works roles - Specialized configuration
    'Degree Works Consultant': {
        'Discover': 10,
        'Plan': 10,
        'Design': 20,
        'Build': 35,
        'Test': 20,
        'Deploy': 3,
        'Post Go-Live': 2
    },
    
    'Degree Works Scribe': {
        'Discover': 5,
        'Plan': 5,
        'Design': 15,
        'Build': 50,
        'Test': 20,
        'Deploy': 3,
        'Post Go-Live': 2
    },
    
    # Reporting Consultant - Design/Build focus
    'Reporting Consultant': {
        'Discover': 10,
        'Plan': 10,
        'Design': 20,
        'Build': 35,
        'Test': 20,
        'Deploy': 3,
        'Post Go-Live': 2
    },
    
    # Experience Consultant - UX design and card development
    'Experience Consultant': {
        'Discover': 15,
        'Plan': 10,
        'Design': 25,
        'Build': 30,
        'Test': 15,
        'Deploy': 3,
        'Post Go-Live': 2
    },
    
    # Change Management - Early and late focus
    'Change Management': {
        'Discover': 20,
        'Plan': 15,
        'Design': 10,
        'Build': 10,
        'Test': 10,
        'Deploy': 20,
        'Post Go-Live': 15
    },
    
    # Contingency - Evenly distributed
    'Other & Contingency': {
        'Discover': 15,
        'Plan': 15,
        'Design': 15,
        'Build': 20,
        'Test': 15,
        'Deploy': 10,
        'Post Go-Live': 10
    }
}

# Role-specific initiative impact multipliers
# Grounded in Banner migration reality: most roles save 18-25%, not wild extremes
# 1.0 = baseline 20% savings, 1.15 = 23%, 0.85 = 17%, etc.
# Group functional consultants together - they do similar configuration work

# Functional consultant group - all save similarly
FUNCTIONAL_CONSULTANT_MULTIPLIER = 1.0  # Standard 20% baseline

ROLE_INITIATIVE_MULTIPLIERS = {
    'Automated Testing': {
        'Project Manager': 0.90,  # Less direct benefit, coordination-heavy
        'Solutions Architect': 0.95,
        'Technical Architect': 1.05,  # Some benefit from build automation
        'Integration Lead': 1.05,
        'Platform Lead': 1.05,
        'Student AR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Fin Aid Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Finance Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'HR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Integration Engineer': 1.10,  # Moderate test automation benefit
        'Degree Works Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Degree Works Scribe': 1.20,  # DW automation tool helps but not dramatic
        'Reporting Consultant': 1.05,
        'Experience Consultant': 1.08,
        'Change Management': 0.75,  # Minimal benefit from technical testing
        'Other & Contingency': 1.0
    },
    'AI/Automation': {
        'Project Manager': 1.05,  # Some planning/coordination tools
        'Solutions Architect': 1.02,
        'Technical Architect': 1.08,
        'Integration Lead': 1.05,
        'Platform Lead': 1.08,
        'Student AR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Fin Aid Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Finance Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'HR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Integration Engineer': 1.10,
        'Degree Works Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Degree Works Scribe': 1.15,  # AI-assisted coding helps moderately
        'Reporting Consultant': 1.08,
        'Experience Consultant': 1.05,
        'Change Management': 0.85,
        'Other & Contingency': 1.0
    },
    'DevSecOps': {
        'Project Manager': 0.95,
        'Solutions Architect': 1.02,
        'Technical Architect': 1.08,
        'Integration Lead': 1.05,
        'Platform Lead': 1.08,
        'Student AR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Fin Aid Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Finance Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'HR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Integration Engineer': 1.12,  # Solid CI/CD benefits
        'Degree Works Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Degree Works Scribe': 0.98,
        'Reporting Consultant': 1.02,
        'Experience Consultant': 1.05,
        'Change Management': 0.80,
        'Other & Contingency': 1.0
    },
    'Reusable Components': {
        'Project Manager': 0.95,
        'Solutions Architect': 1.05,
        'Technical Architect': 1.08,
        'Integration Lead': 1.05,
        'Platform Lead': 1.08,
        'Student AR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Fin Aid Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Finance Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'HR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Integration Engineer': 1.10,
        'Degree Works Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Degree Works Scribe': 1.00,
        'Reporting Consultant': 1.08,
        'Experience Consultant': 1.12,  # Component library helps UX
        'Change Management': 0.85,
        'Other & Contingency': 1.0
    },
    'Knowledge Base': {
        'Project Manager': 1.00,
        'Solutions Architect': 1.03,
        'Technical Architect': 1.03,
        'Integration Lead': 1.02,
        'Platform Lead': 1.03,
        'Student AR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Fin Aid Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Finance Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'HR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Integration Engineer': 1.05,
        'Degree Works Consultant': 1.05,  # Documentation helps with complex rules
        'Degree Works Scribe': 1.08,  # Coding patterns help
        'Reporting Consultant': 1.05,
        'Experience Consultant': 1.03,
        'Change Management': 1.10,  # Training materials help
        'Other & Contingency': 1.0
    },
    'Agile Practices': {
        'Project Manager': 1.08,  # PM benefits from better process
        'Solutions Architect': 1.02,
        'Technical Architect': 1.00,
        'Integration Lead': 1.02,
        'Platform Lead': 1.00,
        'Student AR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Fin Aid Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Finance Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'HR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Integration Engineer': 1.02,
        'Degree Works Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Degree Works Scribe': 0.98,
        'Reporting Consultant': 1.00,
        'Experience Consultant': 1.02,
        'Change Management': 1.05,  # Better collaboration
        'Other & Contingency': 1.0
    },
    'Agile + DevOps': {
        'Project Manager': 1.10,  # PM benefits most from better process/visibility
        'Solutions Architect': 1.03,
        'Technical Architect': 1.05,  # DevOps practices help architects
        'Integration Lead': 1.05,
        'Platform Lead': 1.05,
        'Student AR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Fin Aid Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Finance Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'HR Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Integration Engineer': 1.08,  # CI/CD benefits engineers
        'Degree Works Consultant': FUNCTIONAL_CONSULTANT_MULTIPLIER,
        'Degree Works Scribe': 0.98,
        'Reporting Consultant': 1.02,
        'Experience Consultant': 1.03,
        'Change Management': 1.08,  # Agile improves change management
        'Other & Contingency': 1.0
    }
}


# Strategic savings categories for executive reporting
# Based on Banner client reality: Low CMMI maturity, PMO in shambles
# 
# ACTUAL MODEL OUTPUT (validated Oct 17, 2025):
# - N2S Methodology & Controls: 42.5% (THE STAR - fixing fundamentals with EDCC, CARM, Agile)
# - OOtB Config: 31.6% (Strong value - templates, accelerators, reusable components)
# - AI & Automation: 25.9% (Critical amplifier - tools multiply process effectiveness)
#
# Rationale: When baseline maturity is low (CMMI Level 1-2), the biggest gains come from 
# implementing fundamental delivery discipline (EDCC governance, CARM architecture, Agile practices).
# Templates and automation amplify good process, but cannot fix broken process.
# This ~43/32/26 split is mathematically calculated and defensible (see BOARD_PRESENTATION_NUMBERS.md)

SAVINGS_CATEGORY_MAPPING = {
    # Initiative name -> {category: percentage allocation}
    # Using actual initiative names from INITIATIVE_FALLBACK
    
    'Automated Testing': {
        'AI & Automation': 0.55,  # 55% test automation technology  
        'N2S Methodology & Controls': 0.30,  # 30% shift-left quality methodology (the discipline)
        'OOtB Config': 0.15  # 15% preconfigured test suites and frameworks
    },
    'AI/Automation': {  # Match actual name in model
        'AI & Automation': 0.70,  # 70% AI technology
        'N2S Methodology & Controls': 0.20,  # 20% AI adoption process and governance
        'OOtB Config': 0.10  # 10% AI templates
    },
    'Modernization Studio': {
        'OOtB Config': 0.50,  # 50% reusable components, templates, accelerators
        'N2S Methodology & Controls': 0.35,  # 35% delivery approach and methodology
        'AI & Automation': 0.15  # 15% automation in the studio
    },
    'N2S CARM': {  # Match actual name in model
        'N2S Methodology & Controls': 0.65,  # 65% architecture methodology - KEY DIFFERENTIATOR
        'OOtB Config': 0.35  # 35% reference architectures and patterns
    },
    'EDCC': {
        'N2S Methodology & Controls': 0.80,  # 80% delivery control methodology - FIXING PMO SHAMBLES
        'AI & Automation': 0.12,  # 12% automated reporting/dashboards
        'OOtB Config': 0.08  # 8% environment configurations
    },
    'Preconfigured Envs': {  # Match actual name in model
        'OOtB Config': 0.65,  # 65% preconfigured assets and templates
        'AI & Automation': 0.22,  # 22% IaC/automated provisioning
        'N2S Methodology & Controls': 0.13  # 13% environment management methodology
    },
    'Integration Code Reuse': {  # Match actual name in model
        'OOtB Config': 0.60,  # 60% reusable integration patterns and components
        'N2S Methodology & Controls': 0.27,  # 27% reuse methodology and best practices
        'AI & Automation': 0.13  # 13% automated code generation
    },
    
    # Legacy/alternate names for compatibility
    'DevSecOps Pipeline': {
        'N2S Methodology & Controls': 0.55,  # 55% process, controls, governance
        'AI & Automation': 0.45  # 45% CI/CD automation technology
    },
    'Cloud-Native Patterns': {
        'OOtB Config': 0.45,  # 45% reference implementations
        'N2S Methodology & Controls': 0.35,  # 35% architecture methodology
        'AI & Automation': 0.20  # 20% automated deployment
    },
    'Agile Methodology': {
        'N2S Methodology & Controls': 0.75,  # 75% methodology - PROCESS IS THE VALUE
        'AI & Automation': 0.15,  # 15% automation tools
        'OOtB Config': 0.10  # 10% sprint templates
    },
    'Agile + DevOps Practices': {
        'N2S Methodology & Controls': 0.70,  # 70% process and cultural transformation
        'AI & Automation': 0.20,  # 20% DevOps automation tools (CI/CD, monitoring)
        'OOtB Config': 0.10  # 10% templates and standard workflows
    }
}

# Category descriptions for reporting
SAVINGS_CATEGORIES = {
    'OOtB Config': {
        'name': 'Out-of-the-Box Configuration',
        'description': 'Preconfigured environments, reusable components, templates, test suites, and accelerators',
        'color': '#4CAF50'  # Green
    },
    'N2S Methodology & Controls': {
        'name': 'N2S Methodology & Controls',
        'description': 'CARM, EDCC, Agile practices, governance, and delivery methodology',
        'color': '#2196F3'  # Blue
    },
    'AI & Automation': {
        'name': 'AI & Automation',
        'description': 'AI-powered tools, automated testing, CI/CD automation, and intelligent tooling',
        'color': '#FF9800'  # Orange
    }
}


def get_total_role_hours() -> float:
    """Calculate total hours across all roles"""
    return sum(role['base_hours'] for role in ROLE_DEFINITIONS.values())


def calculate_role_hours_by_phase(role_name: str) -> Dict[str, float]:
    """Calculate hours for a specific role distributed across phases"""
    if role_name not in ROLE_DEFINITIONS or role_name not in ROLE_PHASE_ALLOCATION:
        return {}
    
    base_hours = ROLE_DEFINITIONS[role_name]['base_hours']
    phase_allocation = ROLE_PHASE_ALLOCATION[role_name]
    
    return {
        phase: base_hours * (pct / 100.0)
        for phase, pct in phase_allocation.items()
    }


def calculate_all_roles_by_phase() -> Dict[str, Dict[str, float]]:
    """Calculate hours for all roles distributed across phases"""
    return {
        role_name: calculate_role_hours_by_phase(role_name)
        for role_name in ROLE_DEFINITIONS.keys()
    }


def get_phase_total_by_roles() -> Dict[str, float]:
    """Calculate total hours per phase summed across all roles"""
    all_roles = calculate_all_roles_by_phase()
    phase_totals = {phase: 0.0 for phase in PHASE_ORDER}
    
    for role_hours in all_roles.values():
        for phase, hours in role_hours.items():
            phase_totals[phase] += hours
    
    return phase_totals


def get_role_groups() -> Dict[str, list]:
    """Group roles by type for easier analysis"""
    groups = {'Pod': [], 'Pooled': []}
    for role_name, role_info in ROLE_DEFINITIONS.items():
        groups[role_info['type']].append(role_name)
    return groups 