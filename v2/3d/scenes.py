# Objets 3D Slide Session, construits et rendus dans Blender (sans aucun asset externe).
# Lancement : blender -b --factory-startup -P scenes.py -- <scene> [<frames>]
#   scenes : skis (rotation, séquence d'images), skieur, podium, bonnet
import bpy, bmesh, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['skis']
SCENE = args[0]

BLUE, VIOLET, YELLOW, INK = (0.165, 0.192, 0.706), (0.357, 0.247, 0.847), (1.0, 0.725, 0.216), (0.082, 0.09, 0.31)
PINK, RED, WHITE, BLACK = (0.93, 0.42, 0.68), (0.91, 0.255, 0.235), (0.96, 0.96, 0.97), (0.03, 0.03, 0.05)


def lin(c):  # sRGB -> linéaire (Blender travaille en linéaire)
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'Standard'
    world = bpy.data.worlds.new('w')
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value = lin((0.55, 0.62, 0.85))
    bg.inputs[1].default_value = 0.12
    sc.world = world
    return sc


def mat(name, color, rough=0.35, coat=0.4, metal=0.0, image=None, swap_uv=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = lin(color)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    for k in ('Coat Weight', 'Clearcoat'):
        if k in p.inputs:
            p.inputs[k].default_value = coat
            break
    if image:
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(os.path.join(HERE, image))
        tex.extension = 'EXTEND'
        uv = nt.nodes.new('ShaderNodeTexCoord')
        if swap_uv:  # coordonnées générées : x = longueur, y = largeur
            sep = nt.nodes.new('ShaderNodeSeparateXYZ')
            com = nt.nodes.new('ShaderNodeCombineXYZ')
            nt.links.new(uv.outputs['Generated'], sep.inputs[0])
            nt.links.new(sep.outputs['Y'], com.inputs['X'])
            inv = nt.nodes.new('ShaderNodeMath')
            inv.operation = 'SUBTRACT'
            inv.inputs[0].default_value = 1.0
            nt.links.new(sep.outputs['X'], inv.inputs[1])
            nt.links.new(inv.outputs[0], com.inputs['Y'])
            nt.links.new(com.outputs[0], tex.inputs[0])
        else:
            nt.links.new(uv.outputs['UV'], tex.inputs[0])
        nt.links.new(tex.outputs['Color'], p.inputs['Base Color'])
    return m


def smooth(obj, bevel=0.0, sub=0):
    if bevel:
        b = obj.modifiers.new('bevel', 'BEVEL')
        b.width, b.segments = bevel, 3
    if sub:
        s = obj.modifiers.new('sub', 'SUBSURF')
        s.levels = s.render_levels = sub
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def link(obj):
    bpy.context.collection.objects.link(obj)
    return obj


def ski_mesh(name, length=1.7, seg=80):
    """Ski avec cotes de taille, spatule et talon relevés, épaisseur."""
    bm = bmesh.new()
    rows = []
    for i in range(seg + 1):
        t = i / seg                      # 0 = talon, 1 = spatule
        y = (t - 0.5) * length
        w = 0.052 + 0.014 * (abs(t - 0.5) * 2) ** 2   # plus étroit au patin
        z = 0.012 * math.sin(math.pi * t)             # cambre
        if t > 0.86:
            z += 0.11 * ((t - 0.86) / 0.14) ** 2      # spatule
            w *= 1 - 0.35 * ((t - 0.86) / 0.14) ** 3
        if t < 0.08:
            z += 0.035 * ((0.08 - t) / 0.08) ** 2     # talon
        th = 0.009
        rows.append([bm.verts.new((sx * w, y, z + sz * th)) for sx, sz in ((-1, 1), (1, 1), (1, -1), (-1, -1))])
    for a, b in zip(rows, rows[1:]):
        for k in range(4):
            bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
    bm.faces.new(rows[0][::-1])
    bm.faces.new(rows[-1])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    obj = link(bpy.data.objects.new(name, me))
    smooth(obj, bevel=0.003)
    return obj


def add(prim, name, material, **kw):
    getattr(bpy.ops.mesh, prim)(**kw)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(material)
    return o


def binding(parent, y, top):
    blk = mat('binding', BLACK, rough=0.35, coat=0.6)
    for dy, sx, sz in ((-0.06, 0.05, 0.035), (0.09, 0.045, 0.03)):
        o = add('primitive_cube_add', 'bind', blk, size=1, location=(0, y + dy, top + sz / 2))
        o.scale = (sx * 2, 0.07, sz)
        smooth(o, bevel=0.006)
        o.parent = parent


def lights(key=(3, -4, 5), strength=1.0):
    for loc, power, color, size in ((key, 900, (1, 0.95, 0.88), 3), ((-4, 3, 3), 700, (0.55, 0.6, 1.0), 2), ((0, -6, 1), 110, (1, 1, 1), 6)):
        L = bpy.data.lights.new('l', 'AREA')
        L.energy, L.color, L.size = power * strength, color, size
        o = link(bpy.data.objects.new('l', L))
        o.location = loc
        o.rotation_euler = (Vector((0, 0, 0.6)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()


def camera(loc, target, lens=50, res=(900, 1200)):
    c = bpy.data.cameras.new('cam')
    c.lens = lens
    o = link(bpy.data.objects.new('cam', c))
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc = bpy.context.scene
    sc.camera = o
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def capsule(mb, a, b, r):
    """Capsule de métaboule entre deux points."""
    a, b = Vector(a), Vector(b)
    el = mb.elements.new(type='CAPSULE')
    el.co = (a + b) / 2
    el.radius = r
    el.size_x = (b - a).length / 2
    el.rotation = Vector((1, 0, 0)).rotation_difference(b - a)
    return el


def ball(mb, c, r):
    el = mb.elements.new(type='BALL')
    el.co, el.radius = c, r
    return el


def metaobj(name, material):
    mb = bpy.data.metaballs.new(name)
    mb.resolution, mb.render_resolution, mb.threshold = 0.02, 0.008, 0.6
    o = link(bpy.data.objects.new(name, mb))
    mb.materials.append(material)
    return mb


# ---------------------------------------------------------------- scènes --
def scene_skis(frames):
    reset()
    top = mat('topsheet', BLUE, rough=0.3, coat=0.5, image='tex-ski.png', swap_uv=True)
    pivot = link(bpy.data.objects.new('pivot', None))
    for side in (-1, 1):
        s = ski_mesh('ski%d' % side)
        s.data.materials.append(top)
        binding(s, 0, 0.012)
        holder = link(bpy.data.objects.new('h', None))
        s.parent = holder
        holder.rotation_euler = (math.radians(78), math.radians(13 * side), 0)  # debout, croisés en X
        holder.location = (0.0, 0.03 * side, 0)
        holder.parent = pivot
    lights(key=(3, -4, 3))
    camera((0, -3.6, 0.05), (0, 0, 0.0), lens=55, res=(720, 960))
    for f in range(frames):
        pivot.rotation_euler = (0, 0, 2 * math.pi * f / frames)
        render(os.path.join(OUT, 'skis', 'skis-%03d.png' % f))


def scene_skieur():
    reset()
    jacket = mat('veste', BLUE, rough=0.42, coat=0.3)
    pants = mat('pantalon', INK, rough=0.5, coat=0.2)
    glove = mat('gants', BLACK, rough=0.6, coat=0)
    helmet = mat('casque', YELLOW, rough=0.18, coat=1)
    lens_m = mat('masque', VIOLET, rough=0.05, coat=1, metal=0.6)
    boot = mat('chaussures', WHITE, rough=0.25, coat=0.8)
    pole = mat('batons', (0.75, 0.77, 0.8), rough=0.2, metal=1)
    top = mat('topsheet', BLUE, rough=0.22, coat=0.8, image='tex-ski.png', swap_uv=True)

    # position de descente (recherche de vitesse), le skieur file vers +X
    legs = metaobj('Pantalon', pants)
    body = metaobj('Veste', jacket)
    for s in (-1, 1):
        y = 0.1 * s
        capsule(legs, (0.02, y, 0.14), (0.26, y * 1.05, 0.36), 0.075)   # tibia
        capsule(legs, (0.26, y * 1.05, 0.36), (-0.05, y * 0.9, 0.5), 0.09)  # cuisse
        capsule(body, (0.2, 0.16 * s, 0.77), (0.4, 0.2 * s, 0.58), 0.065)    # bras
        capsule(body, (0.4, 0.2 * s, 0.58), (0.56, 0.15 * s, 0.6), 0.055)    # avant-bras
    capsule(legs, (-0.06, -0.08, 0.52), (-0.06, 0.08, 0.52), 0.11)          # bassin
    capsule(body, (-0.02, 0, 0.56), (0.26, 0, 0.78), 0.16)                  # buste penché
    ball(body, (0.3, 0, 0.82), 0.09)                                        # col

    head = add('primitive_uv_sphere_add', 'casque', helmet, radius=0.125, location=(0.42, 0, 0.93), segments=48, ring_count=24)
    head.scale = (1.08, 0.95, 0.92)
    smooth(head)
    goggles = add('primitive_cylinder_add', 'masque', lens_m, radius=0.065, depth=0.2, location=(0.52, 0, 0.9), vertices=48)
    goggles.rotation_euler = (math.radians(90), 0, 0)
    goggles.scale = (0.7, 1, 1)
    smooth(goggles, bevel=0.01)
    for s in (-1, 1):
        y = 0.1 * s
        g = add('primitive_uv_sphere_add', 'gant', glove, radius=0.055, location=(0.6, 0.15 * s, 0.6))
        smooth(g)
        b = add('primitive_cube_add', 'chaussure', boot, size=1, location=(0.03, y, 0.1))
        b.scale = (0.2, 0.11, 0.17)
        smooth(b, bevel=0.06)
        # bâton glissé sous le bras, vers l'arrière
        a, c = Vector((0.6, 0.15 * s, 0.6)), Vector((-0.55, 0.24 * s, 0.44))
        p = add('primitive_cylinder_add', 'baton', pole, radius=0.009, depth=(c - a).length, location=(a + c) / 2)
        p.rotation_euler = Vector((0, 0, 1)).rotation_difference(c - a).to_euler()
        k = add('primitive_cylinder_add', 'rondelle', glove, radius=0.04, depth=0.01, location=c + (a - c).normalized() * 0.08)
        k.rotation_euler = p.rotation_euler
        sk = ski_mesh('ski', length=1.6)
        sk.data.materials.append(top)
        sk.rotation_euler = (0, 0, math.radians(-90))
        sk.location = (0.05, y, 0.0)
        binding(sk, 0, 0.012)

    lights(key=(2.5, -3.5, 4))
    camera((1.9, -2.6, 1.05), (0.1, 0, 0.45), lens=50, res=(1200, 1000))
    render(os.path.join(OUT, 'skieur.png'))


def scene_podium():
    reset()
    cols = {1: YELLOW, 2: BLUE, 3: VIOLET}
    num = mat('chiffres', WHITE, rough=0.3, coat=0.5)
    for rank, x, h in ((2, -0.56, 0.38), (1, 0, 0.56), (3, 0.56, 0.26)):
        m = mat('marche%d' % rank, cols[rank], rough=0.3, coat=0.7)
        o = add('primitive_cube_add', 'marche', m, size=1, location=(x, 0, h / 2))
        o.scale = (0.54, 0.5, h)
        smooth(o, bevel=0.025)
        bpy.ops.object.text_add(location=(x - 0.075, -0.252, h * 0.5 - 0.1))
        t = bpy.context.active_object
        t.data.body = str(rank)
        t.data.size, t.data.extrude = 0.26, 0.012
        t.rotation_euler = (math.radians(90), 0, 0)
        t.data.materials.append(num if rank != 1 else mat('n1', INK, rough=0.3))
    # drapeau Slide planté sur la 1re marche
    metal = mat('mat', (0.8, 0.82, 0.86), rough=0.2, metal=1)
    pole = add('primitive_cylinder_add', 'mat', metal, radius=0.012, depth=0.9, location=(0.12, 0.05, 0.56 + 0.45))
    bm = bmesh.new()
    nx, nz = 24, 12
    for j in range(nz + 1):
        for i in range(nx + 1):
            u, v = i / nx, j / nz
            bm.verts.new((0.12 + u * 0.62, 0.05 + 0.04 * math.sin(u * 5.5) * u, 1.42 - 0.38 + v * 0.38 - 0.03 * u * u))
    bm.verts.ensure_lookup_table()
    uvl = bm.loops.layers.uv.new()
    for j in range(nz):
        for i in range(nx):
            ids = [j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i]
            f = bm.faces.new([bm.verts[k] for k in ids])
            for loop, k in zip(f.loops, ids):
                loop[uvl].uv = ((k % (nx + 1)) / nx, (k // (nx + 1)) / nz)
    me = bpy.data.meshes.new('drapeau')
    bm.to_mesh(me)
    flag = link(bpy.data.objects.new('drapeau', me))
    fm = mat('drapeau', BLUE, rough=0.6, coat=0, image='tex-flag.png')
    fm.use_backface_culling = False
    flag.data.materials.append(fm)
    smooth(flag)
    lights(key=(2, -4, 4))
    camera((1.4, -3.4, 1.35), (0, 0, 0.55), lens=50, res=(1200, 1000))
    render(os.path.join(OUT, 'podium.png'))


def scene_bonnet():
    reset()
    knit = mat('maille', PINK, rough=0.85, coat=0)
    band = mat('bande', BLUE, rough=0.7, coat=0, image='tex-band.png')
    horn = mat('corne', YELLOW, rough=0.15, coat=1, metal=0.35)
    ear_in = mat('oreille', WHITE, rough=0.8, coat=0)
    dome = add('primitive_uv_sphere_add', 'dome', knit, radius=0.5, location=(0, 0, 0), segments=64, ring_count=32)
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(dome.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.02], context='VERTS')
    bmesh.update_edit_mesh(dome.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    dome.scale = (1, 1, 1.05)
    w = dome.modifiers.new('cotes', 'DISPLACE')  # côtes de maille
    tx = bpy.data.textures.new('rib', 'WOOD')
    tx.wood_type, tx.noise_basis_2 = 'BANDS', 'SIN'
    tx.noise_scale = 0.05
    w.texture, w.strength, w.texture_coords = tx, 0.012, 'GLOBAL'
    sol = dome.modifiers.new('ep', 'SOLIDIFY')
    sol.thickness = 0.02
    smooth(dome, sub=1)
    b = add('primitive_cylinder_add', 'bande', band, radius=0.515, depth=0.2, location=(0, 0, 0.02), vertices=96)
    smooth(b, bevel=0.03)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cylinder_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    # corne torsadée
    c = add('primitive_cone_add', 'corne', horn, radius1=0.085, radius2=0.004, depth=0.42, vertices=48, location=(0.02, -0.04, 0.68))
    c.rotation_euler = (math.radians(-12), math.radians(6), 0)
    smooth(c)
    for k in range(5):  # anneaux de la corne
        t = 0.12 + k * 0.17
        r = 0.085 * (1 - t) + 0.006
        ring = add('primitive_torus_add', 'anneau', horn, major_radius=r, minor_radius=0.011 * (1 - t * 0.6), location=(0, 0, 0))
        ring.parent = c
        ring.location = (0, 0, -0.21 + t * 0.42)
        ring.rotation_euler = (math.radians(-14), 0, 0)
        smooth(ring)
    for s in (-1, 1):
        e = add('primitive_cone_add', 'oreille', knit, radius1=0.13, radius2=0.012, depth=0.27, vertices=32, location=(0.27 * s, 0.05, 0.5))
        e.rotation_euler = (math.radians(-10), math.radians(28 * s), 0)
        e.scale = (1, 0.45, 1)
        smooth(e, sub=1)
        i = add('primitive_cone_add', 'oreille_int', ear_in, radius1=0.06, radius2=0.005, depth=0.14, vertices=32, location=(0.27 * s, 0.0, 0.46))
        i.rotation_euler = e.rotation_euler
        i.scale = (1, 0.3, 1)
        smooth(i, sub=1)
    lights(key=(2, -4, 4))
    camera((0.9, -2.3, 0.9), (0, 0, 0.3), lens=55, res=(1000, 1000))
    render(os.path.join(OUT, 'bonnet.png'))


{'skis': lambda: scene_skis(int(args[1]) if len(args) > 1 else 40),
 'skieur': scene_skieur, 'podium': scene_podium, 'bonnet': scene_bonnet}[SCENE]()
print('SCENE OK', SCENE)
