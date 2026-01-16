# Copyright (C) 2025 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from common import ScriptingToolkitVersionConfig
import pytest


class TestScriptingToolkitVersionConfig:
    """Tests for ScriptingToolkitVersionConfig behavior."""

    def test_version_latest_when_env_var_not_set(self, monkeypatch):
        """Version should be 'latest' when environment variable is not set."""
        monkeypatch.delenv(ScriptingToolkitVersionConfig.ENV_VAR, raising=False)
        config = ScriptingToolkitVersionConfig()
        assert config.version == "latest"

    def test_version_latest_when_env_var_empty(self, monkeypatch):
        """Version should be 'latest' when environment variable is empty string."""
        monkeypatch.setenv(ScriptingToolkitVersionConfig.ENV_VAR, "")
        config = ScriptingToolkitVersionConfig()
        assert config.version == "latest"

    def test_version_4x_when_env_var_set(self, monkeypatch):
        """Version should be '4.x' when environment variable is set to '4.x'."""
        monkeypatch.setenv(ScriptingToolkitVersionConfig.ENV_VAR, "4.x")
        config = ScriptingToolkitVersionConfig()
        assert config.version == "4.x"

    def test_invalid_version_raises_value_error(self, monkeypatch):
        """Invalid version should raise ValueError."""
        monkeypatch.setenv(ScriptingToolkitVersionConfig.ENV_VAR, "invalid_version")
        with pytest.raises(ValueError, match="must be one of"):
            ScriptingToolkitVersionConfig()

    def test_requires_version_matches_single_version(self, monkeypatch):
        """requires_version should return True when version matches."""
        monkeypatch.setenv(ScriptingToolkitVersionConfig.ENV_VAR, "4.x")
        config = ScriptingToolkitVersionConfig()
        assert config.requires_version("4.x") is True
        assert config.requires_version("latest") is False

    def test_requires_version_matches_latest(self, monkeypatch):
        """requires_version should return True when version is 'latest' and 'latest' is passed."""
        monkeypatch.delenv(ScriptingToolkitVersionConfig.ENV_VAR, raising=False)
        config = ScriptingToolkitVersionConfig()
        assert config.requires_version("latest") is True
        assert config.requires_version("4.x") is False

    def test_requires_version_matches_multiple_versions(self, monkeypatch):
        """requires_version should return True when version matches any of multiple versions."""
        monkeypatch.setenv(ScriptingToolkitVersionConfig.ENV_VAR, "4.x")
        config = ScriptingToolkitVersionConfig()
        assert config.requires_version("4.x", "latest") is True
        assert config.requires_version("latest", "4.x") is True

    def test_requires_version_no_match_multiple_versions(self, monkeypatch):
        """requires_version should return False when version doesn't match any."""
        monkeypatch.delenv(ScriptingToolkitVersionConfig.ENV_VAR, raising=False)
        config = ScriptingToolkitVersionConfig()
        assert config.requires_version("4.x") is False
