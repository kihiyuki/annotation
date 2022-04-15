import shutil
from pathlib import Path

import pytest
import pandas as pd

from annotation import main, lib
from annotation.data import CONFIG_DEFAULT


VERBOSE = True
SECTION = "annotation"
TEMPDIR = "./testtemp"
CONFIGFILE = TEMPDIR + "/config.ini"
DATAFILE = TEMPDIR + "/sample.pkl.xz"
WORKDIR = TEMPDIR + "/work"
ARGS = [
    "--config-file", CONFIGFILE,
    "-w", WORKDIR,
    "-f", DATAFILE,
]
if VERBOSE:
    ARGS.append("-v")


@pytest.fixture(scope="class", autouse=True)
def config(verbose=VERBOSE):
    if verbose:
        print()
    tempdirpath = Path(TEMPDIR).resolve()
    if tempdirpath.is_dir():
        shutil.rmtree(str(tempdirpath))
    tempdirpath.mkdir(exist_ok=False)

    args = [
        "--config-file", CONFIGFILE,
        "--create-config-file",
    ]
    _ = main(args=args)

    config_ = lib.config.load(
        file=CONFIGFILE,
        default=CONFIG_DEFAULT,
        section=SECTION,
        cast=True,
        strict_cast=False,
        strict_key=True)

    yield config_

    if verbose:
        print()
        print("shutil.rmtree:", str(tempdirpath))
    shutil.rmtree(str(tempdirpath))


class TestMain(object):
    def test_generate_samplefile(self, config):
        args = ARGS + ["--create-sample-datafile"]
        _ = main(args=args)

        assert Path(DATAFILE).is_file()
        df = pd.read_pickle(str(DATAFILE))
        assert len(df) == 100
        cols = df.columns
        for k in ["col_filename", "col_img"]: # , "col_label"
            assert config[k] in cols

    @pytest.mark.parametrize("option", ["-d", "--deploy"])
    def test_deploy(self, option, config):
        args = ARGS + [option]
        _ = main(args=args)
        assert True
