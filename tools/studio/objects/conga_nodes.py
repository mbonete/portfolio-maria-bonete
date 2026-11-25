# A small shader-node vocabulary for the conga's materials: make a node, wire its inputs from numbers,
# colours or other sockets, and a few arithmetic shorthands, so a node graph reads as a few lines.
import bpy


def tree(name):
    """A new material with an empty node tree and its output node."""
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.target = "CYCLES"
    return m, nt, out


def _sock(coll, key):
    if isinstance(key, int):
        return coll[key]
    for s in coll:
        if s.identifier == key:
            return s
    for s in coll:
        if s.name == key and s.enabled:
            return s
    for s in coll:
        if s.name == key:
            return s
    raise KeyError(key)


def wire(nt, sock, v):
    if isinstance(v, bpy.types.NodeSocket):
        nt.links.new(v, sock)
    elif isinstance(v, bpy.types.Node):
        nt.links.new(v.outputs[0], sock)
    else:
        if sock.type == "RGBA" and len(v) == 3:
            v = (*v, 1.0)
        sock.default_value = v


def node(nt, kind, inputs=None, **props):
    n = nt.nodes.new(kind)
    for k, v in props.items():
        setattr(n, k, v)
    for k, v in (inputs or {}).items():
        wire(nt, _sock(n.inputs, k), v)
    return n


def out(n, key=0):
    return _sock(n.outputs, key)


def math(nt, op, a, b=0.0, c=None, clamp=False):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    wire(nt, n.inputs[0], a)
    wire(nt, n.inputs[1], b)
    if c is not None:
        wire(nt, n.inputs[2], c)
    return n.outputs[0]


def add(nt, a, b, clamp=False):
    return math(nt, "ADD", a, b, clamp=clamp)


def mul(nt, a, b, clamp=False):
    return math(nt, "MULTIPLY", a, b, clamp=clamp)


def mad(nt, a, b, c, clamp=False):
    return math(nt, "MULTIPLY_ADD", a, b, c, clamp=clamp)


def remap(nt, v, a0, a1, b0=0.0, b1=1.0, smooth=False, clamp=True):
    n = nt.nodes.new("ShaderNodeMapRange")
    n.interpolation_type = "SMOOTHSTEP" if smooth else "LINEAR"
    n.clamp = clamp
    wire(nt, n.inputs["Value"], v)
    n.inputs["From Min"].default_value = a0
    n.inputs["From Max"].default_value = a1
    n.inputs["To Min"].default_value = b0
    n.inputs["To Max"].default_value = b1
    return n.outputs[0]


def mix(nt, fac, a, b, blend="MIX", clamp=True):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    n.blend_type = blend
    n.clamp_result = clamp
    wire(nt, _sock(n.inputs, "Factor_Float"), fac)
    wire(nt, _sock(n.inputs, "A_Color"), a)
    wire(nt, _sock(n.inputs, "B_Color"), b)
    return _sock(n.outputs, "Result_Color")


def mixf(nt, fac, a, b):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "FLOAT"
    wire(nt, _sock(n.inputs, "Factor_Float"), fac)
    wire(nt, _sock(n.inputs, "A_Float"), a)
    wire(nt, _sock(n.inputs, "B_Float"), b)
    return _sock(n.outputs, "Result_Float")


def vec(nt, op, a, b=None, scale=None):
    n = nt.nodes.new("ShaderNodeVectorMath")
    n.operation = op
    wire(nt, n.inputs[0], a)
    if b is not None:
        wire(nt, n.inputs[1], b)
    if scale is not None:
        wire(nt, _sock(n.inputs, "Scale"), scale)
    return n.outputs["Value" if op in ("LENGTH", "DOT_PRODUCT", "DISTANCE") else "Vector"]


def xyz(nt, v):
    n = node(nt, "ShaderNodeSeparateXYZ", {"Vector": v})
    return n.outputs["X"], n.outputs["Y"], n.outputs["Z"]


def combine(nt, x, y, z):
    n = nt.nodes.new("ShaderNodeCombineXYZ")
    wire(nt, n.inputs[0], x)
    wire(nt, n.inputs[1], y)
    wire(nt, n.inputs[2], z)
    return n.outputs[0]


def noise(nt, vector, scale, detail=2.0, rough=0.5, distortion=0.0, lac=2.0, dims="3D", w=0.0, kind="FBM"):
    n = node(nt, "ShaderNodeTexNoise", {"Vector": vector, "Scale": scale, "Detail": detail, "Roughness": rough,
                                         "Distortion": distortion, "Lacunarity": lac},
             noise_dimensions=dims, noise_type=kind)
    if dims == "4D":
        n.inputs["W"].default_value = w
    return n


def ramp(nt, fac, stops, interp="LINEAR"):
    n = nt.nodes.new("ShaderNodeValToRGB")
    wire(nt, n.inputs[0], fac)
    cr = n.color_ramp
    cr.interpolation = interp
    while len(cr.elements) > 1:
        cr.elements.remove(cr.elements[-1])
    cr.elements[0].position = stops[0][0]
    cr.elements[0].color = (*stops[0][1], 1)
    for p, c in stops[1:]:
        e = cr.elements.new(p)
        e.color = (*c, 1)
    return n.outputs[0]


def bump(nt, height, strength, distance, normal=None):
    n = node(nt, "ShaderNodeBump", {"Height": height, "Strength": strength, "Distance": distance})
    if normal is not None:
        wire(nt, n.inputs["Normal"], normal)
    return n.outputs[0]


def attr(nt, name, out_name="Fac"):
    n = node(nt, "ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name=name)
    return n.outputs[out_name]


def objpos(nt):
    return node(nt, "ShaderNodeTexCoord").outputs["Object"]


def principled(nt, **inputs):
    return node(nt, "ShaderNodeBsdfPrincipled", {k.replace("_", " "): v for k, v in inputs.items()})
