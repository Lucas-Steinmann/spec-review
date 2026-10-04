const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[character]));

function inline(source) {
  const pattern = /(\[[^\]]+\]\([^)]+\)|`[^`]+`|\*\*[^*]+\*\*|__[^_]+__|~~[^~]+~~|\*[^*]+\*)/g;
  let html = '';
  let offset = 0;
  for (const match of source.matchAll(pattern)) {
    html += escapeHtml(source.slice(offset, match.index));
    const token = match[0];
    if (token.startsWith('[')) {
      const link = token.match(/^\[([^\]]+)\]\((\S+?)(?:\s+"[^"]*")?\)$/);
      if (link) html += `<a href="#" data-review-href="${escapeHtml(link[2])}">${inline(link[1])}</a>`;
      else html += escapeHtml(token);
    } else if (token.startsWith('`')) html += `<code>${escapeHtml(token.slice(1, -1))}</code>`;
    else if (token.startsWith('**') || token.startsWith('__')) html += `<strong>${inline(token.slice(2, -2))}</strong>`;
    else if (token.startsWith('~~')) html += `<del>${inline(token.slice(2, -2))}</del>`;
    else html += `<em>${inline(token.slice(1, -1))}</em>`;
    offset = match.index + token.length;
  }
  return html + escapeHtml(source.slice(offset));
}

export function slug(source) {
  return source.toLowerCase().replace(/\[([^\]]+)\]\([^)]*\)/g, '$1').replace(/[^\p{L}\p{N}_\s-]/gu, '').trim().replace(/\s+/g, '-');
}

function cells(line) {
  return line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((cell) => cell.trim());
}

export function renderMarkdown(source) {
  const lines = String(source).replace(/\r\n?/g, '\n').split('\n');
  const output = [];
  let paragraph = [];
  const flush = () => {
    if (paragraph.length) output.push(`<p>${inline(paragraph.join(' '))}</p>`);
    paragraph = [];
  };
  for (let index = 0; index < lines.length;) {
    const line = lines[index];
    if (!line.trim()) { flush(); index += 1; continue; }
    const heading = line.match(/^(#{1,6})\s+(.+?)\s*#*$/);
    if (heading) {
      flush();
      const text = heading[2];
      output.push(`<h${heading[1].length} id="${escapeHtml(slug(text))}">${inline(text)}</h${heading[1].length}>`);
      index += 1; continue;
    }
    if (/^\s*([-*_])(?:\s*\1){2,}\s*$/.test(line)) { flush(); output.push('<hr>'); index += 1; continue; }
    if (line.includes('|') && index + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[index + 1])) {
      flush();
      const headers = cells(line);
      index += 2;
      const rows = [];
      while (index < lines.length && lines[index].includes('|')) { rows.push(cells(lines[index])); index += 1; }
      output.push(`<table><thead><tr>${headers.map((value) => `<th>${inline(value)}</th>`).join('')}</tr></thead><tbody>${rows.map((row) => `<tr>${headers.map((_, cell) => `<td>${inline(row[cell] || '')}</td>`).join('')}</tr>`).join('')}</tbody></table>`);
      continue;
    }
    if (/^\s*[-+*]\s+/.test(line)) {
      flush(); const items = [];
      while (index < lines.length && /^\s*[-+*]\s+/.test(lines[index])) { items.push(lines[index++].replace(/^\s*[-+*]\s+/, '')); }
      output.push(`<ul>${items.map((item) => `<li>${inline(item)}</li>`).join('')}</ul>`); continue;
    }
    if (/^\s*\d+[.)]\s+/.test(line)) {
      flush(); const items = [];
      while (index < lines.length && /^\s*\d+[.)]\s+/.test(lines[index])) { items.push(lines[index++].replace(/^\s*\d+[.)]\s+/, '')); }
      output.push(`<ol>${items.map((item) => `<li>${inline(item)}</li>`).join('')}</ol>`); continue;
    }
    if (/^>\s?/.test(line)) { flush(); output.push(`<blockquote><p>${inline(line.replace(/^>\s?/, ''))}</p></blockquote>`); index += 1; continue; }
    paragraph.push(line.trim()); index += 1;
  }
  flush();
  return output.join('\n');
}
