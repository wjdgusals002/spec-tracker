"""
직무 매칭 컴포넌트
"""
import streamlit as st
from typing import List, Dict, Any, Optional
import pandas as pd
from utils.helpers import UIHelpers, SessionManager

def show_job_matching_interface(matcher: Any):
    """직무 매칭 인터페이스"""
    st.markdown('<h2 class="section-title">🎯 AI 맞춤 직무 매칭</h2>', unsafe_allow_html=True)
    
    # 직무 타입 선택
    job_types = sorted(list(set(matcher.df['job_type'].dropna())))
    
    if not job_types:
        st.warning("직무 데이터가 없습니다.")
        return
    
    # 직무 선택 UI (개선된 카드 스타일)
    st.markdown("### 💼 관심 직무를 선택하세요")
    
    # 직무별 통계 미리 계산
    job_stats = {}
    for jt in job_types:
        jt_df = matcher.df[matcher.df['job_type'] == jt]
        job_stats[jt] = {
            'count': len(jt_df),
            'avg_salary': jt_df['estimated_salary'].mean(),
            'companies': jt_df['company'].nunique()
        }
    
    # 직무 카드 표시 (3열 그리드)
    cols = st.columns(3)
    selected_jobtype = st.session_state.get('selected_jobtype', job_types[0])
    
    for idx, jt in enumerate(job_types):
        with cols[idx % 3]:
            stats = job_stats[jt]
            is_selected = jt == selected_jobtype
            
            card_style = """
                background: linear-gradient(135deg, {bg_color});
                border: 2px solid {border_color};
                border-radius: 15px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
            """.format(
                bg_color="#667eea33, #764ba233" if is_selected else "#ffffff11, #ffffff22",
                border_color="#667eea" if is_selected else "transparent"
            )
            
            if st.button(
                f"**{jt}**\n\n"
                f"📋 {stats['count']}개 공고\n"
                f"💰 평균 {stats['avg_salary']:,.0f}만원\n"
                f"🏢 {stats['companies']}개 기업",
                key=f"jobtype_{jt}",
                use_container_width=True
            ):
                st.session_state.selected_jobtype = jt
                st.rerun()
    
    # 선택된 직무 표시
    st.markdown(f"<h4 style='color: #667eea; margin-top: 2rem;'>선택된 직무: {selected_jobtype}</h4>", 
                unsafe_allow_html=True)
    
    # 선택된 직무의 데이터 필터링
    filtered_df = matcher.df[matcher.df['job_type'] == selected_jobtype]
    
    # 해당 직무의 스킬 풀 생성
    all_skills = []
    for skills in filtered_df['llm_extracted_tech_skills']:
        all_skills.extend(skills)
    available_skills = sorted(list(set(all_skills)))
    
    # 주요 스킬 표시
    skill_freq = matcher.get_skill_freq_by_jobtype(top_n=5)
    if selected_jobtype in skill_freq:
        st.markdown("**🌟 이 직무의 핵심 스킬**")
        skills_html = ""
        for skill, count in skill_freq[selected_jobtype]:
            skills_html += UIHelpers.create_skill_badge(skill, "primary", count)
        st.markdown(f'<div style="margin: 1rem 0;">{skills_html}</div>', unsafe_allow_html=True)
    
    # 구분선
    st.markdown("---")
    
    # 프로필 입력 섹션
    st.markdown("### 👤 내 프로필 입력")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 스킬 선택 (개선된 UI)
        selected_skills = st.multiselect(
            "보유 기술 스택을 선택하세요",
            options=available_skills,
            default=st.session_state.get('user_skills', []),
            help=f"{selected_jobtype} 직무와 관련된 스킬들입니다"
        )
        
        # 스킬 빠른 추가 버튼
        st.markdown("**🚀 인기 스킬 빠르게 추가**")
        popular_skills = [s[0] for s in skill_freq.get(selected_jobtype, [])[:8]]
        
        cols = st.columns(4)
        for idx, skill in enumerate(popular_skills):
            with cols[idx % 4]:
                if skill not in selected_skills:
                    if st.button(f"+ {skill}", key=f"add_{skill}"):
                        selected_skills.append(skill)
                        st.session_state.user_skills = selected_skills
                        st.rerun()
        
        # 경력 설명
        spec_text = st.text_area(
            "경력 및 프로젝트 설명",
            value=st.session_state.get('spec_text', ''),
            height=150,
            placeholder="예: 3년차 백엔드 개발자로 대규모 트래픽 처리 경험이 있습니다. "
                       "Spring Boot와 MSA 아키텍처를 활용한 프로젝트를 주도했으며..."
        )
        
        # 고급 필터 (확장 가능한 섹션)
        with st.expander("🔧 고급 필터 설정", expanded=False):
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
                experience_years = st.slider(
                    "경력 연차",
                    0, 20, 
                    st.session_state.get('experience_years', 3),
                    help="본인의 경력 연차를 선택하세요"
                )
                
                preferred_locations = st.multiselect(
                    "선호 지역",
                    options=sorted(filtered_df['location'].unique().tolist()),
                    default=st.session_state.get('preferred_locations', [])
                )
                
                employment_type = st.selectbox(
                    "고용 형태",
                    ["전체", "정규직", "계약직", "인턴", "프리랜서"],
                    index=0
                )
            
            with filter_col2:
                min_salary = st.number_input(
                    "희망 최소 연봉 (만원)",
                    min_value=2000,
                    max_value=20000,
                    value=st.session_state.get('min_salary', 4000),
                    step=500
                )
                
                preferred_companies = st.multiselect(
                    "선호 기업",
                    options=sorted(filtered_df['company'].unique().tolist()),
                    default=st.session_state.get('preferred_companies', [])
                )
                
                company_size = st.selectbox(
                    "회사 규모",
                    ["전체", "대기업", "중견기업", "스타트업", "외국계"],
                    index=0
                )
    
    with col2:
        # 프로필 완성도 표시
        st.markdown("### 📊 프로필 완성도")
        
        # 완성도 계산
        completeness = 0
        if selected_skills:
            completeness += 40
        if spec_text and len(spec_text) > 50:
            completeness += 30
        if experience_years > 0:
            completeness += 10
        if preferred_locations:
            completeness += 10
        if min_salary > 0:
            completeness += 10
        
        # 프로그레스 바
        st.markdown(UIHelpers.create_progress_bar(
            completeness, 
            f"{completeness}% 완성"
        ), unsafe_allow_html=True)
        
        # 프로필 팁
        st.markdown("### 💡 프로필 작성 팁")
        tips = [
            "구체적인 프로젝트 경험을 작성하세요",
            "정량적 성과를 포함하면 좋습니다",
            "사용한 기술 스택을 명확히 하세요",
            "팀워크 경험도 중요합니다"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")
        
        # 스킬 추천 (현재 선택된 스킬 기반)
        if selected_skills:
            st.markdown("### 🎯 추천 보완 스킬")
            recommendations = matcher.get_skill_recommendations(selected_skills)[:5]
            
            for rec in recommendations:
                importance_color = {
                    "매우 높음": "#ff4b4b",
                    "높음": "#ffa500",
                    "보통": "#00cc66",
                    "낮음": "#0066cc"
                }
                
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 0.5rem; padding: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: white; font-weight: 600;">{rec['skill']}</span>
                        <span style="color: {importance_color.get(rec['importance'], '#666')}; font-size: 0.9rem;">
                            {rec['importance']}
                        </span>
                    </div>
                    <small style="color: #a0a0a0;">
                        {rec['category']} • {rec['frequency']}개 공고
                    </small>
                </div>
                """, unsafe_allow_html=True)
    
    # AI 매칭 실행 버튼
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            f"🚀 {selected_jobtype} 맞춤 직무 찾기",
            type="primary",
            use_container_width=True,
            disabled=not (selected_skills or spec_text)
        ):
            if selected_skills or spec_text:
                # 세션에 데이터 저장
                st.session_state.user_skills = selected_skills
                st.session_state.spec_text = spec_text
                st.session_state.experience_years = experience_years
                st.session_state.preferred_locations = preferred_locations
                st.session_state.preferred_companies = preferred_companies
                st.session_state.min_salary = min_salary
                
                with st.spinner("🤖 AI가 최적의 직무를 찾고 있습니다..."):
                    # 선호 조건 설정
                    preferences = {
                        'experience_years': experience_years,
                        'preferred_locations': preferred_locations,
                        'preferred_companies': preferred_companies,
                        'min_salary': min_salary,
                        'job_type': selected_jobtype,
                        'employment_type': employment_type,
                        'company_size': company_size
                    }
                    
                    # AI 매칭 실행
                    job_matches = matcher.calculate_advanced_match(
                        selected_skills, spec_text, preferences
                    )
                    
                    # 선택된 직무 타입으로 필터링
                    job_matches = [
                        m for m in job_matches 
                        if matcher.df.loc[matcher.df['job_id'] == m['job_id'], 'job_type'].values[0] == selected_jobtype
                    ]
                    
                    # 결과 저장
                    st.session_state.job_matches = job_matches
                    st.session_state.show_results = True
                    
                    # 검색 이력 저장
                    SessionManager.save_user_action('search', {
                        'skills': selected_skills,
                        'job_type': selected_jobtype,
                        'timestamp': pd.Timestamp.now()
                    })
            else:
                st.warning("⚠️ 최소 하나의 스킬을 선택하거나 경력 설명을 입력해주세요!")
    
    # 매칭 결과 표시
    if st.session_state.get('show_results') and 'job_matches' in st.session_state:
        show_matching_results(matcher, st.session_state.job_matches)

def show_matching_results(matcher: Any, job_matches: List[Dict[str, Any]]):
    """매칭 결과 표시"""
    st.markdown("---")
    st.markdown('<h3 class="section-title">🎯 AI 매칭 결과</h3>', unsafe_allow_html=True)
    
    if not job_matches:
        st.info("😅 조건에 맞는 직무를 찾지 못했습니다. 필터를 조정해보세요!")
        return
    
    # 결과 필터링 옵션
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        min_match = st.slider("최소 매칭률", 0, 100, 50, key="min_match_filter")
    
    with col2:
        sort_options = {
            "매칭률 높은순": "match_percentage",
            "최신순": "created_date",
            "연봉 높은순": "estimated_salary",
            "스킬 매치순": "skill_match_score"
        }
        sort_by = st.selectbox("정렬 기준", list(sort_options.keys()))
    
    with col3:
        view_type = st.radio("보기 방식", ["카드", "테이블", "상세"], horizontal=True)
    
    with col4:
        show_saved_only = st.checkbox("저장한 공고만")
    
    # 필터링 적용
    filtered_matches = [m for m in job_matches if m['match_percentage'] >= min_match]
    
    if show_saved_only:
        saved_jobs = st.session_state.user_history.get('saved_jobs', [])
        filtered_matches = [m for m in filtered_matches if m['job_id'] in saved_jobs]
    
    # 정렬
    sort_field = sort_options[sort_by]
    reverse = sort_by != "최신순"  # 날짜는 내림차순
    filtered_matches.sort(key=lambda x: x.get(sort_field, 0), reverse=reverse)
    
    # 결과 요약
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #667eea22, #764ba222);">
        <p style="margin: 0;">
            총 <b style="color: #667eea;">{len(filtered_matches)}개</b>의 매칭 직무를 찾았습니다. 
            평균 매칭률: <b style="color: #38ef7d;">{sum(m['match_percentage'] for m in filtered_matches) / len(filtered_matches):.1f}%</b>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 결과 표시
    if view_type == "카드":
        show_results_as_cards(matcher, filtered_matches)
    elif view_type == "테이블":
        show_results_as_table(filtered_matches)
    else:  # 상세
        show_results_detailed(matcher, filtered_matches)

def show_results_as_cards(matcher: Any, matches: List[Dict[str, Any]]):
    """카드 형식으로 결과 표시"""
    for idx, match in enumerate(matches[:10]):
        # 매칭률에 따른 색상과 상태
        if match['match_percentage'] >= 80:
            status = "🟢 완벽 매칭"
            badge_color = "success"
            border_color = "#38ef7d"
        elif match['match_percentage'] >= 60:
            status = "🔵 우수 매칭"
            badge_color = "primary"
            border_color = "#667eea"
        else:
            status = "🟡 가능 매칭"
            badge_color = "warning"
            border_color = "#f7b733"
            
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                have_skills = match['matching_skills'][:5]
                need_skills = match['missing_skills'][:3]
                have_html = ''
                need_html = ''
                if have_skills:
                    have_html = (
                        f"<div style='margin-top:0.7rem;'>"
                        f"<span style='color: #38ef7d; font-weight: 600;'>✅ 보유 스킬:</span> "
                        f"{' '.join([UIHelpers.create_skill_badge(s, 'success') for s in have_skills])}"
                        f"</div>"
                    )
                if need_skills:
                    need_html = (
                        f"<div style='margin-top:0.5rem;'>"
                        f"<span style='color: #fc4a1a; font-weight: 600;'>📚 필요 스킬:</span> "
                        f"{' '.join([UIHelpers.create_skill_badge(s, 'danger') for s in need_skills])}"
                        f"</div>"
                    )
                if have_html or need_html:
                    st.markdown(
                        f"""
                        <div class="metric-card" style="border-left: 4px solid {border_color};">
                            <h4 style="color: white;">{match['title']}
                                <span class="skill-badge skill-badge-{badge_color}">{status}</span>
                            </h4>
                            <p style="color: #a0a0a0;">
                                {match['company']} • {match['location']} • {match['experience']}
                            </p>
                            <p style="color: #ffa500;">
                                💰 예상 연봉: {match.get('estimated_salary', 0):,}만원
                            </p>
                            {have_html}
                            {need_html}
                        </div>
                        """, unsafe_allow_html=True
                    )
                else:
                    # 둘 다 없을 때는 아무것도 출력하지 않음
                    pass


            
            with col2:
                # 저장 버튼
                saved = match['job_id'] in st.session_state.user_history.get('saved_jobs', [])
                if st.button(
                    "✅ 저장됨" if saved else "💾 저장",
                    key=f"save_{match['job_id']}_{idx}",
                    use_container_width=True,
                    type="secondary" if saved else "primary"
                ):
                    if not saved:
                        SessionManager.save_user_action('save', {'job_id': match['job_id']})
                        st.rerun()
            
            with col3:
                # 상세보기 버튼
                if st.button(
                    "📋 상세",
                    key=f"detail_{match['job_id']}_{idx}",
                    use_container_width=True
                ):
                    st.session_state.selected_job = match
                    st.session_state.show_job_detail = True
                    st.rerun()
        
        # 구분선 (마지막 항목 제외)
        if idx < len(matches) - 1:
            st.markdown("<hr style='margin: 1rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # 상세 정보 모달 (선택된 경우)
    if st.session_state.get('show_job_detail') and st.session_state.get('selected_job'):
        show_job_detail_modal(matcher, st.session_state.selected_job)

def show_results_as_table(matches: List[Dict[str, Any]]):
    table_data = []
    for match in matches[:20]:
        # ★★ 순수 텍스트만 넣는다! (HTML, 이모지, <span> 등 없음)
        table_data.append({
            '직무명': match['title'],
            '회사': match['company'],
            '위치': match['location'],
            '경력': match['experience'],
            '매칭률': f"{match['match_percentage']}%",
            '예상연봉': f"{match.get('estimated_salary', 0):,}만원",
            '주요스킬': ', '.join(match['required_skills'][:3]),    # HTML X, 텍스트 O
            '등록일': str(match['created_date'])
        })
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, height=600)

def show_results_detailed(matcher: Any, matches: List[Dict[str, Any]]):
    """상세 뷰로 결과 표시"""
    # 한 번에 하나씩 자세히 표시
    if 'current_detail_index' not in st.session_state:
        st.session_state.current_detail_index = 0
    
    current_idx = st.session_state.current_detail_index
    
    if current_idx < len(matches):
        match = matches[current_idx]
        job_detail = matcher.df[matcher.df['job_id'] == match['job_id']].iloc[0]
        
        # 네비게이션
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if st.button("⬅️ 이전", disabled=current_idx == 0):
                st.session_state.current_detail_index -= 1
                st.rerun()
        
        with col2:
            st.markdown(f"<center>{current_idx + 1} / {len(matches)}</center>", unsafe_allow_html=True)
        
        with col3:
            if st.button("다음 ➡️", disabled=current_idx >= len(matches) - 1):
                st.session_state.current_detail_index += 1
                st.rerun()
        
        # 상세 정보 표시
        st.markdown(f"""
            <div class="metric-card" style="margin-top: 2rem; padding: 2rem;">
                <h2 style="color: #667eea; margin-bottom: 1rem;">{job_detail['title']}</h2>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                    <div>
                        <p><b>🏢 회사:</b> {job_detail['company']}</p>
                        <p><b>📍 위치:</b> {job_detail['location']}</p>
                        <p><b>💼 경력:</b> {job_detail['experience']}</p>
                    </div>
                    <div>
                        <p><b>💰 예상 연봉:</b> {match.get('estimated_salary', 0):,}만원</p>
                        <p><b>📅 등록일:</b> {job_detail['created_date']}</p>
                        <p><b>🎯 매칭률:</b> {match['match_percentage']}%</p>
                    </div>
                </div>
                <hr style="margin: 1.5rem 0;">
                <h4 style="color: #667eea;">📝 직무 설명</h4>
                <p style="color: #e0e0e0; line-height: 1.6;">{job_detail.get('description', '설명이 없습니다.')}</p>
                <h4 style="color: #667eea; margin-top: 1.5rem;">📋 자격 요건</h4>
                <p style="color: #e0e0e0; line-height: 1.6;">{job_detail.get('requirements', '요구사항이 없습니다.')}</p>
                <h4 style="color: #667eea; margin-top: 1.5rem;">🛠️ 필요 기술</h4>
                <div style="margin-top: 0.5rem;">
                    {' '.join([UIHelpers.create_skill_badge(s, 'primary') for s in job_detail['llm_extracted_tech_skills']])}
                </div>
                <h4 style="color: #667eea; margin-top: 1.5rem;">📊 매칭 분석</h4>
                <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px;">
                    <p>✅ <b>보유 스킬:</b> {', '.join(match['matching_skills'])}</p>
                    <p>❌ <b>부족한 스킬:</b> {', '.join(match['missing_skills'])}</p>
                    <p>📈 <b>스킬 매치율:</b> {match['skill_match_score']*100:.1f}%</p>
                    <p>👔 <b>경력 적합도:</b> {match['experience_fit']*100:.1f}%</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 액션 버튼
        col1, col2, col3 = st.columns(3)
        
        with col1:
            saved = match['job_id'] in st.session_state.user_history.get('saved_jobs', [])
            if st.button(
                "✅ 저장됨" if saved else "💾 저장하기",
                use_container_width=True,
                type="secondary" if saved else "primary"
            ):
                if not saved:
                    SessionManager.save_user_action('save', {'job_id': match['job_id']})
                    st.success("저장되었습니다!")
        
        with col2:
            if st.button("📮 지원하기", use_container_width=True, type="primary"):
                SessionManager.save_user_action('apply', {'job_id': match['job_id']})
                st.success("지원 정보가 저장되었습니다!")
        
        with col3:
            if st.button("🔗 원본 공고 보기", use_container_width=True):
                st.info("외부 링크 기능은 준비 중입니다.")

def show_job_detail_modal(matcher: Any, job: Dict[str, Any]):
    job_detail = matcher.df[matcher.df['job_id'] == job['job_id']].iloc[0]
    st.markdown(f"""
        <div style="background: rgba(0,0,0,0.8); padding:2rem; border-radius:15px; margin-top:1rem;">
            <h3 style="color: #667eea;">{job_detail['title']}</h3>
            <div>
                <h4 style="color: white;">🛠️ 필요 기술</h4>
                {' '.join([UIHelpers.create_skill_badge(s, 'primary') for s in job_detail['llm_extracted_tech_skills']])}
            </div>
        </div>
        """, unsafe_allow_html=True)


