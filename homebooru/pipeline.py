# This is used to automate the creation of the pipeline configuration
# I wanted to make sure that files are minified on a file-to-file basis rather than merging all files into one
# While this might cause slight overhead overall, some files are used only one some pages and not others.

import pathlib

# Base configuration
config = {
    'PIPELINE_ENABLED': True,
    'DISABLE_WRAPPER': True,

    'CSS_COMPRESSOR': 'pipeline.compressors.yuglify.YuglifyCompressor',
    'JS_COMPRESSOR': 'pipeline.compressors.yuglify.YuglifyCompressor',

    # Stylesheets
    'STYLESHEETS': {},

    # Javascript
    'JAVASCRIPT': {}
}

def add_resource(path : str, pipeline_resource_type : str):
    """Adds a resource file to the pipeline config"""

    name = pathlib.Path(path).parts[-1]

    # Add the file to the config
    config[pipeline_resource_type][name] = {
        'source_filenames': (
            path,
        ),
        'output_filename': path
    }

def add_resources(static_path : str, resource_type : str):
    """
    Adds a folder of resources to the pipeline config.
    
    Note, it ignores third-party files (i.e. files in a folder called 'third-party')
    """

    # Get the type of resource
    r_type = {
        'css': 'STYLESHEETS',
        'js': 'JAVASCRIPT'
    }[resource_type]

    # Get the path
    _path = pathlib.Path(static_path) / resource_type

    # Get the glob pattern
    _glob = '**/*.' + resource_type

    # Get the files
    for path in pathlib.Path(_path).glob(_glob):
        # Make sure that the path ends with the correct extension
        if not str(path).endswith(resource_type):
            continue

        # Make the path relative to the the static directory
        path = path.relative_to(static_path)

        # Make sure it isn't in the thirdparty directory
        if path.parts[1] == 'thirdparty': continue

        # Add the resource
        add_resource(str(path), r_type)

# Booru
add_resources('booru/static', 'css') # Stylesheets
add_resources('booru/static', 'js')  # JavaScript