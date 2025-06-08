import pandas as pd
import numpy as np
import re
import nltk
import json
import sqlite3
import os
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import pickle
import time
from tqdm import tqdm
import requests
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
import asyncio
import math
from cerebras.cloud.sdk import AsyncCerebras, RateLimitError, APIConnectionError, APIStatusError

# 환경 변수 로드
load_dotenv()

# NLTK 자원 다운로드
nltk.download('punkt', quiet=True)
TECH_KEYWORDS = [
    # 프로그래밍 언어
    'Python', '파이썬', 'Java', '자바', 'JavaScript', '자바스크립트', 'TypeScript', 'C', 'C++', '씨플러스플러스',
    'C#', '씨샵', 'Go', 'Golang', 'Kotlin', 'Swift', 'Ruby', 'R', 'Scala', 'Dart', 'Objective-C', 'Perl',
    'PHP', 'MATLAB', 'Rust', 'Groovy', 'Delphi', 'VBA',

    # 프론트엔드 프레임워크/라이브러리
    'React', 'Vue', 'Angular', 'Next.js', 'Nuxt.js', 'Svelte', 'jQuery', 'Bootstrap', 'TailwindCSS', 'Material-UI', 'Redux',
    'Recoil', 'Styled-Components',

    # 백엔드 프레임워크/라이브러리
    'Spring', 'SpringBoot', '스프링', 'Express', 'Django', 'Flask', 'FastAPI', 'NestJS', 'Node.js', 'Koa', 'Ruby on Rails',
    'ASP.NET', 'JSP', 'Tibero', 'nexacro',

    # 데이터베이스
    'MySQL', 'MariaDB', 'PostgreSQL', 'Oracle', 'MSSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra', 'DynamoDB',
    'SQLite', 'Amazon RDS', 'Google BigQuery', 'HBase', 'CouchDB',

    # DevOps/Infra/클라우드
    'AWS', '에이더블유에스', 'Amazon Web Services', 'Azure', 'GCP', 'Google Cloud', 'Google Cloud Platform', 'Kubernetes',
    'Docker', 'Jenkins', 'Git', 'GitHub', 'GitLab', 'Travis CI', 'CircleCI', 'Ansible', 'Terraform', 'Nginx', 'Apache',
    'Tomcat', 'CI/CD', 'CDN', 'S3', 'EC2', 'ECS', 'Lambda', 'VPC', 'Firebase', 'CloudFront', 'ELB', 'Route53', 'SQS', 'Kafka',
    'RabbitMQ', 'Zookeeper', 'Prometheus', 'Grafana', 'Logstash', 'Filebeat', 'Datadog', 'New Relic', 'OpenStack',

    # 빅데이터/머신러닝/AI
    'TensorFlow', '텐서플로우', 'PyTorch', '사이킷런', 'scikit-learn', 'Keras', 'XGBoost', 'LightGBM', 'CatBoost', 'HuggingFace',
    'Transformers', 'OpenCV', 'MXNet', 'Torch', 'ONNX', 'DNN', 'MLlib', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Plotly',
    'DataRobot', 'Dataiku', 'MLflow',

    # 데이터 엔지니어링/분석/ETL
    'Airflow', 'Luigi', 'NiFi', 'Talend', 'Pentaho', 'Informatica', 'Spark', '하둡', 'Hadoop', 'Hive', 'Pig', 'Presto', 'Superset',
    'Tableau', 'PowerBI', 'QlikView', 'Metabase', 'Redash', 'Data Studio', 'Looker', 'Google Analytics',

    # API/통신/보안
    'REST', 'RESTful', 'GraphQL', 'gRPC', 'SOAP', 'WebSocket', 'JWT', 'OAuth', 'OpenAPI', 'Swagger', 'SAML', 'SFTP', 'SSL', 'TLS',

    # 기타 도구/기술/용어
    'Linux', 'Ubuntu', 'CentOS', 'RedHat', 'Windows Server', 'MacOS', 'VSCode', 'IntelliJ', 'PyCharm', 'Eclipse', 'JIRA',
    'Confluence', 'Slack', 'Notion', 'Zoom', 'Teams', 'Figma', 'Zeplin', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator',
    'Firebase', 'Notion', 'GitBook', 'Trello', 'Asana', 'Miro',

    # 테스트/품질/협업
    'Jest', 'Mocha', 'Chai', 'JUnit', 'Mockito', 'Selenium', 'Cypress', 'Appium', 'TestNG', 'QUnit', 'SonarQube', 'Allure',

    # 산업별 솔루션/ERP/CRM/특수 시스템 (예시)
    'SAP', 'ERP', 'CRM', 'Salesforce', 'SAP HANA', 'Oracle EBS', 'PeopleSoft', 'Workday',

    # 자연어처리/챗봇
    'BERT', 'GPT', 'ChatGPT', 'KoBERT', 'ELECTRA', 'spaCy', 'NLTK', 'SentencePiece',

    # 금융/핀테크 특화
    'OpenBanking', 'ISO20022', 'FIDO', 'NICE', 'KISA', 'VAN', 'PG사', 'CMS', '핀테크', '제로페이'
]
STOPWORDS = [
    # 한글 불용어 (일반 명사, 잡단어)
    '경험', '업무', '프로젝트', '기술', '역량', '이상', '기반', '수행', '결과', '관련', '구축', '처리',
    '보유', '데이터', '이력서', '설계', '서비스', '기본', '성과', '주도', '작성', '이용', '부분', '실제',
    '효율', '솔루션', '대한', '검색', '경우', '적용', '조직', '합류', '영향', '제외', '수치', '용도', '분과',
    '개선', '외부', '트러블', '파악', '구체', '애자', '통합', '이해', '항일', '선후', '환경', '추천', '해당',
    '자동화', '자동', '공개', '임팩트', '항일', '슈팅', '대해', '메타데이터', '중심', '활동', '사유', '관점',
    '관리', '적합', '내용', '사항', '구성원', '분야', '대상', '자격', '필수', '요소', '목적', '목표', '지원',
    '최상', '최적', '추가', '도전', '연계', '성과', '과정', '이력', '기회', '포함', '등', '및', '더', '중',
    '신규', '개선', '도입', '포지션', '기타', '연관', '상세', '확대', '검증', '접근', '수립', '제공', '협업',
    '리더', '팀', '부서', '총무', '인사', '관리자', '신입', '경력', '리더십', '자격증', '회사', '기업',
    '부문', '담당', '지원자', '지원서', '전공', '학력', '이수', '출신', '점수', '취득', '추천', '소개',
    '참여', '전반', '필요', '능력', '연구', '업무지', '성장', '기준', '표준', '조건', '변화', '도구',
    # 영어 불용어(일반적 의미)
    'experience', 'project', 'technology', 'service', 'requirement', 'related',
    'role', 'impact', 'leader', 'leadership', 'new', 'addition', 'job', 'work',
    'field', 'area', 'tool', 'position', 'opportunity', 'support', 'candidate',
    'company', 'department', 'result', 'etc', 'include', 'more', 'with', 'in',
    'about', 'required', 'must', 'plus', 'basic', 'member', 'certificate', 'join',
    'management', 'manager', 'research', 'description', 'note', 'and', 'the',
    'for', 'to', 'on', 'of', 'by', 'at', 'as', 'from'
]


