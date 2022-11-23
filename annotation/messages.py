from dataclasses import dataclass


@dataclass(frozen=True)
class __Messages(object):
    replace: str = "already exists. Do you want to replace(overwrite) it?"

messages = __Messages()


@dataclass(frozen=True)
class __OptionMessages(object):
    datafile: str = "Pickled pandas.DataFrame file path"
    workdir: str = "Working directory path"
    cmapfile: str = "Custom matplotlib.cmap file (JSON)"
    configfile: str = "Configuration file path"
    configsection: str = "Configuration section name"
    deploy: str = "Deploy data to working directory"
    register: str = "Register annotation results to datafile"
    deployresult: str = "Deploy results (all annotated images)"
    clearworkdir: str = "Clear working directory"

option_messages = __OptionMessages()


@dataclass(frozen=True)
class __ConfigMessages(object):
    datafile: str = option_messages.datafile
    workdir: str = option_messages.workdir
    cmapfile: str = option_messages.cmapfile
    n: str = "Number of images to annotate at once (If null, deploy all images.)"
    n_example: str = "Number of example images of each label(If null, deploy all images.)"
    col_filename: str = "Column name for image-file name ('index' to use df.index if 'index' not in df.columns)"
    col_img: str = "Column name of image (containing numpy.ndarray)"
    col_label: str = "Column name of label"
    labels: str = "List of initial labels (comma-separated. If null, no initial labels set.)"
    label_null: str = "String representing to be unannotated (If null, '' represens to be unannotated.)"
    random: str = "Deploy randomly (1=Select randomly, 0=order by index)"
    imgext: str = "Image file extension (including .)"
    cmap: str = "matplotlib.cmap (you can use custom cmap name in cmap.py. If null, use default cmap of seaboarn.heatmap.)"
    vmin: str = "seaborn.heatmap.vmin (If null, determined automatically.)"
    vmax: str = "seaborn.heatmap.vmax (If null, determined automatically.)"
    figsize: str = "matplotlib.pyplot.figure.figsize"
    backup: str = "Backup (1=Copy datafile to datafile~ before save)"
    verbose: str = "Verbose (1=Print verbose messages)"

config_messages = __ConfigMessages()
