# Navigate-to-SaaS (N2S) Efficiency Modeling Application

An interactive Streamlit application that quantifies professional services efficiency gains and cost impacts when Ellucian adopts its Navigate-to-SaaS (N2S) "shift-left" delivery methodology.

## ✅ Current Status (October 17, 2025)

**State:** REBUILT - Industry-grounded mathematical foundation  
**Status:** Fully operational with research-backed calculations  
**Recent Update:** Complete model overhaul with proper industry benchmarks  
**See:** `REPAIR_NOTES.md` for detailed technical documentation

## Overview

This application models the efficiency improvements and cost benefits of implementing shift-left practices across the software development lifecycle. 

**Model Calibration:** The model uses a calibrated efficiency matrix grounded in **75th percentile** of published industry research (Gartner, McKinsey, Forrester, DORA, etc.). This represents **ambitious but achievable** outcomes for high-performing organizations.

**Calibration Validated (October 17, 2025):**
- **App defaults** (25% avg maturity) → **~8-9% total project savings**
- **50% maturity** across all initiatives → **~17% total project savings**
- **Realistic achievable mix** (70-95% with constraints) → **~25% total project savings**
  - AI/Automation: 90%, Testing: 71%, Reuse: 56%, Others: 90-95%

**Important:** The model is calibrated so that a realistic mix of high maturity (accounting for implementation constraints) achieves 25%. This 25% includes ~17-20% research-backed improvements plus ~3-8% operational efficiency gains. See `OPERATIONAL_EFFICIENCY_CAVEAT.md` for details.

**Research basis:** Each matrix value is derived from specific studies:
- Test automation: Perfecto/Testlio (30-50% test phase reduction)
- AI/Automation: GitHub Copilot (30% faster coding), McKinsey GenAI (20-40% productivity)
- Agile/DevOps: DORA State of DevOps (15-25% delivery improvement)
- IaC: Puppet State of DevOps (85% reduction in environment setup)
- Component reuse: Gartner/Forrester (30-50% dev time reduction)

**See `Assumptions.md` for complete research citations and calibration methodology.**

## Features

- **Maturity Assessment**: Comprehensive automation maturity assessment (CMMI-based) to determine realistic savings potential
- **Interactive Configuration**: Sidebar controls for all model parameters with real-time updates
- **Role-Based Modeling**: 16 Banner-specific roles with realistic phase allocations and hourly rates
- **Strategic Category Breakdown**: Savings categorized into OOtB Config, N2S Methodology, and AI & Automation
- **Industry-Grounded**: Based on research from Gartner, Forrester, McKinsey, and empirical case studies
- **Comprehensive Analytics**: Hour savings, cost reductions, risk assessments, and cost avoidance calculations
- **Rich Visualizations**: Interactive charts, heatmaps, stacked bars, and executive summaries
- **Export Capabilities**: Download results as CSV/Excel plus complete model parameters as JSON
- **Validation**: Built-in checks against realistic industry improvement bounds (up to 50% for N2S)

## Architecture

```
n2s_efficiency_app/
├── app.py               # Streamlit main application
├── model.py             # Core calculation engine
├── config.py            # Configuration constants and helpers
├── requirements.txt     # Python dependencies
├── data/               # Data directory
│   └── ShiftLeft_Levers_PhaseMatrix_v3.xlsx  # Input matrix (place here)
├── README.md           # This file
└── Assumptions.md      # Industry benchmark sources and assumptions
```

### Core Components

1. **`app.py`** - Streamlit user interface with:
   - Sidebar configuration controls
   - Interactive visualizations (Plotly)
   - Results dashboard and KPI metrics
   - Export functionality

2. **`model.py`** - Business logic containing:
   - `N2SEfficiencyModel` class for all calculations
   - Matrix loading and phase mapping
   - Scenario application with industry benchmarks
   - Cost/savings calculations with validation

3. **`config.py`** - Configuration management:
   - Default values and constants
   - Industry benchmark data
   - Helper functions for formatting and validation
   - Scenario definitions with layered benefits

## Getting Started

### Prerequisites

- Python 3.8+ 
- pip package manager

### Installation

1. **Clone or download** the application files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Place your data file** (optional):
   - Put `ShiftLeft_Levers_PhaseMatrix_v3.xlsx` in the `data/` folder
   - If not provided, the app will use built-in sample data

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Using the Application

### Step 1: Maturity Assessment

Complete the **Current State Assessment** in the sidebar:
- **Test Automation Coverage**: 0-100% of test cases automated
- **CI/CD Maturity**: From manual builds to full GitOps
- **Deployment Automation**: Manual to fully automated deployments
- **Quality Metrics**: Tracking and monitoring practices
- **Cloud Adoption**: Infrastructure as Code and cloud-native practices

