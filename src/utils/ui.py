# ============================================================
# STUDYFLOW UI HELPERS
# ============================================================

from contextlib import contextmanager

import streamlit as st


@contextmanager
def ai_loading(message="AI is thinking..."):
    """
    Display a consistent loading state while an AI operation
    is running.

    Usage:

        with ai_loading("Generating your study plan..."):
            result = generate_study_plan(...)
    """

    with st.spinner(f"🤖 {message}"):
        yield


def show_success(message):
    """Display a consistent success message."""
    st.success(f"✅ {message}")


def show_warning(message):
    """Display a consistent warning message."""
    st.warning(f"⚠️ {message}")


def show_error(message):
    """Display a consistent safe error message."""
    st.error(f"❌ {message}")


def show_info(message):
    """Display a consistent informational message."""
    st.info(f"ℹ️ {message}")