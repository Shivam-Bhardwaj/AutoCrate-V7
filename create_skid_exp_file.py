# create_skid_exp_file.py
import os
import json
import datetime

def generate_nx_exp_file_content_for_skids(product_params):
    """
    Generates the content for an NX .exp file, focusing on Skid Layout,
    based on product parameters.
    """
    p_weight = product_params.get('product_weight', 2500.0)
    p_width = product_params.get('product_width', 90.0)
    p_length = product_params.get('product_length', 90.0)
    p_actual_height = product_params.get('product_actual_height', 48.0)
    p_clearance_side = product_params.get('clearance_side', 2.0)
    p_clearance_above = product_params.get('clearance_above_product', 1.5)
    p_panel_thickness = product_params.get('panel_thickness', 0.25)
    
    p_wall_cleat_thickness = product_params.get('wall_cleat_thickness', 0.75)
    p_wall_cleat_width = product_params.get('wall_cleat_width', 3.5)
    
    p_floor_lumbar_thickness = product_params.get('floor_lumbar_thickness', 1.5)
    p_example_floorboard_width = product_params.get('example_floorboard_width', 7.25)

    p_cap_cleat_thickness = product_params.get('cap_cleat_thickness', 0.75)
    p_cap_cleat_width = product_params.get('cap_cleat_width', 3.5)
    p_max_top_cleat_spacing = product_params.get('max_top_cleat_spacing', 24.0)

    generation_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    exp_content = []
    exp_content.append("// NX Expressions for AutoCrate Wizard - Skid Focus")
    exp_content.append(f"// Parameters loaded from JSON at: {generation_time}")
    exp_content.append("\n// =============================")
    exp_content.append("// 1. USER CONTROLS (Values from Parameter File)")
    exp_content.append("// =============================")
    exp_content.append(f"[lbm]product_weight = {p_weight:.1f}  // Product Weight")
    exp_content.append(f"[Inch]product_width = {p_width:.2f}     // Product Width - across skids")
    exp_content.append(f"[Inch]product_length = {p_length:.2f}    // Product Length - along skids")
    exp_content.append(f"[Inch]product_actual_height = {p_actual_height:.2f} // Product Actual Height (for content)")
    exp_content.append(f"[Inch]clearance_side = {p_clearance_side:.2f}     // Clearance per Side (product to inner wall face)")
    exp_content.append(f"[Inch]clearance_above_product = {p_clearance_above:.2f} // Clearance above product")
    exp_content.append(f"[Inch]panel_thickness = {p_panel_thickness:.3f}   // Panel Sheathing Thickness")
    exp_content.append(f"[Inch]wall_cleat_thickness = {p_wall_cleat_thickness:.3f}   // Wall Cleat Actual Thickness")
    exp_content.append(f"[Inch]wall_cleat_width = {p_wall_cleat_width:.2f} // Wall Cleat Actual Width")
    exp_content.append(f"[Inch]floor_lumbar_thickness = {p_floor_lumbar_thickness:.3f} // Floorboard Actual Thickness")
    exp_content.append(f"[Inch]example_floorboard_width = {p_example_floorboard_width:.3f} // Example fixed floorboard width")
    exp_content.append(f"[Inch]cap_cleat_thickness = {p_cap_cleat_thickness:.3f} // Cap Cleat Actual Thickness")
    exp_content.append(f"[Inch]cap_cleat_width = {p_cap_cleat_width:.2f}     // Cap Cleat Actual Width")
    exp_content.append(f"[Inch]max_cap_cleat_spacing_rule = {p_max_top_cleat_spacing:.2f} // Max rule for cap cleats")

    exp_content.append("\n// --- Constants (Informational) ---")
    exp_content.append("[Inch]min_skid_height_const = 3.5")
    exp_content.append("[Inch]float_tolerance_const = 0.001")

    exp_content.append("\n// ===========================================")
    exp_content.append("// 2. CALCULATED CRATE AND USABLE DIMENSIONS (NX Expressions)")
    exp_content.append("// ===========================================")
    exp_content.append("[Inch]crate_width_OD = product_width + 2 * (clearance_side + panel_thickness + wall_cleat_thickness)")
    exp_content.append("[Inch]crate_length_OD = product_length + 2 * (clearance_side + panel_thickness + wall_cleat_thickness)")
    exp_content.append("[Inch]skid_usable_width_ID = crate_width_OD - 2 * (panel_thickness + wall_cleat_thickness)")

    exp_content.append("\n// =============================")
    exp_content.append("// 3. SKID LAYOUT (NX Expressions - Focused for current goal)")
    exp_content.append("// =============================")
    exp_content.append("[Inch]INPUT_Skid_Nominal_Width = if(product_weight <= 500[lbm]) then (2.5[Inch]) else if(product_weight <= 4500[lbm]) then (3.5[Inch]) else (5.5[Inch])")
    exp_content.append("[Inch]RULE_Max_Skid_Spacing = if(product_weight <= 500[lbm]) then (30.0[Inch]) else if(product_weight <= 4500[lbm]) then (30.0[Inch]) else if(product_weight <= 6000[lbm]) then (41.0[Inch]) else if(product_weight <= 12000[lbm]) then (28.0[Inch]) else if(product_weight <= 20000[lbm]) then (24.0[Inch]) else (0[Inch])")
    exp_content.append("[Inch]INPUT_Skid_Nominal_Height = 3.5")
    exp_content.append("is_overweight_flag = if(product_weight > 20000[lbm]) then (1) else (0)")
    exp_content.append("is_skid_width_error_flag = if(skid_usable_width_ID < INPUT_Skid_Nominal_Width - float_tolerance_const) then (1) else (0)")
    exp_content.append("[Inch]skid_centerline_span_calc = skid_usable_width_ID - INPUT_Skid_Nominal_Width")
    exp_content.append("theoretical_min_skid_count_calc = if(RULE_Max_Skid_Spacing > float_tolerance_const) then (ceil(skid_centerline_span_calc / RULE_Max_Skid_Spacing) + 1) else (999)")
    exp_content.append("CALC_Skid_Count = if(is_overweight_flag == 1 OR is_skid_width_error_flag == 1) then (0) else (if(skid_usable_width_ID < (INPUT_Skid_Nominal_Width * 2) - float_tolerance_const) then (1) else (max(2, theoretical_min_skid_count_calc)))")
    exp_content.append("[Inch]CALC_Skid_Pitch = if(CALC_Skid_Count > 1) then (skid_centerline_span_calc / (CALC_Skid_Count - 1)) else (0.0[Inch])")
    exp_content.append("[Inch]CALC_First_Skid_Pos_X = if(CALC_Skid_Count == 1) then (0.0[Inch]) else (-(CALC_Skid_Pitch * (CALC_Skid_Count - 1)) / 2.0)")
    exp_content.append("[Inch]CALC_Overall_Skid_Span = if(CALC_Skid_Count == 0) then (0[Inch]) else (if(CALC_Skid_Count == 1) then (INPUT_Skid_Nominal_Width) else ((CALC_Skid_Count - 1) * CALC_Skid_Pitch + INPUT_Skid_Nominal_Width))")
    exp_content.append("[Inch]INPUT_Skid_Actual_Length = crate_length_OD")

    exp_content.append("\n// --- Expressions for individual skid positions (Example for up to 10 skids) ---")
    exp_content.append("// Your NX modeling approach would use CALC_Skid_Count and CALC_Skid_Pitch to place skids")
    for i in range(1, 11): # Example for up to 10 skids
        exp_content.append(f"[Inch]POS_Skid_{i}_X = if(CALC_Skid_Count >= {i}) then (CALC_First_Skid_Pos_X + ({i-1} * CALC_Skid_Pitch)) else (0[Inch]) // Position for Skid {i} (0 if not used)")
    
    exp_content.append("\n// End of AutoCrate Wizard Expressions (Skid Focus)")
    return "\n".join(exp_content)

