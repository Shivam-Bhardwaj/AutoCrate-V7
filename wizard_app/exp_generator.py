#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Functions to generate the Siemens NX Expression File content."""

import datetime

try:
    from . import config
except ImportError:
    import config # For direct testing

def generate_nx_exp_file_content(product_params: dict, skid_results: dict, 
                                 floorboard_results: dict, wall_results: dict, 
                                 cap_results: dict, decal_results: dict, 
                                 app_version: str = "N/A") -> str:
    """Compiles all calculated parameters into a string formatted for an NX .exp file.

    Args:
        product_params (dict): Dictionary of product input parameters.
        skid_results (dict): Dictionary of skid calculation results, including an 'exp_data' key.
        floorboard_results (dict): Dictionary of floorboard calculation results, including an 'exp_data' key.
        wall_results (dict): Dictionary of wall calculation results, including an 'exp_data' key.
        cap_results (dict): Dictionary of cap calculation results, including an 'exp_data' key.
        decal_results (dict): Dictionary of decal calculation results, including an 'exp_data' key.
        app_version (str): Version of the AutoCrate application.

    Returns:
        str: The content of the .exp file.
    """
    lines = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"// NX Expressions for AutoCrate Wizard - Skids, Floorboards & Cap Assembly")
    lines.append(f"// Parameters from PyQt GUI at: {now}")
    lines.append(f"// AutoCrate Wizard Version: {app_version}")
    lines.append("")
    # 1. USER CONTROLS
    lines.append("// =============================")
    lines.append("// 1. USER CONTROLS (Values from UI)")
    lines.append("// =============================")
    # Product params (example units)
    lines.append(f"[lbm]product_weight = {product_params.get('product_weight', 0.0)}  // Product Weight")
    lines.append(f"[Inch]product_width = {product_params.get('product_width', 0.0):.3f}     // Product Width - across skids")
    lines.append(f"[Inch]product_length = {product_params.get('product_length', 0.0):.3f}    // Product Length - along skids")
    lines.append(f"[Inch]product_actual_height = {product_params.get('product_actual_height', 0.0):.3f} // Product Actual Height")
    lines.append(f"[Inch]clearance_side = {product_params.get('clearance_side', 0.0):.3f}     // Clearance per Side")
    lines.append(f"[Inch]clearance_above_product = {product_params.get('clearance_above_product', 0.0):.3f} // Clearance above product")
    lines.append(f"[Inch]panel_thickness = {product_params.get('panel_thickness', 0.0):.3f}   // Panel Sheathing Thickness")
    lines.append(f"[Inch]cleat_thickness = {product_params.get('cleat_thickness', 0.0):.3f}   // General Cleat Actual Thickness")
    lines.append(f"[Inch]wall_cleat_width = {product_params.get('wall_cleat_width', 0.0):.3f} // Wall Cleat Actual Width")
    lines.append(f"[Inch]floor_lumbar_thickness = {product_params.get('floor_lumbar_thickness', 0.0):.3f} // Floorboard Actual Thickness")
    lines.append(f"[Inch]cap_cleat_width = {product_params.get('cap_cleat_width', 0.0):.3f}     // Cap Cleat Actual Width")
    lines.append(f"[Inch]max_cap_cleat_spacing_rule = {product_params.get('max_top_cleat_spacing', 0.0):.3f} // Max rule for cap cleats")
    lines.append("")
    # 2. CALCULATED DIMENSIONS
    lines.append("// ===========================================")
    lines.append("// 2. CALCULATED CRATE AND USABLE DIMENSIONS (NX Expressions)")
    lines.append("// ===========================================")
    # Example calculated values (add more as needed)
    lines.append(f"[Inch]crate_width_OD = ... // TODO: Add calculation")
    lines.append(f"[Inch]crate_length_OD = ... // TODO: Add calculation")
    lines.append(f"[Inch]skid_usable_width_ID = ... // TODO: Add calculation")
    lines.append("")
    # 3. SKID LAYOUT
    lines.append("// =============================")
    lines.append("// 3. SKID LAYOUT (Values from Python skid_logic, for NX Pattern)")
    lines.append("// =============================")
    # Example skid values
    lines.append(f"[Inch]INPUT_Skid_Nominal_Width = {skid_results.get('skid_actual_width', 0.0):.3f}")
    lines.append(f"[Inch]INPUT_Skid_Nominal_Height = {skid_results.get('skid_actual_height', 0.0):.3f}")
    lines.append(f"CALC_Skid_Count = {skid_results.get('skid_count', 0)}")
    lines.append(f"[Inch]CALC_Skid_Pitch = {skid_results.get('actual_center_to_center_spacing', 0.0):.4f}")
    lines.append(f"[Inch]CALC_First_Skid_Pos_X = {skid_results.get('first_skid_position_offset_x', 0.0):.4f}")
    lines.append(f"[Inch]INPUT_Skid_Actual_Length = {skid_results.get('skid_actual_length', 0.0):.3f}")
    lines.append("")
    # 4. FLOORBOARD PARAMETERS
    lines.append("// ===========================================")
    lines.append("// 4. FLOORBOARD PARAMETERS (for N-Instance Suppression Strategy)")
    lines.append("// ===========================================")
    # Example floorboard values (add more as needed)
    lines.append(f"[Inch]INPUT_Floorboard_Actual_Thickness = {product_params.get('floor_lumbar_thickness', 0.0):.3f}")
    # ...
    lines.append("")
    # 5. CAP ASSEMBLY PARAMETERS
    lines.append("// ===========================================")
    lines.append("// 5. CAP ASSEMBLY PARAMETERS (for N-Instance Suppression Strategy)")
    lines.append("// ===========================================")
    # Example cap values (add more as needed)
    lines.append(f"[Inch]CAP_Panel_Width = ... // TODO: Add calculation")
    lines.append(f"[Inch]CAP_Panel_Length = ... // TODO: Add calculation")
    lines.append(f"[Inch]CAP_Panel_Thickness = {product_params.get('panel_thickness', 0.0):.3f}")
    # ...
    lines.append("")
    lines.append("// End of AutoCrate Wizard Expressions")
    return '\n'.join(lines)

