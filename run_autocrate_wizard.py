# run_autocrate_wizard.py
# Version 3: Explicitly set developmentMode to false

import streamlit.web.cli as stcli
import sys
import os

if __name__ == "__main__":
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    streamlit_app_path = os.path.join(application_path, "wizard_app", "app.py")

    if not os.path.exists(streamlit_app_path):
        print(f"CRITICAL ERROR: Streamlit app 'app.py' not found at expected bundled location: {streamlit_app_path}")
        # Attempt an alternative path for development if the above fails and not frozen
        if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
            alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_app", "app.py")
            if os.path.exists(alt_path):
                streamlit_app_path = alt_path
            else:
                sys.exit(1) 
        else:
            sys.exit(1) 
    
    print(f"Attempting to run Streamlit app from: {streamlit_app_path}")

    sys.argv = [
        "streamlit",
        "run",
        streamlit_app_path,
        "--server.headless=true",
        "--server.port=8501", 
        "--server.baseUrlPath=/", 
        "--global.developmentMode=false" # Explicitly set developmentMode to false
    ]
    
    sys.exit(stcli.main())