class JobDataProcessor:
    def __init__(self, csv_path='data/job_infos.csv', db_path='data/job_data.db'):
        self.csv_path = csv_path
        self.db_path = db_path
        self.okt = Okt()
        self.url_pattern = re.compile(r'https?://\S+|www\.\S+')
        self.special_char_pattern = re.compile(r'[^\w\s]')
        
        # TF-IDF 벡터화 설정
        self.tfidf_vectorizer = TfidfVectorizer(min_df=0.01, max_df=0.9)
        
        # Cerebras API 키 로드
        self.cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
        if not self.cerebras_api_key:
            print("경고: CEREBRAS_API_KEY가 설정되지 않았습니다. 기술 스택 추출 기능이 제한됩니다.")
        else:
            # Cerebras Client 초기화
            self.cerebras_client = Cerebras(api_key=self.cerebras_api_key)
        
        # 레이트 리밋 설정
        self.rate_limits = {
            'requests': {
                'minute': 30,
                'hour': 900,
                'day': 14400
            },
            'tokens': {
                'minute': 60000,
                'hour': 1000000,
                'day': 1000000
            }
        }
        
        # 토큰 사용량 추적
        self.token_usage = {
            'minute': {'count': 0, 'reset_time': time.time()},
            'hour': {'count': 0, 'reset_time': time.time()},
            'day': {'count': 0, 'reset_time': time.time()}
        }
        
        # 요청 횟수 추적
        self.request_usage = {
            'minute': {'count': 0, 'reset_time': time.time()},
            'hour': {'count': 0, 'reset_time': time.time()},
            'day': {'count': 0, 'reset_time': time.time()}
        }
        
    def _clean_text(self, text):
        """텍스트 클린징: URL 제거, 특수문자 제거, 소문자화"""
        text = str(text)
        # URL 제거
        text = self.url_pattern.sub('', text)
        # 특수문자 제거
        text = self.special_char_pattern.sub(' ', text)
        # 여러 공백을 하나로 치환
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def tokenize_mixed_skills(self, text):
        """
        한글 명사(OKT) + 사전 기반 영어/한글 기술명 '정확 매칭' (실무 표준, 완벽)
        """
        cleaned_text = self._clean_text(text)
        # 1. 한글 명사 추출 (여전히 남기되, 기술명 사전은 대소문자 무관하게 잡음)
        korean_tokens = [token.lower() for token in self.okt.nouns(cleaned_text) if len(token) > 1]
        # 2. 사전 기반 기술명 단어경계 or 특수문자 기준 탐지
        found_keywords = set()
        lowered_text = cleaned_text.lower()
        for kw in TECH_KEYWORDS:
            # 단어경계 또는 /(슬래시), (,), or, . 등 특수문자 붙어도 매칭
            pattern = r'(?i)(?:\b|[^a-zA-Z0-9_])' + re.escape(kw.lower()) + r'(?:\b|[^a-zA-Z0-9_])'
            if re.search(pattern, f' {lowered_text} '):  # 앞뒤 공백 추가
                found_keywords.add(kw)
        tokens = set(korean_tokens) | found_keywords
        filtered_tokens = [tok for tok in tokens if tok not in STOPWORDS and len(tok) > 1]
        return filtered_tokens




    
    def _extract_skills_from_job(self, job_row):
        """직무 공고에서 스킬 추출"""
        # 직무 설명, 요구사항, 우대사항 텍스트 결합
        full_text = f"{job_row['description']} {job_row['requirements']} {job_row['preferred']}"
        return self.tokenize_mixed_skills(full_text)
    
    def _estimate_tokens(self, messages):
        """메시지의 예상 토큰 수 계산"""
        total_chars = sum(len(msg['content']) for msg in messages)
        # 대략적인 추정: 영어 기준 1토큰 = 4글자, 한글 기준 1토큰 = 2글자
        estimated_tokens = total_chars // 3  # 한영 혼용 고려
        return estimated_tokens

    def _check_and_update_limits(self, messages):
        """레이트 리밋 체크 및 대기"""
        current_time = time.time()
        estimated_tokens = self._estimate_tokens(messages)
        
        # 시간 간격별 초기화 및 체크
        intervals = {
            'minute': {'seconds': 60, 'token_limit': 60000, 'request_limit': 30},
            'hour': {'seconds': 3600, 'token_limit': 1000000, 'request_limit': 900},
            'day': {'seconds': 86400, 'token_limit': 1000000, 'request_limit': 14400}
        }
        
        for interval, limits in intervals.items():
            elapsed_time = current_time - self.token_usage[interval]['reset_time']
            
            # 시간 간격이 지났으면 카운터 초기화
            if elapsed_time >= limits['seconds']:
                self.token_usage[interval] = {'count': 0, 'reset_time': current_time}
                self.request_usage[interval] = {'count': 0, 'reset_time': current_time}
                continue
            
            # 토큰 또는 요청 한도 체크
            if (self.token_usage[interval]['count'] + estimated_tokens > limits['token_limit'] or
                self.request_usage[interval]['count'] + 1 > limits['request_limit']):
                
                # 다음 리셋 시간까지 남은 시간 계산
                wait_time = limits['seconds'] - elapsed_time
                
                if wait_time > 0:
                    print(f"\n{interval} 한도 도달. {wait_time:.1f}초 대기 중...")
                    time.sleep(wait_time)
                    # 대기 후 카운터 초기화
                    self.token_usage[interval] = {'count': 0, 'reset_time': time.time()}
                    self.request_usage[interval] = {'count': 0, 'reset_time': time.time()}
        
        # 사용량 업데이트
        for interval in intervals:
            self.token_usage[interval]['count'] += estimated_tokens
            self.request_usage[interval]['count'] += 1
        
        return True

    def _get_tech_skills_schema(self):
        """기술 스택 추출을 위한 JSON 스키마 정의"""
        return {
            "type": "object",
            "properties": {
                "tech_skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of technical skills and technologies extracted from the tokens"
                }
            },
            "required": ["tech_skills"],
            "additionalProperties": False
        }

    def _prepare_llm_messages(self, tokens, job_info):
        """LLM 요청을 위한 메시지 준비"""
        # 중복 제거 및 정렬
        unique_tokens = sorted(set(tokens))
        tokens_str = ", ".join(unique_tokens)
        
        return [
            {
                "role": "system", 
                "content": """당신은 직무 공고에서 기술 스택을 정확하게 추출하는 전문가입니다.
주의사항:
1. 기술 스택은 원문의 표기를 정확히 유지할 것
2. 확실한 기술 스택만 포함하고 애매한 것은 제외
3. 일반적인 용어나 개념은 모두 제외
4. 기술스택의 버전 정보가 있다면 함께 포함"""
            },
            {
                "role": "user", 
                "content": f"""
다음 단어들에 대하여 기술 스택을 추출해주세요.
토큰 목록: {tokens_str}
"""
            }
        ]

    async def _call_llm_with_retry(self, async_client, messages, tokens):
        """재시도 로직이 포함된 LLM 호출"""
        max_retries = 5
        retry_delay = 1  # 초기 대기 시간 (초)
        
        def validate_tech_skills(skills):
            """기술 스택 유효성 검증"""
            if not isinstance(skills, list):
                return False
                        
            # 각 스킬이 일반 용어가 아닌지 확인
            filtered_skills = [
                skill for skill in skills 
                if isinstance(skill, str) and 
                skill.strip()]
            
            return len(filtered_skills) > 0
        
        for attempt in range(max_retries):
            try:
                # 레이트 리밋 체크
                await asyncio.to_thread(self._check_and_update_limits, messages)
                
                chat_completion = await async_client.chat.completions.create(
                    model="llama-3.3-70b",
                    messages=messages,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "tech_skills_schema",
                            "strict": True,
                            "schema": self._get_tech_skills_schema()
                        }
                    },
                    temperature=0.0
                )
                
                try:
                    content = chat_completion.choices[0].message.content
                    tech_skills_data = json.loads(content)
                    extracted_skills = tech_skills_data.get("tech_skills", [])
                    
                    # 추출된 기술 스택 유효성 검증
                    if validate_tech_skills(extracted_skills):
                        return extracted_skills
                    else:
                        print(f"Invalid tech skills format or empty result for job. Retrying...")
                        if attempt == max_retries - 1:
                            return self._extract_fallback_tech_skills(tokens)
                        continue
                        
                except (json.JSONDecodeError, KeyError, AttributeError) as e:
                    print(f"Response parsing error: {str(e)}")
                    print("Retrying the same request immediately...")
                    
                    # 파싱 에러 발생 시 즉시 한 번 더 시도
                    try:
                        await asyncio.sleep(1)  # 1초 대기 후 재시도
                        chat_completion = await async_client.chat.completions.create(
                            model="llama-3.3-70b",
                            messages=messages,
                            response_format={
                                "type": "json_schema",
                                "json_schema": {
                                    "name": "tech_skills_schema",
                                    "strict": True,
                                    "schema": self._get_tech_skills_schema()
                                }
                            },
                            temperature=0.1
                        )
                        content = chat_completion.choices[0].message.content
                        tech_skills_data = json.loads(content)
                        extracted_skills = tech_skills_data.get("tech_skills", [])
                        
                        if validate_tech_skills(extracted_skills):
                            return extracted_skills
                    except Exception as retry_e:
                        print(f"Immediate retry also failed: {str(retry_e)}")
                    
                    if attempt == max_retries - 1:
                        return self._extract_fallback_tech_skills(tokens)
                    continue
                
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    print(f"Rate limit exceeded after {max_retries} attempts. Error: {str(e)}")
                    return self._extract_fallback_tech_skills(tokens)
                
                wait_time = retry_delay * (2 ** attempt)  # 지수 백오프
                print(f"Rate limit hit, waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)
                
            except APIConnectionError as e:
                print(f"Connection error: {str(e)}")
                print(f"Underlying error: {e.__cause__}")
                if attempt == max_retries - 1:
                    return self._extract_fallback_tech_skills(tokens)
                await asyncio.sleep(retry_delay)
                
            except APIStatusError as e:
                print(f"API error: Status {e.status_code}")
                print(f"Response: {e.response}")
                return self._extract_fallback_tech_skills(tokens)
                
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return self._extract_fallback_tech_skills(tokens)
        
        return self._extract_fallback_tech_skills(tokens)  # 모든 재시도 실패 시
        
    def _extract_fallback_tech_skills(self, tokens):
        """LLM 추출 실패 시 폴백 로직으로 기술 스택 추출"""
        # 알려진 기술 스택 목록
        known_tech_stacks = {
            # 프로그래밍 언어
            'python', 'java', 'javascript', 'typescript', 'c++', 'go', 'ruby', 'swift', 'kotlin',
            # 프레임워크/라이브러리
            'react', 'angular', 'vue', 'django', 'spring', 'flask', 'express', 'tensorflow',
            # 데이터베이스
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
            # 클라우드/인프라
            'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'jenkins', 'terraform',
            # 빅데이터/ML
            'hadoop', 'spark', 'kafka', 'airflow', 'scikit-learn', 'pytorch',
            # 개발 도구
            'git', 'vscode', 'intellij', 'jira', 'confluence'
        }
        
        # 토큰에서 알려진 기술 스택만 필터링
        tech_skills = [
            token for token in tokens 
            if token.lower() in known_tech_stacks
        ]
        
        return list(set(tech_skills))  # 중복 제거

    async def extract_tech_skills_batch(self, df):
        """직무에 대한 기술 스택 토큰을 순차적으로 추출"""
        if not self.cerebras_api_key:
            return df
        
        async_client = AsyncCerebras(api_key=self.cerebras_api_key)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # llm_extracted_tech_skills 컬럼이 없으면 추가
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'llm_extracted_tech_skills' not in columns:
            cursor.execute('ALTER TABLE jobs ADD COLUMN llm_extracted_tech_skills TEXT DEFAULT NULL')
            conn.commit()
        
        all_results = []
        total_jobs = len(df)
        
        for idx, row in tqdm(df.iterrows(), total=total_jobs, desc="기술 스택 추출 처리"):
            try:
                job_id = row['job_id']
                print(f"\nProcessing job_id: {job_id}")
                
                tokens = json.loads(row['skills'])
                job_info = {
                    'title': row['title'],
                    'description': row['description'],
                    'requirements': row['requirements'],
                    'preferred': row['preferred']
                }
                
                # LLM 메시지 준비
                messages = self._prepare_llm_messages(tokens, job_info)
                
                # LLM 호출 및 결과 처리
                result = await self._call_llm_with_retry(async_client, messages, tokens)
                all_results.append(result)
                
                # 결과를 즉시 DB에 업데이트
                tech_skills_json = json.dumps(result, ensure_ascii=False)
                cursor.execute(
                    'UPDATE jobs SET llm_extracted_tech_skills = ? WHERE job_id = ?',
                    (tech_skills_json, job_id)
                )
                conn.commit()
                
                # 진행상황 출력 (100개마다)
                if (idx + 1) % 100 == 0:
                    print(f"진행률: {idx + 1}/{total_jobs} 완료")
                
                # 요청 간 짧은 휴식
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Job processing error for job_id {row['job_id']}: {str(e)}")
                all_results.append(tokens)
                # 에러 발생 시에도 원본 토큰을 DB에 저장
                tech_skills_json = json.dumps(tokens, ensure_ascii=False)
                cursor.execute(
                    'UPDATE jobs SET llm_extracted_tech_skills = ? WHERE job_id = ?',
                    (tech_skills_json, job_id)
                )
                conn.commit()
        
        conn.close()
        
        try:
            # DataFrame 업데이트
            tech_skills_json = [json.dumps(skills, ensure_ascii=False) for skills in all_results]
            df.loc[:, 'llm_extracted_tech_skills'] = tech_skills_json
            
        except Exception as e:
            print(f"DataFrame 업데이트 중 오류 발생: {str(e)}")
        
        return df
    
    def _extract_years(self, experience_text):
        """경력 연차 추출"""
        if pd.isna(experience_text) or experience_text == '':
            return 0
        
        # "경력 3-5년" 같은 패턴에서 숫자 추출
        match = re.search(r'(\d+)[-~]?(\d+)?년?', experience_text)
        if match:
            # 범위가 있는 경우 (예: 3-5년)
            if match.group(2):
                return int(match.group(1))  # 최소 연차만 반환
            # 단일 숫자인 경우 (예: 3년)
            return int(match.group(1))
        
        # 신입 또는 숫자가 없는 경우
        if '신입' in experience_text:
            return 0
        
        return 0  # 기본값
    
    def create_database(self):
        """SQLite 데이터베이스 생성 및 테이블 설정"""
        # DB 연결 생성
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 직무 테이블 생성 (존재하지 않는 경우에만)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            experience TEXT,
            years INTEGER,
            description TEXT,
            requirements TEXT,
            preferred TEXT,
            job_type TEXT,
            cleaned_text TEXT,
            tokens_str TEXT,
            skills TEXT,
            llm_extracted_tech_skills TEXT DEFAULT NULL
        )
        ''')
        
        # 모델 정보 저장 테이블 (존재하지 않는 경우에만)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            data BLOB
        )
        ''')
        
        conn.commit()
        conn.close()
        
        print("SQLite 데이터베이스 테이블이 확인/생성되었습니다.")
    
    def process_data(self):
        """CSV 데이터 전처리 및 SQLite에 저장"""
        self.tokenize_mixed_skills
        start_time = time.time()
        print(f"CSV 파일 '{self.csv_path}'을 불러오는 중...")
        
        # CSV 데이터 로드
        df = pd.read_csv(self.csv_path)
        
        # 필요한 칼럼만 선택
        df = df[['job_id', 'title', 'company', 'location', 'experience', 'description', 'requirements', 'preferred', 'job_type']]
        
        # NA 값 처리
        df.fillna('', inplace=True)
        
        # 중복된 job_id 확인 및 제거
        duplicate_count = df.duplicated(subset=['job_id']).sum()
        if duplicate_count > 0:
            print(f"중복된 job_id {duplicate_count}개를 제거합니다...")
            df = df.drop_duplicates(subset=['job_id'])
        
        # 기존 DB에서 데이터 로드
        conn = sqlite3.connect(self.db_path)
        existing_df = pd.read_sql('SELECT job_id, llm_extracted_tech_skills FROM jobs', conn)
        
        # llm_extracted_tech_skills가 NULL인 job_id만 필터링
        if not existing_df.empty:
            null_skills_jobs = existing_df[existing_df['llm_extracted_tech_skills'].isnull()]['job_id'].tolist()
            new_jobs = set(df['job_id']) - set(existing_df['job_id'])
            jobs_to_process = list(new_jobs) + null_skills_jobs
            df = df[df['job_id'].isin(jobs_to_process)]
        
        if df.empty:
            print("처리할 새로운 데이터가 없습니다.")
            conn.close()
            return
        
        print(f"총 {len(df)} 개의 직무 공고를 처리합니다...")
        
        # 데이터 전처리
        print("텍스트 정제 중...")
        df['cleaned_text'] = df.apply(
            lambda row: self._clean_text(f"{row['description']} {row['requirements']} {row['preferred']}"), 
            axis=1
        )
        
        print("텍스트 토큰화 중...")
        tqdm.pandas(desc="토큰화 진행률")
        df['tokenized'] = df['cleaned_text'].progress_apply(self.tokenize_mixed_skills)
        df['tokens_str'] = df['tokenized'].apply(lambda x: ' '.join(x))
        
        # skills 컬럼 저장 직전에, 결과 미리 보기
        for i in range(min(5, len(df))):
            print(f"\n==== {i+1}번째 row ====")
            print("cleaned_text:", df['cleaned_text'].iloc[i])
            print("tokenized   :", df['tokenized'].iloc[i])
            # (아직 df['skills'] 저장 전이니, tokenized만 우선 봅니다)


        print("스킬 추출 중...")
        df['skills'] = df['tokenized'].apply(lambda x: json.dumps(x, ensure_ascii=False))

        
        print("경력 연차 추출 중...")
        df['years'] = df['experience'].apply(self._extract_years)
        
        # TF-IDF 벡터화를 위한 전체 데이터 로드
        all_jobs_df = pd.read_sql('SELECT tokens_str FROM jobs', conn)
        combined_tokens = pd.concat([all_jobs_df['tokens_str'], df['tokens_str']])
        
        # TF-IDF 벡터화
        print("TF-IDF 벡터화 중...")
        job_vectors = self.tfidf_vectorizer.fit_transform(combined_tokens)
        
        # 스킬 빈도 추출
        print("스킬 빈도 계산 중...")
        all_skills = []
        for skills_json in df['skills']:
            all_skills.extend(json.loads(skills_json))
        
        skill_counter = Counter(all_skills)
        common_skills = [skill for skill, count in skill_counter.most_common(100)]
        
        # SQLite에 데이터 저장 (UPSERT)
        print("SQLite 데이터베이스에 저장 중...")
        
        # 직무 데이터 저장 (UPSERT)
        for _, row in df.iterrows():
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO jobs 
                (job_id, title, company, location, experience, years, description, 
                requirements, preferred, job_type, cleaned_text, tokens_str, skills)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['job_id'], row['title'], row['company'], row['location'],
                row['experience'], row['years'], row['description'],
                row['requirements'], row['preferred'], row['job_type'],
                row['cleaned_text'], row['tokens_str'], row['skills']
            ))
        
        # 모델 데이터 저장
        cursor = conn.cursor()
        
        # TF-IDF 벡터라이저 저장
        vectorizer_pickle = pickle.dumps(self.tfidf_vectorizer)
        cursor.execute('INSERT OR REPLACE INTO model_data (name, data) VALUES (?, ?)', 
                       ('tfidf_vectorizer', vectorizer_pickle))
        
        # 직무 벡터 저장
        vectors_pickle = pickle.dumps(job_vectors)
        cursor.execute('INSERT OR REPLACE INTO model_data (name, data) VALUES (?, ?)', 
                       ('job_vectors', vectors_pickle))
        
        # 주요 스킬 목록 저장
        skills_pickle = pickle.dumps(common_skills)
        cursor.execute('INSERT OR REPLACE INTO model_data (name, data) VALUES (?, ?)', 
                       ('common_skills', skills_pickle))
        
        # 피처 이름 저장
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        feature_names_pickle = pickle.dumps(feature_names)
        cursor.execute('INSERT OR REPLACE INTO model_data (name, data) VALUES (?, ?)', 
                       ('feature_names', feature_names_pickle))
        
        conn.commit()
        
        end_time = time.time()
        print(f"기본 전처리 및 저장 완료! 소요 시간: {end_time - start_time:.2f}초")
        
        # LLM으로 기술 스택 추출 및 업데이트
        if self.cerebras_api_key:
            print("\nLLM을 사용하여 기술 스택 추출을 시작합니다...")
            
            try:
                # 전체 데이터셋 한번에 처리
                print(f"총 {len(df)}개의 데이터를 처리합니다.")
                processed_df = asyncio.run(self.extract_tech_skills_batch(df))
                
                # 처리된 결과를 DB에 업데이트
                for _, row in processed_df.iterrows():
                    cursor.execute(
                        'UPDATE jobs SET llm_extracted_tech_skills = ? WHERE job_id = ?',
                        (row['llm_extracted_tech_skills'], row['job_id'])
                    )
                conn.commit()
                
                # 기술 스택 빈도 재계산 및 저장
                print("\n기술 스택 빈도 재계산 중...")
                cursor.execute('SELECT llm_extracted_tech_skills FROM jobs')
                all_tech_skills = []
                for (tech_skills_json,) in cursor.fetchall():
                    if tech_skills_json:  # NULL이 아닌 경우만 처리
                        all_tech_skills.extend(json.loads(tech_skills_json))
                
                tech_skill_counter = Counter(all_tech_skills)
                common_tech_skills = [skill for skill, count in tech_skill_counter.most_common(50)]
                
                # 주요 기술 스택 목록 업데이트
                tech_skills_pickle = pickle.dumps(common_tech_skills)
                cursor.execute('INSERT OR REPLACE INTO model_data (name, data) VALUES (?, ?)', 
                               ('common_tech_skills', tech_skills_pickle))
                
                conn.commit()
                
            except Exception as e:
                print(f"기술 스택 추출 중 오류 발생: {str(e)}")
        else:
            print("\nCEREBRAS_API_KEY가 없어 기술 스택 추출을 건너뜁니다.")

        
        conn.close()
        
        total_end_time = time.time()
        print(f"\n전체 작업 완료! 총 소요 시간: {total_end_time - start_time:.2f}초")



if __name__ == "__main__":
    processor = JobDataProcessor()
    processor.create_database()
    processor.process_data() 
    