This assessment determines your:
- **Maturity Level**: 1 (Ad-hoc) to 5 (Optimizing)
- **Realistic Savings Potential**: 8-25% based on current capabilities

### Step 2: Configure Model Parameters

1. **Project Parameters**:
   - Total project hours (default: 17,054)
   - Blended labor rate (default: $100/hour)

2. **Testing Automation Effectiveness**:
   - Testing Phase Time Reduction: 10-80%
   - Manual Testing Reduction: 10-70%
   
3. **Quality & Defect Reduction**:
   - Overall Quality Improvement: 5-50%
   - Post-Release Defect Reduction: 10-60%

4. **Target & Strategy**:
   - Set your target savings percentage (5-35%) as a REFERENCE
   - **NEW:** The model calculates ACTUAL savings based on initiative maturity
   - UI shows gap if actual < target
   - Model validates feasibility against your maturity level

5. **Phase Allocation**:
   - Adjust percentage allocation across 7 N2S phases
   - Default: Discover (5%), Plan (10%), Design (15%), Build (25%), Test (20%), Deploy (10%), Post Go-Live (15%)

6. **Initiative Maturity Levels**:
   - Set maturity (0-100%) for each N2S initiative
   - Higher maturity = greater benefit realization

7. **Risk Weights**:
   - Multipliers for risk assessment by phase (0.5x to 10x)
   - Default progression: 1-7 (Discover=1, Post Go-Live=7)

8. **Cost Avoidance**:
   - Configure which phases include cost avoidance calculations
   - Set percentage for post-go-live defect prevention benefits

### Step 3: Interpreting Results

The application provides multiple views of savings and efficiency:

#### **Results Dashboard**
- **KPI Metrics**: Total hours saved, cost savings, cost avoidance, financial benefit
- **Actual Modeled Savings %**: Real-time savings percentage - updates as you adjust parameters
- **Initiative Impact Analysis**: See which initiatives contribute most to savings
- **Phase-by-Phase Summary**: Detailed comparison with baseline, modeled, and variance
- **Executive Cost Analysis**: Multi-chart breakdown of costs by phase

#### **Role-Based Analysis** 
Shows how savings distribute across 16 Banner-specific roles:

**Pod Team (Core Delivery):**
- Project Manager (1,600 hrs @ $135/hr)
- Solutions Architect (780 hrs @ $155/hr)
- Technical Architect (468 hrs @ $145/hr)
- Integration Lead (936 hrs @ $140/hr)
- Platform Lead (468 hrs @ $145/hr)
- Student AR Consultant (936 hrs @ $125/hr)

**Pooled Team (Specialized):**
- Functional Consultants: Fin Aid, Finance, HR (137 hrs each @ $125/hr)
- Integration Engineer (951 hrs @ $110/hr)
- Degree Works team: Consultant & Scribe (92 & 46 hrs @ $110-95/hr)
- Reporting Consultant (166 hrs @ $115/hr)
- Experience Consultant (166 hrs @ $120/hr) - Banner Experience cards/UX
- Change Management (320 hrs @ $115/hr)
- Other & Contingency (100 hrs @ $100/hr)

**Role Analysis Includes:**
- Role savings summary table (sorted by cost savings)
- Cost distribution by role (horizontal bar chart)
- Hours heatmaps showing roles × phases distribution
- Pod vs Pooled team hour comparisons

**Role-Specific Initiative Impacts:**
Different roles benefit differently from initiatives:
- **DW Scribe**: High benefit from Automated Testing (20% more than average)
- **Integration Engineer**: Strong benefit from DevSecOps, Testing (10-12% more)
- **Project Manager**: Moderate benefit from Agile (8% more), less from DevSecOps (5% less)
- **Functional Consultants**: Grouped together with standard baseline benefits
- **Change Management**: Lower benefit from technical automation (15-25% less)

#### **Strategic Savings Breakdown**
Categorizes all savings into three executive value buckets:

**🔵 N2S Methodology & Controls (~43% of savings):**
- CARM (Cloud Architecture Reference Model) - 65% methodology
- EDCC (Ellucian Delivery Control Center) - 80% methodology
- Agile + DevOps Practices - 70% methodology
- Governance, quality controls, and delivery discipline
- **Rationale:** When baseline maturity is low (CMMI 1-2), process improvements deliver the most value

**🟢 OOtB Config (~32% of savings):**
- Preconfigured environments and templates - 65% OOtB
- Reusable integration components - 60% OOtB
- Modernization Studio accelerators - 50% OOtB
- Reference architectures and patterns
- **Rationale:** Templates and reusable assets provide significant leverage once process discipline exists

**🟠 AI & Automation (~26% of savings):**
- Automated Testing frameworks - 55% AI/automation
- AI-powered development assistance - 70% AI/automation
- CI/CD pipeline automation
- Automated provisioning and deployment
- **Rationale:** Tools amplify good process; the 43% methodology foundation enables the 26% AI value

