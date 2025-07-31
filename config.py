"""
Configuration file for N2S Efficiency Modeling Application
Contains defaults, constants, and helper functions
"""

from typing import Dict, Tuple

# =============================================================================
# PROJECT DEFAULTS
# =============================================================================

# Version tracking for deployment verification
APP_VERSION = "v2.7.0 - Industry Benchmarks + Initiative Selection"

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
        "description": ("Risk weights multiply your modeled hours to account for project "
                       "complexity, team experience, and potential issues. Higher weights "
                       "= more conservative estimates."),
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
            "description": "Requirements gathering, stakeholder alignment, scope definition",
            "typical_risks": [
                "Unclear or changing requirements",
                "Stakeholder availability and alignment",
                "Scope creep potential",
                "Business process complexity"
            ],
            "low_risk": "Well-defined project with clear requirements",
            "high_risk": "Complex business transformation with unclear scope"
        },
        "Plan": {
            "description": "Project planning, resource allocation, timeline development",
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
            "description": "Architecture design, technical specifications, UI/UX design",
            "typical_risks": [
                "Technical architecture complexity",
                "Integration design challenges",
                "Performance requirements",
                "Scalability considerations"
            ],
            "low_risk": "Standard design patterns and proven architecture",
            "high_risk": "New architecture or complex integration requirements"
        },
        "Build": {
            "description": "Code development, component creation, feature implementation",
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
            "description": "Testing execution, defect resolution, quality assurance",
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
            "description": "Production deployment, release management, go-live activities",
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
            "description": "Production support, issue resolution, user adoption",
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
# SCENARIO DEFINITIONS
# =============================================================================

SCENARIOS = {
    'Baseline Matrix': {
        'base_factor': 1.0,
        'description': ('Conservative improvements using matrix at face value '
                        '(expect 12-15% savings with moderate maturity levels)')
    },
    'Enhanced (20% boost)': {
        'base_factor': 1.0,
        'additional_factor': 1.0,  # 100% additional benefits (was 0.4)
        'description': ('Enhanced benefits from higher test automation '
                        'and deeper reuse - adds 100% boost to testing '
                        'and quality improvements (expect 18-25% savings)')
    },
    'Maximum (30% boost)': {
        'base_factor': 1.0,
        'additional_factor': 1.5,  # 150% additional benefits (was 0.6)
        'max_savings_caps': {  # Maximum credible savings per phase
            'Discover': 0.50,
            'Plan': 0.55,
            'Design': 0.60,
            'Build': 0.65,
            'Test': 0.80,
            'Deploy': 0.60,
            'Post Go-Live': 0.85
        },
        'description': ('Maximum credible improvements with '
                        'empirically defensible limits - adds 150% boost '
                        'with safety caps (expect 25-35% savings)')
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
MAX_TOTAL_COST_REDUCTION = 0.35  # 35% for aggressive N2S implementations

# =============================================================================
# FILE PATHS  
# =============================================================================

DATA_PATH = "data/ShiftLeft_Levers_PhaseMatrix_v3.xlsx"
EXCEL_INPUT_FILE = "data/ShiftLeft_Levers_PhaseMatrix_v3.xlsx"
REFERENCE_FILE = "fy25q3-ps-efficiency-model-02.xlsx"
MATRIX_SHEET_NAME = "10pct_Savings"

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
    "Integration Code Reuse"
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
        "100%": "Full EDCC optimization, serverless, auto-scaling, cost-optimized"
    },
    "Integration Code Reuse": {
        "description": "Standardized integration patterns, reusable components and APIs",
        "0%": "Custom integrations built from scratch each time",
        "25%": "Some common patterns documented, limited reuse",
        "50%": "Standard integration library, moderate component reuse",
        "75%": "Comprehensive reusable component library, good adoption",
        "100%": "Fully optimized integration platform, API-first, maximum reuse"
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
        warning = (f"⚠️ Total cost reduction of {format_percentage(cost_reduction * 100)} "
                  f"exceeds maximum credible limit of {format_percentage(MAX_TOTAL_COST_REDUCTION * 100)}. "
                  f"Consider adjusting initiative maturity levels.")
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