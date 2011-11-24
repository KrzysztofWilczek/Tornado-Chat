import virtualenv, textwrap
output = virtualenv.create_bootstrap_script(textwrap.dedent("""
def after_install(options, home_dir):
	subprocess.call([join(home_dir, 'bin', 'easy_install'),
		'tornado'])
"""))
print output