"""
시장 인사이트 컴포넌트
"""
import streamlit as st
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from utils.helpers import UIHelpers

def show_market_insights_interface(matcher: Any):
    """시장 인사이트 인터페이스"""
    st.markdown('<h2 class="section-title">📊 실시간 시장 인사이트</h2>', unsafe_allow_html=True)
    
    # 시장 데이터 가져오기
    insights = matcher.get_market_insights()
    
    # 탭 구성
    tabs = st.tabs([
        "🔥 스킬 트렌드", 
        "💼 직무 시장", 
        "🏢 기업 분석", 
        "📍 지역 분석",
        "💡 AI 인사이트"
    ])
    
    with tabs[0]:
        show_skill_trends(matcher, insights)
    
    with tabs[1]:
        show_job_market_analysis(matcher, insights)
    
    with tabs[2]:
        show_company_analysis(matcher, insights)
    
    with tabs[3]:
        show_location_analysis(matcher, insights)
    
    with tabs[4]:
        show_ai_insights(matcher, insights)

def show_skill_trends(matcher: Any, insights: Dict[str, Any]):
    """스킬 트렌드 분석"""
    st.markdown("### 🔥 기술 스택 트렌드 분석")
    
    # 상위 스킬 시각화
    if insights.get('top_skills'):
        # 트리맵과 막대 그래프 동시 표시
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # 트리맵
            skills_df = pd.DataFrame(insights['top_skills'], columns=['스킬', '수요'])
            
            fig = px.treemap(
                skills_df,
                path=['스킬'],
                values='수요',
                title='기술 스택 수요 분포',
                color='수요',
                color_continuous_scale='Viridis',
                hover_data={'수요': True}
            )
            
            fig.update_layout(
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # TOP 10 스킬 카드
            st.markdown("#### 🏆 TOP 10 기술 스택")
            
            for i, (skill, count) in enumerate(insights['top_skills'][:10], 1):
                # 순위에 따른 색상
                if i <= 3:
                    badge_type = "danger"
                    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                else:
                    badge_type = "primary"
                    emoji = f"{i}."
                
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 0.5rem; padding: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: white;">
                            <b>{emoji}</b> {skill}
                        </span>
                        <span class="skill-badge skill-badge-{badge_type}">
                            {count}개 공고
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 트렌딩 스킬
    st.markdown("### 📈 급상승 기술")
    
    if insights.get('trending_skills'):
        # 상승/하락 트렌드 분리
        rising_skills = [s for s in insights['trending_skills'] if s['growth'] > 0]
        falling_skills = [s for s in insights['trending_skills'] if s['growth'] < 0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚀 상승 트렌드")
            for skill_info in rising_skills[:5]:
                growth_percent = skill_info['growth'] * 100
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #11998e22, #38ef7d22);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: white; font-weight: 600;">
                            {skill_info['skill']}
                        </span>
                        <span style="color: #38ef7d; font-weight: bold;">
                            ↑ {growth_percent:.1f}%
                        </span>
                    </div>
                    <small style="color: #a0a0a0;">
                        {skill_info['category']} • 최근 {skill_info['recent_count']}개 공고
                    </small>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📉 하락 트렌드")
            if falling_skills:
                for skill_info in falling_skills[:5]:
                    decline_percent = abs(skill_info['growth'] * 100)
                    st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #fc4a1a22, #f7b73322);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: white; font-weight: 600;">
                                {skill_info['skill']}
                            </span>
                            <span style="color: #fc4a1a; font-weight: bold;">
                                ↓ {decline_percent:.1f}%
                            </span>
                        </div>
                        <small style="color: #a0a0a0;">
                            {skill_info['category']}
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("현재 하락 트렌드인 기술이 없습니다.")
    
    # 스킬 조합 분석
    st.markdown("### 🔗 인기 기술 조합")
    
    if insights.get('popular_skill_combinations'):
        # 네트워크 그래프 준비
        combinations = insights['popular_skill_combinations'][:8]
        
        # Sunburst 차트로 표시
        sunburst_data = []
        for combo in combinations:
            skill1, skill2 = combo['skills']
            sunburst_data.append({
                'skill1': skill1,
                'skill2': skill2,
                'count': combo['count'],
                'percentage': combo['percentage']
            })
        
        df_sunburst = pd.DataFrame(sunburst_data)
        
        fig = px.sunburst(
            df_sunburst,
            path=['skill1', 'skill2'],
            values='count',
            title='자주 함께 요구되는 기술 조합',
            color='count',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 상위 조합 리스트
        st.markdown("#### 💎 TOP 기술 조합")
        
        cols = st.columns(2)
        for idx, combo in enumerate(combinations[:6]):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 0.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span class="skill-badge skill-badge-primary">{combo['skills'][0]}</span>
                        <span style="color: #667eea;">+</span>
                        <span class="skill-badge skill-badge-primary">{combo['skills'][1]}</span>
                    </div>
                    <p style="color: #a0a0a0; margin: 0.5rem 0 0 0;">
                        {combo['count']}개 공고 ({combo['percentage']:.1f}%)
                    </p>
                </div>
                """, unsafe_allow_html=True)

def show_job_market_analysis(matcher: Any, insights: Dict[str, Any]):
    """직무 시장 분석"""
    st.markdown("### 💼 직무 시장 현황")
    
    # 경력별 분포
    if insights.get('experience_distribution'):
        exp_df = pd.DataFrame(
            list(insights['experience_distribution'].items()),
            columns=['경력', '공고 수']
        )
        exp_df = exp_df.sort_values('경력')
        
        # 도넛 차트와 막대 그래프
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                exp_df,
                values='공고 수',
                names='경력',
                title='경력별 채용 공고 분포',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 경력별 평균 연봉
            if insights.get('salary_stats'):
                salary_by_exp = insights['salary_stats'].get('by_experience', {})
                
                salary_df = pd.DataFrame(
                    list(salary_by_exp.items()),
                    columns=['경력', '평균 연봉']
                )
                salary_df = salary_df.sort_values('경력')
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=salary_df['경력'],
                        y=salary_df['평균 연봉'],
                        text=salary_df['평균 연봉'].apply(lambda x: f'{x:,.0f}만원'),
                        textposition='outside',
                        marker=dict(
                            color=salary_df['평균 연봉'],
                            colorscale='Blues',
                            showscale=False
                        )
                    )
                ])
                
                fig.update_layout(
                    title='경력별 평균 연봉',
                    xaxis_title='경력 (년)',
                    yaxis_title='평균 연봉 (만원)',
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # 직무별 스킬 요구사항
    st.markdown("### 📊 직무별 평균 요구 스킬")
    
    if insights.get('avg_skills_by_job'):
        job_skills_df = pd.DataFrame(
        [(job, stats, 0)   # stats가 바로 평균값, 표준편차 0으로 처리
        for job, stats in insights['avg_skills_by_job'].items()],
        columns=['직무', '평균', '표준편차']
    )
        
        fig = go.Figure()
        
        # 평균값 막대
        fig.add_trace(go.Bar(
            x=job_skills_df['직무'],
            y=job_skills_df['평균'],
            name='평균 요구 스킬',
            marker_color='#667eea',
            error_y=dict(
                type='data',
                array=job_skills_df['표준편차'],
                visible=True,
                color='#a0a0a0'
            )
        ))
        
        fig.update_layout(
            title='직무별 평균 요구 기술 수',
            xaxis_title='직무',
            yaxis_title='평균 스킬 수',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 급여 통계
    st.markdown("### 💰 급여 현황")
    
    if insights.get('salary_stats'):
        stats = insights['salary_stats']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(UIHelpers.create_metric_card(
                "평균 연봉",
                f"{stats['mean']:,.0f}만원",
                "",
                "💰",
                "#667eea"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(UIHelpers.create_metric_card(
                "중간값",
                f"{stats['median']:,.0f}만원",
                "",
                "📊",
                "#764ba2"
            ), unsafe_allow_html=True)
        
        with col3:
            highest_exp = max(stats.get('by_experience', {}).items(), 
                            key=lambda x: x[1]) if stats.get('by_experience') else (0, 0)
            st.markdown(UIHelpers.create_metric_card(
                "최고 연봉 경력",
                f"{highest_exp[0]}년차",
                f"{highest_exp[1]:,.0f}만원",
                "🏆",
                "#38ef7d"
            ), unsafe_allow_html=True)
        
        with col4:
            salary_range = max(stats.get('by_experience', {}).values()) - \
                          min(stats.get('by_experience', {}).values()) \
                          if stats.get('by_experience') else 0
            st.markdown(UIHelpers.create_metric_card(
                "연봉 격차",
                f"{salary_range:,.0f}만원",
                "최고-최저",
                "📈",
                "#fc4a1a"
            ), unsafe_allow_html=True)

def show_company_analysis(matcher: Any, insights: Dict[str, Any]):
    """기업 분석"""
    st.markdown("### 🏢 기업별 채용 현황")
    
    if insights.get('jobs_by_company'):
        company_df = pd.DataFrame(
            list(insights['jobs_by_company'].items()),
            columns=['기업', '공고 수']
        )
        
        # 상위 10개 기업
        fig = px.bar(
            company_df.head(10),
            x='공고 수',
            y='기업',
            orientation='h',
            title='채용 공고가 많은 기업 TOP 10',
            color='공고 수',
            color_continuous_scale='Blues',
            text='공고 수'
        )
        
        fig.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            yaxis={'categoryorder': 'total ascending'}
        )
        
        fig.update_traces(texttemplate='%{text}개', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 기업별 선호 스킬 분석
    st.markdown("### 🎯 주요 기업 선호 기술")
    
    # 상위 5개 기업의 선호 스킬
    top_companies = list(insights['jobs_by_company'].keys())[:5]
    
    company_skills = {}
    for company in top_companies:
        company_jobs = matcher.df[matcher.df['company'] == company]
        all_skills = []
        for skills in company_jobs['llm_extracted_tech_skills']:
            all_skills.extend(skills)
        
        if all_skills:
            skill_counter = pd.Series(all_skills).value_counts()
            company_skills[company] = skill_counter.head(5).to_dict()
    
    # 기업별 스킬 표시
    for company, skills in company_skills.items():
        with st.expander(f"🏢 {company}", expanded=(company == top_companies[0])):
            skills_html = ""
            for skill, count in skills.items():
                skills_html += UIHelpers.create_skill_badge(skill, "primary", count)
            
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="color: #667eea; margin-bottom: 1rem;">주요 요구 기술</h5>
                <div>{skills_html}</div>
                <p style="color: #a0a0a0; margin-top: 1rem;">
                    총 {insights['jobs_by_company'][company]}개의 채용 공고 진행 중
                </p>
            </div>
            """, unsafe_allow_html=True)

def show_location_analysis(matcher: Any, insights: Dict[str, Any]):
    """지역 분석"""
    st.markdown("### 📍 지역별 일자리 분포")
    
    if insights.get('jobs_by_location'):
        location_df = pd.DataFrame(
            list(insights['jobs_by_location'].items()),
            columns=['지역', '공고 수']
        )
        
        # 지도 시각화를 위한 좌표 (간단한 예시)
        location_coords = {
            '서울': (37.5665, 126.9780),
            '경기': (37.4138, 127.5183),
            '인천': (37.4563, 126.7052),
            '대전': (36.3504, 127.3845),
            '대구': (35.8714, 128.6014),
            '부산': (35.1796, 129.0756),
            '광주': (35.1595, 126.8526),
            '울산': (35.5384, 129.3114),
            '세종': (36.4800, 127.2890),
            '강원': (37.8228, 128.1555)
        }
        
        # 막대 그래프와 파이 차트
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                location_df,
                x='지역',
                y='공고 수',
                title='지역별 채용 공고 수',
                color='공고 수',
                color_continuous_scale='Blues',
                text='공고 수'
            )
            
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis_tickangle=-45
            )
            
            fig.update_traces(texttemplate='%{text}개', textposition='outside')
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(
                location_df.head(5),
                values='공고 수',
                names='지역',
                title='상위 5개 지역 비율',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # 지역별 선호 스킬
    st.markdown("### 🗺️ 지역별 주요 기술 스택")
    
    selected_location = st.selectbox(
        "지역을 선택하세요",
        options=list(insights['jobs_by_location'].keys()),
        index=0
    )
    
    if selected_location:
        # 선택된 지역의 스킬 분석
        location_jobs = matcher.df[matcher.df['location'] == selected_location]
        location_skills = []
        for skills in location_jobs['llm_extracted_tech_skills']:
            location_skills.extend(skills)
        
        if location_skills:
            skill_counter = pd.Series(location_skills).value_counts()
            top_skills = skill_counter.head(10)
            
            # 스킬 시각화
            fig = go.Figure(data=[
                go.Bar(
                    x=top_skills.values,
                    y=top_skills.index,
                    orientation='h',
                    marker=dict(
                        color=top_skills.values,
                        colorscale='Viridis',
                        showscale=False
                    ),
                    text=top_skills.values,
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                title=f'{selected_location} 지역 TOP 10 기술',
                xaxis_title='요구 빈도',
                yaxis_title='기술',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 지역 특성 분석
            col1, col2 = st.columns(2)
            
            with col1:
                # 평균 연봉
                avg_salary = location_jobs['estimated_salary'].mean()
                st.markdown(UIHelpers.create_metric_card(
                    f"{selected_location} 평균 연봉",
                    f"{avg_salary:,.0f}만원",
                    f"전체 평균 대비 {(avg_salary / matcher.df['estimated_salary'].mean() - 1) * 100:+.1f}%",
                    "💰",
                    "#667eea"
                ), unsafe_allow_html=True)
            
            with col2:
                # 평균 요구 스킬
                avg_skills = location_jobs['skill_count'].mean()
                st.markdown(UIHelpers.create_metric_card(
                    "평균 요구 스킬",
                    f"{avg_skills:.1f}개",
                    f"전체 평균 대비 {(avg_skills / matcher.df['skill_count'].mean() - 1) * 100:+.1f}%",
                    "🛠️",
                    "#764ba2"
                ), unsafe_allow_html=True)

def show_ai_insights(matcher: Any, insights: Dict[str, Any]):
    """AI 인사이트"""
    st.markdown("### 💡 AI 시장 인사이트")
    
    # 주요 인사이트 생성
    ai_insights = []
    
    # 1. 가장 인기 있는 스킬
    if insights.get('top_skills'):
        top_skill = insights['top_skills'][0]
        ai_insights.append({
            'title': '🔥 가장 핫한 기술',
            'content': f"현재 가장 수요가 높은 기술은 **{top_skill[0]}**입니다. "
                      f"전체 {top_skill[1]}개의 공고에서 요구하고 있습니다.",
            'type': 'hot'
        })
    
    # 2. 급상승 스킬
    if insights.get('trending_skills'):
        top_trending = insights['trending_skills'][0]
        growth_percent = top_trending['growth'] * 100
        ai_insights.append({
            'title': '📈 급상승 기술',
            'content': f"**{top_trending['skill']}**이(가) 최근 {growth_percent:.0f}% 상승했습니다. "
                      f"이 기술을 학습하면 경쟁력을 확보할 수 있습니다.",
            'type': 'trend'
        })
    
    # 3. 연봉 인사이트
    if insights.get('salary_stats'):
        avg_salary = insights['salary_stats']['mean']
        by_exp = insights['salary_stats'].get('by_experience', {})
        if by_exp:
            best_exp = max(by_exp.items(), key=lambda x: x[1])
            ai_insights.append({
                'title': '💰 연봉 인사이트',
                'content': f"현재 평균 연봉은 **{avg_salary:,.0f}만원**이며, "
                          f"**{best_exp[0]}년차**가 평균 **{best_exp[1]:,.0f}만원**으로 가장 높습니다.",
                'type': 'salary'
            })
    
    # 4. 스킬 조합 인사이트
    if insights.get('popular_skill_combinations'):
        top_combo = insights['popular_skill_combinations'][0]
        ai_insights.append({
            'title': '🔗 황금 조합',
            'content': f"**{top_combo['skills'][0]}**와 **{top_combo['skills'][1]}**는 "
                      f"함께 요구되는 경우가 많습니다 ({top_combo['count']}개 공고). "
                      f"두 기술을 모두 보유하면 시너지 효과를 얻을 수 있습니다.",
            'type': 'combo'
        })
    
    # 5. 지역 인사이트
    if insights.get('jobs_by_location'):
        top_location = list(insights['jobs_by_location'].items())[0]
        ai_insights.append({
            'title': '📍 지역 인사이트',
            'content': f"**{top_location[0]}** 지역에 가장 많은 일자리가 있습니다 "
                      f"({top_location[1]}개 공고). 이 지역에서 구직 활동을 집중하면 효과적입니다.",
            'type': 'location'
        })
    
    # 인사이트 카드 표시
    for insight in ai_insights:
        icon_map = {
            'hot': '🔥',
            'trend': '📈',
            'salary': '💰',
            'combo': '🔗',
            'location': '📍'
        }
        
        color_map = {
            'hot': '#ff4b4b',
            'trend': '#38ef7d',
            'salary': '#ffa500',
            'combo': '#667eea',
            'location': '#4facfe'
        }
        
        st.markdown(f"""
        <div class="metric-card" style="
            background: linear-gradient(135deg, {color_map[insight['type']]}11, {color_map[insight['type']]}22);
            border-left: 4px solid {color_map[insight['type']]};
            margin-bottom: 1rem;
        ">
            <h4 style="color: {color_map[insight['type']]}; margin: 0;">
                {icon_map[insight['type']]} {insight['title']}
            </h4>
            <p style="color: #e0e0e0; margin: 0.5rem 0 0 0; line-height: 1.6;">
                {insight['content']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 추천 액션
    st.markdown("### 🎯 추천 액션")
    
    recommendations = []
    
    # 트렌딩 스킬 학습 추천
    if insights.get('trending_skills'):
        trending_skills = [s['skill'] for s in insights['trending_skills'][:3]]
        recommendations.append(
            f"📚 급상승 중인 **{', '.join(trending_skills)}** 기술을 학습하여 미래에 대비하세요."
        )
    
    # 스킬 조합 추천
    if insights.get('popular_skill_combinations'):
        combo = insights['popular_skill_combinations'][0]['skills']
        recommendations.append(
            f"🔗 **{combo[0]}**를 학습 중이라면 **{combo[1]}**도 함께 학습하여 시너지를 만드세요."
        )
    
    # 지역 추천
    if insights.get('jobs_by_location'):
        top_locations = list(insights['jobs_by_location'].keys())[:3]
        recommendations.append(
            f"📍 **{', '.join(top_locations)}** 지역을 중심으로 구직 활동을 진행하세요."
        )
    
    for rec in recommendations:
        st.info(rec)
    
    # 시장 예측 (간단한 시뮬레이션)
    st.markdown("### 🔮 시장 예측")
    
    # 향후 6개월 예측 (단순 트렌드 기반)
    months = ['현재', '1개월', '2개월', '3개월', '4개월', '5개월', '6개월']
    
    # 가상의 예측 데이터
    job_forecast = [len(matcher.df)]
    for i in range(1, 7):
        # 월 5% 성장 가정
        job_forecast.append(int(job_forecast[-1] * 1.05))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=job_forecast,
        mode='lines+markers',
        name='예상 채용 공고 수',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='향후 6개월 채용 시장 예측',
        xaxis_title='기간',
        yaxis_title='예상 공고 수',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("📊 AI 예측에 따르면 향후 6개월간 채용 시장은 지속적으로 성장할 것으로 예상됩니다.")