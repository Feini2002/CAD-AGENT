"""Visual-first CAD asset retrieval helpers."""

from core.visual_retrieval.cad_block_retrieval import (
    BlockCandidate,
    RetrievalReport,
    VisualQueryProfile,
    parse_visual_query_profile,
    retrieve_visual_blocks,
    retrieve_visual_blocks_from_driver,
)
from core.visual_retrieval.current_dwg_cache import (
    build_block_cache_manifest,
    build_block_cache_manifest_from_driver,
    cache_matches_document,
)
from core.visual_retrieval.dimension_annotation import (
    DimensionAnnotationPlan,
    DimensionOperation,
    build_bbox_dimension_plan,
    execute_dimension_annotation_plan,
)

__all__ = [
    "BlockCandidate",
    "DimensionAnnotationPlan",
    "DimensionOperation",
    "RetrievalReport",
    "VisualQueryProfile",
    "build_block_cache_manifest",
    "build_block_cache_manifest_from_driver",
    "build_bbox_dimension_plan",
    "cache_matches_document",
    "execute_dimension_annotation_plan",
    "parse_visual_query_profile",
    "retrieve_visual_blocks",
    "retrieve_visual_blocks_from_driver",
]
