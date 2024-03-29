from typing import Dict, Tuple
import re

def find_children(function_names, function_definition):
    children = []
    for f_name in function_names:
        if f"{f_name}(" in function_definition:
            children.append(f_name)
    return children

def get_f_state_attrs(attr_names, function_definition):
    state_attrs = []
    for attr_name in attr_names:
        pattern = r'\b' + re.escape(attr_name) + \
            r'\b|\b' + re.escape(attr_name) + r'\[\]'
        if re.search(pattern, function_definition):
            state_attrs.append(attr_name)
    return state_attrs


def annotate_tree_if_leaf(
    f_name,
    function_annotation,
) -> Tuple[Dict[str, Dict[str, str]], bool]:
    # Pre: f_name is a recursive function

    # Base Case: All children are annotated
    children = function_annotation[f_name]["children"]
    all_children_annotated = True
    min_mutex_dim = float('inf')
    dep_state_attr = {}
    for child in children:
        if "mutex_dim" not in function_annotation[child] \
         or function_annotation[child]["mutex_dim"] is None:
            all_children_annotated = False
            break
        else:
            min_mutex_dim = min(
                min_mutex_dim,
                function_annotation[child]["mutex_dim"]
            )
            # Union of the children dep_state_attr and current based on keys
            for key in function_annotation[child]["dep_state_attr"].keys():
                dep_state_attr[key] = function_annotation[child]["dep_state_attr"][key]

    if all_children_annotated:
        function_annotation[f_name]["mutex_dim"] = min_mutex_dim
        function_annotation[f_name]["dep_state_attr"] = dep_state_attr
        return function_annotation, True
    else:
        return function_annotation, False



def recursive_annotation(function_annotation, attr_dimensions) -> Dict[str, Dict[str, str]]:
    recursive_f_names = []

    # Base Case: Annotate as much as possible (leaves)
    for f_name, f_annot in function_annotation.items():
        non_recursive = True
        f_def_code = f_annot["definition"]

        # Step 1: Check if the function uses another function
        if f_annot["children"]!=[]:
            non_recursive = False
            recursive_f_names.append(f_name)


        # Step 2: If non-recursive, set function state equal to min. dim
        #         calculate via min value of state attribute
        if non_recursive:
            min_attr_dim = 3
            dep_state_attr = {}
            for attr_name, attr_dim in attr_dimensions.items():
                if attr_name in f_def_code:
                    min_attr_dim = min(
                        attr_dim,
                        min_attr_dim,
                    )
                    dep_state_attr[attr_name] = attr_dim
            function_annotation[f_name]["mutex_dim"] = min_attr_dim
            function_annotation[f_name]["dep_state_attr"] = dep_state_attr


    if not recursive_f_names:
        # There are no recursive f_names, we are done
        return function_annotation

    # Assumption: No Circular Definition
    # Recursive Step: Keep annotating until all are annotated
    recursive_f_names = set(recursive_f_names)
    while recursive_f_names:
        for f_name in list(recursive_f_names):
            function_annotation, annotated = annotate_tree_if_leaf(
                f_name,
                function_annotation,
            )
            if annotated:
                recursive_f_names.remove(f_name)

    return function_annotation

