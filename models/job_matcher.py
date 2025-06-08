"""
직무 매칭 핵심 모델 (최적화 버전)
"""
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import timedelta
import pandas as pd
import numpy as np
from collections import Counter
from sentence_transformers import SentenceTransformer, util
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
import os

class AdvancedJobMatcher:
    """최적화된 직무 매칭 시스템"""

    def __init__(self, db_path: str = 'data/job_data.db'):
        self.db_path = db_path
        self._validate_database()
        self._initialize_data()
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/opt/venv/model_cache'
        # 임베딩 모델 및 job_vectors 반드시 여기서 직접 초기화 (Streamlit 캐시 안 씀)
        self.embedder = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
        self._create_job_vectors()
        # 나머지 속성들 초기화
        self.skill_clusters = self._create_skill_clusters()
        self.career_paths = self._create_career_paths()

    def _validate_database(self):
        """데이터베이스 유효성 검사"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"데이터베이스를 찾을 수 없습니다: {self.db_path}")

    def _initialize_data(self):
        """데이터 초기화 및 전처리"""
        self.conn = sqlite3.connect(self.db_path)
        self.df = pd.read_sql("SELECT * FROM jobs", self.conn)

        # JSON 파싱
        self.df['skills'] = self.df['skills'].apply(
            lambda x: json.loads(x) if pd.notna(x) else []
        )
        self.df['llm_extracted_tech_skills'] = self.df['llm_extracted_tech_skills'].apply(
            lambda x: json.loads(x) if pd.notna(x) else []
        )

        # 메타데이터 생성
        self._create_metadata()

    def _create_metadata(self):
        """메타데이터 생성"""
        self.df['skill_count'] = self.df['llm_extracted_tech_skills'].apply(len)

        base_date = pd.Timestamp.now()
        weights = np.exp(-np.linspace(0, 3, 90))
        weights = weights / weights.sum()
        random_days = np.random.choice(range(90), size=len(self.df), p=weights)

        self.df['created_date'] = [
            base_date - pd.Timedelta(days=int(d)) for d in random_days
        ]
        self.df['created_date'] = pd.to_datetime(self.df['created_date']).dt.date

        # 급여 정보 추정 (경력 기반)
        self.df['estimated_salary'] = self.df['years'].apply(
            lambda x: 3000 + (x * 500) + np.random.randint(-500, 500)
        )

    def _create_job_vectors(self):
        """임베딩 벡터 생성"""
        texts = self.df['description'].fillna('') + ' ' + self.df['requirements'].fillna('')
        self.job_vectors = self.embedder.encode(list(texts), convert_to_tensor=True)

    def _create_skill_clusters(self) -> Dict[str, List[str]]:
        """스킬 클러스터 생성"""
        return {
            'Frontend': [
                'React', 'Vue', 'Angular', 'JavaScript', 'TypeScript', 
                'HTML', 'CSS', 'Sass', 'webpack', 'Next.js', 'Nuxt.js'
            ],
            'Backend': [
                'Python', 'Java', 'Node.js', 'Django', 'Spring', 
                'Express', 'FastAPI', 'Flask', 'Ruby on Rails', 'PHP'
            ],
            'Database': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 
                'SQLite', 'Elasticsearch', 'Cassandra', 'DynamoDB'
            ],
            'DevOps': [
                'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 
                'Jenkins', 'GitLab CI', 'Terraform', 'Ansible', 'CircleCI'
            ],
            'Data Science': [
                'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 
                'Keras', 'R', 'Jupyter', 'Spark', 'Hadoop'
            ],
            'Mobile': [
                'React Native', 'Flutter', 'Swift', 'Kotlin', 
                'Android', 'iOS', 'Xamarin', 'Ionic'
            ],
            'Security': [
                'OWASP', 'Penetration Testing', 'Cryptography', 
                'Network Security', 'SSL/TLS', 'OAuth', 'JWT'
            ],
            'Soft Skills': [
                'Leadership', 'Communication', 'Problem Solving', 
                'Team Work', 'Agile', 'Scrum', 'Project Management'
            ]
        }

    def _create_career_paths(self) -> Dict[str, Dict[str, Any]]:
        """경력 경로 정의"""
        return {
            'Junior Developer': {
                'next': ['Mid-level Developer', 'Specialized Developer'],
                'skills': ['Git', 'Basic Programming', 'Problem Solving', 'Communication'],
                'years': 0,
                'salary_range': (3000, 4500)
            },
            'Mid-level Developer': {
                'next': ['Senior Developer', 'Tech Lead', 'Architect'],
                'skills': ['Advanced Programming', 'System Design', 'Mentoring', 'Code Review'],
                'years': 3,
                'salary_range': (4500, 7000)
            },
            'Senior Developer': {
                'next': ['Tech Lead', 'Architect', 'Engineering Manager'],
                'skills': ['Architecture', 'Leadership', 'Strategic Thinking', 'Performance Optimization'],
                'years': 5,
                'salary_range': (7000, 10000)
            },
            'Tech Lead': {
                'next': ['Engineering Manager', 'CTO', 'Principal Engineer'],
                'skills': ['Team Management', 'Technical Strategy', 'Stakeholder Management', 'Mentoring'],
                'years': 7,
                'salary_range': (9000, 13000)
            },
            'Architect': {
                'next': ['Principal Architect', 'CTO', 'VP of Engineering'],
                'skills': ['System Architecture', 'Cloud Architecture', 'Microservices', 'Technical Leadership'],
                'years': 8,
                'salary_range': (10000, 15000)
            }
        }
    
    def calculate_advanced_match(self, user_skills: List[str], 
                               spec_text: str, 
                               preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """개선된 매칭 알고리즘"""
        # 사용자 프로필 벡터화
        user_text = ' '.join(user_skills) + ' ' + spec_text
        user_vector = self.embedder.encode(user_text, convert_to_tensor=True)
        
        # 코사인 유사도 계산
        similarities = util.cos_sim(user_vector, self.job_vectors)[0].cpu().numpy()
        
        # 결과 데이터프레임 생성
        result_df = self.df.copy()
        result_df['similarity'] = similarities
        
        # 다양한 매칭 점수 계산
        result_df['skill_match_score'] = result_df['llm_extracted_tech_skills'].apply(
            lambda job_skills: self._calculate_skill_match(user_skills, job_skills)
        )
        
        # 경력 적합도 (개선된 알고리즘)
        if preferences and 'experience_years' in preferences:
            result_df['experience_fit'] = result_df['years'].apply(
                lambda y: self._calculate_experience_fit(y, preferences['experience_years'])
            )
        else:
            result_df['experience_fit'] = 1
        
        # 최신성 점수 (가중치 조정)
        result_df['freshness_score'] = self._calculate_freshness_score(result_df['created_date'])
        
        # 급여 적합도
        if preferences and 'min_salary' in preferences:
            result_df['salary_fit'] = result_df['estimated_salary'].apply(
                lambda s: 1 if s >= preferences['min_salary'] else s / preferences['min_salary']
            )
        else:
            result_df['salary_fit'] = 1
        
        # 회사 규모/인기도 점수 (가상)
        company_scores = self._get_company_scores()
        result_df['company_score'] = result_df['company'].map(company_scores).fillna(0.5)
        
        # 최종 점수 계산 (가중치 조정)
        weights = {
            'similarity': 0.35,
            'skill_match_score': 0.25,
            'experience_fit': 0.15,
            'freshness_score': 0.10,
            'salary_fit': 0.10,
            'company_score': 0.05
        }
        
        result_df['final_score'] = sum(
            result_df[col] * weight for col, weight in weights.items()
        )
        
        # 선호 조건 부스팅
        if preferences:
            result_df = self._apply_preference_boosting(result_df, preferences)
        
        # 정렬 및 정규화
        sorted_df = result_df.sort_values('final_score', ascending=False)
        
        # 상위 결과 포맷팅
        return self._format_job_matches(sorted_df, user_skills, preferences)
    
    def _calculate_skill_match(self, user_skills: List[str], job_skills: List[str]) -> float:
        """개선된 스킬 매칭 점수"""
        if not job_skills:
            return 0
        
        user_skills_set = set(s.lower() for s in user_skills)
        job_skills_set = set(s.lower() for s in job_skills)
        
        # 정확한 매치
        exact_matches = user_skills_set.intersection(job_skills_set)
        
        # 부분 매치 (예: React와 React.js)
        partial_matches = 0
        for user_skill in user_skills_set:
            for job_skill in job_skills_set:
                if user_skill in job_skill or job_skill in user_skill:
                    partial_matches += 0.5
        
        total_matches = len(exact_matches) + partial_matches
        return min(total_matches / len(job_skills_set), 1.0)
    
    def _calculate_experience_fit(self, job_years: int, user_years: int) -> float:
        """경력 적합도 계산 (개선)"""
        diff = abs(job_years - user_years)
        
        # 차이가 작을수록 높은 점수
        if diff == 0:
            return 1.0
        elif diff <= 1:
            return 0.9
        elif diff <= 2:
            return 0.7
        elif diff <= 3:
            return 0.5
        else:
            return max(0.2, 1 - (diff / 10))
    
    def _calculate_freshness_score(self, dates: pd.Series) -> np.ndarray:
        """최신성 점수 계산"""
        current_date = pd.Timestamp.now().date()
        days_old = [(current_date - date).days for date in dates]
        
        # 30일 이내: 1.0, 90일까지 선형 감소
        scores = []
        for days in days_old:
            if days <= 30:
                scores.append(1.0)
            elif days <= 90:
                scores.append(1 - (days - 30) / 60)
            else:
                scores.append(0.1)
        
        return np.array(scores)
    
    def _get_company_scores(self) -> Dict[str, float]:
        """회사 점수 (인기도/규모 기반)"""
        # 실제로는 DB나 API에서 가져올 데이터
        company_counts = self.df['company'].value_counts()
        max_count = company_counts.max()
        
        return {
            company: 0.5 + (count / max_count) * 0.5
            for company, count in company_counts.items()
        }
    
    def _apply_preference_boosting(self, df: pd.DataFrame, 
                                  preferences: Dict[str, Any]) -> pd.DataFrame:
        """선호 조건에 따른 점수 부스팅"""
        df = df.copy()
        
        # 선호 회사
        if 'preferred_companies' in preferences and preferences['preferred_companies']:
            df.loc[df['company'].isin(preferences['preferred_companies']), 'final_score'] *= 1.2
        
        # 선호 지역
        if 'preferred_locations' in preferences and preferences['preferred_locations']:
            df.loc[df['location'].isin(preferences['preferred_locations']), 'final_score'] *= 1.1
        
        # 직무 타입
        if 'job_type' in preferences and preferences['job_type']:
            df.loc[df['job_type'] == preferences['job_type'], 'final_score'] *= 1.15
        
        return df
    
    def _format_job_matches(self, sorted_df: pd.DataFrame, 
                           user_skills: List[str], 
                           preferences: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """매칭 결과 포맷팅"""
        # 점수 정규화
        scaler = MinMaxScaler()
        if len(sorted_df) > 1:
            sorted_df['normalized_score'] = scaler.fit_transform(sorted_df[['final_score']])
        else:
            sorted_df['normalized_score'] = sorted_df['final_score']
        
        job_matches = []
        for _, row in sorted_df.head(20).iterrows():
            match_percentage = int(row['normalized_score'] * 100)
            
            job_match = {
                'job_id': row['job_id'],
                'title': row['title'],
                'company': row['company'],
                'location': row['location'],
                'experience': row['experience'],
                'match_percentage': match_percentage,
                'similarity_score': round(row['similarity'], 3),
                'skill_match_score': round(row['skill_match_score'], 3),
                'experience_fit': round(row['experience_fit'], 3),
                'freshness_score': round(row['freshness_score'], 3),
                'salary_fit': round(row.get('salary_fit', 1), 3),
                'required_skills': row['llm_extracted_tech_skills'],
                'missing_skills': self._get_missing_skills(user_skills, row['llm_extracted_tech_skills']),
                'matching_skills': self._get_matching_skills(user_skills, row['llm_extracted_tech_skills']),
                'created_date': row['created_date'],
                'skill_count': row['skill_count'],
                'estimated_salary': row.get('estimated_salary', 0),
                'job_type': row.get('job_type', ''),
                'description': row.get('description', ''),
                'requirements': row.get('requirements', '')
            }
            job_matches.append(job_match)
        
        return job_matches
    
    def _get_missing_skills(self, user_skills: List[str], job_skills: List[str]) -> List[str]:
        """부족한 스킬 찾기"""
        user_skills_lower = set(s.lower() for s in user_skills)
        return [s for s in job_skills if s.lower() not in user_skills_lower]
    
    def _get_matching_skills(self, user_skills: List[str], job_skills: List[str]) -> List[str]:
        """매칭되는 스킬 찾기"""
        user_skills_lower = set(s.lower() for s in user_skills)
        return [s for s in job_skills if s.lower() in user_skills_lower]
    
    def get_skill_recommendations(self, current_skills: List[str], 
                                top_n: int = 10) -> List[Dict[str, Any]]:
        """개선된 스킬 추천"""
        # 현재 스킬과 함께 나타나는 스킬 분석
        skill_pairs = []
        for skills in self.df['llm_extracted_tech_skills']:
            if any(s in skills for s in current_skills):
                skill_pairs.extend(skills)
        
        # 현재 스킬 제외
        skill_counter = Counter(skill_pairs)
        for skill in current_skills:
            skill_counter.pop(skill, None)
        
        # 추천 생성
        recommendations = []
        for skill, count in skill_counter.most_common(top_n):
            # 카테고리 찾기
            category = self._find_skill_category(skill)
            
            # 중요도 계산
            importance = self._calculate_skill_importance(skill)
            
            # 학습 난이도 추정
            difficulty = self._estimate_learning_difficulty(skill)
            
            # 트렌드 분석
            trend = self._analyze_skill_trend(skill)
            
            recommendations.append({
                'skill': skill,
                'frequency': count,
                'category': category,
                'importance': importance,
                'difficulty': difficulty,
                'trend': trend,
                'related_skills': self._get_related_skills(skill)
            })
        
        return recommendations
    
    def _find_skill_category(self, skill: str) -> str:
        """스킬 카테고리 찾기"""
        for category, skills_list in self.skill_clusters.items():
            if any(s.lower() in skill.lower() or skill.lower() in s.lower() 
                  for s in skills_list):
                return category
        return 'General'
    
    def _calculate_skill_importance(self, skill: str) -> str:
        """스킬 중요도 계산"""
        total_jobs = len(self.df)
        jobs_with_skill = sum(1 for skills in self.df['llm_extracted_tech_skills'] 
                             if skill in skills)
        
        ratio = jobs_with_skill / total_jobs if total_jobs > 0 else 0
        
        if ratio > 0.3:
            return "매우 높음"
        elif ratio > 0.15:
            return "높음"
        elif ratio > 0.05:
            return "보통"
        else:
            return "낮음"
    
    def _estimate_learning_difficulty(self, skill: str) -> str:
        """학습 난이도 추정"""
        # 실제로는 더 복잡한 로직이 필요
        difficult_skills = {'Kubernetes', 'TensorFlow', 'React Native', 'Spring', 'Django'}
        medium_skills = {'React', 'Node.js', 'Docker', 'MySQL', 'Python'}
        
        if skill in difficult_skills:
            return "어려움"
        elif skill in medium_skills:
            return "보통"
        else:
            return "쉬움"
    
    def _analyze_skill_trend(self, skill: str) -> str:
        """스킬 트렌드 분석"""
        # 최근 30일 vs 이전 60일 비교
        current_date = pd.Timestamp.now().date()
        recent_date = current_date - timedelta(days=30)
        older_date = current_date - timedelta(days=90)
        
        recent_jobs = self.df[self.df['created_date'] >= recent_date]
        older_jobs = self.df[(self.df['created_date'] >= older_date) & 
                            (self.df['created_date'] < recent_date)]
        
        recent_count = sum(1 for skills in recent_jobs['llm_extracted_tech_skills'] 
                          if skill in skills)
        older_count = sum(1 for skills in older_jobs['llm_extracted_tech_skills'] 
                         if skill in skills)
        
        if recent_count > older_count * 1.2:
            return "상승"
        elif recent_count < older_count * 0.8:
            return "하락"
        else:
            return "유지"
    
    def _get_related_skills(self, skill: str, top_n: int = 3) -> List[str]:
        """관련 스킬 찾기"""
        related = []
        for skills in self.df['llm_extracted_tech_skills']:
            if skill in skills:
                related.extend([s for s in skills if s != skill])
        
        if related:
            return [s for s, _ in Counter(related).most_common(top_n)]
        return []
    
    def get_career_path_analysis(self, current_skills: List[str], 
                               experience_years: int) -> Dict[str, Any]:
        """경력 경로 분석"""
        # 현재 레벨 결정
        current_level = self._determine_career_level(experience_years)
        current_path = self.career_paths.get(current_level, {})
        
        # 다음 포지션 분석
        next_positions = current_path.get('next', [])
        skill_gaps = []
        
        for next_pos in next_positions:
            next_path = self.career_paths.get(next_pos, {})
            next_skills = next_path.get('skills', [])
            
            missing_skills = [s for s in next_skills if s not in current_skills]
            matching_skills = [s for s in next_skills if s in current_skills]
            
            readiness = len(matching_skills) / len(next_skills) if next_skills else 0
            
            skill_gaps.append({
                'position': next_pos,
                'missing_skills': missing_skills,
                'matching_skills': matching_skills,
                'readiness': readiness,
                'salary_range': next_path.get('salary_range', (0, 0)),
                'required_years': next_path.get('years', 0)
            })
        
        # 추천 액션
        recommendations = self._generate_career_recommendations(
            current_level, skill_gaps, current_skills
        )
        
        return {
            'current_level': current_level,
            'next_positions': next_positions,
            'skill_gaps': sorted(skill_gaps, key=lambda x: x['readiness'], reverse=True),
            'years_to_next': max(0, current_path.get('years', 0) + 2 - experience_years),
            'recommendations': recommendations,
            'salary_range': current_path.get('salary_range', (0, 0))
        }
    
    def _determine_career_level(self, experience_years: int) -> str:
        """경력 레벨 결정"""
        if experience_years < 2:
            return 'Junior Developer'
        elif experience_years < 5:
            return 'Mid-level Developer'
        elif experience_years < 8:
            return 'Senior Developer'
        elif experience_years < 12:
            return 'Tech Lead'
        else:
            return 'Architect'
    
    def _generate_career_recommendations(self, current_level: str, 
                                       skill_gaps: List[Dict[str, Any]], 
                                       current_skills: List[str]) -> List[str]:
        """경력 개발 추천 생성"""
        recommendations = []
        
        # 가장 준비된 다음 포지션
        if skill_gaps:
            best_next = max(skill_gaps, key=lambda x: x['readiness'])
            if best_next['readiness'] > 0.7:
                recommendations.append(
                    f"✅ {best_next['position']} 포지션으로 전환 준비가 잘 되어 있습니다!"
                )
            else:
                recommendations.append(
                    f"📚 {best_next['position']}을 위해 {', '.join(best_next['missing_skills'][:3])} 스킬을 보강하세요."
                )
        
        # 스킬 다양성
        skill_categories = set()
        for skill in current_skills:
            skill_categories.add(self._find_skill_category(skill))
        
        if len(skill_categories) < 3:
            recommendations.append("🎯 다양한 카테고리의 스킬을 학습하여 T자형 인재가 되세요.")
        
        return recommendations
    
    def get_market_insights(self) -> Dict[str, Any]:
        """시장 인사이트 생성"""
        insights = {}
        
        # 전체 스킬 수요
        all_skills = []
        for skills in self.df['llm_extracted_tech_skills']:
            all_skills.extend(skills)
        
        skill_demand = Counter(all_skills)
        insights['top_skills'] = skill_demand.most_common(15)
        
        # 직무별 평균 스킬
        insights['avg_skills_by_job'] = self.df.groupby('job_type')['skill_count'].agg(['mean', 'std']).to_dict()
        
        # 경력 분포
        insights['experience_distribution'] = self.df['years'].value_counts().to_dict()
        
        # 지역별 분포
        insights['jobs_by_location'] = self.df['location'].value_counts().head(10).to_dict()
        
        # 회사별 분포
        insights['jobs_by_company'] = self.df['company'].value_counts().head(10).to_dict()
        
        # 트렌딩 스킬 분석
        insights['trending_skills'] = self._analyze_trending_skills()
        
        # 급여 통계
        insights['salary_stats'] = {
            'mean': self.df['estimated_salary'].mean(),
            'median': self.df['estimated_salary'].median(),
            'by_experience': self.df.groupby('years')['estimated_salary'].mean().to_dict()
        }
        
        # 스킬 조합 분석
        insights['popular_skill_combinations'] = self._analyze_skill_combinations()
        
        return insights
    
    def _analyze_trending_skills(self) -> List[Dict[str, Any]]:
        """트렌딩 스킬 분석"""
        current_date = pd.Timestamp.now().date()
        recent_date = current_date - timedelta(days=30)
        older_date = current_date - timedelta(days=90)
        
        recent_jobs = self.df[self.df['created_date'] >= recent_date]
        older_jobs = self.df[(self.df['created_date'] >= older_date) & 
                            (self.df['created_date'] < recent_date)]
        
        recent_skills = []
        older_skills = []
        
        for skills in recent_jobs['llm_extracted_tech_skills']:
            recent_skills.extend(skills)
        for skills in older_jobs['llm_extracted_tech_skills']:
            older_skills.extend(skills)
        
        recent_counter = Counter(recent_skills)
        older_counter = Counter(older_skills)
        
        trending = []
        all_skills = set(recent_skills + older_skills)
        
        for skill in all_skills:
            recent_ratio = recent_counter.get(skill, 0) / len(recent_skills) if recent_skills else 0
            older_ratio = older_counter.get(skill, 0) / len(older_skills) if older_skills else 0
            
            if recent_ratio > older_ratio * 1.2 and recent_counter.get(skill, 0) > 5:
                growth = (recent_ratio - older_ratio) / older_ratio if older_ratio > 0 else 1
                trending.append({
                    'skill': skill,
                    'growth': growth,
                    'recent_count': recent_counter.get(skill, 0),
                    'category': self._find_skill_category(skill)
                })
        
        return sorted(trending, key=lambda x: x['growth'], reverse=True)[:10]
    
    def _analyze_skill_combinations(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """인기 스킬 조합 분석"""
        combinations = []
        
        for skills in self.df['llm_extracted_tech_skills']:
            if len(skills) >= 2:
                # 2개 조합만 분석 (계산 효율성)
                for i in range(len(skills)):
                    for j in range(i + 1, len(skills)):
                        combinations.append(tuple(sorted([skills[i], skills[j]])))
        
        combo_counter = Counter(combinations)
        
        results = []
        for combo, count in combo_counter.most_common(top_n):
            results.append({
                'skills': list(combo),
                'count': count,
                'percentage': count / len(self.df) * 100
            })
        
        return results
    
    def get_skill_freq_by_jobtype(self, top_n: int = 10) -> Dict[str, List[Tuple[str, int]]]:
        """직무별 스킬 빈도"""
        result = {}
        job_types = self.df['job_type'].dropna().unique()
        
        for jt in job_types:
            rows = self.df[self.df['job_type'] == jt]
            all_skills = []
            for skills in rows['llm_extracted_tech_skills']:
                all_skills.extend(skills)
            
            counter = Counter(all_skills)
            result[jt] = counter.most_common(top_n)
        
        return result