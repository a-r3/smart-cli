"""Compatibility shim so tests importing ``pyyaml`` resolve to the YAML package."""

from yaml import *  # noqa: F401,F403
