# One module per finished object: objects/<name>.py defines build(), which makes the object at its real
# size around the origin (on the floor at z = 0; the desk's parts in desk-local coordinates, its top at
# DESK_H). scene.py and turntable.py use it in place of the stand-in of the same name.
