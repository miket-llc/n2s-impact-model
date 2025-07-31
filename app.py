"""
N2S Efficiency Modeling Application
Interactive Streamlit app for quantifying professional services efficiency gains
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
import os

from model import N2SEfficiencyModel, run_model_scenario, get_initiatives
from config import (
    DEFAULT_TOTAL_HOURS, DEFAULT_BLENDED_RATE, DEFAULT_PHASE_ALLOCATION,
    DEFAULT_RISK_WEIGHTS, PHASE_ORDER, SCENARIOS, COST_AVOIDANCE_OPTIONS,
    get_phase_colors, format_currency, format_hours, format_percentage, 
    validate_scenario_results
)

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

@st.cache_data
def initialize_model():
    """Initialize and cache the model instance"""
    model = N2SEfficiencyModel()
    success = model.load_matrix("data/ShiftLeft_Levers_PhaseMatrix_v3.xlsx")
    if not success:
        st.warning("Using sample data. Place ShiftLeft_Levers_PhaseMatrix_v3.xlsx in data/ folder for actual data.")
    return model

def create_sidebar_controls():
    """Create sidebar input controls for model parameters"""
    from config import (
        get_initiative_description, get_maturity_description,
        RISK_LEVEL_DEFINITIONS, get_phase_risk_info, get_risk_level_description,
        INITIATIVE_FALLBACK, INDUSTRY_BENCHMARKS
    )
    
    st.sidebar.title("🎛️ Model Parameters")
    
    # Version indicator in sidebar
    from config import APP_VERSION
    st.sidebar.caption(f"📊 {APP_VERSION}")
    
    # =============================================================================
    # PROJECT CONFIGURATION
    # =============================================================================
    
    st.sidebar.subheader("🏗️ Project Configuration")
    
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
        help="Average hourly cost across all team members (developers, testers, architects, etc.)"
    )
    
    # =============================================================================
    # INITIATIVE SELECTION & WEIGHTS
    # =============================================================================
    
    st.sidebar.subheader("🎯 Initiative Selection")
    st.sidebar.markdown("**Select which N2S initiatives your organization has access to:**")
    
    initiative_weights = {}
    available_initiatives = []
    
    for initiative in INITIATIVE_FALLBACK:
        col1, col2 = st.sidebar.columns([3, 1])
        
        with col1:
            enabled = st.checkbox(
                initiative,
                value=True,
                key=f"enable_{initiative}",
                help=get_initiative_description(initiative)
            )
        
        with col2:
            if enabled:
                weight = st.number_input(
                    "Weight",
                    min_value=0,
                    max_value=100,
                    value=100,
                    step=5,
                    key=f"weight_{initiative}",
                    help="Relevance to your project (0-100%)"
                )
                initiative_weights[initiative] = weight / 100.0
                available_initiatives.append(initiative)
            else:
                initiative_weights[initiative] = 0.0
    
    # =============================================================================
    # DEVELOPMENT EFFICIENCY SCENARIO
    # =============================================================================
    
    st.sidebar.subheader("⚡ Development Efficiency")
    
    scenario = st.sidebar.selectbox(
        "Development Efficiency Scenario",
        options=list(SCENARIOS.keys()),
        index=0,  # Default to conservative "Baseline Matrix"
        help="Choose the level of efficiency improvements to model"
    )
    
    # =============================================================================
    # INITIATIVE MATURITY LEVELS
    # =============================================================================
    
    st.sidebar.subheader("📈 Initiative Maturity Levels")
    
    maturity_levels = {}
    for initiative in available_initiatives:
        if initiative_weights[initiative] > 0:  # Only show enabled initiatives
            help_text = get_maturity_description(initiative)
            caption = f"Weight: {initiative_weights[initiative]*100:.0f}% | {help_text}"
            
            maturity_levels[initiative] = st.sidebar.slider(
                f"{initiative}",
                min_value=0,
                max_value=100,
                value=50,
                step=5,
                help=f"Current implementation maturity for {initiative}",
                key=f"maturity_{initiative}"
            )
            st.sidebar.caption(caption)
        else:
            maturity_levels[initiative] = 0  # Disabled initiatives
    
    # =============================================================================
    # INDUSTRY BENCHMARKS
    # =============================================================================
    
    st.sidebar.subheader("🏭 Industry Benchmarks")
    st.sidebar.markdown("""
    **Adjust these benchmarks based on your organization's current automation maturity:**
    
    📊 **Research Sources:**
    - Gartner/Forrester automation studies
    - McKinsey quality improvement research  
    - Perfecto/Testlio testing efficiency reports
    - IBM Systems Sciences shift-left analysis
    """)
    
    # Testing Phase Reduction
    st.sidebar.markdown("**🧪 Testing Automation Effectiveness**")
    testing_reduction = st.sidebar.slider(
        "Testing Phase Time Reduction",
        min_value=0.1,
        max_value=0.8,
        value=float(INDUSTRY_BENCHMARKS['testing_phase_reduction']),
        step=0.05,
        format="%.0f%%",
        help="""How much can automated testing reduce overall testing time?

