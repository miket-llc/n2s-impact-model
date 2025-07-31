"""
Configuration file for N2S Efficiency Modeling Application
Contains defaults, constants, and helper functions
"""

from typing import Dict, Tuple

# =============================================================================
# PROJECT DEFAULTS
# =============================================================================

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

# =============================================================================
# SCENARIO DEFINITIONS
# =============================================================================

SCENARIOS = {
    'Moderate (10%)': {
        'base_factor': 1.0,
        'description': 'Conservative improvements using matrix at face value'
    },
    'Elevated (20%)': {
        'base_factor': 1.0,
        'additional_factor': 0.5,  # 50% additional benefits
        'description': ('Enhanced benefits from higher test automation '
                       'and deeper reuse')
    },
    'Aggressive (30%)': {
        'base_factor': 1.0,
        'additional_factor': 0.75,  # 75% additional benefits
        'max_savings_caps': {  # Maximum credible savings per phase
            'Discover': 0.30,
            'Plan': 0.35,
            'Design': 0.40,
            'Build': 0.45,
            'Test': 0.50,
            'Deploy': 0.40,
            'Post Go-Live': 0.75
        },
        'description': ('Near-maximum credible improvements with '
                       'empirically defensible limits')
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
    'testing_phase_reduction': 0.35,  # 30-40% from Perfecto/Testlio
    'manual_testing_reduction': 0.35,  # 35% manual testing reduction
    'defect_fix_cost_multipliers': {
        'unit_test': 10,
        'system_test': 40, 
        'production': 70
    }
}

# Maximum credible total cost reduction (validation check)
MAX_TOTAL_COST_REDUCTION = 0.30  # 30% without radical scope change

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