def load_params_from_json(json_filepath):
    try:
        with open(json_filepath, 'r') as f:
            params = json.load(f)
        print(f"Successfully loaded parameters from {json_filepath}")
        return params
    except FileNotFoundError:
        print(f"Error: Parameter file not found at {json_filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_filepath}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading {json_filepath}: {e}")
        return None

if __name__ == "__main__":
    param_file = "parameters.json" 
    # Use product dimensions in the output filename for uniqueness
    
    product_parameters = load_params_from_json(param_file)

    if product_parameters:
        # Construct a filename based on some parameters to make it unique
        p_w = product_parameters.get('product_width', 'NA')
        p_l = product_parameters.get('product_length', 'NA')
        output_exp_filename = f"AutoCrate_Skids_{p_w}W_{p_l}L.exp"

        print(f"Generating NX Expression file content using parameters from '{param_file}'...")
        exp_file_str_content = generate_nx_exp_file_content_for_skids(product_parameters)

        try:
            with open(output_exp_filename, 'w') as f:
                f.write(exp_file_str_content)
            print(f"\nSuccessfully wrote NX Expressions to: {os.path.abspath(output_exp_filename)}")
            print("\nNext Steps:")
            print(f"1. Ensure your `SKID_LUMBER_TEMPLATE.prt` in NX has expressions like `INPUT_Skid_Width`, `INPUT_Skid_Length`, `INPUT_Skid_Height`.")
            print(f"2. In your main NX assembly, import the generated '{output_exp_filename}' (`File -> Utilities -> Expressions -> Import Expressions...`).")
            print(f"3. In the NX Expressions dialog (Ctrl+E), verify the 'USER CONTROLS' and see how `CALC_Skid_Count`, `CALC_Skid_Pitch`, and `POS_Skid_i_X` values are calculated.")
            print(f"4. Manually add `CALC_Skid_Count` instances of your `SKID_LUMBER_TEMPLATE.prt`.")
            print(f"   - Link their dimensions to the imported expressions (e.g., instance's `INPUT_Skid_Width` = assembly's `INPUT_Skid_Nominal_Width`).")
            print(f"   - Position them using the `POS_Skid_i_X` expressions from the imported file.")
            print(f"5. Change 'USER CONTROLS' in NX Expressions (e.g., product_weight) to see parameters update.")

        except Exception as e:
            print(f"\nError writing .exp file: {e}")
    else:
        print(f"\nCould not generate .exp file because parameters were not loaded from '{param_file}'.")
        print(f"Please ensure '{param_file}' exists in the same directory as this script and contains valid JSON.")