import sys
import os
import glob
import json
import shutil

import click

from .pxd_writer import PxdWriter, parse as parse_c_header
from ..cpp_interop.compiler import compile
from ..binding_generator import generate

pygodot_lib_root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--version', '-V', is_flag=True)
def pygodot(ctx, version):
    if version or not ctx.invoked_subcommand:
        from .. import get_version
        click.echo(f'pygodot v{get_version()}')

        if not version:
            click.echo('Usage: pygodot <command>')

        sys.exit(0)


# Not used
def install_dependencies(project_root, new_lib_root, symlink, force):
    project_files = os.listdir(project_root)
    if 'dist' not in project_files:
        click.echo('Please run py2app/py2exe command to collect Python dependencies')
        return False

    # macOS-only section
    plugin_dirs = glob.glob(os.path.join(project_root, 'dist', '*.plugin'))

    if not plugin_dirs or not os.path.isdir(os.path.join(plugin_dirs[0], 'Contents', 'Resources')):
        click.echo(f'Collected plugin was not found at "{project_root}"')
        return False

    resource_dir = os.path.join(plugin_dirs[0], 'Contents', 'Resources')
    # end macOS

    target_resource_dir = os.path.join(new_lib_root, '_pygodot.env')
    print(resource_dir, target_resource_dir)

    # Run only if there is no target_resource_dir or with a --force flag
    if force and os.path.exists(target_resource_dir):
        if not os.path.islink(target_resource_dir):
            click.echo(f'Please remove "{target_resource_dir}" and try again')
            return False
        # Remove only symlinks, not full directory trees!
        click.echo(f'Removing old destination resources "{target_resource_dir}"')
        os.unlink(target_resource_dir)
    if not os.path.exists(target_resource_dir):
        if symlink:
            os.symlink(resource_dir, target_resource_dir)
        else:
            shutil.copytree(resource_dir, target_resource_dir)
    return True


def ensure_godot_project_path(path):
    godot_root = detect_godot_project(path)

    if not godot_root:
        click.echo('No Godot project detected')
        sys.exit(1)

    return os.path.realpath(godot_root)


def detect_godot_project(dir, fn='project.godot'):
    if not dir or not fn:
        return

    if os.path.isdir(dir) and 'project.godot' in os.listdir(dir):
        return dir

    return detect_godot_project(*os.path.split(dir))


@pygodot.add_command
@click.command()
@click.argument('sourcefile', nargs=-1, type=click.File('r'))
@click.option('--output-dir', '-o')
def compilecpp(sourcefile, **opts):
    if not len(sourcefile):
        click.echo('No source files given')
        sys.exit(1)

    output_dir = opts.get('output_dir')

    for src in sourcefile:
        default_output_dir, filename = os.path.split(os.path.realpath(src.name))
        name, ext = os.path.splitext(filename)

        if not output_dir:
            output_dir = default_output_dir
        elif not os.path.isdir(output_dir):
            click.echo(f'Output directory "{output_dir}" does not exist')
            sys.exit(1)

        compile(src.read(), output_dir, name)


@pygodot.add_command
@click.command()
def genapi():
    output_dir = os.path.join(pygodot_lib_root, 'godot_headers')

    if not os.path.isdir(output_dir):
        click.echo(f'"{output_dir}" does not exist. Something went wrong…')
        sys.exit(1)

    click.echo('Converting\n\tgdnative_api_struct.gen.h -> gdnative_api.pxd\n'
               f'inside "{output_dir}" directory\n')

    inpath = os.path.join(output_dir, 'gdnative_api_struct.gen.h')
    if not os.path.exists(inpath):
        click.echo(f'Required "gdnative_api_struct.gen.h" file doesn\'t exist in "{output_dir}"')
        sys.exit(1)

    os.chdir(output_dir)
    fname = 'gdnative_api_struct.gen.h'

    with open(fname, 'r') as infile:
        code = infile.read()

    extra_cpp_args = ['-I', '.']
    if sys.platform == 'darwin':
        extra_cpp_args += ['-I', "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include"]

    p = PxdWriter(fname)
    p.visit(parse_c_header(code, extra_cpp_args=extra_cpp_args))

    pxd = 'from libc.stdint cimport {:s}\n'.format(', '.join(p.stdint_declarations))
    pxd += 'from libc.stddef cimport wchar_t\nfrom libcpp cimport bool\n\n'
    pxd += str(p)
    pxd = pxd.replace('uint8_t _dont_touch_that[]', 'pass')
    pxd = pxd.replace('extern from "gdnative_api_struct.gen.h":', 'extern from "gdnative_api_struct.gen.h" nogil:')

    with open('gdnative_api.pxd', 'w', encoding='utf-8') as f:
        f.write(pxd)

    with open('__init__.py', 'w', encoding='utf-8') as f:
        pass


@pygodot.add_command
@click.command()
def genbindings():
    generate(pygodot_lib_root, click.echo)
