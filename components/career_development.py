"""
경력 개발 컴포넌트 - HTML 렌더링 문제 해결
"""
import streamlit as st
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import UIHelpers, SessionManager
import pandas as pd
from plotly.subplots import make_subplots


def show_career_development_interface(matcher: Any):
    """경력 개발 인터페이스"""
    st.markdown('<h2 class="section-title">🚀 맞춤형 경력 개발 로드맵</h2>', unsafe_allow_html=True)
    
    # 현재 프로필 섹션
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 내 경력 프로필")
        
        # 기본 정보 입력
        col_a, col_b = st.columns(2)
        
        with col_a:
            current_position = st.selectbox(
                "현재 포지션",
                ["Junior Developer", "Mid-level Developer", "Senior Developer", 
                "Tech Lead", "Architect", "Engineering Manager"],
                index=st.session_state.get('career_position_index', 1)
            )
            
            experience_years = st.slider(
                "경력 연차",
                0, 20,
                value=st.session_state.get('experience_years', 3),
                help="실무 경력 기간을 선택하세요"
            )
        
        with col_b:
            career_goal = st.selectbox(
                "목표 포지션",
                ["Senior Developer", "Tech Lead", "Architect", 
                 "Engineering Manager", "Principal Engineer", "CTO"],
                index=2
            )
            
            target_years = st.slider(
                "목표 달성 기간 (년)",
                1, 10,
                value=3,
                help="목표 포지션 달성까지의 예상 기간"
            )
        
        # 현재 스킬 입력
        all_skills = []
        for skills in matcher.df['llm_extracted_tech_skills']:
            all_skills.extend(skills)
        available_skills = sorted(list(set(all_skills)))
        
        current_skills = st.multiselect(
            "현재 보유 스킬",
            options=available_skills,
            default=st.session_state.get('user_skills', []),
            help="현재 보유하고 있는 기술 스택을 모두 선택하세요"
        )
        
        # 추가 정보
        with st.expander("🎯 상세 정보 입력", expanded=False):
            col_x, col_y = st.columns(2)
            
            with col_x:
                current_salary = st.number_input(
                    "현재 연봉 (만원)",
                    min_value=2000,
                    max_value=20000,
                    value=5000,
                    step=500
                )
                
                preferred_domain = st.selectbox(
                    "관심 도메인",
                    ["웹 개발", "모바일", "데이터/AI", "DevOps", "보안", "블록체인"]
                )
            
            with col_y:
                learning_hours = st.slider(
                    "주당 학습 가능 시간",
                    0, 40,
                    value=10,
                    help="경력 개발에 투자할 수 있는 주당 시간"
                )
                
                learning_style = st.selectbox(
                    "선호 학습 방식",
                    ["온라인 강의", "실습 프로젝트", "독서", "스터디 그룹", "멘토링"]
                )
    
    with col2:
        # 경력 분석 결과
        if current_skills and experience_years >= 0:
            career_analysis = matcher.get_career_path_analysis(current_skills, experience_years)
            
            st.markdown("### 🎯 AI 경력 분석")
            
            # 현재 레벨 카드
            current_path = matcher.career_paths.get(career_analysis['current_level'], {})
            salary_range = current_path.get('salary_range', (0, 0))
            
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #667eea22, #764ba222);">
                <h4 style="color: #667eea; margin: 0;">현재 레벨</h4>
                <p style="font-size: 1.5rem; color: white; margin: 0.5rem 0;">
                    {career_analysis['current_level']}
                </p>
                <p style="color: #a0a0a0; margin: 0;">
                    💰 예상 연봉: {salary_range[0]:,} ~ {salary_range[1]:,}만원
                </p>
                <p style="color: #38ef7d; margin: 0.5rem 0 0 0;">
                    다음 레벨까지 약 {career_analysis['years_to_next']}년
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📈 다음 커리어 옵션")

            for gap in career_analysis['skill_gaps'][:3]:
                readiness_percent = int(gap['readiness'] * 100)
                readiness_color = "#38ef7d" if readiness_percent >= 70 else "#ffa500" if readiness_percent >= 50 else "#fc4a1a"

                # HTML 직접 출력 대신 Streamlit 컴포넌트 사용
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{gap['position']}**")
                        st.progress(readiness_percent / 100)
                        st.caption(f"💰 {gap['salary_range'][0]:,} ~ {gap['salary_range'][1]:,}만원")
                    
                    with col2:
                        st.metric("준비도", f"{readiness_percent}%")

            # AI 추천
            if career_analysis.get('recommendations'):
                st.markdown("### 💡 AI 추천사항")
                for rec in career_analysis['recommendations']:
                    st.info(rec)
    
    # 분석 실행 버튼
    if st.button("🔍 상세 경력 분석 시작", type="primary", use_container_width=True):
        if current_skills:
            st.session_state.career_profile = {
                'current_position': current_position,
                'experience_years': experience_years,
                'career_goal': career_goal,
                'target_years': target_years,
                'current_skills': current_skills,
                'current_salary': current_salary,
                'learning_hours': learning_hours
            }
            st.session_state.show_career_analysis = True
        else:
            st.warning("최소 하나 이상의 스킬을 선택해주세요!")
    
    # 상세 분석 결과
    if st.session_state.get('show_career_analysis'):
        show_detailed_career_analysis(matcher)

