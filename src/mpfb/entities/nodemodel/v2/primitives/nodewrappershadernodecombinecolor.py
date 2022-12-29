import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "color": {
            "class": "Color",
            "name": "color",
            "value": [
                0.608,
                0.608,
                0.608
            ]
        },
        "height": {
            "class": "float",
            "name": "height",
            "value": 100.0
        },
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "mode": {
            "class": "enum",
            "name": "mode",
            "value": "RGB"
        },
        "use_custom_color": {
            "class": "bool",
            "name": "use_custom_color",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeCombineColor",
    "inputs": {
        "Blue": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Blue",
            "name": "Blue",
            "value_type": "VALUE"
        },
        "Green": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Green",
            "name": "Green",
            "value_type": "VALUE"
        },
        "Red": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Red",
            "name": "Red",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeCombineColor(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snCombineColor = _NodeWrapperShaderNodeCombineColor()
