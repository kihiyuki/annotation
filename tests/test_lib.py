from random import sample
import shutil
from pathlib import Path

import pytest

from annotation import lib


VERBOSE = True
TEMPDIR = "./testtemp"
CONFIGFILE = TEMPDIR + "/config.ini"


@pytest.fixture(scope="class", autouse=True)
def tempdir():
    tempdirpath = Path(TEMPDIR).resolve()
    if tempdirpath.is_dir():
        shutil.rmtree(str(tempdirpath))
    tempdirpath.mkdir(exist_ok=False)

    yield None

    shutil.rmtree(str(tempdirpath))


@pytest.fixture(scope="function", autouse=False)
def sampleconfig():
    config =  dict(
        DEFAULT = dict(
            x = "xdef",
        ),
        a = dict(
            x = "ax",
            y = "ay",
        ),
        b = dict(
            x = "bx",
            y = "by",
        ),
    )
    lib.config.save(config, file=CONFIGFILE, mode="overwrite")
    yield config
    Path(CONFIGFILE).unlink()


class TestConfig(object):
    def test_load(self, sampleconfig):
        config_load = lib.config.load(file=CONFIGFILE)
        assert config_load == sampleconfig

    @pytest.mark.parametrize("mode", ["o", "OVERWRITE"])
    def test_save_overwrite(self, sampleconfig, mode):
        config = dict(hoge=dict(fuga=5))
        config_str = dict(hoge=dict(fuga="5"))
        lib.config.save(config, file=CONFIGFILE, mode=mode)
        config_load = lib.config.load(file=CONFIGFILE)
        assert config_load == config_str

    @pytest.mark.parametrize("mode", ["a", "add"])
    def test_save_add(self, sampleconfig, mode):
        config = dict(a=dict(x="addx", z="addz"), b=dict(y="addy"))
        lib.config.save(config, file=CONFIGFILE, mode=mode)
        config_load = lib.config.load(file=CONFIGFILE)
        sampleconfig["a"]["z"] = "addz"
        assert config_load == sampleconfig

    @pytest.mark.parametrize("section", [None, "a", "c"])
    @pytest.mark.parametrize("has_section", [False, True])
    def test_save_add_param(self, sampleconfig, section, has_section):
        config = dict(x="addx", z="addz")
        if section is None:
            with pytest.raises(ValueError):
                lib.config.save(config, file=CONFIGFILE, mode="a", section=section)
        else:
            lib.config.save(
                {section: config} if has_section else config,
                file=CONFIGFILE,
                mode="a",
                section=None if has_section else section,
            )
            config_load = lib.config.load(file=CONFIGFILE)
            c = sampleconfig.copy()
            if section == "c":
                c[section] = dict()
                c[section]["x"] = "addx"
            c[section]["z"] = "addz"
            assert c == config_load


    @pytest.mark.parametrize("mode", ["l", "leave", "c", "cancel", "n", "no"])
    def test_save_leave(self, sampleconfig, mode):
        config = dict(hoge=dict(fuga="5"))
        lib.config.save(config, file=CONFIGFILE, mode=mode)
        config_load = lib.config.load(file=CONFIGFILE)
        assert config_load != config
        assert config_load == sampleconfig
