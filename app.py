"""
Spec Tracker - 메인 애플리케이션
AI 기반 맞춤형 직무 추천 시스템
"""

import streamlit as st
import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent))

# 설정 임포트
from config.settings import AppConfig, ColorTheme
from config.styles import get_custom_css

# 유틸리티 임포트
from utils.helpers import SessionManager

# 모델 임포트
from models.job_matcher import AdvancedJobMatcher

# 컴포넌트 임포트
from components.header import show_main_header
from components.dashboard import show_dashboard_metrics, show_skill_distribution_by_jobtype
from components.job_matching import show_job_matching_interface
from components.career_development import show_career_development_interface
from components.market_insights import show_market_insights_interface

# 페이지 설정
st.set_page_config(
    page_title=AppConfig.PAGE_TITLE,
    page_icon=AppConfig.PAGE_ICON,
    layout=AppConfig.LAYOUT,
    initial_sidebar_state=AppConfig.INITIAL_SIDEBAR_STATE
)

# 커스텀 CSS 적용
st.markdown(get_custom_css(), unsafe_allow_html=True)

def initialize_app():
    """애플리케이션 초기화"""
    # 세션 상태 초기화
    SessionManager.init_session_state()
    
    # 데이터베이스 확인
    if not os.path.exists(AppConfig.DB_PATH):
        st.error("💾 데이터베이스를 찾을 수 없습니다!")
        st.info("데이터 전처리를 먼저 실행해주세요: `python scripts/data_processing.py`")
        st.stop()
    
    # JobMatcher 초기화
    if 'job_matcher' not in st.session_state:
        with st.spinner('🤖 AI 시스템을 초기화하고 있습니다...'):
            try:
                st.session_state.job_matcher = AdvancedJobMatcher(AppConfig.DB_PATH)
            except Exception as e:
                st.error(f"시스템 초기화 실패: {e}")
                st.stop()
    
    return st.session_state.job_matcher

def show_sidebar():
    """사이드바 표시"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h1 style="color: #667eea;">🎯 Spec Tracker</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 네비게이션
        st.markdown("### 📍 네비게이션")
        
        # 사용자 프로필 요약
        if 'user_skills' in st.session_state and st.session_state.user_skills:
            st.markdown("### 👤 내 프로필")
            st.markdown(f"**보유 스킬:** {len(st.session_state.user_skills)}개")
            
            # 스킬 표시 (최대 5개)
            skills_to_show = st.session_state.user_skills[:5]
            for skill in skills_to_show:
                st.markdown(f"• {skill}")
            
            if len(st.session_state.user_skills) > 5:
                st.markdown(f"... 외 {len(st.session_state.user_skills) - 5}개")
        
        # 활동 통계
        st.markdown("### 📊 내 활동")
        
        history = st.session_state.user_history
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("조회", len(history.get('viewed_jobs', [])))
            st.metric("지원", len(history.get('applied_jobs', [])))
        
        with col2:
            st.metric("저장", len(history.get('saved_jobs', [])))
            st.metric("검색", len(history.get('skill_searches', [])))
        

def main():
    """메인 애플리케이션"""
    # 앱 초기화
    matcher = initialize_app()
    
    # 사이드바
    show_sidebar()
    
    # 메인 헤더
    show_main_header()
    
    # 대시보드 메트릭
    show_dashboard_metrics(matcher)
    
    # 구분선
    st.markdown("---")
    
    # 메인 탭 네비게이션
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 직무 인사이트",
        "🎯 직무 매칭",
        "🚀 경력 개발",
        "🛠️ 직무별 스킬"
    ])
    
    with tab1:
        show_market_insights_interface(matcher)
    
    with tab2:
        show_job_matching_interface(matcher)
    
    with tab3:
        show_career_development_interface(matcher)
    
    with tab4:
        show_skill_distribution_by_jobtype(matcher)
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0; color: rgba(255,255,255,0.5);">
        <p style="margin: 0;">
            <span style="font-size: 1.1rem;">🚀 Spec Tracker</span><br>
            <span style="font-size: 0.9rem;">AI 기반 맞춤형 직무 추천 시스템</span>
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem;">
            Copyright © 2024 Capstone Project. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)



if __name__ == "__main__":
    main()
