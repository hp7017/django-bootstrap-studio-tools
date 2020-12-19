import sys
from bs4 import BeautifulSoup, Tag
import shutil
import os

# path where html file will be export
export_add = sys.argv[1]

# extracting exported filenames
files = os.listdir(export_add)

# the whole project path which consist app.py and export
project_add = os.path.dirname(export_add)


def extract_htmls():
    '''function to extract only html file nmaes from files'''

    htmls = [html for html in files if html.split('.')[-1] == 'html']
    return htmls


def convert(infile):
    '''function to convert html block to jinja2 block'''

    # read_again will be True for extending htmls
    read_again = False

    # reading html file and creating a soup
    with open(infile, "r", encoding='utf8') as fp:
        soup = BeautifulSoup(fp)

    # deleting rest(other than block) elements when extends in body
    if soup.body is not None and 'dj-extends' in soup.body.attrs:
        # read_again set true because file need to be
        # read again after deleting some element
        read_again = True

        # extranting all element having block in there attribute
        divs = soup.findAll(attrs={'dj-block': True})

        # extracting which html is extending from
        extend_from = soup.body.attrs['dj-extends']

        # writing only block element rest will be ignored
        with open(infile, 'w') as file:
            file.write(f"{{% extends '{extend_from}' %}}\n")

            # writing static as well because each html
            # needs to have static load
            file.write("{% load static %}\n")

            for div in divs:
                file.write(div.prettify())
    else:
        # writing static as well because each html
        # needs to have static load
        soup.html.insert_before("{% load static %}\n")

    # reading html again if html has changed(extend page case see above)
    if read_again:
        with open(infile, "r", encoding='utf8') as fp:
            soup = BeautifulSoup(fp)

    # handle if
    # eg: <div dj-if="form.errors" >  will get translated to:
    # {% if form.errors %}
    # ...
    # {% endif %}
    for ifs in soup.find_all(attrs={"dj-if": True}):
        if ifs:
            ifline = "{% if " + ifs.get("dj-if") + " %}"
            ifs.insert_before(ifline)
            else_ = ifs.next_sibling
            # check for second next sibling if newline
            # has shifted else block to new line
            second_else_ = else_.next_sibling
            if "dj-if" in ifs.attrs:
                del ifs.attrs["dj-if"]
            if isinstance(else_, Tag):
                if 'dj-else' in else_.attrs:
                    ifs = else_
            elif isinstance(second_else_, Tag):
                if 'dj-else' in second_else_.attrs:
                    ifs = second_else_
            ifs.insert_after("{% endif %}")

    for elses in soup.find_all(attrs={'dj-else': True}):
        if elses:
            elseline = "{% else %}"
            elses.insert_before(elseline)
            if 'dj-else' in elses.attrs:
                del elses.attrs['dj-else']

    # deleting sr-only
    # for srs in soup.find_all(attrs={'class': 'sr-only'}):
    #     if srs:
    #         print(srs)
    #         print(srs.attrs)
    #         # attrs = srs.attrs.get('class', ['sr-only'])
    #         # attrs.remove('sr-only')
    #         # srs.attrs=attrs

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

    # handle block
    for div in soup.find_all(attrs={"dj-block": True}):
        if div:
            blockline = "{% block " + div.get('dj-block') + " %}"
            if read_again:
                div.insert_before(blockline)
                div.insert_after('{% endblock %}')
            else:
                div.insert(0, '{% endblock %}')
                div.insert(0, blockline)
            del div.attrs['dj-block']

    # handle scripts,
    # eg: <script src="https://cdnjs.cloudflare.com/ajax/libs/
    # jquery-easing/1.4.1/jquery.easing.js">
    # eg <script src="{% static "assets/js/theme.js" %}">
    for div in soup.find_all("script"):
        if div:
            if not div.get("src").startswith("http"):
                div.attrs["src"] = "{% static \"" +\
                    div.attrs["src"] + "\" %}"""

    for div in soup.find_all("link"):
        if div:
            if not div.get("href").startswith("http"):
                div.attrs["href"] =\
                    "{% static \"" + div.attrs["href"] + "\" %}"""
    print(infile)
    for div in soup.find_all("img"):
        if div:
            div.attrs["src"] =\
                    '{{{{ url_for(\'static\', filename=\'{0}\')}}}}'.\
                    format(div.attrs["src"])

    # write changes
    with open(infile, "w", encoding='utf8') as outfp:
        outfp.write(soup.prettify())


# def enable_mobile_animation():
#     if os.path.exists(os.path.join(
#         export_add, 'assets',
#         'js', 'bs-animation.js'
#     )):
#         file = open(
#               os.path.join(export_add, 'assets', 'js', 'bs-animation.js'
#              ))
#         content = file.read()
#         c = content[:content.index('AOS.init')+9] +\
#             content[(content.index("{ disable: 'mobile' }")+21):]
#         file = open(os.path.join(
#             export_add, 'assets',
#             'js', 'bs-animation.js'), 'w')
#         file.write(c)
#         file.close()


# trying to delete templates from project folder else pass
try:
    shutil.rmtree(os.path.join(project_add, 'templates'))
except FileNotFoundError:
    pass

# creating folder everytime
os.makedirs(os.path.join(project_add, 'templates'))

# converting html to jinja2 and copy them to project template folder
for html in extract_htmls():
    convert(os.path.join(export_add, html))
    shutil.copy(
        os.path.join(export_add, html),
        os.path.join(project_add, 'templates')
    )

# trying to delete static folder else pass
try:
    shutil.rmtree(os.path.join(project_add, 'static'))
except FileNotFoundError:
    pass

# enable_mobile_animation()

# copying assests as it is into static folder under project dirs
shutil.copytree(
    os.path.join(export_add, 'assets'),
    os.path.join(project_add, 'static', 'assets')
    )
