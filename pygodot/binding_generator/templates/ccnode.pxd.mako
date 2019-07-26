# Generated by PyGodot binding generator
<%!
  from pygodot.binding_generator import python_module_name, remove_nested_type_prefix
  enum_values = set()
  def clean_value_name(value_name):
    enum_values.add(value_name)
    return remove_nested_type_prefix(value_name)
%>
from godot_headers.gdnative_api cimport *
from ..cctypes cimport *
% if class_def['base_class']:
from .${python_module_name(class_def['base_class'])} cimport ${class_def['base_class']}
% endif
% for included_from, included in includes:
from .${python_module_name(included_from)} cimport ${included}
% endfor

cdef extern from "${class_name}.cpp" namespace "godot" nogil:
    cdef cppclass ${class_name}(${class_def['base_class'] or '_Wrapped'}):
% for enum in class_def['enums']:
        enum ${enum['name'].lstrip('_')}:
    % for value_name, value in enum['values'].items():
            ${clean_value_name(value_name)} = ${value}
    % endfor

% endfor
% for method_name, return_type, args, signature in methods:
        ${return_type}${method_name}(${signature})
% endfor
% if not methods:
        pass
% endif

% for name, value in class_def['constants'].items():
    % if name not in enum_values:
    cdef int ${python_module_name(class_name).upper()}_${name} "godot::${class_name}::${name}" = ${value}
    % endif
% endfor