def show_detailed_career_analysis(matcher: Any):
    """상세 경력 분석 결과"""
    st.markdown("---")
    st.markdown('<h3 class="section-title">📊 상세 경력 개발 분석</h3>', unsafe_allow_html=True)
    
    profile = st.session_state.get('career_profile', {})
    current_skills = profile.get('current_skills', [])
    career_goal = profile.get('career_goal', 'Senior Developer')
    target_years = profile.get('target_years', 3)
    
    # 탭 구성
    tabs = st.tabs(["🗺️ 스킬 로드맵", "📚 학습 계획", "💼 프로젝트 추천", "📈 경력 시뮬레이션"])
    
    with tabs[0]:
        show_skill_roadmap(matcher, current_skills, career_goal)
    
    with tabs[1]:
        show_learning_plan(matcher, current_skills, target_years, profile.get('learning_hours', 10))
    
    with tabs[2]:
        show_project_recommendations(matcher, current_skills, career_goal)
    
    with tabs[3]:
        show_career_simulation(matcher, profile)

def show_skill_roadmap(matcher: Any, current_skills: List[str], career_goal: str):
    """스킬 로드맵 표시"""
    st.markdown("### 🗺️ 맞춤형 스킬 개발 로드맵")
    
    # 스킬 추천 가져오기
    skill_recommendations = matcher.get_skill_recommendations(current_skills, top_n=15)
    
    # 스킬 카테고리별 분류
    skill_by_category = {}
    for rec in skill_recommendations:
        category = rec['category']
        if category not in skill_by_category:
            skill_by_category[category] = []
        skill_by_category[category].append(rec)
    
    # Sankey 다이어그램으로 스킬 경로 시각화
    if skill_recommendations:
        # 노드와 링크 생성
        nodes = ["현재 스킬"]
        node_colors = ["#667eea"]
        
        categories = list(skill_by_category.keys())
        nodes.extend(categories)
        node_colors.extend(["#764ba2", "#f093fb", "#4facfe", "#00f2fe", "#38ef7d"][:len(categories)])
        
        for rec in skill_recommendations[:10]:
            nodes.append(rec['skill'])
            importance_colors = {
                "매우 높음": "#ff4b4b",
                "높음": "#ffa500",
                "보통": "#00cc66",
                "낮음": "#0066cc"
            }
            node_colors.append(importance_colors.get(rec['importance'], "#666"))
        
        # 링크 생성
        source = []
        target = []
        value = []
        
        # 현재 스킬 -> 카테고리
        for i, category in enumerate(categories):
            source.append(0)
            target.append(i + 1)
            value.append(len(skill_by_category[category]))
        
        # 카테고리 -> 개별 스킬
        for rec in skill_recommendations[:10]:
            category_idx = categories.index(rec['category']) + 1
            skill_idx = nodes.index(rec['skill'])
            source.append(category_idx)
            target.append(skill_idx)
            value.append(rec['frequency'])
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=nodes,
                color=node_colors
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color="rgba(255,255,255,0.2)"
            )
        )])
        
        fig.update_layout(
            title=f"{career_goal}을 위한 스킬 개발 경로",
            font_size=12,
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 카테고리별 스킬 카드 - HTML 대신 Streamlit 컴포넌트 사용
    st.markdown("### 📚 카테고리별 추천 스킬")
    
    for category, skills in skill_by_category.items():
        with st.expander(f"📁 {category}", expanded=True):
            for skill in skills[:5]:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{skill['skill']}**")
                    st.caption(f"중요도: {skill['importance']}")
                
                with col2:
                    difficulty_emoji = {
                        "쉬움": "🟢",
                        "보통": "🟡",
                        "어려움": "🔴"
                    }
                    st.markdown(f"{difficulty_emoji.get(skill['difficulty'], '⚪')} {skill['difficulty']}")
                
                with col3:
                    trend_emoji = {
                        "상승": "📈",
                        "유지": "➡️",
                        "하락": "📉"
                    }
                    st.markdown(f"{trend_emoji.get(skill['trend'], '➡️')} {skill['trend']}")

def show_learning_plan(matcher: Any, current_skills: List[str], target_years: int, weekly_hours: int):
    """학습 계획 표시"""
    st.markdown("### 📚 개인 맞춤형 학습 계획")
    
    # 스킬 추천
    skill_recommendations = matcher.get_skill_recommendations(current_skills, top_n=12)
    
    # 학습 계획 계산
    total_months = target_years * 12
    total_hours = weekly_hours * 52 * target_years
    skills_per_quarter = max(1, len(skill_recommendations) // (target_years * 4))
    
    # 요약 정보 - Streamlit 메트릭 사용
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 학습 기간", f"{target_years}년", f"{total_months}개월")
    
    with col2:
        st.metric("주당 학습 시간", f"{weekly_hours}시간", f"총 {total_hours:,}시간")
    
    with col3:
        st.metric("목표 스킬 수", f"{len(skill_recommendations)}개", f"분기당 {skills_per_quarter}개")
    
    with col4:
        hours_per_skill = total_hours // len(skill_recommendations) if skill_recommendations else 0
        st.metric("스킬당 학습시간", f"{hours_per_skill}시간", "평균 소요시간")
    
    # 분기별 학습 계획
    st.markdown("### 📅 분기별 학습 로드맵")
    
    quarters = min(target_years * 4, 8)  # 최대 2년(8분기)까지만 표시
    
    for q in range(quarters):
        year = q // 4 + 1
        quarter = q % 4 + 1
        
        # 해당 분기 스킬
        start_idx = q * skills_per_quarter
        end_idx = min((q + 1) * skills_per_quarter, len(skill_recommendations))
        quarter_skills = skill_recommendations[start_idx:end_idx]
        
        if not quarter_skills:
            continue
        
        with st.expander(f"📍 {year}년차 {quarter}분기 계획", expanded=(q < 2)):
            # 분기 정보
            st.info(f"학습 스킬: {len(quarter_skills)}개 | 예상 학습시간: {weekly_hours * 13}시간 | 완료 목표: {(q + 1) * 3}개월 후")
            
            # 스킬별 상세 계획
            for skill in quarter_skills:
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**{skill['skill']}**")
                        st.caption(f"{skill['category']} • 난이도: {skill['difficulty']} • 중요도: {skill['importance']}")
                        
                        tags = ["온라인 강의 2개", "실습 프로젝트 1개", "관련 서적 1권"]
                        # 인라인 코드 대신, 뱃지 스타일로!
                        st.markdown(" ".join([
                            f'<span style="background:#eee; color:#555; padding:0.3em 0.8em; border-radius:12px; font-size:0.9em;">{tag}</span>'
                            for tag in tags
                        ]), unsafe_allow_html=True)
                        
                        if skill.get('related_skills'):
                            st.success(f"💡 연관 스킬: {', '.join(skill['related_skills'][:3])}")

                    with col2:
                        estimated_hours = hours_per_skill
                        st.metric("예상 시간", f"{estimated_hours}h", f"약 {estimated_hours // weekly_hours}주")

    
    # 학습 리소스 추천
    st.markdown("### 📖 추천 학습 리소스")
    
    resource_types = {
        "온라인 강의": ["Coursera", "Udemy", "인프런", "노마드코더"],
        "책": ["오라일리", "한빛미디어", "위키북스"],
        "실습 플랫폼": ["GitHub", "LeetCode", "HackerRank", "프로그래머스"],
        "커뮤니티": ["Stack Overflow", "Reddit", "Discord", "Slack"]
    }
    
    cols = st.columns(len(resource_types))
    for idx, (rtype, resources) in enumerate(resource_types.items()):
        with cols[idx]:
            st.markdown(f"**{rtype}**")
            for resource in resources:
                st.markdown(f"• {resource}")

def show_project_recommendations(matcher: Any, current_skills: List[str], career_goal: str):
    """프로젝트 추천"""
    st.markdown("### 💼 포트폴리오 프로젝트 추천")
    
    # 스킬 카테고리 파악
    skill_categories = set()
    for skill in current_skills:
        category = matcher._find_skill_category(skill)
        skill_categories.add(category)
    
    # 프로젝트 아이디어 DB
    project_ideas = {
        'Frontend': [
            {
                'title': '실시간 협업 대시보드',
                'description': 'WebSocket을 활용한 실시간 데이터 시각화 대시보드',
                'skills': ['React', 'WebSocket', 'D3.js', 'Redux'],
                'difficulty': '중급',
                'duration': '6-8주',
                'impact': '높음'
            },
            {
                'title': '프로그레시브 웹 앱 (PWA)',
                'description': '오프라인 지원 및 푸시 알림 기능이 있는 PWA',
                'skills': ['Vue.js', 'Service Worker', 'IndexedDB'],
                'difficulty': '중급',
                'duration': '4-6주',
                'impact': '높음'
            }
        ],
        'Backend': [
            {
                'title': '마이크로서비스 아키텍처 구현',
                'description': 'Docker와 Kubernetes를 활용한 MSA 시스템',
                'skills': ['Node.js', 'Docker', 'Kubernetes', 'RabbitMQ'],
                'difficulty': '고급',
                'duration': '8-10주',
                'impact': '매우 높음'
            },
            {
                'title': 'RESTful API with GraphQL',
                'description': '확장 가능한 API 서버 구축',
                'skills': ['Python', 'FastAPI', 'GraphQL', 'PostgreSQL'],
                'difficulty': '중급',
                'duration': '4-6주',
                'impact': '높음'
            }
        ],
        'Data Science': [
            {
                'title': '실시간 이상 탐지 시스템',
                'description': '머신러닝을 활용한 실시간 이상 패턴 감지',
                'skills': ['Python', 'TensorFlow', 'Kafka', 'Elasticsearch'],
                'difficulty': '고급',
                'duration': '10-12주',
                'impact': '매우 높음'
            },
            {
                'title': '추천 시스템 구축',
                'description': '협업 필터링과 콘텐츠 기반 추천 시스템',
                'skills': ['Python', 'Scikit-learn', 'Redis', 'Flask'],
                'difficulty': '중급',
                'duration': '6-8주',
                'impact': '높음'
            }
        ],
        'DevOps': [
            {
                'title': 'CI/CD 파이프라인 구축',
                'description': '자동화된 빌드, 테스트, 배포 시스템',
                'skills': ['Jenkins', 'Docker', 'Terraform', 'AWS'],
                'difficulty': '중급',
                'duration': '4-6주',
                'impact': '높음'
            },
            {
                'title': '모니터링 및 로깅 시스템',
                'description': 'ELK 스택을 활용한 중앙 집중식 로깅',
                'skills': ['Elasticsearch', 'Logstash', 'Kibana', 'Prometheus'],
                'difficulty': '중급',
                'duration': '6-8주',
                'impact': '높음'
            }
        ]
    }
    
    # 추천 프로젝트 표시
    recommended_projects = []
    for category in skill_categories:
        if category in project_ideas:
            recommended_projects.extend(project_ideas[category])
    
    # 목표 포지션에 맞는 프로젝트 우선순위 지정
    if career_goal in ['Tech Lead', 'Engineering Manager']:
        recommended_projects.sort(key=lambda x: x['impact'] == '매우 높음', reverse=True)
    
    # 프로젝트 카드들을 컨테이너로 표시
    for idx, project in enumerate(recommended_projects[:6]):
        # 임팩트에 따른 색상 설정
        impact_colors = {
            '매우 높음': '🔴',
            '높음': '🟠', 
            '보통': '🟡'
        }
        
        difficulty_colors = {
            '초급': '🟢',
            '중급': '🟡',
            '고급': '🔴'
        }
        
        # 카드 스타일 컨테이너
        with st.container():
            # 카드 헤더
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"#### {project['title']}")
                st.write(project['description'])
            
            with col2:
                if st.button("📋 상세", key=f"btn_{idx}", help="프로젝트 상세 정보"):
                    st.session_state.selected_project = project
                    st.session_state.show_project_detail = True
            
            # 프로젝트 정보 표시
            info_col1, info_col2, info_col3 = st.columns(3)
            
            with info_col1:
                st.caption(f"{difficulty_colors.get(project['difficulty'], '⚪')} **난이도:** {project['difficulty']}")
            
            with info_col2:
                st.caption(f"⏱️ **기간:** {project['duration']}")
            
            with info_col3:
                st.caption(f"{impact_colors.get(project['impact'], '⚪')} **임팩트:** {project['impact']}")
            
            # 필요 스킬들을 코드 블록으로 표시
            skills_text = " • ".join([f"`{skill}`" for skill in project['skills']])
            st.markdown(f"**필요 스킬:** {skills_text}")
            
            st.divider()
    
    # 프로젝트 상세 정보 (선택시)
    if st.session_state.get('show_project_detail') and st.session_state.get('selected_project'):
        project = st.session_state.selected_project
        
        with st.expander("📋 프로젝트 상세 계획", expanded=True):
            # 프로젝트 제목
            st.markdown(f"## {project['title']}")
            st.write(project['description'])
            
            # 두 컬럼으로 정보 분할
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.markdown("### 📊 프로젝트 개요")
                
                # 기본 정보를 표로 표시
                project_info = {
                    "난이도": project['difficulty'],
                    "예상 기간": project['duration'],
                    "임팩트": project['impact'],
                    "필요 스킬 수": f"{len(project['skills'])}개"
                }
                
                for key, value in project_info.items():
                    st.write(f"**{key}:** {value}")
                
                st.markdown("### 🛠️ 필요 기술 스택")
                for skill in project['skills']:
                    st.write(f"• `{skill}`")
            
            with detail_col2:
                st.markdown("### 🎯 주요 학습 포인트")
                learning_points = [
                    "시스템 설계 및 아키텍처",
                    "성능 최적화 기법", 
                    "테스트 및 배포 전략",
                    "코드 품질 관리",
                    "문서화 및 유지보수"
                ]
                
                for point in learning_points:
                    st.write(f"• {point}")
                
                st.markdown("### 📅 주차별 계획")
                weekly_plan = [
                    ("1-2주차", "요구사항 분석 및 설계"),
                    ("3-4주차", "핵심 기능 구현"),
                    ("5-6주차", "테스트 및 최적화"),
                    ("7-8주차", "배포 및 문서화")
                ]
                
                for week, task in weekly_plan:
                    st.write(f"**{week}:** {task}")
            
            # 추가 리소스
            st.markdown("### 📚 추천 학습 리소스")
            
            resource_col1, resource_col2 = st.columns(2)
            
            with resource_col1:
                st.markdown("**온라인 강의**")
                st.write("• Udemy - 관련 기술 강의")
                st.write("• Coursera - 전문 과정")
                st.write("• 인프런 - 한국어 강의")
            
            with resource_col2:
                st.markdown("**참고 자료**")
                st.write("• GitHub - 오픈소스 프로젝트")
                st.write("• Medium - 기술 블로그")
                st.write("• Stack Overflow - Q&A")
            
            # 닫기 버튼
            if st.button("❌ 닫기", key="close_detail", type="secondary"):
                st.session_state.show_project_detail = False
                st.session_state.selected_project = None
                st.rerun()  # 페이지 새로고침으로 상태 업데이트


def show_career_simulation(matcher: Any, profile: Dict[str, Any]):
    """경력 시뮬레이션"""
    st.markdown("### 📈 경력 성장 시뮬레이션")
    
    # 시뮬레이션 매개변수
    current_position = profile.get('current_position', 'Mid-level Developer')
    current_salary = profile.get('current_salary', 5000)
    target_years = profile.get('target_years', 3)
    learning_hours = profile.get('learning_hours', 10)
    
    # 성장 곡선 계산
    years = list(range(target_years + 1))
    
    # 연봉 성장 (연 10-15% 상승 가정)
    salary_growth = [current_salary]
    for year in range(1, target_years + 1):
        growth_rate = 0.10 + (learning_hours / 100)  # 학습 시간에 따른 보너스
        new_salary = salary_growth[-1] * (1 + growth_rate)
        salary_growth.append(int(new_salary))
    
    # 스킬 성장
    current_skill_count = len(profile.get('current_skills', []))
    skills_per_year = (learning_hours * 52) / 100  # 100시간당 1개 스킬 습득
    skill_growth = [current_skill_count]
    for year in range(1, target_years + 1):
        new_skills = skill_growth[-1] + skills_per_year
        skill_growth.append(int(new_skills))
    
    # 시각화
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("연봉 성장 예측", "스킬 성장 예측", 
                       "포지션 변화", "종합 성장 지표"),
        specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
               [{'type': 'bar'}, {'type': 'scatter'}]]
    )
    
    # 연봉 성장 그래프
    fig.add_trace(
        go.Scatter(
            x=years,
            y=salary_growth,
            mode='lines+markers',
            name='연봉',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10)
        ),
        row=1, col=1
    )
    
    # 스킬 성장 그래프
    fig.add_trace(
        go.Scatter(
            x=years,
            y=skill_growth,
            mode='lines+markers',
            name='스킬 수',
            line=dict(color='#38ef7d', width=3),
            marker=dict(size=10)
        ),
        row=1, col=2
    )
    
    # 레이아웃 설정
    fig.update_layout(
        height=800,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 성장 요약 - Streamlit 메트릭 사용
    st.markdown("### 📊 성장 예측 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        salary_increase = salary_growth[-1] - salary_growth[0]
        st.metric("예상 연봉 상승", f"+{salary_increase:,}만원", f"{(salary_increase/salary_growth[0]*100):.1f}% 증가")
    
    with col2:
        skill_increase = skill_growth[-1] - skill_growth[0]
        st.metric("새로운 스킬", f"+{skill_increase}개", f"총 {skill_growth[-1]}개 보유")
    
    with col3:
        experience_years = profile.get('experience_years', 3)
        total_exp = experience_years + target_years
        if total_exp < 5:
            final_position = "Mid-level Developer"
        elif total_exp < 8:
            final_position = "Senior Developer"
        else:
            final_position = "Tech Lead"
        st.metric("예상 포지션", final_position, f"{target_years}년 후")
    
    with col4:
        total_study_hours = learning_hours * 52 * target_years
        st.metric("총 학습 시간", f"{total_study_hours:,}시간", "투자 예정")
    
    # 개인화된 조언
    st.markdown("### 💡 AI 맞춤 조언")
    
    # 학습 시간 기반 조언
    if learning_hours < 5:
        st.warning("⏰ 주당 학습 시간을 늘리면 성장 속도가 크게 향상됩니다.")
    elif learning_hours > 20:
        st.info("🔥 높은 학습 의지가 인상적입니다! 번아웃에 주의하세요.")
    
    # 연봉 기반 조언
    if salary_increase / salary_growth[0] > 0.5:
        st.success("💰 예상 연봉 상승률이 매우 높습니다. 스킬 향상에 집중하세요.")
    
    # 포지션 기반 조언
    if final_position in ['Tech Lead', 'Architect']:
        st.info("👥 리더십과 커뮤니케이션 스킬도 함께 개발하세요.")