"""
헤더 컴포넌트
"""
import streamlit as st
from config.styles import get_custom_css

def show_main_header():
    """메인 헤더 표시"""
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; font-size: 3rem; margin: 0;">Spec Tracker</h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-top: 1rem;">
            AI 기반 맞춤형 직무 추천 | 경력 개발 로드맵 | 실시간 시장 인사이트
        </p>
        <div style="margin-top: 2rem;">
            <span class="skill-badge skill-badge-primary">머신러닝</span>
            <span class="skill-badge skill-badge-success">실시간 분석</span>
            <span class="skill-badge skill-badge-info">맞춤 추천</span>
        </div>
    </div>
    """, unsafe_allow_html=True)