"""LVP Core Module"""

from lvp.core.chunking import ChunkedLVPResult, plan_chunks
from lvp.core.ffmpeg_compat import check_ffmpeg_compatibility, get_ffmpeg_version
from lvp.core.package import LVPPackage
from lvp.core.processor import DEVICE_PROFILES, LVPProcessor
from lvp.core.reader import LVPReader
from lvp.core.selection import estimate_token_cost, select_by_query

__all__ = [
    'DEVICE_PROFILES',
    'ChunkedLVPResult',
    'LVPPackage',
    'LVPProcessor',
    'LVPReader',
    'check_ffmpeg_compatibility',
    'estimate_token_cost',
    'get_ffmpeg_version',
    'plan_chunks',
    'select_by_query',
]
