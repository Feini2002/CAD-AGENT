"""External backend adapters for cleanroom."""

from cad_agent.adapters.fake_backend import FakeCadBackend
from cad_agent.adapters.autocad_backend import AutoCadBackend

__all__ = ["FakeCadBackend", "AutoCadBackend"]
