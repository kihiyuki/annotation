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
            x = "dx",
        ),
        a = dict(
            x = "ax",
            y = "ay",
            n = "1",
        ),
        b = dict(
            x = "bx",
            y = "by",
            n = "2",
        ),
    )
    lib.config.save(config, file=CONFIGFILE, mode="overwrite")

    yield config

    Path(CONFIGFILE).unlink()


class TestConfig(object):
    def test_load(self, sampleconfig):
        config_load = lib.config.load(file=CONFIGFILE)
        assert config_load == sampleconfig

        with pytest.raises(FileNotFoundError):
            # notfound_ok = False
            _ = lib.config.load(file=".INVALID")
        config_load = lib.config.load(file=".INVALID", notfound_ok=True)
        assert config_load == dict()

    def test_load_section(self, sampleconfig):
        config_load = lib.config.load(file=CONFIGFILE, section="a")
        assert config_load == sampleconfig["a"]

        with pytest.raises(KeyError):
            _ = lib.config.load(file=CONFIGFILE, section="c")

    def test_load_default(self, sampleconfig):
        default = dict(n=11, m=12)
        config_load = lib.config.load(file=CONFIGFILE, section="a", default=default)
        config_load2 = lib.config.load(file=CONFIGFILE, default={"a": default})
        c = sampleconfig.copy()
        c["a"]["m"] = 12
        assert config_load == c["a"]
        assert config_load2 == c

        # strict_key
        with pytest.raises(KeyError):
            _ = lib.config.load(file=CONFIGFILE, default={"a": default}, strict_key=True)

        # strict_cast
        with pytest.raises(ValueError):
            _ = lib.config.load(file=CONFIGFILE, default={"a": dict(x=0)}, cast=True, strict_cast=True)

        # cast
        config_load = lib.config.load(file=CONFIGFILE, default={"a": default}, cast=True)
        c = sampleconfig.copy()
        c["a"]["n"] = int(c["a"]["n"])
        c["a"]["m"] = 12
        assert config_load == c

    def test_save(self, sampleconfig):
        # invalid mode
        config = dict(hoge=dict(fuga=5))
        with pytest.raises(ValueError):
            lib.config.save(config, file=CONFIGFILE, mode="x")

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
