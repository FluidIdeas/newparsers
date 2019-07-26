mesa_configure = '''
export XORG_PREFIX=/usr

mkdir build &&
cd    build &&

meson --prefix=$XORG_PREFIX          \\
      --sysconfdir=/etc              \\
      -Dllvm=true                    \\
      -Dshared-llvm=true             \\
      -Degl=true                     \\
      -Dshared-glapi=true            \\
      -Dgallium-xa=true              \\
      -Dgallium-nine=true            \\
      -Dgallium-vdpau=true           \\
      -Dgallium-va=true              \\
      -Ddri3=true                    \\
      -Dglx=dri                      \\
      -Dosmesa=gallium               \\
      -Dgbm=true                     \\
      -Dglx-direct=true              \\
      -Dgles1=true                   \\
      -Dgles2=true                   \\
      -Dvalgrind=false               \\
      -Ddri-drivers=auto             \\
      -Dgallium-drivers=auto         \\
      -Dplatforms=auto               \\
      -Dvulkan-drivers=auto          \\
      ..                             &&

unset GALLIUM_DRIVERS DRI_DRIVERS EGL_PLATFORMS &&

ninja
'''

def mesafilter(package, commands):
	if package['name'] == 'mesa':
		new_commands = list()
		for command in commands:
			if 'meson' in command:
				new_commands.append(mesa_configure)
			else:
				new_commands.append(command)
		return (package, new_commands)
	else:
		return (package, commands)

def rustfilter(package, commands):
	if 'rust' in package['dependencies']:
		commands.insert(0, '. /etc/profile.d/rustc.sh')
	return (package, commands)


