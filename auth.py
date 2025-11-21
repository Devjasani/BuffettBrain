# auth.py
import streamlit as st

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Disable sidebar when not authenticated
    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        # Hide sidebar completely
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Show login form in main area
        st.title("🔐 BuffettBrain Login")
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 User not known or password incorrect")
        
        return False
    else:
        # Password correct - show sidebar
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] {
                    display: block !important;
                }
            </style>
        """, unsafe_allow_html=True)
        return True