import pandas as pd
import plotly.express as px

def create_pipeline_phase_chart(pipeline_data):
    """Create a bar chart showing the distribution of drugs by phase"""
    try:
        # Define expected phases
        expected_phases = ['Preclinical', 'Phase 1', 'Phase 2', 'Phase 3', 'Approved']
        
        # Initialize phase counts with zeros
        phase_counts = {phase: 0 for phase in expected_phases}
        
        # Handle empty or invalid data
        if pipeline_data is None or not isinstance(pipeline_data, pd.DataFrame) or pipeline_data.empty:
            print("Creating empty chart due to invalid data")
            return create_empty_chart(expected_phases)
        
        # Ensure phase column exists
        if 'phase' not in pipeline_data.columns:
            print("No phase column found")
            return create_empty_chart(expected_phases)
        
        # Clean and standardize phase data
        pipeline_data['phase'] = pipeline_data['phase'].astype(str).str.strip().str.lower()
        
        # Create phase mapping
        phase_mapping = {
            'preclinical': 'Preclinical',
            'phase 1': 'Phase 1',
            'phase 2': 'Phase 2',
            'phase 3': 'Phase 3',
            'approved': 'Approved'
        }
        
        # Count phases manually
        for phase in pipeline_data['phase']:
            standardized_phase = phase_mapping.get(phase, 'Other')
            if standardized_phase in phase_counts:
                phase_counts[standardized_phase] += 1
        
        # Create the bar chart using the counts dictionary
        fig = px.bar(
            x=list(phase_counts.keys()),
            y=list(phase_counts.values()),
            title='Pipeline by Phase',
            labels={'x': 'Phase', 'y': 'Number of Drugs'}
        )
        
        # Update layout
        fig.update_layout(
            showlegend=False,
            xaxis_title='Phase',
            yaxis_title='Number of Drugs',
            plot_bgcolor='white'
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating phase chart: {str(e)}")
        return create_empty_chart(expected_phases)

def create_empty_chart(phases):
    """Helper function to create an empty chart"""
    return px.bar(
        x=phases,
        y=[0] * len(phases),
        title='Pipeline by Phase',
        labels={'x': 'Phase', 'y': 'Number of Drugs'}
    ) 