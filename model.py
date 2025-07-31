"""
Core calculation engine for N2S Efficiency Modeling Application
Handles data loading, scenario application, and cost calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
import os
from config import (
    PHASE_ORDER, SCENARIOS, DEFAULT_PHASE_ALLOCATION,
    INDUSTRY_BENCHMARKS, validate_scenario_results,
    calculate_baseline_hours, DATA_PATH, MATRIX_SHEET_NAME, INITIATIVE_FALLBACK
)


def get_initiatives() -> List[str]:
    """Return list of initiative names from Excel or fallback."""
    try:
        if os.path.exists(DATA_PATH):
            df = pd.read_excel(DATA_PATH, sheet_name=MATRIX_SHEET_NAME, index_col=0)
            return df.index.tolist()
    except Exception as e:
        print(f"Error loading initiatives from Excel: {e}")
    
    # Fall back to authoritative list
    return INITIATIVE_FALLBACK.copy()


class N2SEfficiencyModel:
    """
    Core model for calculating N2S efficiency improvements
    """
    
    def __init__(self):
        self.matrix_data = None
        self.initiatives = []
        self.loaded = False
    
    def load_matrix(self, file_path: str, sheet_name: str = "10pct_Savings") -> bool:
        """
        Load the shift-left levers matrix from Excel file
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name containing the matrix
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                # Create sample data if file doesn't exist
                self._create_sample_matrix()
                return True
                
            # Load matrix from Excel
            df = pd.read_excel(file_path, sheet_name=sheet_name, index_col=0)
            
            # Rename columns to N2S phases if needed
            self._rename_columns_to_n2s_phases(df)
            
            # Ensure all required phases exist
            for phase in PHASE_ORDER:
                if phase not in df.columns:
                    df[phase] = 0
            
            # Reorder columns to match phase order
            df = df[PHASE_ORDER]
            
            self.matrix_data = df
            self.initiatives = df.index.tolist()
            self.loaded = True
            
            return True
            
        except Exception as e:
            print(f"Error loading matrix: {e}")
            # Fall back to sample data
            self._create_sample_matrix()
            return False
    
    def _rename_columns_to_n2s_phases(self, df: pd.DataFrame) -> None:
        """
        Rename DataFrame columns to standardized N2S phase names
        """
        # Common column name mappings
        column_mappings = {
            'discovery': 'Discover',
            'planning': 'Plan',
            'plan': 'Plan',
            'design': 'Design',
            'development': 'Build',
            'build': 'Build',
            'testing': 'Test',
            'test': 'Test',
            'deployment': 'Deploy',
            'deploy': 'Deploy',
            'post-go-live': 'Post Go-Live',
            'post_go_live': 'Post Go-Live',
            'support': 'Post Go-Live',
            'maintenance': 'Post Go-Live'
        }
        
        # Apply mappings (case-insensitive)
        new_columns = []
        for col in df.columns:
            col_lower = str(col).lower().strip()
            new_name = column_mappings.get(col_lower, col)
            new_columns.append(new_name)
        
        df.columns = new_columns
    
    def _create_sample_matrix(self) -> None:
        """
        Create sample matrix data for demonstration
        Updated to reflect realistic N2S savings potential (10-30% range)
        """
        initiatives = INITIATIVE_FALLBACK.copy()
        
        # Realistic hour deltas based on N2S industry benchmarks
        # (+ adds effort, - saves effort)
        # Total potential savings: ~15-25% with high maturity
        sample_data = {
            # Early phases: Moderate savings from better planning/reuse
            'Discover': [-20, -15, -30, -40, -10, -25, -35],      # ~175 hours saved
            'Plan': [-30, -25, -50, -60, -15, -40, -45],          # ~265 hours saved
            'Design': [-50, -40, -70, -80, -60, -55, -65],        # ~420 hours saved
            
            # Development: Major savings from automation, reuse, modern tools
            'Build': [-80, -120, -100, -150, -200, -90, -180],    # ~920 hours saved
            
            # Testing: Biggest savings potential from automation
            'Test': [-200, -180, -160, -120, -250, -100, -280],   # ~1290 hours saved
            
            # Deployment: Significant savings from automation/environments
            'Deploy': [-40, -80, -30, -60, -50, -35, -45],        # ~340 hours saved
            
            # Post Go-Live: Major savings from quality improvements
            'Post Go-Live': [-150, -100, -120, -180, -80, -90, -140] # ~860 hours saved
        }
        
        # Total potential savings at 100% maturity: ~4270 hours
        # Percentage of 17,054 total hours: ~25% savings potential
        # At 50% maturity (default): ~12.5% savings
        # This aligns with realistic N2S expectations of 10-30%
        
        self.matrix_data = pd.DataFrame(sample_data, index=initiatives)
        self.initiatives = initiatives
        self.loaded = True
    
    def apply_maturity_and_scenario(
        self, 
        maturity_levels: Dict[str, float], 
        scenario: str
    ) -> pd.DataFrame:
        """
        Apply maturity levels and scenario factors to the base matrix
        
        Args:
            maturity_levels: Dict mapping initiative names to maturity % (0-100)
            scenario: Scenario name from SCENARIOS
            
        Returns:
            DataFrame with effective deltas
        """
        if not self.loaded:
            raise ValueError("Matrix data not loaded")
        
        # Start with base matrix (ensure float type)
        effective_matrix = self.matrix_data.copy().astype(float)
        
        # Apply maturity levels
        for initiative in self.initiatives:
            maturity = maturity_levels.get(initiative, 0) / 100.0
            effective_matrix.loc[initiative] *= maturity
        
        # Apply scenario factors
        scenario_config = SCENARIOS[scenario]
        
        if scenario == 'Moderate (10%)':
            # Use matrix at face value (already applied maturity)
            pass
            
        elif scenario == 'Elevated (20%)':
            # Enhanced benefits from deeper automation and process maturity
            additional_factor = scenario_config['additional_factor']
            
            # Enhanced test automation benefits
            test_boost = INDUSTRY_BENCHMARKS['testing_phase_reduction'] * additional_factor
            effective_matrix['Test'] *= (1 + test_boost)
            
            # Quality improvements affect post-release
            quality_boost = INDUSTRY_BENCHMARKS['quality_improvement'] * additional_factor
            effective_matrix['Post Go-Live'] *= (1 + quality_boost)
            
        elif scenario == 'Aggressive (30%)':
            # Maximum credible improvements
            additional_factor = scenario_config['additional_factor']
            
            # Enhanced test automation and shift-left benefits
            test_boost = INDUSTRY_BENCHMARKS['testing_phase_reduction'] * additional_factor
            effective_matrix['Test'] *= (1 + test_boost)
            
            # Quality improvements affect post-release
            quality_boost = INDUSTRY_BENCHMARKS['quality_improvement'] * additional_factor
            effective_matrix['Post Go-Live'] *= (1 + quality_boost)
            
            # Apply caps to prevent unrealistic savings
            caps = scenario_config['max_savings_caps']
            baseline_hours = calculate_baseline_hours(17054, DEFAULT_PHASE_ALLOCATION)
            
            for phase in PHASE_ORDER:
                phase_baseline = baseline_hours[phase]
                max_savings = phase_baseline * caps[phase]
                
                # Ensure total savings don't exceed cap
                total_phase_savings = -effective_matrix[phase].sum()
                if total_phase_savings > max_savings:
                    # Scale down all initiatives proportionally
                    scale_factor = max_savings / total_phase_savings
                    effective_matrix[phase] = effective_matrix[phase] * scale_factor
        
        return effective_matrix
    
    def calculate_phase_hours(
        self,
        total_hours: float,
        phase_allocation: Dict[str, float],
        effective_deltas: pd.DataFrame
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Calculate baseline and modeled hours for each phase
        
        Returns:
            Tuple of (baseline_hours, modeled_hours)
        """
        baseline_hours = calculate_baseline_hours(total_hours, phase_allocation)
        modeled_hours = {}
        
        for phase in PHASE_ORDER:
            phase_delta = effective_deltas[phase].sum()
            modeled_hours[phase] = baseline_hours[phase] + phase_delta
            
            # Ensure non-negative hours
            modeled_hours[phase] = max(0, modeled_hours[phase])
        
        return baseline_hours, modeled_hours
    
    def calculate_costs_and_savings(
        self,
        baseline_hours: Dict[str, float],
        modeled_hours: Dict[str, float],
        blended_rate: float,
        include_cost_avoidance: bool = True,
        cost_avoidance_config: Optional[Dict] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate costs, savings, and cost avoidance
        
        Returns:
            Dict with 'savings' and 'avoidance' breakdown
        """
        results = {
            'savings': {},
            'avoidance': {},
            'baseline_cost': {},
            'modeled_cost': {}
        }
        
        # Development phases (Discover through Deploy)
        dev_phases = ['Discover', 'Plan', 'Design', 'Build', 'Test', 'Deploy']
        
        # Calculate total development savings for cost avoidance multiplier
        total_dev_savings = 0
        for phase in dev_phases:
            baseline_cost = baseline_hours[phase] * blended_rate
            modeled_cost = modeled_hours[phase] * blended_rate
            cost_diff = baseline_cost - modeled_cost
            if cost_diff > 0:  # Only positive savings
                total_dev_savings += cost_diff
        
        for phase in PHASE_ORDER:
            baseline_cost = baseline_hours[phase] * blended_rate
            modeled_cost = modeled_hours[phase] * blended_rate
            
            results['baseline_cost'][phase] = baseline_cost
            results['modeled_cost'][phase] = modeled_cost
            
            cost_diff = baseline_cost - modeled_cost
            
            if phase in dev_phases:
                # Direct cost savings during development
                results['savings'][phase] = cost_diff
                results['avoidance'][phase] = 0
            else:
                # Post Go-Live = cost avoidance
                if include_cost_avoidance:
                    # Base cost avoidance from phase improvements
                    base_avoidance = cost_diff
                    
                    # Apply cost avoidance multiplier and ongoing factor
                    if cost_avoidance_config and total_dev_savings > 0:
                        multiplier = cost_avoidance_config.get('multiplier', 1.0)
                        ongoing_factor = cost_avoidance_config.get('ongoing_factor', 0.8)
                        
                        # Apply multiplier to base avoidance
                        enhanced_base = base_avoidance * multiplier
                        
                        # Add ongoing cost avoidance based on development savings
                        additional_avoidance = total_dev_savings * ongoing_factor
                        
                        results['avoidance'][phase] = enhanced_base + additional_avoidance
                    else:
                        results['avoidance'][phase] = base_avoidance
                    
                    results['savings'][phase] = 0
                else:
                    results['savings'][phase] = 0
                    results['avoidance'][phase] = 0
        
        return results
    
    def calculate_risk_adjusted_hours(
        self,
        modeled_hours: Dict[str, float],
        risk_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Apply risk weights to modeled hours
        """
        return {
            phase: hours * risk_weights.get(phase, 1.0)
            for phase, hours in modeled_hours.items()
        }
    
    def generate_summary_table(
        self,
        baseline_hours: Dict[str, float],
        modeled_hours: Dict[str, float],
        baseline_costs: Dict[str, float],
        modeled_costs: Dict[str, float],
        risk_adjusted_hours: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Generate comprehensive summary table for display
        """
        data = []
        
        for phase in PHASE_ORDER:
            b_hours = baseline_hours[phase]
            m_hours = modeled_hours[phase]
            b_cost = baseline_costs[phase]
            m_cost = modeled_costs[phase]
            r_hours = risk_adjusted_hours[phase]
            
            hour_variance = m_hours - b_hours
            hour_variance_pct = (hour_variance / b_hours * 100) if b_hours > 0 else 0
            
            cost_variance = m_cost - b_cost
            cost_variance_pct = (cost_variance / b_cost * 100) if b_cost > 0 else 0
            
            data.append({
                'Phase': phase,
                'Baseline Hours': b_hours,
                'Modeled Hours': m_hours,
                'Hour Variance': hour_variance,
                'Hour Variance %': hour_variance_pct,
                'Baseline Cost': b_cost,
                'Modeled Cost': m_cost,
                'Cost Variance': cost_variance,
                'Cost Variance %': cost_variance_pct,
                'Risk-Adjusted Hours': r_hours
            })
        
        return pd.DataFrame(data)
    
    def get_kpi_summary(
        self,
        baseline_hours: Dict[str, float],
        modeled_hours: Dict[str, float],
        cost_results: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Calculate key performance indicators
        """
        total_baseline_hours = sum(baseline_hours.values())
        total_modeled_hours = sum(modeled_hours.values())
        
        total_savings = sum(cost_results['savings'].values())
        total_avoidance = sum(cost_results['avoidance'].values())
        
        return {
            'total_hours_saved': total_baseline_hours - total_modeled_hours,
            'total_hours_saved_pct': ((total_baseline_hours - total_modeled_hours) / 
                                    total_baseline_hours * 100) if total_baseline_hours > 0 else 0,
            'total_cost_savings': total_savings,
            'total_cost_avoidance': total_avoidance,
            'total_financial_benefit': total_savings + total_avoidance,
            'baseline_total_cost': sum(cost_results['baseline_cost'].values()),
            'modeled_total_cost': sum(cost_results['modeled_cost'].values())
        }
    
    def generate_initiative_impact_table(
        self,
        effective_deltas: pd.DataFrame,
        maturity_levels: Dict[str, float],
        blended_rate: float,
        include_cost_avoidance: bool = True,
        cost_avoidance_config: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Generate detailed table showing impact of each initiative
        """
        dev_phases = ['Discover', 'Plan', 'Design', 'Build', 'Test', 'Deploy']
        
        impact_data = []
        
        for initiative in self.initiatives:
            maturity = maturity_levels.get(initiative, 0)
            
            # Calculate hour impacts per phase
            total_hour_impact = 0
            dev_hour_impact = 0
            post_golive_impact = 0
            
            for phase in PHASE_ORDER:
                phase_impact = effective_deltas.loc[initiative, phase]
                total_hour_impact += phase_impact
                
                if phase in dev_phases:
                    dev_hour_impact += phase_impact
                else:
                    post_golive_impact += phase_impact
            
            # Calculate financial impact
            dev_cost_impact = dev_hour_impact * blended_rate
            
            if include_cost_avoidance and cost_avoidance_config:
                # Apply cost avoidance multiplier
                multiplier = cost_avoidance_config.get('multiplier', 1.0)
                post_golive_cost_impact = post_golive_impact * blended_rate * multiplier
            else:
                post_golive_cost_impact = post_golive_impact * blended_rate if include_cost_avoidance else 0
                
            total_financial_impact = dev_cost_impact + post_golive_cost_impact
            
            # Get baseline deltas (before maturity adjustment)
            baseline_total_impact = self.matrix_data.loc[initiative].sum()
            
            impact_data.append({
                'Initiative': initiative,
                'Maturity %': maturity,
                'Baseline Hour Delta': baseline_total_impact,
                'Effective Hour Delta': total_hour_impact,
                'Development Hours': dev_hour_impact,
                'Post Go-Live Hours': post_golive_impact,
                'Development Cost Impact': dev_cost_impact,
                'Post Go-Live Cost Impact': post_golive_cost_impact,
                'Total Financial Impact': total_financial_impact,
                'Top Phase Impact': self._get_top_phase_impact(effective_deltas, initiative)
            })
        
        df = pd.DataFrame(impact_data)
        # Sort by total financial impact (highest benefit first)
        df = df.sort_values('Total Financial Impact', ascending=False)
        return df
    
    def _get_top_phase_impact(self, effective_deltas: pd.DataFrame, initiative: str) -> str:
        """Get the phase with the highest impact for this initiative"""
        initiative_row = effective_deltas.loc[initiative]
        # Find phase with most negative value (biggest savings)
        min_phase = initiative_row.idxmin()
        min_value = initiative_row[min_phase]
        
        if min_value < -1:  # Only show if significant impact
            return f"{min_phase} ({min_value:.0f}h)"
        else:
            return "No major impact"


# Convenience functions for testing
def run_model_scenario(
    total_hours: float = 17054,
    phase_allocation: Optional[Dict[str, float]] = None,
    maturity_levels: Optional[Dict[str, float]] = None,
    scenario: str = 'Moderate (10%)',
    blended_rate: float = 100,
    risk_weights: Optional[Dict[str, float]] = None,
    include_cost_avoidance: bool = True
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Run a complete modeling scenario
    
    Returns:
        Tuple of (summary_table, kpi_summary)
    """
    model = N2SEfficiencyModel()
    model.load_matrix("data/ShiftLeft_Levers_PhaseMatrix_v3.xlsx")
    
    # Use defaults if not provided
    if phase_allocation is None:
        phase_allocation = DEFAULT_PHASE_ALLOCATION.copy()
    
    if maturity_levels is None:
        maturity_levels = {initiative: 50 for initiative in model.initiatives}
    
    if risk_weights is None:
        from config import DEFAULT_RISK_WEIGHTS
        risk_weights = DEFAULT_RISK_WEIGHTS.copy()
    
    # Run calculations
    effective_deltas = model.apply_maturity_and_scenario(maturity_levels, scenario)
    baseline_hours, modeled_hours = model.calculate_phase_hours(
        total_hours, phase_allocation, effective_deltas
    )
    
    cost_results = model.calculate_costs_and_savings(
        baseline_hours, modeled_hours, blended_rate, include_cost_avoidance
    )
    
    risk_adjusted_hours = model.calculate_risk_adjusted_hours(modeled_hours, risk_weights)
    
    summary_table = model.generate_summary_table(
        baseline_hours, modeled_hours,
        cost_results['baseline_cost'], cost_results['modeled_cost'],
        risk_adjusted_hours
    )
    
    kpi_summary = model.get_kpi_summary(baseline_hours, modeled_hours, cost_results)
    
    return summary_table, kpi_summary 