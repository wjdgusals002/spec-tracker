#  Spec Tracker

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)

**AI 기반 맞춤형 직무 추천 시스템**

Spec Tracker는 AI와 머신러닝을 활용하여 개발자들에게 최적의 직무를 추천하고, 경력 개발 로드맵을 제공하는 종합적인 플랫폼입니다.

##  주요 기능

###  **AI 맞춤 직무 매칭**
- **고도화된 매칭 알고리즘**: 코사인 유사도, 스킬 매칭, 경력 적합도를 종합한 다중 점수 시스템
- **실시간 점수 계산**: 사용자 프로필과 직무 요구사항의 정확한 매칭률 제공
- **스마트 필터링**: 지역, 연봉, 회사 규모 등 다양한 조건으로 정밀 검색

###  **경력 개발 로드맵**
- **개인화된 학습 계획**: 현재 스킬 수준과 목표에 맞는 맞춤형 로드맵
- **스킬 갭 분석**: 원하는 포지션까지 필요한 기술 스택 분석
- **프로젝트 추천**: 포트폴리오 강화를 위한 실전 프로젝트 제안
- **경력 시뮬레이션**: 학습 계획에 따른 연봉/포지션 성장 예측

###  **실시간 시장 인사이트**
- **기술 트렌드 분석**: 급상승/하락 기술 스택 모니터링
- **급여 데이터**: 경력/지역/기술별 상세 연봉 정보
- **기업 분석**: 주요 기업들의 채용 동향 및 선호 기술
- **AI 추천**: 시장 데이터 기반 맞춤형 조언

###  **고급 기술 스택**
- **LLM 기반 스킬 추출**: Cerebras AI를 활용한 정확한 기술 스택 분석
- **한영 혼합 텍스트 처리**: KoNLPy + 사전 기반 토큰화
- **실시간 데이터 시각화**: Plotly를 활용한 인터랙티브 차트

##  아키텍처

```
📁 spec-tracker/
├── 📁 components/          # UI 컴포넌트
│   ├── career_development.py    # 경력 개발 UI
│   ├── dashboard.py            # 대시보드
│   ├── job_matching.py         # 직무 매칭 UI
│   ├── market_insights.py      # 시장 인사이트 UI
│   └── header.py              # 헤더 컴포넌트
├── 📁 config/             # 설정 파일
│   ├── settings.py            # 앱 설정
│   └── styles.py              # CSS 스타일
├── 📁 models/             # AI 모델
│   └── job_matcher.py         # 핵심 매칭 알고리즘
├── 📁 scripts/            # 데이터 처리
│   └── data_processing.py     # ETL 파이프라인
├── 📁 utils/              # 유틸리티
│   └── helpers.py             # 헬퍼 함수
├── 📁 data/               # 데이터 저장소
│   ├── job_infos.csv          # 원본 데이터
│   └── job_data.db            # SQLite DB
└── app.py                 # 메인 애플리케이션
```

##  빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-username/spec-tracker.git
cd spec-tracker

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
echo "CEREBRAS_API_KEY=your_api_key_here" > .env
```

### 3. 데이터 준비

```bash
# 데이터 전처리 실행
python scripts/data_processing.py
```

### 4. 앱 실행

```bash
# Streamlit 앱 시작
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요!

## 📋 요구사항

### 시스템 요구사항
- **Python**: 3.8 이상
- **메모리**: 4GB 이상 권장
- **저장공간**: 2GB 이상

### 핵심 의존성

```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
scikit-learn>=1.3.0
sentence-transformers>=2.2.0
konlpy>=0.6.0
cerebras-cloud-sdk>=1.0.0
python-dotenv>=1.0.0
sqlite3  # 내장 모듈
```

## 🔧 설정 가이드

### Cerebras API 설정

