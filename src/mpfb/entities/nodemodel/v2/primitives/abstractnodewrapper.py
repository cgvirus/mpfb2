import bpy
from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("nodemodel.v2.abstractnodewrapper")

_VALID_ARRAY_TYPES = ["tuple", "list", "array", "Vector", "Color", "NodeSocketColor", "NodeSocketVector"]
_VALID_NUMERIC_TYPES = ["int", "float", "NodeSocketFloat", "NodeSocketFloatFactor", "NodeSocketInt", "NodeSocketIntFactor"]
_VALID_STRING_TYPES = ["str", "enum"]

class AbstractNodeWrapper():

    def __init__(self, node_def):
        self.node_def = node_def
        self.node_class_name = self.node_def["class"]

    def _validate_names(self, input_socket_values=None, attribute_values=None, output_socket_values=None):
        if input_socket_values:
            for key in input_socket_values:
                if not key in self.node_def["inputs"]:
                    _LOG.error(key + " is not a valid input socket for " + self.node_class_name)
                    raise ValueError(key + " is not a valid input socket for " + self.node_class_name)
        if output_socket_values:
            for key in output_socket_values:
                if not key in self.node_def["outputs"]:
                    _LOG.error(key + " is not a valid output socket for " + self.node_class_name)
                    raise ValueError(key + " is not a valid output socket for " + self.node_class_name)
        if attribute_values:
            for key in attribute_values:
                if not key in self.node_def["attributes"]:
                    _LOG.error(key + " is not a valid attribute for " + self.node_class_name)
                    raise ValueError(key + " is not a valid attribute for " + self.node_class_name)

    def _find_socket(self, socket_list, socket_id):
        for socket in socket_list:
            if socket.identifier == socket_id:
                return socket
        for socket in socket_list:
            if socket.name == socket_id:
                return socket
        return None

    def _check_is_valid_assignment(self, value, definition_class):
        value_class = type(value).__name__
        if value_class == definition_class:
            return True
        if value_class in _VALID_NUMERIC_TYPES and definition_class in _VALID_NUMERIC_TYPES:
            return True
        if value_class in _VALID_ARRAY_TYPES and definition_class in _VALID_ARRAY_TYPES:
            return True
        if value_class in _VALID_STRING_TYPES and definition_class in _VALID_STRING_TYPES:
            return True
        return False

    def _set_attributes(self, node, attribute_values, forgiving=False):
        if not attribute_values:
            return
        for key in attribute_values:
            value = attribute_values[key]
            attribute = self.node_def["attributes"][key]
            if not self._check_is_valid_assignment(value, attribute["class"]):
                _LOG.error("Cannot use '" + str(value) + "' as value for " + key + " attribute of " + self.node_class_name + ". Expected value of type " + attribute["class"] + ".")
                raise ValueError("Cannot use '" + str(value) + "' as value for " + key + " attribute of " + self.node_class_name + ". Expected value of type " + attribute["class"] + ".")
            setattr(node, key, value)

    def _set_input_sockets(self, node, input_socket_values, forgiving=False):
        if not input_socket_values:
            return
        for key in input_socket_values:
            value = input_socket_values[key]
            input = self.node_def["inputs"][key]
            if not self._check_is_valid_assignment(value, input["class"]):
                _LOG.error("Cannot use '" + str(value) + "' as value for " + key + " input of " + self.node_class_name + ". Expected value of type " + input["class"] + ".")
                raise ValueError("Cannot use '" + str(value) + "' as value for " + key + " input of " + self.node_class_name + ". Expected value of type " + input["class"] + ".")
            input_socket = self._find_socket(node.inputs, key)
            if not input_socket:
                _LOG.error("Input socket '" + key + "' was valid per the original definition, but does not exist on node with class " + node.__class__.__name__)
                raise KeyError("Input socket '" + key + "' was valid per the original definition, but does not exist on node with class " + node.__class__.__name__)
            input_socket.default_value = value

    def _set_output_sockets(self, node, output_socket_values, forgiving=False):
        if not output_socket_values:
            return
        for key in output_socket_values:
            value = output_socket_values[key]
            output = self.node_def["outputs"][key]
            if not self._check_is_valid_assignment(value, output["class"]):
                _LOG.error("Cannot use '" + str(value) + "' as value for " + key + " output of " + self.node_class_name + ". Expected value of type " + output["class"] + ".")
                raise ValueError("Cannot use '" + str(value) + "' as value for " + key + " output of " + self.node_class_name + ". Expected value of type " + output["class"] + ".")
            output_socket = self._find_socket(node.outputs, key)
            if not output_socket:
                _LOG.error("Output socket '" + key + "' was valid per the original definition, but does not exist on node with class " + node.__class__.__name__)
                raise KeyError("Output socket '" + key + "' was valid per the original definition, but does not exist on node with class " + node.__class__.__name__)
            if hasattr(output_socket, "default_value"):
                output_socket.default_value = value
            else:
                _LOG.warn("Output socket did not have default_value attribute", output_socket)

    def _is_same(self, value_class, node_value, default_value):
        if node_value is None:
            return True
        if value_class in _VALID_ARRAY_TYPES:
            for i in range(len(node_value)):
                delta = node_value[i] - default_value[i]
                if abs(delta) > 0.00009:
                    return False
            return True
        if value_class in _VALID_NUMERIC_TYPES:
            delta = node_value - default_value
            return abs(delta) < 0.00009
        return node_value == default_value

    def _cleanup(self, value):
        if type(value).__name__ in ["Vector", "Color"]:
            return list(value)
        return value

    def find_non_default_settings(self, node):
        if node.__class__.__name__ != self.node_class_name:
            raise ValueError("Cannot compare " + node.__class__.__name__ + " with " + self.node_class_name)

        comparison = dict()
        comparison["attribute_values"] = dict()
        comparison["input_socket_values"] = dict()
        comparison["output_socket_values"] = dict()

        for key in self.node_def["attributes"]:
            attribute = self.node_def["attributes"][key]
            default_value = attribute["value"]
            node_value = getattr(node, attribute["name"])
            value_class = attribute["class"]
            if not self._is_same(value_class, node_value, default_value):
                comparison["attribute_values"][key] = self._cleanup(node_value)

        for key in self.node_def["inputs"]:
            socket_def = self.node_def["inputs"][key]
            default_value = socket_def["default_value"]
            socket = self._find_socket(node.inputs, socket_def["identifier"])
            node_value = None
            if hasattr(socket, "default_value"):
                node_value = socket.default_value
            value_class = socket_def["class"]
            if not self._is_same(value_class, node_value, default_value):
                comparison["input_socket_values"][key] = self._cleanup(node_value)

        for key in self.node_def["outputs"]:
            socket_def = self.node_def["outputs"][key]
            default_value = socket_def["default_value"]
            socket = self._find_socket(node.outputs, socket_def["identifier"])
            node_value = None
            if hasattr(socket, "default_value"):
                node_value = socket.default_value
            value_class = socket_def["class"]
            if not self._is_same(value_class, node_value, default_value):
                comparison["output_socket_values"][key] = self._cleanup(node_value)

        return comparison

    def create_instance(self, node_tree, name=None, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
        self.pre_create_instance(node_tree)
        self._validate_names(input_socket_values, attribute_values, output_socket_values)
        node = node_tree.nodes.new(self.node_class_name)
        self._set_attributes(node, attribute_values)
        self._set_input_sockets(node, input_socket_values)
        self._set_output_sockets(node, output_socket_values)
        if name:
            node.name = name
        if label:
            node.label = label
        else:
            if name:
                node.label = name
        return node

    def pre_create_instance(self, node_tree):
        pass
