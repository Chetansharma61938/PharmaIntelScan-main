def render_competitor_pipeline():
    """Render the competitor pipeline analysis section"""
    st.header("Competitor Pipeline Analysis")
    
    # Get pipeline data
    pipeline_data = get_pipeline_data()
    
    if pipeline_data is not None and not pipeline_data.empty:
        # Display pipeline table
        st.subheader("Pipeline Overview")
        
        # Define columns to display
        display_cols = ['name', 'company', 'phase', 'condition', 'therapeutic_area']
        
        # Create styled DataFrame
        styled_df = pipeline_data[display_cols].copy()
        
        # Apply styling
        def color_phase(val):
            colors = {
                'Preclinical': 'lightblue',
                'Phase 1': 'lightgreen',
                'Phase 2': 'yellow',
                'Phase 3': 'orange',
                'Approved': 'lightgreen'
            }
            return f'background-color: {colors.get(val, "white")}'
        
        # Apply the styling
        styled_df = styled_df.style.applymap(color_phase, subset=['phase'])
        
        # Display the styled DataFrame
        st.dataframe(styled_df) 