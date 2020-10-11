import sys
from bs4 import BeautifulSoup
import shutil
import os

# convert a file from Bootstrap Studio to Django Template

export_add = sys.argv[1]
filename = sys.argv[2]
htmls = os.listdir(export_add)
project_add = os.path.dirname(export_add)
htmls = [html for html in htmls if html.split('.')[-1] == 'html']

# infile = sys.argv[-1]
def convert(infile):
	with open(infile, "r") as fp:
		soup = BeautifulSoup(fp, "lxml")

	# handle load
	for div in soup.find_all(attrs={"dj-load": True}):
		if div:
			forline = "{% load " + div.get('dj-load') + " %}"
			div.insert_before(forline)
			del div

	# handle for
	for div in soup.find_all(attrs={"dj-for": True}):
		if div:
			forline = "{% for " + div.get('dj-for') + " %}"
			div.insert_before(forline)
			if 'dj-for' in div.attrs:
				del div.attrs['dj-for']
				div.insert_after('{% endfor %}')

	# handle refs
	for ref in soup.find_all(attrs={"dj-ref": True}):
		if ref:
			if 'dj-ref' in ref.attrs:
				refattr = ref.get('dj-ref')
				if ref.string:
					ref.string.replace_with('{{ ' + refattr + ' }}')
				del ref.attrs['dj-ref']

	# handle if
	# eg: <div dj-if="form.errors" >  will get translated to: 
	# {% if form.errors %}
	# ...
	# {% endif %}
	for ifs in soup.find_all(attrs={"dj-if": True}):
		if ifs:
			ifline = "{% if " + ifs.get("dj-if") + " %}"
			ifs.insert_before(ifline)
			if "dj-if" in ifs.attrs:
				del ifs.attrs["dj-if"]
				ifs.insert_after("{% endif %}")

				
	# handle block
	for div in soup.find_all(attrs={"dj-block": True}):
		if div:
			blockline = "{% block " + div.get('dj-block') + " %}"
			div.insert_before(blockline)
			if 'dj-block' in div.attrs:
				del div.attrs['dj-block']
				div.insert_after('{% endblock %}')
	 
	# handle scripts,
	# eg: <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-easing/1.4.1/jquery.easing.js">
	# eg <script src="{% static "assets/js/theme.js" %}">
	for div in soup.find_all("script"):
		if div:
			if not div.get("src").startswith("http"):
				add = div.attrs["src"].split('/')[2:]
				add = '/'.join(add)
				div.attrs["src"] = "{% static \"" + filename + '/' + add + "\" %}"""
				
	for div in soup.find_all("link"):
		if div:
			if not div.get("href").startswith("http"):
				add = div.attrs["href"].split('/')[2:]
				add = '/'.join(add)
				div.attrs["href"] = "{% static \"" + filename + '/' + add + "\" %}"""

	for div in soup.find_all("img"):
		if div:
			add = div.attrs["src"].split('/')[2:]
			add = '/'.join(add)
			div.attrs["src"] = "{% static \"" + filename + '/' + add + "\" %}"""
				
	for csrf in soup.find_all(attrs={"dj-csrf": True}):
		if csrf:
			csrf.insert(0, "{% csrf_token %}")
			if "dj-csrf" in csrf.attrs:
				del csrf.attrs["dj-csrf"]

	#print(soup.prettify())
	# handle extends
	with open(infile, "w") as outfp:
		if 'dj-extends' in soup.body.attrs.keys():
			outfp.write("{% extends '" + filename + soup.body.get('dj-extends') + "' %}\n")
		outfp.write("{% load static %}\n")
		outfp.write(soup.prettify())

try:
	shutil.rmtree(os.path.join(project_add, 'templates', filename))
except FileNotFoundError as e:
	os.makedirs(os.path.join(project_add, 'templates', filename))
for html in htmls:
	convert(os.path.join(export_add, html))
	shutil.copy(os.path.join(export_add, html), os.path.join(project_add, 'templates', filename))

try:
	shutil.rmtree(os.path.join(project_add, 'static', filename))
except FileNotFoundError as e:
	shutil.copytree(os.path.join(export_add, 'assets'), os.path.join(project_add, 'static', filename))