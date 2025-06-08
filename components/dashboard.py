"""
대시보드 컴포넌트
"""
import streamlit as st
from typing import Any
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import UIHelpers
import pandas as pd

def show_dashboard_metrics(matcher: Any):
    """대시보드 메트릭 표시"""
    st.markdown('<h2 class="section-title">📊 실시간 취업 시장 현황</h2>', unsafe_allow_html=True)
    
    # 메트릭 계산
    total_jobs = len(matcher.df)
    total_companies = matcher.df['company'].nunique()
    avg_skills = matcher.df['skill_count'].mean()
    avg_salary = matcher.df['estimated_salary'].mean()
    
    # 오늘의 신규 공고
    today = pd.Timestamp.now().date()
    new_jobs_today = len(matcher.df[matcher.df['created_date'] == today])
    
    # 사용자 활동
    saved_jobs = len(st.session_state.user_history.get('saved_jobs', []))
    viewed_jobs = len(st.session_state.user_history.get('viewed_jobs', []))
    
    # 메트릭 카드 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(UIHelpers.create_metric_card(
            "전체 채용공고", 
            f"{total_jobs:,}",
            f"신규 {new_jobs_today}건",
            "📋",
            "#667eea"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(UIHelpers.create_metric_card(
            "참여 기업",
            f"{total_companies:,}",
            "활발히 채용 중",
            "🏢",
            "#764ba2"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(UIHelpers.create_metric_card(
            "평균 요구 스킬",
            f"{avg_skills:.1f}개",
            "직무당 평균",
            "🛠️",
            "#f093fb"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(UIHelpers.create_metric_card(
            "평균 연봉",
            f"{avg_salary:,.0f}만원",
            "전체 평균",
            "💰",
            "#4facfe"
        ), unsafe_allow_html=True)
    
    # 사용자 활동 메트릭
    st.markdown('<h3 class="section-title">👤 내 활동</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(UIHelpers.create_metric_card(
            "조회한 공고",
            viewed_jobs,
            "",
            "👁️",
            "#11998e"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(UIHelpers.create_metric_card(
            "저장한 공고",
            saved_jobs,
            "",
            "💾",
            "#38ef7d"
        ), unsafe_allow_html=True)
    
    with col3:
        applied = len(st.session_state.user_history.get('applied_jobs', []))
        st.markdown(UIHelpers.create_metric_card(
            "지원한 공고",
            applied,
            "",
            "📮",
            "#fc4a1a"
        ), unsafe_allow_html=True)
    
    with col4:
        skill_searches = len(st.session_state.user_history.get('skill_searches', []))
        st.markdown(UIHelpers.create_metric_card(
            "스킬 검색",
            skill_searches,
            "",
            "🔍",
            "#f7b733"
        ), unsafe_allow_html=True)

def show_skill_distribution_by_jobtype(matcher: Any):
    """직무별 스킬 분포 시각화"""
    st.markdown('<h3 class="section-title">🛠️ 직무별 핵심 기술 스택</h3>', unsafe_allow_html=True)
    
    skill_freq = matcher.get_skill_freq_by_jobtype(top_n=8)
    job_types = list(skill_freq.keys())
    
    if not job_types:
        st.info("직무별 기술 스택 데이터가 없습니다.")
        return
    
    # 탭으로 직무별 표시
    tabs = st.tabs(job_types)
    
    for i, job_type in enumerate(job_types):
        with tabs[i]:
            skills = skill_freq[job_type]
            if not skills:
                st.info(f"{job_type} 직무의 스킬 데이터가 없습니다.")
                continue
            
            # 시각화
            skill_names = [s[0] for s in skills]
            counts = [s[1] for s in skills]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=skill_names,
                    y=counts,
                    marker=dict(
                        color=counts,
                        colorscale='viridis',
                        showscale=True,
                        colorbar=dict(title="빈도")
                    ),
                    text=counts,
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>요구 공고: %{y}개<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title=f"{job_type} - 주요 기술 스택",
                xaxis_title="기술 스택",
                yaxis_title="공고 수",
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 스킬 카드로 표시
            st.markdown("**💡 핵심 스킬 요약**")
            skills_html = ""
            for skill, count in skills[:5]:
                badge_type = "primary" if count > 50 else "success" if count > 20 else "info"
                skills_html += UIHelpers.create_skill_badge(skill, badge_type, count)
            
            st.markdown(f'<div style="margin: 1rem 0;">{skills_html}</div>', unsafe_allow_html=True)