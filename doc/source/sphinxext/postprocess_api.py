"""
Sphinx plugin to run example scripts and create a gallery page.

Lightly modified from the seaborn project (Michael Waskom).
Originally, lightly modified from the mpld3 project.

"""
import os.path as op
from pathlib import Path
import glob
from sphinx.application import Sphinx


def on_build_finished(app: Sphinx, exception: Exception) -> None:
    html_dir = Path(app.builder.outdir)
    api_dir = html_dir / 'api'

    # Check if the index has Jekyll template marks
    index_html = html_dir / 'index.html'
    with open(index_html, 'rt') as f:
        lines = f.readlines()
        # The Jekyll template starts with a --- line
        # Nontemplated HTML starts with some kind of XML tag
        if lines[0] != '---\n':
            return
        mark_end = lines.index('---\n', 1) + 1
        lines_mark = lines[: mark_end]

    # Relative links to stylesheets break, repair them
    for i, line in enumerate(lines_mark):
        pattern = 'href="_static/'
        j = line.find(pattern)
        if j == -1:
            continue
        line = line[:j] + 'href="../_static/' + line[j + len(pattern):]
        lines_mark[i] = line

    # Write individual example files, fixing footers
    for filename in sorted(glob.glob(op.join(api_dir, "*.html"))):
        # Open file
        with open(filename, 'rt') as f:
            content = f.read()
            start = content.find('<head>') + len('<head>')
            end = content.find('</head>', start)
            head, content = content[start: end], content[end:]

            start = content.find('<body>') + len('<body>')
            end = content.find('</body>', start)
            body, _ = content[start: end], content[end:]

        # Exclude title from head
        start = head.find('<title>')
        end = head.find('</title>') + len('</title>')
        head = head[:start] + head[end:]

        # Bootstrap from Jekyll and pydoctor conflict, remove the pydoctor one
        headlines = head.split('\n')
        for i, line in enumerate(headlines):
            if 'bootstrap.min.css' in line:
                break
        head = '\n'.join(headlines[:i] + headlines[i+1:])

        # Repair footer that conflicts with igraph footer
        start_pre = body.find('<footer')
        start = body.find('>', start_pre) + 1
        end = body.find('</footer>', start)
        body, footer = body[:start_pre], body[start: end]
        footer = footer.strip('\n')

        # Patch style of footer
        footer = footer.replace('"container"', '"container-fluid text-muted credit"')

        # Patch-up content for Jekyll
        content = (''.join(lines_mark[:-1]) + 
                   head +
                   'extrafoot:\n' +
                   footer +
                   '\n' +
                   lines_mark[-1] +
                   body)
        with open(filename, 'wt') as f:
            f.write(content)


def setup(app):
    app.connect('build-finished', on_build_finished, priority=900)