1. [Cerebras 플랫폼](https://cloud.cerebras.ai/)에서 계정 생성
2. API 키 발급
3. `.env` 파일에 키 추가:
   ```
   CEREBRAS_API_KEY=your_actual_api_key
   ```

### 데이터베이스 설정

앱은 SQLite를 사용하며, 초기 실행 시 자동으로 데이터베이스가 생성됩니다.

```python
# 커스텀 데이터베이스 경로 설정
from config.settings import AppConfig
AppConfig.DB_PATH = "custom/path/to/database.db"
```

## 📊 데이터 스키마

### 직무 정보 (jobs 테이블)
```sql
CREATE TABLE jobs (
    job_id INTEGER PRIMARY KEY,
    title TEXT,                    -- 직무명
    company TEXT,                  -- 회사명
    location TEXT,                 -- 근무지
    experience TEXT,               -- 경력 요구사항
    years INTEGER,                 -- 경력 연차
    description TEXT,              -- 직무 설명
    requirements TEXT,             -- 자격 요건
    preferred TEXT,                -- 우대 사항
    job_type TEXT,                 -- 직무 유형
    skills TEXT,                   -- 추출된 스킬 (JSON)
    llm_extracted_tech_skills TEXT -- LLM 추출 기술스택 (JSON)
);
```

## 🎨 주요 알고리즘

### 직무 매칭 스코어 계산

```python
# 최종 점수 = 가중합
final_score = (
    similarity_score * 0.35 +      # 텍스트 유사도
    skill_match_score * 0.25 +     # 스킬 매칭률
    experience_fit * 0.15 +        # 경력 적합도
    freshness_score * 0.10 +       # 공고 최신성
    salary_fit * 0.10 +            # 급여 적합도
    company_score * 0.05           # 회사 평점
)
```

### 스킬 추천 로직

1. **연관 분석**: 현재 스킬과 함께 나타나는 기술 분석
2. **트렌드 분석**: 최근 30일 vs 이전 60일 비교
3. **중요도 계산**: 전체 공고 대비 해당 스킬 요구 비율
4. **학습 난이도**: 기술 복잡도 기반 난이도 추정

## 🔍 핵심 기능 상세

### 1. 스마트 토큰화

```python
def tokenize_mixed_skills(self, text):
    """한글 + 영어 기술명 정확 매칭"""
    # 1. 한글 명사 추출 (KoNLPy)
    korean_tokens = self.okt.nouns(text)
    
    # 2. 기술명 사전 기반 매칭
    tech_keywords = self._extract_tech_keywords(text)
    
    # 3. 불용어 제거 및 정제
    return self._filter_tokens(korean_tokens + tech_keywords)
```

### 2. 실시간 트렌드 분석

```python
def _analyze_trending_skills(self):
    """30일 vs 60일 비교로 트렌드 분석"""
    recent_ratio = skill_count_recent / total_recent_jobs
    older_ratio = skill_count_older / total_older_jobs
    
    growth_rate = (recent_ratio - older_ratio) / older_ratio
    return growth_rate
```

### 3. 경력 경로 예측

```python
def _determine_career_level(self, experience_years):
    """경력 연차 기반 레벨 결정"""
    if experience_years < 2: return 'Junior Developer'
    elif experience_years < 5: return 'Mid-level Developer'
    elif experience_years < 8: return 'Senior Developer'
    # ...
```

## 📈 성능 최적화

### 캐싱 전략
- **@st.cache_data**: 데이터 로딩 최적화
- **세션 상태**: 사용자 상호작용 상태 유지
- **지연 로딩**: 필요시에만 모델 로드

### 메모리 관리
- **벡터 연산**: NumPy 활용 고속 계산
- **배치 처리**: 대량 데이터 효율적 처리
- **가비지 컬렉션**: 메모리 누수 방지

## 🚀 배포 가이드

### Streamlit Community Cloud 배포

1. **GitHub 레포지토리 준비**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **[share.streamlit.io](https://share.streamlit.io) 접속**
   - GitHub 계정으로 로그인
   - 레포지토리 선택
   - `app.py` 경로 지정

3. **Secrets 설정**
   ```toml
   # .streamlit/secrets.toml
   CEREBRAS_API_KEY = "your_api_key"
   ```

### Docker 배포

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🤝 기여 가이드

### 개발 환경 설정

```bash
# 개발용 의존성 설치
pip install -r requirements-dev.txt

# 코드 품질 검사
flake8 .
black .
pytest
```

### 기여 프로세스

1. **Fork** 저장소
2. **Feature 브랜치** 생성: `git checkout -b feature/amazing-feature`
3. **커밋**: `git commit -m 'Add amazing feature'`
4. **Push**: `git push origin feature/amazing-feature`
5. **Pull Request** 생성

### 코딩 스타일

- **PEP 8** 준수
- **타입 힌트** 사용
- **Docstring** 작성 (Google 스타일)
- **테스트** 코드 포함

## 🐛 문제 해결

### 자주 발생하는 이슈

1. **모듈 import 오류**
   ```bash
   # 해결방법
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **데이터베이스 오류**
   ```bash
   # 데이터베이스 재생성
   rm data/job_data.db
   python scripts/data_processing.py
   ```

3. **API 키 오류**
   ```bash
   # .env 파일 확인
   cat .env
   ```

### 성능 이슈

- **메모리 부족**: 데이터 배치 크기 줄이기
- **느린 로딩**: 캐시 활용 및 지연 로딩 적용
- **API 제한**: 요청 빈도 조절

## 👥 팀

- **개발자**: [Your Name](https://github.com/your-username)
- **데이터 사이언티스트**: [Data Scientist Name]
- **UI/UX 디자이너**: [Designer Name]

## 📞 연락처

- **이메일**: your.email@example.com
- **이슈 트래킹**: [GitHub Issues](https://github.com/your-username/spec-tracker/issues)
- **문의사항**: [Discussion](https://github.com/your-username/spec-tracker/discussions)

## 🙏 감사의 말

- **Streamlit**: 놀라운 웹앱 프레임워크
- **Cerebras**: 강력한 LLM API 제공
- **KoNLPy**: 한국어 자연어 처리 지원
- **오픈소스 커뮤니티**: 모든 기여자들에게 감사

---

<div align="center">


[시작하기](#-빠른-시작) • [문서](docs/) • [데모](https://your-demo-link.streamlit.app) • [기여하기](#-기여-가이드)

</div>