**Research Base:** Perfecto/Testlio studies show 30-50% reduction in testing cycles with proper automation.

**Your Context:**
• **Legacy/Manual (20-30%)**: Heavy manual testing, minimal automation
• **Moderate (35-50%)**: Some automation, mixed manual/automated  
• **Advanced (55-70%)**: Comprehensive test automation suites
• **Best-in-Class (70%+)**: AI-driven testing, full CI/CD integration

**Higher values appropriate for:** Organizations transitioning from manual to automated testing
**Lower values appropriate for:** Already automated organizations with limited additional gains"""
    )
    
    # Manual Testing Reduction  
    manual_testing_reduction = st.sidebar.slider(
        "Manual Testing Reduction",
        min_value=0.1,
        max_value=0.7,
        value=float(INDUSTRY_BENCHMARKS['manual_testing_reduction']),
        step=0.05,
        format="%.0f%%",
        help="""How much manual testing effort can be eliminated through automation?

**Research Base:** Industry studies show 35-45% reduction in manual testing effort.

**Your Context:**
• **High Manual (50-70%)**: Currently 80%+ manual testing
• **Mixed (30-50%)**: 50/50 manual vs automated testing
• **Automated (15-35%)**: Already mostly automated testing

**Consider your current state:** Higher reduction rates apply to organizations with significant manual testing overhead."""
    )
    
    # Quality Improvement
    st.sidebar.markdown("**✨ Quality & Defect Reduction**")
    quality_improvement = st.sidebar.slider(
        "Overall Quality Improvement",
        min_value=0.05,
        max_value=0.5,
        value=float(INDUSTRY_BENCHMARKS['quality_improvement']),
        step=0.05,
        format="%.0f%%",
        help="""Overall improvement in software quality from shift-left practices.

**Research Base:** McKinsey studies show 20% average quality improvement from shift-left methodologies.

**Factors:**
• **Early defect detection** through better testing
• **Improved code quality** through better tools/processes  
• **Reduced post-production issues** from better validation

**Your Context:**
• **High Defect Rate (30-50%)**: Currently experiencing significant quality issues
• **Average (15-25%)**: Industry-standard quality metrics
• **High Quality (5-15%)**: Already high-quality processes with limited improvement potential"""
    )
    
    defect_reduction = st.sidebar.slider(
        "Post-Release Defect Reduction", 
        min_value=0.1,
        max_value=0.6,
        value=float(INDUSTRY_BENCHMARKS['post_release_defect_reduction']),
        step=0.05,
        format="%.0f%%",
        help="""Reduction in post-production defects from better early-stage practices.

**Research Base:** IBM studies show 25% average reduction in production defects with shift-left.

**Impact Areas:**
• **Fewer hotfixes** and emergency releases
• **Reduced support overhead** and user escalations
• **Lower maintenance burden** on development teams

