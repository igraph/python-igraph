"""
Sphinx plugin to run example scripts and create a gallery page.

Lightly modified from the seaborn project (Michael Waskom).
Originally, lightly modified from the mpld3 project.

"""
import os.path as op
import glob
from sphinx.application import Sphinx


def on_build_finished(app: Sphinx, exception: Exception) -> None:
    html_dir = op.abspath(app.builder.outdir)
    api_dir = op.join(html_dir, 'api')

    # Check if the index has Jekyll template marks
    has_jekyll_marks = False
    index_html = op.join(html_dir, 'index.html')
    with open(index_html, 'rt') as f:
        lines = f.readlines()
        if sum(line == '---\n' for line in lines) == 2:
            has_jekyll_marks = True
        mark_start = lines.index('---\n')
        mark_end = lines[mark_start + 1:].index('---\n') + mark_start + 2
        lines_mark = lines[mark_start: mark_end]

    if not has_jekyll_marks:
        return

    # Write individual example files
    for filename in sorted(glob.glob(op.join(api_dir, "*.html"))):
        # Open file
        with open(filename, 'rt') as f:
            content = f.read()
            start = content.find('<head>') + len('<head>')
            end = content[start:].find('</head>') + start
            head, content = content[start:end], content[end:]

            start = content.find('<body>') + len('<body>')
            end = content[start:].find('</body>') + start
            body, _ = content[start:end], content[end:]

        # Exclude title from head
        start = head.find('<title>')
        end = head.find('</title>') + len('</title>')
        head = head[:start] + head[end:]

        # Patch-up conent for Jekyll
        content = ''.join(lines_mark[:-1]) + head + lines_mark[-1] + body
        with open(filename, 'wt') as f:
            f.write(content)


def setup(app):
    app.connect('build-finished', on_build_finished, priority=900)
