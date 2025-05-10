# standards_analysis/services/visualization_generator.py
import os
import io
import logging
from typing import Dict, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend

from .ai_config import aicfg

logger = logging.getLogger('standards_analysis.ai_system.visualization')

def generate_shariah_compliance_chart_image(
    shariah_assessment_data: Optional[Dict[str, Any]], 
    standard_name: str
) -> Optional[bytes]:
    # (Logic copied and adapted from FastAPI version's generate_shariah_compliance_chart)
    logger.info(f"Attempting to generate Shariah compliance chart image for {standard_name}")
    if not shariah_assessment_data:
        logger.warning("No Shariah assessment data provided for visualization.")
        return None

    rulings_data = shariah_assessment_data.get("overall_ruling") # This comes from ShariahComplianceAgent
    if not rulings_data or not isinstance(rulings_data, dict):
        logger.warning(f"No 'overall_ruling' dict in Shariah data for {standard_name}.")
        return None

    valid_rulings = {
        cat: rul for cat, rul in rulings_data.items() 
        if rul and not (str(rul).lower() == "not specifically assessed" or "not found" in str(rul).lower())
    }

    if not valid_rulings:
        logger.info(f"No specific Shariah rulings to visualize for {standard_name}.")
        return None

    df_data = {'Category': list(valid_rulings.keys()), 'Ruling': list(valid_rulings.values())}
    df = pd.DataFrame(df_data)
    ruling_map = {'Approved': 3, 'Conditionally Approved': 2, 'Requires Modification': 1, 'Rejected': 0}
    df['Score'] = df['Ruling'].map(lambda x: ruling_map.get(x, 0.5))
    df['Category'] = df['Category'].str.replace('_', ' ').str.title()

    plt.figure(figsize=(10, 7)) # Slightly smaller for web
    bar_colors = ['#4CAF50' if s >= 2.5 else '#8BC34A' if s >= 1.8 else '#FFC107' if s >= 1.2 else '#FF9800' if s >= 0.8 else '#F44336' for s in df['Score']]
    bars = plt.bar(df['Category'], df['Score'], color=bar_colors)
    
    plt.title(f'Shariah Compliance: {standard_name}', fontsize=16)
    plt.xlabel('Enhancement Category', fontsize=12)
    plt.ylabel('Compliance Level', fontsize=12)
    plt.xticks(rotation=25, ha='right', fontsize=10)
    
    yticks_locs = sorted(list(set(ruling_map.values())))
    yticks_labels = [key for score_val in yticks_locs for key, val in ruling_map.items() if val == score_val]
    plt.yticks(yticks_locs, yticks_labels, fontsize=10)
    plt.ylim(bottom=min(-0.1, min(yticks_locs)-0.1 if yticks_locs else -0.1), 
             top=max(3.1, max(yticks_locs)+0.1 if yticks_locs else 3.1))
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    plt.tight_layout(pad=1.5)

    for bar_obj, ruling_text in zip(bars, df['Ruling']):
        plt.text(bar_obj.get_x() + bar_obj.get_width()/2., bar_obj.get_height() + 0.03,
                 ruling_text, ha='center', va='bottom', fontsize=8.5, color='black')

    img_byte_arr = io.BytesIO()
    plt.savefig(img_byte_arr, format='PNG', dpi=100) # Control DPI for web
    img_byte_arr.seek(0)
    plt.close()
    
    logger.info(f"Successfully generated Shariah compliance chart image for {standard_name}.")
    return img_byte_arr.getvalue()

# You can add more chart generation functions here based on VisualizationAgent's specs
# e.g., generate_enhancement_impact_matrix_image, etc.