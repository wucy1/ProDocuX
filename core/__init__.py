"""
ProDocuX Core Engine
AI驅動的智能文檔轉換平台核心引擎
"""

__version__ = "1.0.0"
__author__ = "ProDocuX Team"
__email__ = "team@prodocux.com"

from .extractor import DocumentExtractor
from .transformer import DocumentTransformer
from .learner import ProfileLearner
from .profile_manager import ProfileManager

__all__ = [
    'DocumentExtractor',
    'DocumentTransformer', 
    'ProfileLearner',
    'ProfileManager'
]




