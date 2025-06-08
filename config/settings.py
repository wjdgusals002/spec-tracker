"""
프로젝트 설정 및 상수
"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AppConfig:
    """애플리케이션 설정"""
    PAGE_TITLE = "🎯 Spec Tracker"
    PAGE_ICON = "🎯"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"
    
    # 데이터베이스 경로
    DB_PATH = "data/job_data.db"
    
    # 모델 설정
    EMBEDDING_MODEL = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
    
    # UI 설정
    MAX_DISPLAY_JOBS = 20
    DEFAULT_MIN_MATCH_SCORE = 50
    
    # 캐시 설정
    CACHE_TTL = 3600  # 1시간

@dataclass
class ColorTheme:
    """색상 테마"""
    # 메인 색상
    PRIMARY = "#667eea"
    SECONDARY = "#764ba2"
    SUCCESS = "#11998e"
    DANGER = "#fc4a1a"
    WARNING = "#f7b733"
    INFO = "#4facfe"
    
    # 배경 색상
    DARK_BG = "#0a0e27"
    LIGHT_BG = "#1a1f3a"
    CARD_BG = "rgba(255,255,255,0.05)"
    
    # 텍스트 색상
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_MUTED = "#6c757d"
    
    # 그라데이션
    GRADIENT_PRIMARY = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    GRADIENT_SUCCESS = "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
    GRADIENT_DANGER = "linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)"
    GRADIENT_DARK = "linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)"

