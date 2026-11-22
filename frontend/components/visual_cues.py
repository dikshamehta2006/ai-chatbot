import streamlit as st

def render_emergency_banner():
    st.markdown(
        """
        <div style="background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 12px 16px; border-radius: 4px; margin-bottom: 16px;">
            <strong style="color: #856404;">Crisis Resources:</strong>
            <span style="color: #856404;">If you are in acute distress or need immediate human help, call or text 
            <strong>988</strong> (USA/Canada), <strong>14416</strong> (India Tele-MANAS), <strong>116 123</strong> (UK), or visit 
            <a href="https://findahelpline.com" target="_blank" style="color: #533f03; text-decoration: underline;">findahelpline.com</a>.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_grounding_toolkit():
    with st.expander("🌿 Instant Grounding Toolkit & Visual Guides", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Box Breathing", "5-4-3-2-1 Sensory", "DBT STOP Skill"])
        
        with tab1:
            st.markdown("""
            **Box Breathing (4x4 Protocol)**
            1. **Inhale** through nose — *4 seconds* 🌬️
            2. **Hold** breath gently — *4 seconds* ⏸️
            3. **Exhale** completely — *4 seconds* 💨
            4. **Hold** empty lungs — *4 seconds* 🧘
            *Repeat for 4 to 6 continuous cycles.*
            """)
            
        with tab2:
            st.markdown("""
            **5-4-3-2-1 Sensory Re-centering**
            - 👁️ **5 things you can see** around you.
            - ✋ **4 things you can physically touch** right now.
            - 👂 **3 sounds you can hear** in the background.
            - 👃 **2 things you can smell**.
            - 👅 **1 thing you can taste**.
            """)
            
        with tab3:
            st.markdown("""
            **DBT STOP Protocol**
            - **S** — **Stop**: Pause, do not react.
            - **T** — **Take a step back**: Breathe deeply.
            - **O** — **Observe**: What are you feeling inside? What are the facts?
            - **P** — **Proceed mindfully**: Choose an action that serves your wellbeing.
            """)
