"""
유틸리티 함수들
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any, Optional
import numpy as np

class DataValidator:
    """데이터 검증 클래스"""
    
    @staticmethod
    def validate_skills(skills: List[str]) -> List[str]:
        """스킬 데이터 검증 및 정제"""
        if not skills:
            return []
        
        # 중복 제거 및 정제
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            if skill and len(skill) > 1:  # 너무 짧은 스킬명 제외
                cleaned_skills.append(skill)
        
        return list(set(cleaned_skills))
    
    @staticmethod
    def validate_date(date_str: str) -> Optional[datetime]:
        """날짜 문자열 검증"""
        try:
            return pd.to_datetime(date_str)
        except:
            return None

class UIHelpers:
    """UI 관련 헬퍼 함수들"""
    
    @staticmethod
    def create_metric_card(title: str, value: Any, subtitle: str = "", 
                          icon: str = "", color: str = "#667eea") -> str:
        """메트릭 카드 HTML 생성"""
        return f"""
        <div class="metric-card fade-in">
            <h3 style="color: {color};">{icon}</h3>
            <h2 style="color: white;">{value}</h2>
            <p style="color: #a0a0a0;">{title}</p>
            {f'<small style="color: #6c757d;">{subtitle}</small>' if subtitle else ''}
        </div>
        """
    
    @staticmethod
    def create_skill_badge(skill: str, badge_type: str = "primary", 
                          count: Optional[int] = None) -> str:
        """스킬 배지 HTML 생성"""
        count_text = f' <span style="opacity: 0.8;">({count})</span>' if count else ''
        return f'<span class="skill-badge skill-badge-{badge_type}">{skill}{count_text}</span>'
    
    @staticmethod
    def create_progress_bar(percentage: float, text: str = "") -> str:
        display_text = text if text else f"{percentage}%"
        html = f"""
        <div class="progress-bar" style="background: #393e4b; border-radius: 10px; height: 28px; width: 100%; margin: 12px 0; overflow: hidden;">
            <div class="progress-fill" style="background: linear-gradient(90deg, #6a82fb, #fc5c7d); width: {percentage}%; height: 100%; border-radius: 10px 0 0 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 1.15rem;">
                {display_text}
            </div>
        </div>
        """
        print("progress bar html:", html)  # 이거 넣어봐!
        return html



class SessionManager:
    """세션 상태 관리"""
    
    @staticmethod
    def init_session_state():
        """세션 상태 초기화"""
        defaults = {
            'user_history': {
                'viewed_jobs': [],
                'saved_jobs': [],
                'applied_jobs': [],
                'skill_searches': [],
                'feedback': {}
            },
            'filters': {
                'job_type': None,
                'location': None,
                'experience': None,
                'skills': []
            },
            'current_tab': 0,
            'theme': 'dark'
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def save_user_action(action_type: str, data: Dict[str, Any]):
        """사용자 액션 저장"""
        if action_type == 'view':
            if data['job_id'] not in st.session_state.user_history['viewed_jobs']:
                st.session_state.user_history['viewed_jobs'].append(data['job_id'])
        elif action_type == 'save':
            if data['job_id'] not in st.session_state.user_history['saved_jobs']:
                st.session_state.user_history['saved_jobs'].append(data['job_id'])
                st.success("✅ 저장되었습니다!")
        elif action_type == 'apply':
            if data['job_id'] not in st.session_state.user_history['applied_jobs']:
                st.session_state.user_history['applied_jobs'].append(data['job_id'])
                st.success("📮 지원 완료!")
