"""External backend adapters for vNext."""

from cad_agent_vnext.adapters.fake_backend import FakeCadBackend
from cad_agent_vnext.adapters.legacy_autocad_backend import LegacyAutoCadBackend

__all__ = ["FakeCadBackend", "LegacyAutoCadBackend"]
