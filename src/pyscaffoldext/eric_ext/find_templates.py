import os
from copy import deepcopy
from pathlib import Path
from string import Template
from typing import Dict, List, Tuple, Union

from pyscaffold.actions import ScaffoldOpts, Structure
from pyscaffold.operations import FileOp, create


def recursively_build_struct_from_templates(
    templates_dir: Path, opts: ScaffoldOpts
) -> Structure:
    """
    Recurse through the templates in the template directory and create a nested struct dict.

    The struct dict has the following properties:

    1. Occurences of ``"template"`` and ``".template"`` have been removed from the
       template file names.
    2. Folders whose name match ``{{ some_opt }}`` will be renamed to ``opts["some_opt"]``
    3. The final tuples contain template contents and ``create`` File operations.

    Consider this example:

    .. code-block:: python

        fpaths = [
            Path('template.Dockerfile'),
            Path('TEST-ROOT-DIR.template.md'),
            Path('template.gitignore'),
            Path('src/{{ package }}/sub_package/__init__.template.py')
        ]
        recursively_build_struct_from_templates({"package": "eric-ext"})

    The above input should produce this output:

    .. code-block:: python

        {
            'src': {
                'eric-ext': {
                    'sub_package': {
                        '__init__.py': (<string.Template object at 0x109325130>, <function create at 0x1090e35e0>)
                    }
                }
            },
            'Dockerfile': (<string.Template object at 0x109325580>, <function create at 0x1090e35e0>),
            'gitignore': (<string.Template object at 0x109325040>, <function create at 0x1090e35e0>),
            'TEST-ROOT-DIR.md': (<string.Template object at 0x109325850>, <function create at 0x1090e35e0>)
        }
    """
    relative_template_fpaths = set(
        get_all_template_fpaths_relative_to_templates_dir(templates_dir)
    )

    nested_dict_with_placeholders = get_nested_dict_from_fpaths(
        relative_template_fpaths
    )

    nested_dict_with_placeholders_and_tuples = fill_struct_dict_with_template_tuples(
        relative_template_fpaths,
        nested_dict_with_placeholders,
        templates_dir=templates_dir,
    )

    nested_dict_without_placeholders = substitute_placeholder_keys_with_opts(
        nested_dict_with_placeholders_and_tuples, opts
    )

    nested_dict = recursively_remove_template_from_key_strings(
        nested_dict_without_placeholders
    )

    return nested_dict


def fill_struct_dict_with_template_tuples(
    template_fpaths: List[Path],
    nested_dict_with_placeholders: dict,
    templates_dir: Path,
):
    """Traverse the file tree dict for each fpath and place a ``(Template, create)`` tuple as a leaf node."""
    nested_dict_with_placeholders_copy = deepcopy(nested_dict_with_placeholders)

    for path in template_fpaths:
        path_parts = str(path).split("/")

        d = nested_dict_with_placeholders_copy
        for part in path_parts:
            if d[part] == {}:
                d[part] = make_pyscaffold_struct_file_tuple(templates_dir / path)
                break

            d = d[part]

    return nested_dict_with_placeholders_copy


def substitute_placeholder_keys_with_opts(
    dict_with_placeholders: dict, opts: ScaffoldOpts
) -> dict:
    """Replace key names of the form ``{{ some_opt }}`` in the dict with ``opt["some_opt"]`` recursively."""

    def substitute_opts(d: Dict[str, Union[Dict, Tuple]]):
        new = {}
        for k, v in d.items():
            if isinstance(v, dict):
                v = substitute_opts(v)
            new_key_name = opts.get(
                get_opt_name_from_templated_string(k)
                if is_placeholder_string(k)
                else None,
                k,
            )
            new[new_key_name] = v
        return new

    d = substitute_opts(dict_with_placeholders)

    return d


def recursively_remove_template_from_key_strings(
    dict_with_template_string_keys: dict,
) -> dict:
    """Remove occurrences of ``template.`` and ``template`` from key names recursively."""

    def rename_keys(d: Dict[str, Union[Dict, Tuple]]):
        new = {}
        for k, v in d.items():
            if isinstance(v, dict):
                v = rename_keys(v)
            new_key_name = remove_template_from_string(k)
            new[new_key_name] = v
        return new

    d = rename_keys(dict_with_template_string_keys)

    return d


def is_placeholder_string(string: str):
    return string.startswith("{{") and string.endswith("}}")


def make_pyscaffold_struct_file_tuple(template_fpath: Path) -> Tuple[Template, FileOp]:
    template = get_template_from_fpath(template_fpath)
    file_op: FileOp = create
    return template, file_op


def get_opt_name_from_templated_string(templated_string: str) -> str:
    return templated_string.lstrip("{{").rstrip("}}").strip()


def get_nested_dict_from_fpaths(fpaths: List[Path]) -> dict:
    """
    Convert a list of file paths to a nested tree structure simulating a file tree.

    >>> from pathlib import Path
    >>> from pprint import pprint
    >>>
    >>> nested_dict = get_nested_dict_from_fpaths([
    ...     Path('template.Dockerfile'),
    ...     Path('TEST-ROOT-DIR.template.md'),
    ...     Path('template.gitignore'),
    ...     Path('src/{{ package }}/sub_package/__init__.template.py')
    ... ])
    >>> pprint(nested_dict)
    {'TEST-ROOT-DIR.template.md': {},
     'src': {'{{ package }}': {'sub_package': {'__init__.template.py': {}}}},
     'template.Dockerfile': {},
     'template.gitignore': {}}

    Any path that maps to an empty ``{}`` (dict) is a file. There are no
    empty directories since those cannot be committed to git.
    """
    split_fpaths: List[List[str]] = [str(fpath).split("/") for fpath in fpaths]
    file_tree_structure: dict = get_nested_dict_from_list_of_lists(split_fpaths)
    return file_tree_structure


def get_nested_dict_from_list_of_lists(l: List[List[str]]) -> dict:
    """
    Convert the list of lists into a nested tree.

    This example should help this make sense:

    >>> assert get_nested_dict_from_list_of_lists([[1, 2, 3], [1, 2, 4]]) == {1: {2: {3: {}, 4: {}}}}
    """
    d = {}

    for path in l:
        current_level = d
        for part in path:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

    return d


def get_template_from_fpath(fpath: Path) -> Template:
    """Retrieve the template by filepath."""
    data = fpath.read_text(encoding="utf-8")
    # we assure that line endings are converted to '\n' for all OS
    content = data.replace(os.linesep, "\n")
    return Template(content)


def get_all_template_fpaths_relative_to_templates_dir(
    templates_dir: Path,
) -> List[Path]:
    template_fpaths: List[Path] = templates_dir.glob("**/*template*")
    template_fpaths_relative_to_template_dir = [
        path.relative_to(templates_dir) for path in template_fpaths
    ]
    return template_fpaths_relative_to_template_dir


def remove_template_from_string(string: str) -> Path:
    fname_without_dot_template = (
        string.replace("template_", "").replace("template.", "").replace("template", "")
    )
    return fname_without_dot_template


if __name__ == "__main__":
    from rich import print

    print(get_all_template_fpaths_relative_to_templates_dir())

    print(recursively_build_struct_from_templates({"package": "eric-ext"}))