if __name__ == '__main__':
    # Mock data for testing
    mock_product_params = {
        'product_weight': 1800.0, 'product_width': 75.0, 'product_length': 110.0, 
        'product_actual_height': 55.0, 'clearance_side': 2.5, 'clearance_above_product': 2.0,
        'panel_thickness': 0.75, 'cleat_thickness': 0.75, 'wall_cleat_width': 3.5,
        'floor_lumbar_thickness': 1.5, 'cap_cleat_width': 3.5, 'max_top_cleat_spacing': 24.0,
        'chosen_standard_floorboard_nominal': "2x6", 'allow_custom_floorboard_fill': True,
        'product_is_fragile': True, 'product_requires_special_handling': True,
        'side_panel_1_removable': True, 'top_panel_removable': False
    }
    
    mock_skid_results = {
        "exp_data": {"INPUT_Skid_Nominal_Width": 3.5, "CALC_Skid_Count": 3},
        "crate_overall_width_calculated": 80.0,
        "skid_actual_length": 115.0,
        "skid_actual_height": 3.5
    }
    
    mock_floor_results = {"exp_data": {"CALC_Floor_Board_Length_Across_Skids": 115.0, "FB_Std_Front_1_Suppress_Flag": 0}}
    
    mock_wall_results = {
        "exp_data": {
            "CALC_Side_Panel_Plywood_Length": 115.0, 
            "INPUT_Wall_Cleat_Actual_Width": 3.5,
            "CALC_Side_Panel_1_Removable": 1,
            "CALC_Side_Panel_2_Removable": 0,
            "CALC_End_Panel_1_Removable": 0,
            "CALC_End_Panel_2_Removable": 0
        },
        "removable_panels": {
            "count": 1,
            "positions": ["side_1"],
            "drop_end_style": True
        }
    }
    
    mock_cap_results = {
        "exp_data": {
            "CALC_Cap_Panel_Actual_Length_X": 115.0, 
            "INPUT_Cap_Cleat_Actual_Width": 3.5,
            "CALC_Cap_Top_Panel_Removable": 0
        },
        "cap_panel": {
            "width": 80.0,
            "length": 115.0,
            "thickness": 0.75,
            "removable": False
        }
    }
    
    mock_decal_results = {"exp_data": {"CALC_Fragile_Decal_Suppress": 0}}

    exp_content = generate_nx_exp_file_content(
        product_params=mock_product_params,
        skid_results=mock_skid_results,
        floorboard_results=mock_floor_results,
        wall_results=mock_wall_results,
        cap_results=mock_cap_results,
        decal_results=mock_decal_results,
        app_version="0.6.0"
    )
    print(exp_content)

    # Save to a test file
    with open("Test_AutoCrate_Expressions.exp", "w") as f:
        f.write(exp_content)
    print("\nTest .exp file generated as Test_AutoCrate_Expressions.exp") 