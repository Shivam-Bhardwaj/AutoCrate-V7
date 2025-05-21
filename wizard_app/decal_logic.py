#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Logic for calculating decal/stencil placements."""

# try:
#     from . import config
# except ImportError:
#     import config # For direct testing

def calculate_decal_placements(product_is_fragile: bool, product_requires_special_handling: bool, 
                                 panel_height_side: float, panel_width_side: float,
                                 panel_height_end: float, panel_width_end: float,
                                 overall_crate_height: float) -> dict:
    """Calculates placement for standard decals based on product and crate properties.

    Args:
        product_is_fragile (bool): If the product is marked as fragile.
        product_requires_special_handling (bool): If special handling (e.g. "This Way Up") is needed.
        panel_height_side (float): Height of the side panel where decals might be placed.
        panel_width_side (float): Width of the side panel.
        panel_height_end (float): Height of the end panel.
        panel_width_end (float): Width of the end panel.
        overall_crate_height (float): The total external height of the crate for CoG decal placement.

    Returns:
        dict: {
            "decals_to_apply": [], # List of decal objects with their properties and target placements
            "exp_data": {} # Parameters for NX expression file related to decals
        }
    """
    decals_to_apply = []
    exp_data_decals = {}

    # This is highly dependent on how decals are represented and controlled in NX.
    # The `DECAL_RULES` in config.py will be the primary source.
    # We need to translate those rules into specific X, Y, Z positions, angles, and suppression flags for NX.

    # Example for a "Fragile" decal (simplified)
    if product_is_fragile:
        fragile_rule = config.DECAL_RULES.get("fragile", {})
        if fragile_rule:
            decal_info_side = {
                "id": fragile_rule["id"],
                "target_panel_type": "side",
                # Placeholder positions - actual calculation needed based on rule["horizontal_placement"] etc.
                "nx_pos_x": 0, 
                "nx_pos_y": 0, 
                "nx_pos_z": panel_height_side / 2, # Example: centered vertically
                "nx_angle": fragile_rule.get("angle", 0),
                "nx_suppression_flag": 0 # 0 to show, 1 to suppress
            }
            decals_to_apply.append(decal_info_side)
            # Add to exp_data if specific expressions control this decal instance
            # exp_data_decals["CALC_Fragile_Side_Decal_Suppress"] = 0

    # Similar logic for "handling_horizontal", "cog" based on their rules in config.DECAL_RULES
    # CoG placement will be more complex due to its vertical_placement_rules_crate_height

    return {
        "decals_to_apply": decals_to_apply,
        "exp_data": exp_data_decals
    }

if __name__ == '__main__':
    # Basic test case
    # Assuming config.py is in the same directory or accessible via PYTHONPATH for direct execution
    try:
        from . import config
    except ImportError:
        import config
        
    decal_results = calculate_decal_placements(
        product_is_fragile=True,
        product_requires_special_handling=True,
        panel_height_side=40.0,
        panel_width_side=96.0,
        panel_height_end=40.0,
        panel_width_end=48.0,
        overall_crate_height=40.0 + 3.5 + 1.5 # skid + floor + internal height approx
    )
    import json
    print(json.dumps(decal_results, indent=2)) 