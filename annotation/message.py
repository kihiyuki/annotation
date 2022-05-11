DATAFILE = "Pickled pandas.DataFrame file path"
WORKDIR = "Working directory path"
CONFIGFILE = "Configuration file path"
CONFIGSECTION = "Configuration section name"
DEPLOY = "Deploy data to working directory"
REGISTER = "Register annotation results to datafile"
DEPROYRESULT = "Deploy results (all annotated images)"

CONFIG = dict(
    datafile = DATAFILE,
    workdir = WORKDIR,
    n = "Number of images to annotate at once (If null, deploy all images.)",
    n_example = "Number of example images of each label(If null, deploy all images.)",
    col_filename = "Column name for image-file name ('index' to use df.index if 'index' not in df.columns)",
    col_img = "Column name of image (containing numpy.ndarray)",
    col_label = "Column name of label",
    labels = "List of initial labels (comma-separated. If null, no initial labels set.)",
    label_null = "String representing to be unannotated (If null, '' represens to be unannotated.)",
    random = "Deploy randomly (1=Select randomly, 0=order by index)",
    imgext = "Image file extension (including .)",
    cmap = "matplotlib.cmap (you can use custom cmap name in cmap.py. If null, use default cmap of seaboarn.heatmap.)",
    vmin = "seaborn.heatmap.vmin (If null, determined automatically.)",
    vmax = "seaborn.heatmap.vmax (If null, determined automatically.)",
    figsize = "matplotlib.pyplot.figure.figsize",
    backup = "Backup (1=Copy datafile to datafile~ before save)",
    verbose = "Verbose (1=Print verbose messages)",
)
