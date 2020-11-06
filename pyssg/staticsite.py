from pathlib import Path
import shutil
from jinja2 import Template, Environment, ChoiceLoader, FileSystemLoader, select_autoescape
import mimetypes

class StaticSite:
	def __init__(self, root):
		assert Path(root).exists(), "provided root path: '{}', does not exists!".format(root)
		self.root = Path(root)

		# Create Jinja envionment
		theme = Path(self.root, "_theme")
		self.env = Environment(
		    loader=ChoiceLoader([FileSystemLoader(str(theme))]),
		    autoescape=select_autoescape(['html', 'xml'])
		)

	def build(self, watch=True):
		# clean _site folder
		if Path(self.root, "_site").exists():
			shutil.rmtree(Path(self.root, "_site"))

		# generate static files for routes
		for route in self.routes():
			data, mime = self.serve(route)
			if isinstance(data, str):
				folder = Path(self.root, "_site", route[1:])
				folder.mkdir(parents=True, exist_ok=True)
				file = Path(folder, "index.html")
				file.write_text(data)
			elif isinstance(data, bytes):
				file = Path(self.root, "_site", route[1:])
				file.parent.mkdir(parents=True, exist_ok=True)
				file.write_bytes(data)

	def files(self):
		"""return all files, but the exceptions"""
		for file in self.root.rglob("*.*"):
			if file.name.startswith("."):
				pass
			elif file.is_file and any(part.startswith("_") for part in file.parent.parts):
				pass
			elif file.suffix == ".meta":
				pass
			else:
				yield file

	def routes(self):
		"""return all valid routes on website, including the pages and assets"""
		for file in self.files():
			if file.suffix in [".html", ".j2", ".md"]:
				# process page
				if file.stem == "index":
					if file.parent == self.root:
						yield "/"
					else:
						yield "/"+str(file.parent.relative_to(self.root))
				else:
					yield "/"+str(file.relative_to(self.root).with_suffix(""))
			else:
				# process assets
				yield "/"+str(file.relative_to(self.root))

	def process(self, file):
		file = Path(file)
		if file.suffix == ".html":
			# process html
			return file.read_text(), ('text/html', None)
		elif file.suffix == ".j2":
			# process jinja2 template
			t = self.env.from_string(file.read_text())
			return t.render(), ('text/html', None)
		elif file.suffix == ".md":
			# process markdown as jinja2 template
			t = self.env.from_string(file.read_text())
			return t.render(), ('text/html', None)
		else:
			# process assets, potentially rescale file
			mime = mimetypes.guess_type(str(file))
			return file.read_bytes(), mime

	def serve(self, route)->"HTML string":
		"""get content for route, if valid"""

		# Get file for route
		path = Path(self.root, route[1:])
		if path.is_dir():
			# if the path is a dir then get the first index.* file
			path=list(path.glob("index.*") )[0]

		if path.suffix == "":
			# if path has no suffix, find the first matching file
			path = list(path.parent.glob(path.name+".*"))[0]

		if not path.is_file():
			return """
			<html>devserv
				<head></head>
				<body>404</body>
			</html>
			""", ('text/html', None)
		else:
			return self.process(path)

	def tree(self):
		result = {}
		for route in self.routes():
			p = result
			for x in route.split("/"):
				p = p.setdefault(x, {})

		return result


if __name__ == "__main__":
	import logging
	from pathlib import Path
	logging.basicConfig(level=logging.DEBUG)

	# build portfolio
	root = Path("../examples/juditfischer")
	import os
	dic	= {}
	for path in root.rglob("[!_]*"):
		if path.is_dir():
			path = path.relative_to(root)
			print( path.parts )


		# print(file.relative_to(root))
	# site = StaticSite("../examples/juditfischer")
	# for route in site.routes():
	# 	print(route)
	# site.build()



	# print(tree)
	# {'': {
	# 		'cv': {}, 
	# 		'': {}, 
	# 		'assets': {
	# 			'kapcsolo.jpg': {}, 
	# 			'style.css': {}
	# 			}, 
	# 		'mindenkinek': {
	# 			'IMG_3858.jpg': {}, 
	# 			'IMG_8879x.jpg': {}
	# 		}
	# 	}
	# }


