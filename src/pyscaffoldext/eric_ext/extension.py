import configparser
import string
from pathlib import Path
from typing import Callable, Dict, List, Tuple, Union

from pyparsing import Optional
from pyscaffold.actions import Action, ActionParams, ScaffoldOpts, Structure
from pyscaffold.extensions import Extension
from pyscaffold.operations import FileOp, no_overwrite
from pyscaffold.structure import get_template, merge
from rich import print

from pyscaffoldext.eric_ext.find_templates import (
    recursively_build_struct_from_templates,
)

NO_OVERWRITE: FileOp = no_overwrite()
THIS_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = THIS_DIR / "templates"


class EricExt(Extension):
    """
    This class serves as the skeleton for your new PyScaffold Extension. Refer
    to the official documentation to discover how to implement a PyScaffold
    extension - https://pyscaffold.org/en/latest/extensions.html
    """

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activate extension. See :obj:`pyscaffold.extension.Extension.activate`."""
        actions = self.register(actions, add_files)
        print("Printing Actions:")
        print(actions)
        return actions


def add_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Add custom extension files. See :obj:`pyscaffold.actions.Action`"""

    # since we are overwriting pyscaffold's official "setup.cfg" with our own template,
    # we need to make sure we add the special [pyscaffold] section to our setup.cfg file.
    # The [pyscaffold] section contains information about the "putup" arguments that
    # were used. It's important to store that in the setup.cfg file so that the
    # "putup PROJECT_PATH --update --force" command works.
    opts["pyscaffold"] = get_section_of_the_official_pyscaffold__setup_cfg__file(
        "pyscaffold", opts=opts, struct=struct
    )

    print("Printing struct")
    print(struct)
    print("Printing opts")
    print(opts)

    files: Structure = recursively_build_struct_from_templates(
        templates_dir=TEMPLATES_DIR, opts=opts
    )
    print("printing recursively generated struct dict")
    print(files)

    return merge(struct, files), opts


def get_proposed_file_as_string(
    path: Union[str, Path], opts: ScaffoldOpts, struct: Structure
):
    """
    Find the path relative to the given struct and render the template as a string.

    A sample struct may look like this:

    .. code-block:: text

        {
            ...
            "setup.cfg": (<function object at 0x101e44670>, <function create at 0x101b561f0>),
            "": (<string.Template object at 0x101e446d0>, <function create at 0x101b561f0>),
            ...
        }

    This function handles the possibility that the files are represented as functions or
    ``string.Template``s.

    :param path: A string or path like ``"src/{{ package }}/__init__.py"`` would have this
        function access and render the Template at ``struct["src"]["{{ package }}"]["__init__.py"]``.
    """
    path_parts = str(path).split("/")

    TFunctionBasedFile = Tuple[Callable[[ScaffoldOpts], str], FileOp]
    TTemplateBasedFile = Tuple[string.Template, FileOp]

    value = None
    for part in path_parts:
        value = struct[part]

    value: Union[TFunctionBasedFile, TTemplateBasedFile]
    template_or_callable, file_op = value

    if isinstance(template_or_callable, string.Template):
        print("it's a template!")
        template: string.Template = template_or_callable
        return str(template)

    print("It's a callable!")
    callable: Callable[[ScaffoldOpts], str] = template_or_callable
    return callable(opts)


# def get_official_pyscaffold_template(import_path: str) -> string.Template:
#     from


def get_section_of_the_official_pyscaffold__setup_cfg__file(
    section: str, opts: ScaffoldOpts, struct: Structure
) -> str:
    setup_cfg = get_proposed_file_as_string("setup.cfg", opts=opts, struct=struct)
    setup_cfg_data: dict = parse_ini_file_to_dict(setup_cfg)
    return dict_to_string(setup_cfg_data[section])


def parse_ini_file_to_dict(cfg: str) -> dict:
    """Parse a the string contents of a ``.ini`` file and return the configuration as a dict."""
    parser = configparser.ConfigParser()
    parser.read_string(cfg)
    return {s: dict(parser.items(s)) for s in parser.sections()}


def dict_to_string(item: Dict[str, str]) -> str:
    """Convert a dictionary to a string."""
    s = ""
    for k, v in item.items():
        v = v.replace("\n", "\n    ")
        s = f"{s}\n{k} = {v}"
    return s
