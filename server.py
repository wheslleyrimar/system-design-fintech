#!/usr/bin/env python3
"""
Servidor local para o curso. Serve:
- .html: normal
- .md: renderizado como HTML com suporte a UTF-8, tabelas, código e estilos
"""
import http.server
import socketserver
import os
import re
import urllib.parse

PORT = 8743
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

MD_CSS = """
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 15px;
    line-height: 1.7;
    color: #1a1a2e;
    background: #f8f9fb;
    padding: 0;
    margin: 0;
  }
  .wrapper {
    max-width: 860px;
    margin: 0 auto;
    padding: 40px 32px 80px;
    background: #fff;
    min-height: 100vh;
    border-left: 1px solid #e8eaed;
    border-right: 1px solid #e8eaed;
  }
  h1 { font-size: 2em; font-weight: 700; margin: 0 0 24px; color: #0f172a; border-bottom: 3px solid #6366f1; padding-bottom: 12px; }
  h2 { font-size: 1.4em; font-weight: 700; margin: 40px 0 12px; color: #1e293b; border-left: 4px solid #6366f1; padding-left: 12px; }
  h3 { font-size: 1.1em; font-weight: 600; margin: 28px 0 8px; color: #334155; }
  h4 { font-size: 1em; font-weight: 600; margin: 20px 0 6px; color: #475569; }
  p { margin: 0 0 14px; }
  a { color: #6366f1; text-decoration: none; }
  a:hover { text-decoration: underline; }
  ul, ol { margin: 0 0 14px 24px; }
  li { margin: 4px 0; }
  li > ul, li > ol { margin-top: 4px; margin-bottom: 4px; }
  strong { font-weight: 700; color: #0f172a; }
  em { font-style: italic; color: #475569; }
  code {
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 0.875em;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 1px 5px;
    color: #be185d;
  }
  pre {
    background: #0f172a;
    color: #e2e8f0;
    border-radius: 8px;
    padding: 20px;
    overflow-x: auto;
    margin: 0 0 20px;
  }
  pre code {
    background: none;
    border: none;
    padding: 0;
    color: #e2e8f0;
    font-size: 0.875em;
  }
  blockquote {
    border-left: 4px solid #c7d2fe;
    background: #eef2ff;
    padding: 12px 16px;
    margin: 0 0 16px;
    border-radius: 0 6px 6px 0;
    color: #4338ca;
  }
  blockquote p { margin: 0; }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 0 0 20px;
    font-size: 0.9em;
  }
  th {
    background: #6366f1;
    color: #fff;
    font-weight: 600;
    padding: 10px 14px;
    text-align: left;
    border: 1px solid #4f46e5;
  }
  td {
    padding: 9px 14px;
    border: 1px solid #e2e8f0;
    vertical-align: top;
  }
  tr:nth-child(even) td { background: #f8fafc; }
  tr:hover td { background: #eef2ff; }
  hr { border: none; border-top: 2px solid #e2e8f0; margin: 32px 0; }
  .nav-bar {
    background: #0f172a;
    color: #94a3b8;
    padding: 10px 32px;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .nav-bar a { color: #c7d2fe; }
  .nav-bar span { color: #475569; }
  .filename { font-weight: 600; color: #e2e8f0; font-family: monospace; }
</style>
"""

def render_md_to_html(content, filename):
    """Convert markdown to HTML with basic but solid rendering."""
    lines = content.split('\n')
    html_lines = []
    in_code_block = False
    in_table = False
    in_blockquote = False
    i = 0

    def inline(text):
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        # Inline code
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        # Links
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        return text

    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
                html_lines.append('<pre><code>')
            else:
                in_code_block = False
                html_lines.append('</code></pre>')
            i += 1
            continue

        if in_code_block:
            html_lines.append(line
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))
            i += 1
            continue

        # Table
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                html_lines.append('<table>')
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                html_lines.append('<tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells) + '</tr>')
                i += 1
                # skip separator row
                if i < len(lines) and re.match(r'^\|[-| :]+\|$', lines[i].strip()):
                    i += 1
                continue
            else:
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                html_lines.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>')
                i += 1
                continue
        else:
            if in_table:
                in_table = False
                html_lines.append('</table>')

        # Headings
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            html_lines.append(f'<h{level}>{inline(m.group(2))}</h{level}>')
            i += 1
            continue

        # HR
        if re.match(r'^---+$', line.strip()):
            html_lines.append('<hr>')
            i += 1
            continue

        # Blockquote
        if line.startswith('> '):
            html_lines.append(f'<blockquote><p>{inline(line[2:])}</p></blockquote>')
            i += 1
            continue

        # Unordered list
        m = re.match(r'^(\s*)([-*+])\s+(.+)$', line)
        if m:
            indent = len(m.group(1))
            # Look ahead for a list block
            list_lines = []
            while i < len(lines) and (re.match(r'^\s*[-*+]\s+', lines[i]) or (list_lines and lines[i].startswith('  '))):
                list_lines.append(lines[i])
                i += 1
            html_lines.append('<ul>')
            for ll in list_lines:
                mm = re.match(r'^\s*[-*+]\s+(.+)$', ll)
                if mm:
                    html_lines.append(f'<li>{inline(mm.group(1))}</li>')
                else:
                    # continuation line - append to last li
                    if html_lines and html_lines[-1].endswith('</li>'):
                        html_lines[-1] = html_lines[-1][:-5] + ' ' + inline(ll.strip()) + '</li>'
            html_lines.append('</ul>')
            continue

        # Ordered list
        m = re.match(r'^\s*\d+\.\s+(.+)$', line)
        if m:
            list_lines = []
            while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                list_lines.append(lines[i])
                i += 1
            html_lines.append('<ol>')
            for ll in list_lines:
                mm = re.match(r'^\s*\d+\.\s+(.+)$', ll)
                if mm:
                    html_lines.append(f'<li>{inline(mm.group(1))}</li>')
            html_lines.append('</ol>')
            continue

        # Empty line
        if line.strip() == '':
            html_lines.append('')
            i += 1
            continue

        # Paragraph
        html_lines.append(f'<p>{inline(line)}</p>')
        i += 1

    if in_table:
        html_lines.append('</table>')
    if in_code_block:
        html_lines.append('</code></pre>')

    body = '\n'.join(html_lines)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{MD_CSS}
<title>{filename}</title>
</head>
<body>
<div class="nav-bar">
  <span>📁 curso-system-design-fintech /</span>
  <span class="filename">{filename}</span>
  <span style="margin-left:auto; font-size:12px;">localhost:{PORT}</span>
</div>
<div class="wrapper">
{body}
</div>
</body>
</html>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Decode URL
        path = urllib.parse.unquote(self.path.split('?')[0])
        filepath = os.path.join(DIRECTORY, path.lstrip('/'))

        if filepath.endswith('.md') and os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            filename = os.path.basename(filepath)
            html = render_md_to_html(content, filename)
            encoded = html.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass  # silence request logs


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    with ReusableTCPServer(('', PORT), Handler) as httpd:
        print(f'Servidor rodando em http://localhost:{PORT}')
        print(f'Servindo: {DIRECTORY}')
        print('Ctrl+C para parar.')
        httpd.serve_forever()
