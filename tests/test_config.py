import json
import pytest
import re

from pathlib import Path

import wol


CONFIG_PATH = Path(__file__).parent / "configs"


@pytest.mark.parametrize(
    "config_filename",
    [
        f
        for f in CONFIG_PATH.iterdir()
        if re.match(r"^default-\d+\.json$", f.name)
    ],
)
def test_default(config_filename):
    """
    Test that WOLConfig overwrites defaults with only those specified in the
    file.
    """
    config_file = CONFIG_PATH / config_filename
    config_file_dict = json.loads(config_file.read_text())["DEFAULT"]

    wol_config = wol.WOLConfig(config_file)

    for k, v in config_file_dict.items():
        assert wol_config._default_config[k] == v


def test_default_file_not_found():
    """
    Test that the WOLConfig user configuration is the same as the class
    defaults when the config file is not found.
    """
    # guarentee a nonexistent file by looking for a longer filename than the
    # longest filename in a directory
    longest_filename = max(CONFIG_PATH.iterdir(), key=lambda p: len(p.name))
    nonexistent_file = (
        longest_filename.parent / f"{longest_filename.name}.not-here"
    )

    wol_config = wol.WOLConfig(nonexistent_file)

    assert wol_config._default_config == wol.WOLConfig.DEFAULTS
