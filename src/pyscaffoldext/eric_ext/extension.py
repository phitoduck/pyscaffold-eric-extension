import string
from pathlib import Path
from typing import List

from pyscaffold.actions import Action, ActionParams, ScaffoldOpts, Structure
from pyscaffold.extensions import Extension
from pyscaffold.operations import FileOp, no_overwrite
from pyscaffold.structure import merge
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
