"""
Sphinx plugin to run example scripts and create a gallery page.

Lightly modified from the seaborn project (Michael Waskom).
Originally, lightly modified from the mpld3 project.

"""

from pathlib import Path
from sphinx.application import Sphinx
from textwrap import indent


def on_build_finished(app: Sphinx, exception: Exception) -> None:
    html_dir = Path(app.builder.outdir)
    api_dir = html_dir / 'api'

    # Check if the index has Jekyll template marks. If it does, extract the
    # YAML frontmatter into a separate variable
    index_html = html_dir / 'index.html'
    with open(index_html, 'rt') as f:
        lines = f.readlines()
        # The Jekyll template starts with a --- line
        # Nontemplated HTML starts with some kind of XML tag
        if lines[0] != '---\n':
            return
        mark_end = lines.index('---\n', 1) + 1
        lines_mark = lines[: mark_end]

    # We will insert the same YAML frontmatter into the generated API docs.
    # Relative links to stylesheets in the frontmatter will break so repair
    # them
    lines_mark = [line.replace('href="_static/', 'href="../_static/') for line in lines_mark]

    # Write individual example files, fixing footers
    for path in sorted(api_dir.glob("*.html")):
        # Skip symbolic links, otherwise we could potentially process the same
        # file twice
        if path.is_symlink():
            continue

        # Read contents of file
        content = path.read_text()

        # Split part between <head> and </head> and the rest
        start = content.find('<head>') + len('<head>')
        end = content.find('</head>', start)
        head, content = content[start:end].strip(), content[end:].strip()

        # Split part between <body> and </body> and the rest
        start = content.find('<body>') + len('<body>')
        end = content.find('</body>', start)
        body = content[start:end].strip()

        # Exclude title from head
        start = head.find('<title>')
        end = head.find('</title>') + len('</title>')
        head = head[:start] + head[end:]

        # Bootstrap from Jekyll and pydoctor conflict, remove the pydoctor one
        headlines = head.split('\n')
        head = "\n".join(line for line in headlines if "bootstrap.min.css" not in line)

        # Repair last footer that conflicts with igraph footer
        start_pre = body.rfind('<footer')
        if start_pre >= 0:
            start = body.find('>', start_pre) + 1
            end = body.find('</footer>', start)
            body, footer, rest = body[:start_pre], body[start: end], body[end + len('</footer>'):]

            body_end = rest.rfind('</body>')
            rest = rest[:body_end]
        else:
            footer, rest = "", ""
        footer = footer.strip('\n')

        # Patch style of footer
        footer = footer.replace('"container"', '"container-fluid text-muted credit"').strip()

        # Patch-up content for Jekyll
        content = (''.join(lines_mark[:-1]) + 
                   indent(head, "    ") + "\n" +
                   'extrafoot: |\n' +
                   indent(footer, "    ") +
                   indent(rest, "    ") +
                   '\n' +
                   lines_mark[-1] +
                   body)

        # Write the patched content back to the file
        path.write_text(content)


def setup(app):
    app.connect('build-finished', on_build_finished, priority=900)
