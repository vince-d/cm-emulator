cm-emulator
===========

3D emulator for the Connection Machine LED matrix. More info at http://www.teco.edu/cm/dev/

Enabling `USE_POST_PROCESSING` might cause lag on older graphics cards, as it currently uses the pyglet feature `pyglet.image.get_buffer_manager().get_color_buffer()`, which effectively reads the back buffer on every frame.