**Category Analysis Includes:**
- Category totals with percentage of overall savings
- Savings by role and category table
- Stacked bar chart showing category distribution by role
- Category definitions and descriptions

## Extending the Application

### Adding New Initiatives

1. Update the Excel matrix with new initiative rows
2. The application will automatically load new initiatives
3. Initiative names become slider labels in the sidebar

### Modifying Phase Structure

1. Update `PHASE_ORDER` in `config.py`
2. Ensure Excel matrix columns match or use column mapping
3. Update any phase-specific logic in `model.py`

### Adding New Scenarios

1. Add scenario definition to `SCENARIOS` in `config.py`
2. Implement scenario logic in `apply_maturity_and_scenario()` method
3. Update UI scenario selector

### Custom Industry Benchmarks

1. Modify `INDUSTRY_BENCHMARKS` in `config.py`
2. Update scenario calculations in `model.py` to use new benchmarks
3. Document changes in `Assumptions.md`

## Data Requirements

### Input Matrix Format

The Excel file should contain:
- **Sheet Name**: "10pct_Savings" (configurable)
- **Rows**: Initiative names (e.g., "Test Automation Framework")
- **Columns**: Phase names (will be mapped to N2S phases)
- **Values**: Hour deltas (positive = adds effort, negative = saves effort)

### Phase Mapping

The application automatically maps common column names:
- "discovery" → "Discover"
- "planning"/"plan" → "Plan"
- "design" → "Design"
- "development"/"build" → "Build"
- "testing"/"test" → "Test"
- "deployment"/"deploy" → "Deploy"
- "post-go-live"/"support"/"maintenance" → "Post Go-Live"

## Testing

The application includes sample data for testing and demonstration. Key test scenarios:

1. **Baseline Test**: All initiatives at 0% maturity should show no improvements
2. **Full Maturity**: All initiatives at 100% should show maximum configured benefits
3. **Scenario Validation**: Aggressive scenario should show higher benefits than Moderate
4. **Bounds Checking**: Ensure no scenario exceeds 30% total cost reduction

### Running Test Scenarios

```python
from model import run_model_scenario

# Test with different configurations
summary, kpis = run_model_scenario(
    total_hours=17054,
    scenario='Aggressive (30%)',
    maturity_levels={'Test Automation Framework': 100}
)
```

## Future Enhancements

Planned improvements (see TODOs in code):

1. **Role-Based Costing**: Different hourly rates by role/phase
2. **Time-to-Market Calculations**: Revenue impact of faster delivery
3. **Confidence Intervals**: Statistical bounds on improvement estimates
4. **Monte Carlo Simulation**: Risk-adjusted scenario modeling
5. **Historical Tracking**: Compare actual vs. predicted outcomes
6. **Advanced Visualizations**: Gantt charts, sensitivity analysis

## Troubleshooting

### Current Known Issues (Oct 17, 2025)

1. **Safari Compatibility**: App may not respond to slider changes in Safari due to CORS/WebSocket issues
   - **Fix**: Use Chrome or Firefox instead
   - **Command**: `open -a "Google Chrome" http://localhost:8501`

2. **Sliders Not Updating**: If changes don't affect results:
   - **Try**: Hard refresh (Cmd+Shift+R / Ctrl+Shift+R)
   - **Try**: Clear browser cache
   - **Try**: Switch to Chrome browser
   - **Check**: "Reruns" counter in sidebar (should increment when sliders move)

3. **Target Savings Slider Resets**: May reset when maturity assessment changes
   - **Status**: Under investigation
   - **Workaround**: Set target after completing maturity assessment

### Common Issues

1. **Phase allocation error**: Ensure percentages sum to exactly 100%
2. **File not found**: Place Excel file in `data/` folder or use sample data
3. **Import errors**: Verify all dependencies installed with `pip install -r requirements.txt`
4. **Performance**: Large Excel files may take time to load - consider data optimization

### Debug Panels

The app includes debug panels to help diagnose issues:
- **🔍 Debug: Input Values** (sidebar): Shows current slider values
- **🔬 Calculation Trace** (results section): Shows step-by-step model calculations
- **Reruns counter** (sidebar): Confirms Streamlit is responding to changes

### Getting Help

1. Check `SESSION_NOTES.md` for detailed current status and investigation plan
2. Review error messages in browser console (Safari → Develop → Show JavaScript Console)
3. Check the **Model Details & Assumptions** expandable section in the app
4. Verify Streamlit is still running in terminal

## License

This application is provided for internal use at Ellucian. See organization policies for usage guidelines.

## Contributing

For questions, improvements, or bug reports:
1. Document the issue with steps to reproduce
2. Include relevant configuration and data details
3. Suggest improvements with business justification

---

*Built using Streamlit, Pandas, and Plotly* 