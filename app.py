"""
N2S Efficiency Modeling Application
Interactive Streamlit app for quantifying professional services efficiency
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
from datetime import datetime

from model import N2SEfficiencyModel, get_initiatives
from config import (
    DEFAULT_PHASE_ALLOCATION, DEFAULT_RISK_WEIGHTS, PHASE_ORDER,
    get_phase_colors, format_currency, format_hours,
    validate_scenario_results
)

# Adapter function to bridge old app logic with new model
def calculate_with_new_model(
    model, maturity_levels, total_hours, phase_allocation,
    blended_rate, risk_weights, cost_avoidance_config
):
    """Adapter to use new model with old app interface"""
    # New model calculates savings directly from maturity levels
    baseline_hours, modeled_hours, savings_detail_df = model.apply_maturity_levels(
        maturity_levels, total_hours, phase_allocation
    )
    
    # Calculate actual savings percentage
    total_baseline = sum(baseline_hours.values())
    total_modeled = sum(modeled_hours.values())
    actual_savings_pct = ((total_baseline - total_modeled) / total_baseline * 100) if total_baseline > 0 else 0
    
    # Calculate costs
    cost_results = model.calculate_costs_and_savings(
        baseline_hours, modeled_hours, blended_rate,
        True, cost_avoidance_config
    )
    
    # Calculate risk-adjusted hours
    risk_adjusted_hours = model.calculate_risk_adjusted_hours(
        modeled_hours, risk_weights
    )
    
    # Generate summary table
    summary_df = model.generate_summary_table(
        baseline_hours, modeled_hours,
        cost_results['baseline_cost'], cost_results['modeled_cost'],
        risk_adjusted_hours
    )
    
    # Generate KPIs
    kpi_summary = model.get_kpi_summary(
        baseline_hours, modeled_hours, cost_results
    )
    
    # Generate initiative impact with new model signature
    initiative_impact_df = model.generate_initiative_impact_table(
        baseline_hours, modeled_hours,
        maturity_levels, blended_rate,
        True, cost_avoidance_config
    )
    
    return {
        'baseline_hours': baseline_hours,
        'modeled_hours': modeled_hours,
        'cost_results': cost_results,
        'risk_adjusted_hours': risk_adjusted_hours,
        'summary_df': summary_df,
        'kpi_summary': kpi_summary,
        'initiative_impact_df': initiative_impact_df,
        'savings_detail_df': savings_detail_df,
        'actual_savings_pct': actual_savings_pct
    }

# Page configuration
st.set_page_config(
    page_title="N2S Efficiency Model",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_custom_css():
    """Load custom CSS for better styling"""
    st.markdown("""
    <style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .big-metric {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .savings-positive {
        color: #28a745;
    }
    .cost-negative {
        color: #dc3545;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_model():
    """Initialize the model instance (no caching - need fresh calculations)"""
    model = N2SEfficiencyModel()
    # New model is automatically initialized with calibrated matrix
    return model


def create_sidebar_controls():
    """Create sidebar input controls for model parameters"""
    from config import (
        get_initiative_description, get_maturity_description,
        RISK_LEVEL_DEFINITIONS, get_phase_risk_info,
        get_risk_level_description,
        INDUSTRY_BENCHMARKS, COST_AVOIDANCE_OPTIONS
    )
    
    # Get initiatives from the NEW research-based model
    available_initiative_names = get_initiatives()
    
    # Rerun counter to verify Streamlit is responding
    if 'rerun_count' not in st.session_state:
        st.session_state.rerun_count = 0
    st.session_state.rerun_count += 1
    
    st.sidebar.title("Model Parameters")
    st.sidebar.caption(f"Reruns: {st.session_state.rerun_count}")
    
    # Version indicator in sidebar
    from config import APP_VERSION
    st.sidebar.caption(f"{APP_VERSION}")
    
    # Baseline Efficiency Reminder - Updated
    st.sidebar.info("""
    **Step 1: Assess Your Current Automation Maturity**
    
    Complete the assessment below to understand your starting point 
    and realistic savings potential.
    """)
    
    # Current State Assessment
    st.sidebar.subheader("Current State Assessment")
    
    from config import AUTOMATION_ASSESSMENT, assess_current_maturity
    
    # Collect assessment responses
    assessment_responses = {}
    
    for question_key, question_config in AUTOMATION_ASSESSMENT.items():
        if question_config['type'] == 'slider':
            assessment_responses[question_key] = st.sidebar.slider(
                question_config['question'],
                min_value=question_config['min_value'],
                max_value=question_config['max_value'],
                value=question_config['default'],
                help=question_config['help'],
                key=f"assess_{question_key}"
            )
        elif question_config['type'] == 'selectbox':
            assessment_responses[question_key] = st.sidebar.selectbox(
                question_config['question'],
                options=question_config['options'],
                index=question_config['default'],
                help=question_config['help'],
                key=f"assess_{question_key}"
            )
    
    # Calculate current maturity
    current_maturity = assess_current_maturity(assessment_responses)
    
    # Display maturity assessment results
    st.sidebar.success(f"""
    **Your Current Maturity: Level {current_maturity['maturity_level']} - {current_maturity['maturity_name']}**
    
    Realistic Savings Potential: {current_maturity['current_savings_potential']:.1f}%
    """)
    
    # Map assessment to initiative defaults
    test_coverage = assessment_responses.get('test_automation_coverage', 30)
    cicd_maturity_idx = 0
    cicd_response = assessment_responses.get('ci_cd_maturity', 'Manual deployments')
    cicd_options = AUTOMATION_ASSESSMENT['ci_cd_maturity']['options']
    if cicd_response in cicd_options:
        cicd_maturity_idx = cicd_options.index(cicd_response)
    cicd_pct = (cicd_maturity_idx / (len(cicd_options) - 1)) * 100 if len(cicd_options) > 1 else 0
    
    code_reuse = assessment_responses.get('code_reuse_level', 20)
    
    env_auto_idx = 0
    env_response = assessment_responses.get('environment_automation', 'Manual environment setup')
    env_options = AUTOMATION_ASSESSMENT['environment_automation']['options']
    if env_response in env_options:
        env_auto_idx = env_options.index(env_response)
    env_pct = (env_auto_idx / (len(env_options) - 1)) * 100 if len(env_options) > 1 else 0
    
    doc_auto_idx = 0
    doc_response = assessment_responses.get('documentation_automation', 'Manual documentation')
    doc_options = AUTOMATION_ASSESSMENT['documentation_automation']['options']
    if doc_response in doc_options:
        doc_auto_idx = doc_options.index(doc_response)
    doc_pct = (doc_auto_idx / (len(doc_options) - 1)) * 100 if len(doc_options) > 1 else 0
    
    # Calculate average assessment maturity
    avg_assessment_maturity = (test_coverage + cicd_pct + code_reuse + env_pct + doc_pct) / 5
    
    st.sidebar.info(f"""
    ℹ️ **Assessment sets initiative defaults:**
    
    Based on your answers, initiative sliders below are pre-set to **{avg_assessment_maturity:.0f}%** (you can adjust each individually).
    """)
    
    # Major Modeling Decisions
    st.sidebar.subheader("Target & Strategy")
    
    # Target savings with proper persistence
    # Only initialize default once, then let user control it
    if 'initialized_target' not in st.session_state:
        st.session_state.initialized_target = True
        st.session_state.default_target = min(20, int(current_maturity['current_savings_potential']))
    
    target_savings = st.sidebar.slider(
        "Target Project Savings %",
        min_value=5,
        max_value=35,
        value=st.session_state.default_target,
        step=1,
        key='target_pct_slider',
        help=(
            f"Set your target savings percentage (5-35%). "
            f"Based on your maturity, realistic potential is ~{current_maturity['current_savings_potential']:.1f}%. "
            f"Model will show if higher targets are achievable."
        ),
        on_change=lambda: setattr(st.session_state, 'default_target', st.session_state.target_pct_slider)
    )
    
    # Generate scenario configuration based on target and maturity
    from config import calculate_target_feasibility
    
    # We'll need selected initiatives for feasibility check - get a preview first
    available_initiatives = available_initiative_names  # From new research-based model
    
    feasibility = calculate_target_feasibility(
        current_maturity, target_savings, available_initiatives
    )
    
    # Display feasibility assessment
    if feasibility['feasible']:
        st.sidebar.success(f"✓ Target {target_savings}% is achievable with your current maturity")
    else:
        st.sidebar.warning(f"""
        ⚠️ Target {target_savings}% requires maturity improvements
        
        Gap: {feasibility['gap']:.1f}% 
        Recommended: Level {feasibility['required_maturity_level']} ({feasibility['required_maturity_name']})
        """)
    
    # Convert to scenario config for the existing model
    scenario_config = {
        'target_percentage': target_savings,
        'current_maturity': current_maturity,
        'feasibility': feasibility,
        'description': f"Target {target_savings}% savings (Current maturity: Level {current_maturity['maturity_level']})"
    }
    
    # Display the approach being used
    st.sidebar.caption(f"Approach: {scenario_config['description']}")
    
    cost_avoidance_selection = st.sidebar.selectbox(
        "Cost Avoidance Model",
        options=list(COST_AVOIDANCE_OPTIONS.keys()),
        index=3,  # Default to "Moderate (2.5x)"
        help="Additional value beyond direct savings"
    )
    
    cost_avoidance_config = COST_AVOIDANCE_OPTIONS[cost_avoidance_selection]
    
    # Project Basics
    st.sidebar.subheader("Project Basics")
    
    total_hours = st.sidebar.number_input(
        "Total Project Hours",
        min_value=1000,
        max_value=100000,
        value=17054,
        step=500,
        help="Total estimated hours for your project across all phases"
    )
    
    blended_rate = st.sidebar.number_input(
        "Blended Hourly Rate ($)",
        min_value=50,
        max_value=300,
        value=100,
        step=5,
        help=(
            "Average hourly cost across all team members "
            "(developers, testers, architects, etc.)"
        )
    )
    
    # Phase Allocation
    st.sidebar.subheader("Phase Time Allocation")
    st.sidebar.markdown("**Adjust based on your project type:**")
    
    phase_allocation = {}
    
    # Show sliders for all phases
    for phase in PHASE_ORDER:
        default_value = DEFAULT_PHASE_ALLOCATION[phase]
        phase_allocation[phase] = st.sidebar.slider(
            f"{phase} %",
            min_value=1,
            max_value=50,
            value=default_value,
            step=1,
            help=f"Percentage of total project time spent in {phase} phase"
        )
    
    # Validation
    total_allocation = sum(phase_allocation.values())
    if abs(total_allocation - 100) > 0.1:
        st.sidebar.error(
            f"Phase allocation must sum to 100% "
            f"(currently {total_allocation}%)"
        )
        st.sidebar.info("Adjust the sliders above so they total exactly 100%")
    
    # Industry benchmarks are now BAKED INTO the calibrated matrix
    # No need for user to adjust - matrix already at 75th percentile of research
    custom_benchmarks = INDUSTRY_BENCHMARKS  # For compatibility
    
    # Debug display for key values
    with st.sidebar.expander("🔍 Debug: Current State", expanded=False):
        st.write("**Assessment-Derived Values:**")
        st.write(f"Test Coverage: {test_coverage}%")
        st.write(f"Code Reuse: {code_reuse}%")
        st.write(f"CI/CD Maturity: {cicd_pct:.0f}%")
        st.write(f"Environment Automation: {env_pct:.0f}%")
        st.write(f"Documentation Automation: {doc_pct:.0f}%")
        st.write(f"Average Maturity: {avg_assessment_maturity:.0f}%")
        st.write("")
        st.write("**Target:**")
        st.write(f"Target Savings %: {target_savings}%")
        st.write(f"Maturity Potential: {current_maturity['current_savings_potential']:.1f}%")
    
    # Initiative Maturity Levels  
    st.sidebar.subheader("⚙️ Initiative Maturity Levels")
    st.sidebar.markdown("**🎯 ADJUST THESE TO CHANGE SAVINGS:**")
    
    # First, set all initiatives to default values for enabled ones
    maturity_levels = {}
    for initiative in available_initiative_names:
        maturity_levels[initiative] = 50  # Default to 50% (validated baseline)
    
    # Risk Assessment
    st.sidebar.subheader("Risk Assessment")
    
    # General risk information
    general_risk_info = RISK_LEVEL_DEFINITIONS["general"]["description"]
    st.sidebar.markdown(f"**Risk Multipliers:** {general_risk_info}")
    
    risk_weights = {}
    for phase in PHASE_ORDER:
        phase_info = get_phase_risk_info(phase)
        help_text = f"""**{phase_info['description']}**

**Typical Risks:**
{chr(10).join([f"• {risk}" for risk in phase_info['typical_risks']])}

**Low Risk Example:** {phase_info['low_risk']}
**High Risk Example:** {phase_info['high_risk']}"""
        
        risk_weights[phase] = st.sidebar.slider(
            f"{phase} Risk",
            min_value=0.5,
            max_value=10.0,
            value=float(DEFAULT_RISK_WEIGHTS[phase]),
            step=0.5,
            format="%.1fx",
            help=help_text,
            key=f"risk_{phase}"
        )
        
        # Real-time risk level description
        risk_level_desc = get_risk_level_description(risk_weights[phase])
        st.sidebar.caption(f"{risk_level_desc}")
    
    # Initiative Maturity - DIRECTLY SET BY ASSESSMENT (with manual override option)
    st.sidebar.subheader("📊 Initiative Maturity (Derived from Assessment)")
    
    # Map assessment responses directly to initiative maturity
    maturity_levels = {
        'Automated Testing': test_coverage,  # Direct from test coverage slider
        'Preconfigured Envs': env_pct,       # From environment automation dropdown
        'AI/Automation': avg_assessment_maturity,  # General maturity level
        'Integration Code Reuse': code_reuse,  # Direct from code reuse slider
        'Agile + DevOps Practices': cicd_pct,  # From CI/CD maturity dropdown
        'EDCC': doc_pct,  # From documentation automation dropdown
        'N2S CARM': avg_assessment_maturity,  # General maturity level
        'Modernization Studio': avg_assessment_maturity  # General maturity level
    }
    
    # Display calculated maturity with override option
    with st.sidebar.expander("🔧 Fine-Tune Initiative Maturity (Optional)", expanded=False):
        st.markdown("**Override calculated values if needed:**")
        for initiative in available_initiative_names:
            help_text = get_initiative_description(initiative)
            default_value = int(maturity_levels.get(initiative, avg_assessment_maturity))
            
            maturity_levels[initiative] = st.slider(
                f"{initiative}",
                min_value=0,
                max_value=100,
                value=default_value,
                step=5,
                help=help_text,
                key=f"maturity_{initiative}_override"
            )
    
    # Show current maturity levels
    st.sidebar.markdown("**Current Initiative Maturity:**")
    for initiative in available_initiative_names:
        st.sidebar.caption(f"• {initiative}: {maturity_levels[initiative]:.0f}%")
    
    # For compatibility, create these even though we're not using them now
    initiative_weights = {init: 1.0 for init in available_initiative_names}
    available_initiatives = available_initiative_names
    
    return {
        'total_hours': total_hours,
        'blended_rate': blended_rate,
        'phase_allocation': phase_allocation,
        'maturity_levels': maturity_levels,
        'initiative_weights': initiative_weights,
        'available_initiatives': available_initiatives,
        'scenario_config': scenario_config,
        'risk_weights': risk_weights,
        'cost_avoidance_config': cost_avoidance_config,
        'industry_benchmarks': custom_benchmarks,
        'current_maturity': current_maturity,
        'feasibility': feasibility,
        'assessment_responses': assessment_responses
    }


def display_kpi_metrics(kpi_summary):
    """Display key performance indicators"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Hours Saved",
            format_hours(kpi_summary['total_hours_saved']),
            delta=f"{kpi_summary['total_hours_saved_pct']:.1f}%"
        )
    
    with col2:
        st.metric(
            "Cost Savings",
            format_currency(kpi_summary['total_cost_savings']),
            delta="Direct savings"
        )
    
    with col3:
        st.metric(
            "Cost Avoidance",
            format_currency(kpi_summary['total_cost_avoidance']),
            delta="Future savings"
        )
    
    with col4:
        st.metric(
            "Total Financial Benefit",
            format_currency(kpi_summary['total_financial_benefit']),
            delta=format_currency(
                kpi_summary['total_baseline_cost'] - kpi_summary['total_modeled_cost']
            )
        )


def create_cost_breakdown_by_phase_chart(cost_results, summary_df):
    """Create detailed cost breakdown chart showing baseline, savings, and avoidance by phase"""
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=('Cost Breakdown by Phase',)
    )
    
    phases = summary_df['Phase']
    baseline_costs = [cost_results['baseline_cost'][phase] for phase in phases]
    direct_savings = [cost_results['savings'][phase] for phase in phases]
    cost_avoidance = [cost_results['avoidance'][phase] for phase in phases]
    modeled_costs = [cost_results['modeled_cost'][phase] for phase in phases]
    
    # Baseline costs (what we would spend without initiatives)
    fig.add_trace(go.Bar(
        x=phases,
        y=baseline_costs,
        name='Baseline Cost',
        marker_color='#8D33EF',
        text=[format_currency(c) for c in baseline_costs],
        textposition='outside',
        textfont=dict(size=11, color='black')
    ))
    
    # Modeled costs (what we actually spend after initiatives)
    fig.add_trace(go.Bar(
        x=phases,
        y=modeled_costs,
        name='Actual Cost (After Initiatives)',
        marker_color='#AA66F3',
        text=[format_currency(c) for c in modeled_costs],
        textposition='outside',
        textfont=dict(size=11, color='black')
    ))
    
    # Direct cost savings (negative bars showing savings)
    fig.add_trace(go.Bar(
        x=phases,
        y=[-s for s in direct_savings],  # Show savings as negative
        name='Direct Savings',
        marker_color='green',
        text=[format_currency(-s) if s > 0 else '' for s in direct_savings],
        textposition='outside',
        textfont=dict(size=11, color='black')
    ))
    
    # Cost avoidance (additional benefits, shown as negative)
    fig.add_trace(go.Bar(
        x=phases,
        y=[-a for a in cost_avoidance],  # Show avoidance as negative
        name='Cost Avoidance',
        marker_color='darkgreen',
        text=[format_currency(-a) if a > 0 else '' for a in cost_avoidance],
        textposition='outside',
        textfont=dict(size=11, color='black')
    ))
    
    fig.update_layout(
        title=dict(
            text="Executive Cost Summary: Baseline vs Actual Costs with Benefits",
            font=dict(size=18, color='black')
        ),
        xaxis_title=dict(text="Project Phase", font=dict(size=14, color='black')),
        yaxis_title=dict(text="Cost ($)", font=dict(size=14, color='black')),
        barmode='group',
        height=600,
        font=dict(size=12, color='black'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color='black')
        ),
        annotations=[
            dict(
                x=0.5, xref='paper',
                y=1.15, yref='paper',
                text="Green bars show financial benefits (savings = immediate, avoidance = future)",
                showarrow=False,
                font=dict(size=14, color='gray')
            )
        ]
    )
    
    # Add zero line for reference
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    return fig


def create_hours_breakdown_by_phase_chart(summary_df, cost_results):
    """Create detailed hours breakdown chart showing baseline vs modeled hours with savings"""
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=('Hours Breakdown by Phase',)
    )
    
    phases = summary_df['Phase']
    baseline_hours = summary_df['Baseline Hours'].tolist()
    modeled_hours = summary_df['Modeled Hours'].tolist()
    hours_saved = summary_df['Hour Variance'].tolist()  # Negative values = savings
    
    # Calculate hours avoided (equivalent to cost avoidance but in hours)
    # This represents future operational time savings
    hours_avoided = []
    for phase in phases:
        if phase == 'Post Go-Live':
            # For Post Go-Live, calculate hours avoided based on cost avoidance
            cost_avoidance = cost_results['avoidance'][phase]
            blended_rate = cost_results['baseline_cost'][phase] / baseline_hours[phases.tolist().index(phase)] if baseline_hours[phases.tolist().index(phase)] > 0 else 100
            hours_avoided.append(cost_avoidance / blended_rate if blended_rate > 0 else 0)
        else:
            hours_avoided.append(0)  # No hours avoided in development phases
    
    # Baseline hours (what we would work without initiatives)
    fig.add_trace(go.Bar(
        x=phases,
        y=baseline_hours,
        name='Baseline Hours',
        marker_color='#8D33EF',
        text=[format_hours(h) for h in baseline_hours],
        textposition='outside',
        textfont=dict(size=11, color='black')
    ))
    
    # Modeled hours (what we actually work after initiatives)
    fig.add_trace(go.Bar(
        x=phases,
        y=modeled_hours,
        name='Actual Hours (After Initiatives)',
        marker_color='#AA66F3',
        text=[format_hours(h) for h in modeled_hours],
        textposition='outside',
        textfont=dict(size=11, color='black')
    ))
    
    # Hours saved (negative bars showing time savings)
    fig.add_trace(go.Bar(
        x=phases,
        y=hours_saved,  # hours_saved is already negative from Hour Variance
        name='Hours Saved',
        marker_color='green',
        text=[format_hours(-h) if h < 0 else '' for h in hours_saved],
        textposition='outside',
        textfont=dict(size=11, color='black')
    ))
    
    # Hours avoided (additional future time benefits, shown as negative)
    fig.add_trace(go.Bar(
        x=phases,
        y=[-h for h in hours_avoided],  # Show avoidance as negative
        name='Hours Avoided',
        marker_color='darkgreen',
        text=[format_hours(-h) if h > 0 else '' for h in hours_avoided],
        textposition='outside',
        textfont=dict(size=11, color='black')
    ))
    
    fig.update_layout(
        title=dict(
            text="Executive Hours Summary: Baseline vs Actual Hours with Time Benefits",
            font=dict(size=18, color='black')
        ),
        xaxis_title=dict(text="Project Phase", font=dict(size=14, color='black')),
        yaxis_title=dict(text="Hours", font=dict(size=14, color='black')),
        barmode='group',
        height=600,
        font=dict(size=12, color='black'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color='black')
        ),
        annotations=[
            dict(
                x=0.5, xref='paper',
                y=1.15, yref='paper',
                text="Green bars show time benefits (saved = immediate, avoided = future)",
                showarrow=False,
                font=dict(size=14, color='gray')
            )
        ]
    )
    
    # Add zero line for reference
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    return fig


def create_phase_comparison_chart(summary_df):
    """Create side-by-side bar chart comparing baseline vs modeled hours"""
    fig = go.Figure()
    
    # Add baseline hours
    fig.add_trace(go.Bar(
        x=summary_df['Phase'],
        y=summary_df['Baseline Hours'],
        name='Baseline Hours',
        marker_color='lightblue',
        text=[format_hours(h) for h in summary_df['Baseline Hours']],
        textposition='outside',
        offsetgroup=1
    ))
    
    # Add modeled hours
    fig.add_trace(go.Bar(
        x=summary_df['Phase'],
        y=summary_df['Modeled Hours'],
        name='Modeled Hours',
        marker_color='darkblue',
        text=[format_hours(h) for h in summary_df['Modeled Hours']],
        textposition='outside',
        offsetgroup=2
    ))
    
    fig.update_layout(
        title="Baseline vs Modeled Hours by Phase",
        xaxis_title="Phase",
        yaxis_title="Hours",
        barmode='group',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_hours_saved_chart(summary_df):
    """Create chart showing hours saved/added by phase"""
    fig = go.Figure()
    
    # Calculate hours saved (negative = savings, positive = additional hours)
    hours_variance = summary_df['Hour Variance']
    colors = ['green' if x < 0 else 'red' if x > 0 else 'gray' for x in hours_variance]
    
    fig.add_trace(go.Bar(
        x=summary_df['Phase'],
        y=hours_variance,
        name='Hours Saved',
        marker_color=colors,
        text=[f"{h:+,.0f}" for h in hours_variance],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Hours Saved by Phase (Negative = Savings)",
        xaxis_title="Phase",
        yaxis_title="Hour Variance",
        height=400,
        showlegend=False
    )
    
    # Add zero line for reference
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    return fig


def create_cost_breakdown_chart(cost_results):
    """Create pie chart showing cost savings vs avoidance"""
    total_savings = sum(cost_results['savings'].values())
    total_avoidance = sum(cost_results['avoidance'].values())
    
    if total_savings + total_avoidance == 0:
        st.warning("No cost benefits calculated")
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=['Direct Cost Savings', 'Cost Avoidance'],
        values=[total_savings, total_avoidance],
        hole=0.3,
        marker_colors=['#2E8B57', '#4682B4']
    )])
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12
    )
    
    fig.update_layout(
        title="Financial Benefits Breakdown",
        annotations=[dict(text=f'Total<br>{format_currency(total_savings + total_avoidance)}', 
                         x=0.5, y=0.5, font_size=16, showarrow=False)]
    )
    
    return fig


def create_variance_chart(summary_df):
    """Create variance analysis chart"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Hour Variance by Phase', 'Cost Variance by Phase'),
        vertical_spacing=0.1
    )
    
    colors = get_phase_colors()
    
    # Hour variance
    fig.add_trace(
        go.Bar(
            x=summary_df['Phase'],
            y=summary_df['Hour Variance'],
            name='Hour Variance',
            marker_color=[colors[phase] for phase in summary_df['Phase']],
            text=[f"{h:,.0f}" for h in summary_df['Hour Variance']],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Cost variance
    fig.add_trace(
        go.Bar(
            x=summary_df['Phase'],
            y=summary_df['Cost Variance'],
            name='Cost Variance',
            marker_color=[colors[phase] for phase in summary_df['Phase']],
            text=[format_currency(c) for c in summary_df['Cost Variance']],
            textposition='outside'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title="Variance Analysis (Negative = Savings)",
        showlegend=False,
        height=600
    )
    
    fig.update_xaxes(title_text="Phase", row=2, col=1)
    fig.update_yaxes(title_text="Hour Variance", row=1, col=1)
    fig.update_yaxes(title_text="Cost Variance ($)", row=2, col=1)
    
    return fig


def create_initiative_impact_chart(initiative_df):
    """Create chart showing financial impact by initiative"""
    # Filter to show only initiatives with meaningful impact
    significant_df = initiative_df[
        abs(initiative_df['Total Financial Impact']) > 1000
    ].head(10)  # Top 10 initiatives
    
    if len(significant_df) == 0:
        return None
    
    # Reverse the order so best initiatives (most negative/savings) appear at top
    significant_df = significant_df.iloc[::-1]
    
    fig = go.Figure()
    
    # Color code by impact (green for savings, red for costs)
    colors = ['#28a745' if x < 0 else '#dc3545' 
              for x in significant_df['Total Financial Impact']]
    
    fig.add_trace(go.Bar(
        x=significant_df['Total Financial Impact'],
        y=significant_df['Initiative'],
        orientation='h',
        marker_color=colors,
        text=[format_currency(abs(x)) for x in significant_df['Total Financial Impact']],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Initiative Financial Impact (Top Contributors)",
        xaxis_title="Financial Impact ($)",
        yaxis_title="",
        height=max(400, len(significant_df) * 40),
        showlegend=False
    )
    
    return fig


def export_to_excel(summary_df, kpi_summary, cost_results, initiative_impact_df=None):
    """Export results to Excel file"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary table
        summary_df.to_excel(writer, sheet_name='Phase Summary', index=False)
        
        # Initiative impacts
        if initiative_impact_df is not None:
            initiative_impact_df.to_excel(writer, sheet_name='Initiative Impacts', index=False)
        
        # KPI summary
        kpi_df = pd.DataFrame([kpi_summary]).T
        kpi_df.columns = ['Value']
        kpi_df.to_excel(writer, sheet_name='KPIs')
        
        # Cost breakdown
        cost_breakdown = []
        for phase in PHASE_ORDER:
            cost_breakdown.append({
                'Phase': phase,
                'Baseline Cost': cost_results['baseline_cost'][phase],
                'Modeled Cost': cost_results['modeled_cost'][phase],
                'Cost Savings': cost_results['savings'][phase],
                'Cost Avoidance': cost_results['avoidance'][phase]
            })
        
        cost_df = pd.DataFrame(cost_breakdown)
        cost_df.to_excel(writer, sheet_name='Cost Details', index=False)
    
    return output.getvalue()


def main():
    """Main application function"""
    load_custom_css()
    
    # Title and version
    from config import APP_VERSION
    st.title("N2S Impact Modeling Tool")
    st.markdown(f"*{APP_VERSION}*")
    
    # Getting Started Guide for Novices
    with st.expander("Getting Started Guide - How This Model Works", expanded=False):
        st.markdown("""
        ## Understanding the N2S Impact Model
        
        This tool helps you estimate the time and cost savings from implementing Next to Source (N2S) efficiency initiatives across your development projects.
        
        ### The Big Picture: How It Works
        
        **1. Initiatives Work Across All Development Phases**
        Your project has 7 phases: Discover → Plan → Design → Build → Test → Deploy → Post Go-Live
        
        Each N2S initiative (like "Automated Testing" or "AI/Automation") can save hours in multiple phases:
        - **Automated Testing** saves the most in Test phase, but also helps in Build and Deploy
        - **Modernization Studio** primarily helps Build and Design phases
        - **Integration Code Reuse** saves time in Build, Test, and Deploy phases
        
        The model calculates how much time each initiative saves in each phase, then adds them up.
        
        ### Key Concepts You Need to Understand
        
        #### **Cost Savings vs Cost Avoidance**
        - **Cost Savings** = Direct money saved during development (fewer hours = lower cost)
        - **Cost Avoidance** = Future costs you avoid after go-live (fewer bugs, faster fixes, less maintenance)
        
        **Think of it this way:**
        - Cost Savings: "We finished the project $50k under budget"
        - Cost Avoidance: "Because we built it better, we're saving $20k/month in support costs"
        
        #### **How to Set Cost Avoidance:**
        - **Conservative (1.5x)**: Very risk-averse, minimal long-term benefits
        - **Moderate (2.5x)**: Industry average for shift-left practices
        - **Aggressive (4-6x)**: High-maturity organizations with strong DevOps practices
        
        ### Step-by-Step: How to Use This Model
        
        #### **Step 1: Set Your Project Context (Do This First)**
        1. **Total Project Hours**: How big is your project? (5k = small, 20k = medium, 50k = large)
        2. **Phase Allocation**: What type of project?
           - **Greenfield/New**: More Design (20%) and Build (30%)
           - **Maintenance**: More Test (25%) and Deploy (15%)
           - **Migration**: More Discover (10%) and Plan (15%)
        3. **Cost Avoidance Model**: Start with "Moderate (2.5x)" - adjust later based on your organization's maturity
        
        #### **Step 2: Choose Your Initiatives (Core Decision)**
        - **Enable only initiatives your organization actually has access to**
        - **Weight them by relevance** (100% = fully applicable, 50% = partially applicable)
        - Common starting point: Enable all at 100% weight, then adjust down
        
        #### **Step 3: Set Industry Benchmarks (Important!)**
        These reflect your organization's **current state automation maturity**:
        
        **If you're a legacy organization (lots of manual processes):**
        - Testing Phase Reduction: 50-70% (high savings potential)
        - Manual Testing Reduction: 60-70% (lots of manual work to automate)
        - Quality Improvement: 30-40% (big gains from better practices)
        
        **If you're already modern/automated:**
        - Testing Phase Reduction: 20-35% (already automated, smaller gains)
        - Manual Testing Reduction: 15-30% (less manual work to eliminate)
        - Quality Improvement: 10-20% (incremental improvements only)
        
        #### **Step 4: Fine-Tune the Details (Do This Last)**
        1. **Initiative Maturity Levels**: Start with 50% for all, then adjust based on your organization's adoption
        2. **Blended Hourly Rate**: Adjust for your location and team composition
        3. **Risk Weights**: Start with defaults, increase for high-risk/complex phases
        
        ### What the Results Tell You
        
        - **Hours Saved**: Direct time reduction in your project
        - **Cost Savings**: Money saved during development 
        - **Cost Avoidance**: Future operational savings
        - **Total Financial Benefit**: Combined impact over time
        
        ### Pro Tips for Realistic Results
        
        1. **Start Conservative**: It's better to under-promise and over-deliver
        2. **Focus on 2-3 Key Initiatives**: Don't try to implement everything at once
        3. **Adjust Industry Benchmarks First**: This has the biggest impact on results
        4. **Validate with Pilots**: Run small pilots to validate your assumptions before scaling
        
        ---
        **Ready to start? Work through Steps 1-4 above, then review your results!**
        """)
    
    # Understanding Your Baseline - NEW SECTION
    with st.expander("Understanding Your Baseline Efficiency", expanded=False):
        st.markdown("""
        ## What Does "Baseline" Mean in This Model?
        
        **Your baseline represents your organization's CURRENT development efficiency** - how you build software TODAY without any N2S initiatives.
        
        ### Baseline Assumptions (Industry Averages)
        
        The model assumes your current baseline includes:
        
        #### **Current Automation Level: ~20-30%**
        - **Some basic unit testing** (but not comprehensive)
        - **Manual regression testing** for most critical paths
        - **Basic CI/CD pipelines** (but not fully automated)
        - **Standard development tools** (IDEs, version control)
        - **Traditional project management** approaches
        
        #### **Current Quality Practices:**
        - **Bug detection primarily in testing phases** (not shift-left)
        - **Manual code reviews** without extensive automation
        - **Standard defect rates** (industry average: 1-5 defects per 1000 lines of code)
        - **Traditional environment setup** (some manual configuration)
        
        #### **Current Integration Patterns:**
        - **Custom integrations** built from scratch for most projects
        - **Limited code reuse** between projects
        - **Manual deployment processes** for production releases
        
        ### How N2S Initiatives Improve Upon Baseline
        
        **The efficiency gains calculated represent improvements ABOVE your current baseline:**
        
        #### **Example: Automated Testing Initiative**
        - **Your Baseline**: 70% manual testing, 30% automated
        - **At 50% N2S Maturity**: 45% manual testing, 55% automated  
        - **At 100% N2S Maturity**: 15% manual testing, 85% automated
        - **Hours Saved**: Reduction in manual testing effort + faster feedback loops
        
        #### **Example: Integration Code Reuse**
        - **Your Baseline**: Build each integration from scratch
        - **At 50% N2S Maturity**: Reuse 40-50% of integration components
        - **At 100% N2S Maturity**: Reuse 80-90% via standardized API library
        - **Hours Saved**: Reduction in custom development time
        
        ### Calibrating to YOUR Baseline
        
        **If your organization is MORE advanced than industry average:**
        - Set **Industry Benchmarks lower** (20-30% improvements)
        - Your actual savings will be **smaller** than shown
        - Focus on **incremental optimization** rather than transformation
        
        **If your organization is LESS advanced than industry average:**
        - Set **Industry Benchmarks higher** (50-70% improvements)  
        - Your actual savings will be **larger** than shown
        - You have **significant transformation opportunity**
        
        ### Key Principle: Conservative by Design
        
        **This model errs on the side of conservative estimates:**
        - Baseline assumes you're **already doing some automation**
        - Efficiency gains are **incremental improvements**, not wholesale transformation
        - Results should be **achievable and defensible** to stakeholders
        
                 **Bottom Line:** The baseline represents a "typical" software development organization with moderate automation maturity. Adjust the Industry Benchmarks to reflect YOUR organization's current state relative to this baseline.
        """)
    
    # Load model
    model = initialize_model()
    
    # Create sidebar controls (includes maturity assessment)
    controls = create_sidebar_controls()
    if controls is None:
        st.error("Please fix the phase allocation percentages in the sidebar.")
        return
    
    # Display Maturity Assessment Results
    st.header("Maturity Assessment Results")
    
    current_maturity = controls['current_maturity']
    feasibility = controls['feasibility']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Current Maturity Level",
            f"Level {current_maturity['maturity_level']}",
            delta=current_maturity['maturity_name']
        )
    
    with col2:
        st.metric(
            "Maturity-Based Potential", 
            f"{current_maturity['current_savings_potential']:.1f}%",
            delta=f"Based on assessment",
            help="Maximum realistic savings based on your current automation maturity level"
        )
    
    with col3:
        target_savings = controls['scenario_config']['target_percentage']
        if feasibility['feasible']:
            st.metric("Target Feasibility", f"{target_savings}% Target", delta="✓ Achievable")
        else:
            st.metric("Target Feasibility", f"{target_savings}% Target", delta=f"⚠ {feasibility['gap']:.1f}% gap")
    
    # Maturity Details and Recommendations
    with st.expander("Maturity Analysis & Recommendations", expanded=False):
        st.markdown(f"""
        ### Current State: {current_maturity['maturity_name']}
        
        **Description:** {current_maturity['maturity_description']}
        
        ### Current Automation Characteristics:
        """)
        
        for area, description in current_maturity['automation_characteristics'].items():
            st.markdown(f"- **{area.replace('_', ' ').title()}**: {description}")
        
        if not feasibility['feasible']:
            st.markdown(f"""
            ### Recommendations to Reach {target_savings}% Target:
            
            **Required Maturity Level:** {feasibility['required_maturity_name']} (Level {feasibility['required_maturity_level']})
            """)
            
            for i, recommendation in enumerate(feasibility['recommendations'], 1):
                st.markdown(f"{i}. {recommendation}")
        
        else:
            st.success("Your current maturity level supports your target savings goal!")
    
    # Run calculations with NEW INDUSTRY-GROUNDED MODEL
    try:
        # Use new simplified model that calculates savings directly from initiative maturity
        results = calculate_with_new_model(
            model,
            controls['maturity_levels'],
            controls['total_hours'],
            controls['phase_allocation'],
            controls['blended_rate'],
            controls['risk_weights'],
            controls['cost_avoidance_config']
        )
        
        # Unpack results
        baseline_hours = results['baseline_hours']
        modeled_hours = results['modeled_hours']
        cost_results = results['cost_results']
        risk_adjusted_hours = results['risk_adjusted_hours']
        summary_df = results['summary_df']
        kpi_summary = results['kpi_summary']
        initiative_impact_df = results['initiative_impact_df']
        savings_detail_df = results['savings_detail_df']
        actual_savings_pct = results['actual_savings_pct']
        
        # Validate results
        is_valid, warning = validate_scenario_results(
            kpi_summary['total_baseline_cost'],
            kpi_summary['total_modeled_cost']
        )
        
        if not is_valid:
            st.warning(warning)
        
        # Display results
        st.header("Results Dashboard")
        
        # KPI Metrics
        st.subheader("Key Performance Indicators")
        display_kpi_metrics(kpi_summary)
        
        # Add Actual Modeled Savings metric prominently below KPIs
        # NOTE: actual_savings_pct is now calculated from the new model
        target_savings = controls['scenario_config']['target_percentage']
        
        col1, col2, col3, col4 = st.columns(4)
        with col2:
            st.metric(
                "🎯 Actual Modeled Savings",
                f"{actual_savings_pct:.1f}%",
                delta=f"Target: {target_savings}%",
                help="Real-time savings percentage - updates when you change initiative maturity or sliders"
            )
        with col3:
            if actual_savings_pct >= target_savings:
                st.success(f"✅ At or above target!")
            elif actual_savings_pct >= target_savings * 0.8:
                gap = target_savings - actual_savings_pct
                st.info(f"📈 {gap:.1f}% to target")
            else:
                gap = target_savings - actual_savings_pct
                st.warning(f"⚠️ {gap:.1f}% gap to target")
        
        # Detailed calculation trace
        with st.expander("🔬 Calculation Trace (Debug)", expanded=False):
            st.write("**Model Inputs:**")
            st.write(f"Total Hours: {controls['total_hours']:,.0f}")
            st.write(f"Target Savings: {target_savings}%")
            st.write(f"Maturity Level: {controls['current_maturity']['maturity_level']}")
            st.write("")
            
            st.write("**Initiative Maturity Levels Being Used:**")
            for init, mat in controls['maturity_levels'].items():
                if mat > 0:
                    st.write(f"  {init}: {mat}%")
            st.write("")
            
            st.write("**NOTE:** Change the initiative sliders below to see savings update!")
            st.write("")
            
            st.write("**Model Calculations:**")
            st.write(f"Baseline Hours: {sum(baseline_hours.values()):,.0f}")
            st.write(f"Modeled Hours: {sum(modeled_hours.values()):,.0f}")
            st.write(f"Hours Saved: {kpi_summary['total_hours_saved']:,.0f}")
            st.write(f"**Actual Savings %: {actual_savings_pct:.2f}%**")
            st.write("")
            
            st.write("**Phase-by-Phase Breakdown:**")
            for phase in PHASE_ORDER:
                if phase in baseline_hours and phase in modeled_hours:
                    base = baseline_hours[phase]
                    mod = modeled_hours[phase]
                    saved = base - mod
                    pct = (saved / base * 100) if base > 0 else 0
                    st.write(f"  {phase}: {saved:,.0f} hrs ({pct:.1f}%)")
            st.write("")
            
            if actual_savings_pct < target_savings:
                gap = target_savings - actual_savings_pct
                st.write(f"**Gap to Target: {gap:.1f}%**")
                hours_needed = (sum(baseline_hours.values()) * gap / 100)
                st.write(f"Need {hours_needed:,.0f} more hours saved")
                st.write(f"💡 Try: Increase initiative maturity levels above {max([m for m in controls['maturity_levels'].values()])}%")
        
        # Initiative Impact Analysis
        st.subheader("Initiative Impact Analysis")
        st.markdown("See how each initiative contributes to overall savings:")
        
        # Show initiative impact table
        st.dataframe(
            initiative_impact_df.style.format({
                'Maturity %': '{:.0f}%',
                'Baseline Hour Delta': '{:,.0f}',
                'Effective Hour Delta': '{:,.0f}',
                'Development Hours': '{:,.0f}',
                'Post Go-Live Hours': '{:,.0f}',
                'Development Cost Impact': '${:,.0f}',
                'Post Go-Live Cost Impact': '${:,.0f}',
                'Total Financial Impact': '${:,.0f}'
            }),
            use_container_width=True,
            height=400
        )
        
        # Summary table
        st.subheader("Phase-by-Phase Summary")
        st.dataframe(
            summary_df.style.format({
                'Baseline Hours': '{:,.0f}',
                'Modeled Hours': '{:,.0f}',
                'Hour Variance': '{:,.0f}',
                'Hour Variance %': '{:.1f}%',
                'Baseline Cost': '${:,.0f}',
                'Modeled Cost': '${:,.0f}',
                'Cost Variance': '${:,.0f}',
                'Cost Variance %': '{:.1f}%',
                'Risk-Adjusted Hours': '{:,.0f}'
            }),
            use_container_width=True
        )
        
        # Charts
        st.subheader("Executive Cost Analysis")
        
        # New comprehensive cost breakdown chart
        cost_breakdown_chart = create_cost_breakdown_by_phase_chart(cost_results, summary_df)
        st.plotly_chart(cost_breakdown_chart, use_container_width=True)
        
        st.markdown("""
        **Key for Executives:**
        - **Baseline Cost**: What we'd spend without any efficiency initiatives
        - **Actual Cost**: What we actually spend after implementing initiatives  
        - **Direct Savings**: Immediate cost reductions during development
        - **Cost Avoidance**: Future operational savings from better quality/processes
        """)
        
        # New comprehensive hours breakdown chart
        hours_breakdown_chart = create_hours_breakdown_by_phase_chart(summary_df, cost_results)
        st.plotly_chart(hours_breakdown_chart, use_container_width=True)
        
        st.markdown("""
        **Key for Executives (Hours):**
        - **Baseline Hours**: Time we'd spend without any efficiency initiatives
        - **Actual Hours**: Time we actually spend after implementing initiatives  
        - **Hours Saved**: Direct time reductions from efficiency improvements
        - **Hours Avoided**: Future operational time savings from better quality/processes
        """)
        
        # Hours chart data table
        st.subheader("Hours Chart Data Breakdown")
        st.markdown("**Data used to create the Executive Hours Summary chart above:**")
        
        # Create the data table for hours chart using available data
        hours_chart_data = []
        for phase in summary_df['Phase']:
            baseline_hours_val = summary_df[summary_df['Phase'] == phase]['Baseline Hours'].iloc[0]
            modeled_hours_val = summary_df[summary_df['Phase'] == phase]['Modeled Hours'].iloc[0]
            hours_saved_val = summary_df[summary_df['Phase'] == phase]['Hour Variance'].iloc[0]
            
            # Calculate hours avoided for this phase
            if phase == 'Post Go-Live':
                cost_avoidance = cost_results['avoidance'][phase]
                blended_rate = cost_results['baseline_cost'][phase] / baseline_hours_val if baseline_hours_val > 0 else 100
                hours_avoided_val = cost_avoidance / blended_rate if blended_rate > 0 else 0
            else:
                hours_avoided_val = 0
            
            hours_chart_data.append({
                'Phase': phase,
                'Baseline Hours': baseline_hours_val,
                'Actual Hours (After Initiatives)': modeled_hours_val,
                'Hours Saved': hours_saved_val,
                'Hours Avoided': hours_avoided_val
            })
        
        hours_chart_df = pd.DataFrame(hours_chart_data)
        
        # Display the table with formatting
        st.dataframe(
            hours_chart_df.style.format({
                'Baseline Hours': '{:,.0f}',
                'Actual Hours (After Initiatives)': '{:,.0f}',
                'Hours Saved': '{:,.0f}',
                'Hours Avoided': '{:,.0f}'
            }),
            use_container_width=True,
            height=300
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Phase Hours Comparison")
            phase_chart = create_phase_comparison_chart(summary_df)
            st.plotly_chart(phase_chart, use_container_width=True)
        
        with col2:
            st.subheader("Hours Saved by Phase")
            hours_saved_chart = create_hours_saved_chart(summary_df)
            st.plotly_chart(hours_saved_chart, use_container_width=True)
        
        # Financial Benefits Chart
        st.subheader("Financial Benefits Summary")
        cost_chart = create_cost_breakdown_chart(cost_results)
        if cost_chart:
            st.plotly_chart(cost_chart, use_container_width=True)
        
        # Initiative Impact Chart
        st.subheader("Top Initiative Contributors")
        initiative_chart = create_initiative_impact_chart(initiative_impact_df)
        if initiative_chart:
            st.plotly_chart(initiative_chart, use_container_width=True)
        else:
            st.info("No significant initiative impacts to display (adjust maturity levels to see impacts)")
        
        # Variance analysis
        st.subheader("Detailed Variance Analysis")
        variance_chart = create_variance_chart(summary_df)
        st.plotly_chart(variance_chart, use_container_width=True)
        
        # Role-Based Analysis
        st.header("📊 Role-Based Analysis")
        st.markdown("""
        **Role allocation shows how hours and costs are distributed across team members**
        
        This breakdown reflects realistic Banner migration activities by role and phase.
        """)
        
        # Import role-based calculation functions
        from model import (
            calculate_role_based_hours, calculate_role_based_costs,
            get_role_summary, calculate_role_group_totals,
            calculate_role_initiative_multipliers
        )
        from config import (
            ROLE_DEFINITIONS, get_total_role_hours, get_role_groups
        )
        
        # Calculate role-specific multipliers based on initiative maturity levels
        role_multipliers = calculate_role_initiative_multipliers(controls['maturity_levels'])
        
        # Calculate role-based hours for baseline and modeled scenarios
        # Baseline: normal distribution
        baseline_role_hours = calculate_role_based_hours(
            baseline_hours, 
            include_savings=False
        )
        
        # Modeled: apply role-specific multipliers so different roles benefit differently
        modeled_role_hours = calculate_role_based_hours(
            modeled_hours, 
            include_savings=True,
            role_specific_multipliers=role_multipliers
        )
        
        # Calculate costs
        baseline_role_costs = calculate_role_based_costs(baseline_role_hours)
        modeled_role_costs = calculate_role_based_costs(modeled_role_hours)
        
        # Role summary comparison
        role_summary_df = get_role_summary(baseline_role_hours, modeled_role_hours)
        
        # Display role group totals
        col1, col2, col3 = st.columns(3)
        
        baseline_group_totals = calculate_role_group_totals(baseline_role_hours)
        modeled_group_totals = calculate_role_group_totals(modeled_role_hours)
        
        with col1:
            st.metric(
                "Pod Team Hours (Baseline)",
                f"{baseline_group_totals['Pod']:,.0f}",
                f"{modeled_group_totals['Pod'] - baseline_group_totals['Pod']:,.0f}"
            )
        
        with col2:
            st.metric(
                "Pooled Team Hours (Baseline)",
                f"{baseline_group_totals['Pooled']:,.0f}",
                f"{modeled_group_totals['Pooled'] - baseline_group_totals['Pooled']:,.0f}"
            )
        
        with col3:
            total_role_hours = get_total_role_hours()
            st.metric(
                "Total Role-Based Hours",
                f"{total_role_hours:,.0f}",
                help="Sum of base hours across all roles"
            )
        
        # Role savings summary table
        st.subheader("Role Savings Summary")
        
        # Format the role summary for display
        display_role_summary = role_summary_df.copy()
        display_role_summary['Baseline Hours'] = display_role_summary['Baseline Hours'].apply(lambda x: f"{x:,.0f}")
        display_role_summary['Modeled Hours'] = display_role_summary['Modeled Hours'].apply(lambda x: f"{x:,.0f}")
        display_role_summary['Hours Saved'] = display_role_summary['Hours Saved'].apply(lambda x: f"{x:,.0f}")
        display_role_summary['% Saved'] = display_role_summary['% Saved'].apply(lambda x: f"{x:.1f}%")
        display_role_summary['Hourly Rate'] = display_role_summary['Hourly Rate'].apply(lambda x: f"${x:,.0f}")
        display_role_summary['Cost Savings'] = display_role_summary['Cost Savings'].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(
            display_role_summary,
            use_container_width=True,
            hide_index=True
        )
        
        # Role-based cost comparison chart
        st.subheader("Cost Distribution by Role")
        
        # Create cost comparison chart
        fig_role_costs = go.Figure()
        
        # Calculate total costs by role
        baseline_costs_by_role = baseline_role_costs.sum(axis=1).sort_values(ascending=True)
        modeled_costs_by_role = modeled_role_costs.sum(axis=1).loc[baseline_costs_by_role.index]
        
        fig_role_costs.add_trace(go.Bar(
            name='Baseline Cost',
            y=baseline_costs_by_role.index,
            x=baseline_costs_by_role.values,
            orientation='h',
            marker_color='lightcoral',
            text=[f"${v:,.0f}" for v in baseline_costs_by_role.values],
            textposition='auto'
        ))
        
        fig_role_costs.add_trace(go.Bar(
            name='Modeled Cost',
            y=modeled_costs_by_role.index,
            x=modeled_costs_by_role.values,
            orientation='h',
            marker_color='lightblue',
            text=[f"${v:,.0f}" for v in modeled_costs_by_role.values],
            textposition='auto'
        ))
        
        fig_role_costs.update_layout(
            title="Total Cost by Role: Baseline vs Modeled",
            xaxis_title="Cost ($)",
            yaxis_title="Role",
            barmode='group',
            height=600,
            showlegend=True
        )
        
        st.plotly_chart(fig_role_costs, use_container_width=True)
        
        # Phase-by-role heatmap
        st.subheader("Hours Distribution: Roles × Phases")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Baseline Hours by Role and Phase**")
            # Create heatmap for baseline
            fig_baseline_heatmap = go.Figure(data=go.Heatmap(
                z=baseline_role_hours.values,
                x=baseline_role_hours.columns,
                y=baseline_role_hours.index,
                colorscale='Blues',
                text=baseline_role_hours.round(0).values,
                texttemplate='%{text}',
                textfont={"size": 8},
                colorbar=dict(title="Hours")
            ))
            
            fig_baseline_heatmap.update_layout(
                height=600,
                xaxis_title="Phase",
                yaxis_title="Role"
            )
            
            st.plotly_chart(fig_baseline_heatmap, use_container_width=True)
        
        with col2:
            st.markdown("**Modeled Hours by Role and Phase**")
            # Create heatmap for modeled
            fig_modeled_heatmap = go.Figure(data=go.Heatmap(
                z=modeled_role_hours.values,
                x=modeled_role_hours.columns,
                y=modeled_role_hours.index,
                colorscale='Greens',
                text=modeled_role_hours.round(0).values,
                texttemplate='%{text}',
                textfont={"size": 8},
                colorbar=dict(title="Hours")
            ))
            
            fig_modeled_heatmap.update_layout(
                height=600,
                xaxis_title="Phase",
                yaxis_title="Role"
            )
            
            st.plotly_chart(fig_modeled_heatmap, use_container_width=True)
        
        # Role details expander
        with st.expander("📋 Role Definitions & Responsibilities"):
            role_groups = get_role_groups()
            
            st.markdown("### Pod Team (Core Delivery)")
            for role_name in role_groups['Pod']:
                role_info = ROLE_DEFINITIONS[role_name]
                st.markdown(f"""
                **{role_name}** - ${role_info['hourly_rate']}/hr ({role_info['base_hours']} hrs)
                - {role_info['description']}
                """)
            
            st.markdown("### Pooled Team (Specialized)")
            for role_name in role_groups['Pooled']:
                role_info = ROLE_DEFINITIONS[role_name]
                st.markdown(f"""
                **{role_name}** - ${role_info['hourly_rate']}/hr ({role_info['base_hours']} hrs)
                - {role_info['description']}
                """)
        
        # Strategic Savings Category Breakdown
        st.header("💰 Strategic Savings Breakdown")
        st.markdown("""
        **Savings categorized by strategic value drivers**
        
        This view shows how each role's savings break down across three key N2S value categories.
        """)
        
        # Import category calculation functions
        from model import (
            calculate_savings_by_category,
            get_category_savings_summary
        )
        from config import SAVINGS_CATEGORIES
        
        # Calculate savings by category
        category_savings_df = calculate_savings_by_category(
            baseline_role_hours,
            modeled_role_hours,
            controls['maturity_levels']
        )
        
        category_summary_df = get_category_savings_summary(
            category_savings_df,
            baseline_role_hours,
            modeled_role_hours
        )
        
        # Display category totals
        col1, col2, col3, col4 = st.columns(4)
        
        total_ootb = category_summary_df['OOtB Config $'].sum()
        total_methodology = category_summary_df['Methodology $'].sum()
        total_ai = category_summary_df['AI & Automation $'].sum()
        total_all = total_ootb + total_methodology + total_ai
        
        with col1:
            st.metric(
                "🟢 OOtB Config Savings",
                format_currency(total_ootb),
                delta=f"{(total_ootb/total_all*100):.0f}% of total" if total_all > 0 else ""
            )
        
        with col2:
            st.metric(
                "🔵 Methodology Savings",
                format_currency(total_methodology),
                delta=f"{(total_methodology/total_all*100):.0f}% of total" if total_all > 0 else ""
            )
        
        with col3:
            st.metric(
                "🟠 AI & Automation Savings",
                format_currency(total_ai),
                delta=f"{(total_ai/total_all*100):.0f}% of total" if total_all > 0 else ""
            )
        
        with col4:
            st.metric(
                "Total Savings",
                format_currency(total_all)
            )
        
        # Category breakdown table
        st.subheader("Savings by Role and Category")
        
        display_category_df = category_summary_df.copy()
        display_category_df['Total Hours Saved'] = display_category_df['Total Hours Saved'].apply(lambda x: f"{x:,.0f}")
        display_category_df['Total % Saved'] = display_category_df['Total % Saved'].apply(lambda x: f"{x:.1f}%")
        display_category_df['OOtB Config Hours'] = display_category_df['OOtB Config Hours'].apply(lambda x: f"{x:,.0f}")
        display_category_df['Methodology Hours'] = display_category_df['Methodology Hours'].apply(lambda x: f"{x:,.0f}")
        display_category_df['AI & Automation Hours'] = display_category_df['AI & Automation Hours'].apply(lambda x: f"{x:,.0f}")
        display_category_df['OOtB Config $'] = display_category_df['OOtB Config $'].apply(lambda x: f"${x:,.0f}")
        display_category_df['Methodology $'] = display_category_df['Methodology $'].apply(lambda x: f"${x:,.0f}")
        display_category_df['AI & Automation $'] = display_category_df['AI & Automation $'].apply(lambda x: f"${x:,.0f}")
        display_category_df['Total Cost Saved'] = display_category_df['Total Cost Saved'].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(
            display_category_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Category breakdown chart
        st.subheader("Cost Savings Distribution by Category")
        
        # Create stacked bar chart by role
        fig_categories = go.Figure()
        
        roles = category_summary_df['Role'].tolist()
        
        fig_categories.add_trace(go.Bar(
            name='OOtB Config',
            x=roles,
            y=category_summary_df['OOtB Config $'].tolist(),
            marker_color=SAVINGS_CATEGORIES['OOtB Config']['color'],
            text=[f"${v:,.0f}" for v in category_summary_df['OOtB Config $'].tolist()],
            textposition='inside'
        ))
        
        fig_categories.add_trace(go.Bar(
            name='Methodology',
            x=roles,
            y=category_summary_df['Methodology $'].tolist(),
            marker_color=SAVINGS_CATEGORIES['N2S Methodology & Controls']['color'],
            text=[f"${v:,.0f}" for v in category_summary_df['Methodology $'].tolist()],
            textposition='inside'
        ))
        
        fig_categories.add_trace(go.Bar(
            name='AI & Automation',
            x=roles,
            y=category_summary_df['AI & Automation $'].tolist(),
            marker_color=SAVINGS_CATEGORIES['AI & Automation']['color'],
            text=[f"${v:,.0f}" for v in category_summary_df['AI & Automation $'].tolist()],
            textposition='inside'
        ))
        
        fig_categories.update_layout(
            barmode='stack',
            title="Cost Savings by Role and Category",
            xaxis_title="Role",
            yaxis_title="Cost Savings ($)",
            height=600,
            showlegend=True,
            xaxis={'tickangle': -45}
        )
        
        st.plotly_chart(fig_categories, use_container_width=True)
        
        # Category descriptions
        with st.expander("📋 Category Definitions"):
            for category_key, category_info in SAVINGS_CATEGORIES.items():
                st.markdown(f"""
                **{category_info['name']}**
                - {category_info['description']}
                """)
        
        # Export functionality
        st.header("Export Results")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV export
            csv_data = summary_df.to_csv(index=False)
            st.download_button(
                label="📄 Download Results CSV",
                data=csv_data,
                file_name=f"n2s_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )
        
        with col2:
            # Excel export
            excel_data = export_to_excel(summary_df, kpi_summary, cost_results, initiative_impact_df)
            st.download_button(
                label="📊 Download Results Excel",
                data=excel_data,
                file_name=f"n2s_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        with col3:
            # Model parameters export
            model_params = {
                'export_timestamp': datetime.now().isoformat(),
                'project_parameters': {
                    'total_hours': controls['total_hours'],
                    'blended_rate': controls['blended_rate'],
                    'target_savings_percentage': controls['scenario_config']['target_percentage']
                },
                'phase_allocation': controls['phase_allocation'],
                'initiative_maturity_levels': controls['maturity_levels'],
                'risk_weights': controls['risk_weights'],
                'industry_benchmarks': {
                    'testing_phase_reduction': controls['industry_benchmarks']['testing_phase_reduction'],
                    'manual_testing_reduction': controls['industry_benchmarks']['manual_testing_reduction'],
                    'quality_improvement': controls['industry_benchmarks']['quality_improvement'],
                    'post_release_defect_reduction': controls['industry_benchmarks']['post_release_defect_reduction']
                },
                'maturity_assessment': {
                    'level': controls['current_maturity']['maturity_level'],
                    'name': controls['current_maturity']['maturity_name'],
                    'savings_potential': controls['current_maturity']['current_savings_potential']
                },
                'cost_avoidance_config': controls['cost_avoidance_config'],
                'model_results': {
                    'actual_savings_percentage': abs(kpi_summary['total_hours_saved_pct']),
                    'total_hours_saved': kpi_summary['total_hours_saved'],
                    'total_cost_savings': kpi_summary['total_cost_savings'],
                    'total_financial_benefit': kpi_summary['total_financial_benefit']
                }
            }
            
            params_json = json.dumps(model_params, indent=2)
            st.download_button(
                label="⚙️ Download Model Parameters",
                data=params_json,
                file_name=f"n2s_parameters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime='application/json',
                help="Export all model inputs and settings for documentation or reloading"
            )
        
        # Model details
        with st.expander("Model Details & Assumptions"):
            st.markdown("""
            **Dynamic Scaling Approach:**
            - **5-12%**: Conservative automation, proven low-risk approaches
            - **13-22%**: Moderate automation with enhanced testing and quality  
            - **23%+**: Aggressive transformation with comprehensive safety caps
            
            **Scenario Definitions:**
            - **Target: ~10% Savings**: Light automation improvements, proven approaches
            - **Target: ~20% Savings**: Moderate automation with enhanced testing  
            - **Target: ~30% Savings**: Aggressive automation transformation
            
            **Key Assumptions:**
            - Direct savings apply to development phases (Discover-Deploy)
            - Cost avoidance applies to Post Go-Live phase
            - Risk weights multiply modeled hours for risk assessment
            - Maximum total cost reduction capped at 30%
            """)
        
        # Initiative Maturity Guide
        with st.expander("Initiative Maturity Level Guide"):
            from config import (
                INITIATIVE_MATURITY_DEFINITIONS,
                get_initiative_description, get_maturity_description
            )
            
            st.markdown("### Initiative Definitions and Maturity Levels")
            
            initiative_list = get_initiatives()
            for initiative in initiative_list:
                st.markdown(f"#### {initiative}")
                desc = get_initiative_description(initiative)
                st.markdown(f"**Description:** {desc}")
                
                st.markdown("**Maturity Levels:**")
                if initiative in INITIATIVE_MATURITY_DEFINITIONS:
                    definitions = INITIATIVE_MATURITY_DEFINITIONS[initiative]
                    for level, definition in definitions.items():
                        if level != "description":  # Skip the main description
                            st.markdown(f"- **{level}:** {definition}")
                else:
                    st.markdown("- **0%:** Not implemented")
                    st.markdown("- **25%:** Initial adoption")  
                    st.markdown("- **50%:** Regular use")
                    st.markdown("- **75%:** Advanced implementation")
                    st.markdown("- **100%:** Fully mature and optimized")
                
                st.markdown("---")
        
        # Risk Assessment Guide
        with st.expander("Risk Assessment Guide"):
            from config import (
                RISK_LEVEL_DEFINITIONS,
                get_phase_risk_info, get_risk_level_description
            )
            # Note: PHASE_ORDER already imported at module level
            
            st.markdown("### Risk Level Guidelines")
            
            # General risk information
            general_info = RISK_LEVEL_DEFINITIONS["general"]
            st.markdown(f"**Overview:** {general_info['description']}")
            
            st.markdown("### Risk Level Definitions")
            for level, desc in general_info.items():
                if level != "description":  # Skip the general description
                    st.markdown(f"- **{level}x:** {desc}")
            
            st.markdown("### Phase-Specific Risk Factors")
            
            for phase in PHASE_ORDER:
                phase_info = get_phase_risk_info(phase)
                st.markdown(f"#### {phase}")
                st.markdown(f"**Description:** {phase_info['description']}")
                
                st.markdown("**Typical Risk Factors:**")
                for risk in phase_info['typical_risks']:
                    st.markdown(f"- {risk}")
                
                st.markdown(f"**Low Risk Example:** {phase_info['low_risk']}")
                st.markdown(f"**High Risk Example:** {phase_info['high_risk']}")
                st.markdown("---")
    
    except Exception as e:
        st.error(f"Error running calculations: {e}")
        st.exception(e)

if __name__ == "__main__":
    main() 