**Your Context:**
• **High Production Issues (40-60%)**: Frequent post-release defects
• **Moderate (20-30%)**: Occasional production issues  
• **Stable (10-20%)**: Already low defect rates"""
    )
    
    # Package the industry benchmarks
    custom_benchmarks = {
        'testing_phase_reduction': testing_reduction,
        'manual_testing_reduction': manual_testing_reduction,
        'quality_improvement': quality_improvement,
        'post_release_defect_reduction': defect_reduction,
        'test_automation_cost_reduction': INDUSTRY_BENCHMARKS['test_automation_cost_reduction'],
        'defect_fix_cost_multipliers': INDUSTRY_BENCHMARKS['defect_fix_cost_multipliers']
    }
    
    # =============================================================================
    # PHASE ALLOCATION
    # =============================================================================
    
    st.sidebar.subheader("⏱️ Phase Time Allocation")
    st.sidebar.markdown("**Adjust based on your project type:**")
    
    phase_allocation = {}
    remaining = 100
    
    for i, phase in enumerate(PHASE_ORDER):
        if i == len(PHASE_ORDER) - 1:  # Last phase gets remainder
            phase_allocation[phase] = remaining
            st.sidebar.metric(f"{phase} %", f"{remaining}%")
        else:
            default_value = DEFAULT_PHASE_ALLOCATION[phase]
            phase_allocation[phase] = st.sidebar.slider(
                f"{phase} %",
                min_value=1,
                max_value=50,
                value=default_value,
                step=1,
                help=f"Percentage of total project time spent in {phase} phase"
            )
            remaining -= phase_allocation[phase]
    
    # Validation
    total_allocation = sum(phase_allocation.values())
    if abs(total_allocation - 100) > 0.1:
        st.sidebar.error(f"⚠️ Phase allocation must sum to 100% (currently {total_allocation}%)")
    
    # =============================================================================
    # RISK ASSESSMENT
    # =============================================================================
    
    st.sidebar.subheader("⚠️ Risk Assessment")
    
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
        st.sidebar.caption(f"📊 {risk_level_desc}")
    
    # =============================================================================
    # COST AVOIDANCE
    # =============================================================================
    
    st.sidebar.subheader("💰 Cost Avoidance")
    
    cost_avoidance_selection = st.sidebar.selectbox(
        "Cost Avoidance Model",
        options=list(COST_AVOIDANCE_OPTIONS.keys()),
        index=3,  # Default to "Moderate (2.5x)"
        help="How much additional value beyond direct development savings?"
    )
    
    cost_avoidance_config = COST_AVOIDANCE_OPTIONS[cost_avoidance_selection]
    
    return {
        'total_hours': total_hours,
        'blended_rate': blended_rate,
        'phase_allocation': phase_allocation,
        'maturity_levels': maturity_levels,
        'initiative_weights': initiative_weights,
        'available_initiatives': available_initiatives,
        'scenario': scenario,
        'risk_weights': risk_weights,
        'cost_avoidance_config': cost_avoidance_config,
        'industry_benchmarks': custom_benchmarks
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
                kpi_summary['baseline_total_cost'] - kpi_summary['modeled_total_cost']
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
        marker_color='lightcoral',
        text=[format_currency(c) for c in baseline_costs],
        textposition='outside'
    ))
    
    # Modeled costs (what we actually spend after initiatives)
    fig.add_trace(go.Bar(
        x=phases,
        y=modeled_costs,
        name='Actual Cost (After Initiatives)',
        marker_color='lightblue',
        text=[format_currency(c) for c in modeled_costs],
        textposition='outside'
    ))
    
    # Direct cost savings (negative bars showing savings)
    fig.add_trace(go.Bar(
        x=phases,
        y=[-s for s in direct_savings],  # Show savings as negative
        name='Direct Savings',
        marker_color='green',
        text=[format_currency(-s) if s > 0 else '' for s in direct_savings],
        textposition='outside'
    ))
    
    # Cost avoidance (additional benefits, shown as negative)
    fig.add_trace(go.Bar(
        x=phases,
        y=[-a for a in cost_avoidance],  # Show avoidance as negative
        name='Cost Avoidance',
        marker_color='darkgreen',
        text=[format_currency(-a) if a > 0 else '' for a in cost_avoidance],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Executive Cost Summary: Baseline vs Actual Costs with Benefits",
        xaxis_title="Project Phase",
        yaxis_title="Cost ($)",
        barmode='group',
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        annotations=[
            dict(
                x=0.5, xref='paper',
                y=1.15, yref='paper',
                text="Green bars show financial benefits (savings = immediate, avoidance = future)",
                showarrow=False,
                font=dict(size=12, color='gray')
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
    
    # Header
    st.title("Navigate-to-SaaS Efficiency Model")
    
    # Version indicator for deployment tracking
    from config import APP_VERSION
    st.markdown(f"**{APP_VERSION}** | *Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC*")
    
    st.markdown("""
    **Quantifying Professional Services Efficiency Gains**  
    Interactive modeling tool for Ellucian's N2S "shift-left" delivery methodology
    """)
    
    # Initialize model
    model = initialize_model()
    
    # Create sidebar controls
    controls = create_sidebar_controls()
    if controls is None:
        st.error("Please fix the phase allocation percentages in the sidebar.")
        return
    
    # Run calculations
    try:
        # Apply maturity and scenario with custom industry benchmarks
        effective_deltas = model.apply_maturity_and_scenario(
            controls['maturity_levels'],
            controls['scenario'],
            controls['industry_benchmarks']
        )
        
        baseline_hours, modeled_hours = model.calculate_phase_hours(
            controls['total_hours'], 
            controls['phase_allocation'], 
            effective_deltas
        )
        
        # Get cost avoidance configuration
        cost_avoidance_config = controls['cost_avoidance_config']
        
        cost_results = model.calculate_costs_and_savings(
            baseline_hours, 
            modeled_hours, 
            controls['blended_rate'],
            True, # Always include cost avoidance for now
            cost_avoidance_config
        )
        
        risk_adjusted_hours = model.calculate_risk_adjusted_hours(
            modeled_hours, 
            controls['risk_weights']
        )
        
        summary_df = model.generate_summary_table(
            baseline_hours, 
            modeled_hours,
            cost_results['baseline_cost'], 
            cost_results['modeled_cost'],
            risk_adjusted_hours
        )
        
        kpi_summary = model.get_kpi_summary(
            baseline_hours, 
            modeled_hours, 
            cost_results
        )
        
        # Generate initiative impact analysis
        initiative_impact_df = model.generate_initiative_impact_table(
            effective_deltas,
            controls['maturity_levels'],
            controls['blended_rate'],
            True, # Always include cost avoidance for now
            cost_avoidance_config
        )
        
        # Validate results
        is_valid, warning = validate_scenario_results(
            kpi_summary['baseline_total_cost'],
            kpi_summary['modeled_total_cost']
        )
        
        if not is_valid:
            st.warning(warning)
        
        # Display results
        st.header("Results Dashboard")
        
        # KPI Metrics
        st.subheader("Key Performance Indicators")
        display_kpi_metrics(kpi_summary)
        
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
        
        # Export functionality
        st.header("Export Results")
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export
            csv_data = summary_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"n2s_efficiency_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )
        
        with col2:
            # Excel export
            excel_data = export_to_excel(summary_df, kpi_summary, cost_results, initiative_impact_df)
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name=f"n2s_efficiency_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        # Model details
        with st.expander("Model Details & Assumptions"):
            st.markdown("""
            **Industry Benchmarks Used:**
            - Test automation cost reduction: 15% (Gartner/Forrester)
            - Quality improvement: 20% 
            - Post-release defect reduction: 25% (McKinsey)
            - Testing phase reduction: 30-40% (Perfecto/Testlio)
            - Manual testing reduction: 35%
            
            **Scenario Definitions:**
            - **Baseline Matrix**: Conservative improvements using matrix values
            - **Enhanced (20% boost)**: Enhanced benefits from higher automation
            - **Maximum (30% boost)**: Near-maximum credible improvements with caps
            
            **Key Assumptions:**
            - Direct savings apply to development phases (Discover-Deploy)
            - Cost avoidance applies to Post Go-Live phase
            - Risk weights multiply modeled hours for risk assessment
            - Maximum total cost reduction capped at 30%
            """)
        
        # Initiative Maturity Guide
        with st.expander("📚 Initiative Maturity Level Guide"):
            from config import INITIATIVE_MATURITY_DEFINITIONS
            
            st.markdown("""
            **Understanding Maturity Levels:**
            
            Maturity levels represent how well your organization has adopted each efficiency initiative:
            - **0%**: Not implemented
            - **25%**: Basic implementation
            - **50%**: Standard adoption
            - **75%**: Advanced implementation
            - **100%**: Fully optimized
            """)
            
            st.markdown("**Initiative Details:**")
            for initiative, definitions in INITIATIVE_MATURITY_DEFINITIONS.items():
                st.markdown(f"**{initiative}**")
                st.markdown(f"*{definitions['description']}*")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"• **0%**: {definitions['0%']}")
                    st.markdown(f"• **50%**: {definitions['50%']}")
                with col2:
                    st.markdown(f"• **25%**: {definitions['25%']}")
                    st.markdown(f"• **75%**: {definitions['75%']}")
                    st.markdown(f"• **100%**: {definitions['100%']}")
                
                st.markdown("---")
        
        # Risk Assessment Guide
        with st.expander("⚠️ Risk Assessment Guide"):
            from config import RISK_LEVEL_DEFINITIONS
            
            st.markdown("""
            **Understanding Risk Weights:**
            
            Risk weights multiply your modeled hours to create more conservative estimates based on project complexity and uncertainty. Use higher weights for riskier phases.
            """)
            
            # General risk level guide
            st.markdown("**Risk Level Guide:**")
            general_risks = RISK_LEVEL_DEFINITIONS["general"]
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"• **0.5x**: {general_risks['0.5']}")
                st.markdown(f"• **2.0x**: {general_risks['2.0']}")
                st.markdown(f"• **5.0x**: {general_risks['5.0']}")
            with col2:
                st.markdown(f"• **1.0x**: {general_risks['1.0']}")
                st.markdown(f"• **3.0x**: {general_risks['3.0']}")
                st.markdown(f"• **7.0x**: {general_risks['7.0']}")
            
            st.markdown("---")
            
            # Phase-specific risk information
            st.markdown("**Phase-Specific Risk Factors:**")
            phase_risks = RISK_LEVEL_DEFINITIONS["phases"]
            
            for phase, info in phase_risks.items():
                st.markdown(f"**{phase} Phase**")
                st.markdown(f"*{info['description']}*")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Typical Risk Factors:**")
                    for risk in info['typical_risks']:
                        st.markdown(f"• {risk}")
                
                with col2:
                    st.markdown(f"**Low Risk Example:** {info['low_risk']}")
                    st.markdown(f"**High Risk Example:** {info['high_risk']}")
                
                st.markdown("---")
    
    except Exception as e:
        st.error(f"Error running calculations: {e}")
        st.exception(e)

if __name__ == "__main__":
    main() 