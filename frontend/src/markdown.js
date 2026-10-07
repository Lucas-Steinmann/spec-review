const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[character]));

function inline(source) {
  const pattern = /(\uE000(?:added|removed)\uE001[\s\S]*?\uE002|\[[^\]]+\]\([^)]+\)|`[^`]+`|\*\*[^*]+\*\*|__[^_]+__|~~[^~]+~~|\*[^*]+\*)/g;
  let html = '';
  let offset = 0;
  for (const match of source.matchAll(pattern)) {
    html += escapeHtml(source.slice(offset, match.index));
    const token = match[0];
    if (token.startsWith('\uE000')) {
      const kind = token.includes('added') ? 'added' : 'removed';
      const value = token.slice(token.indexOf('\uE001') + 1, -1);
      html += `<span class="diff-text ${kind}">${inline(value)}</span>`;
    } else if (token.startsWith('[')) {
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

function wordTokens(value) {
  return [...value.matchAll(/[\p{L}\p{N}_]+/gu)].map((match) => ({ text: match[0], start: match.index, end: match.index + match[0].length }));
}

function changedWords(source, other) {
  const left = wordTokens(source);
  const right = wordTokens(other);
  const table = Array.from({ length: left.length + 1 }, () => new Uint32Array(right.length + 1));
  for (let i = left.length - 1; i >= 0; i--) for (let j = right.length - 1; j >= 0; j--) {
    table[i][j] = left[i].text === right[j].text ? table[i + 1][j + 1] + 1 : Math.max(table[i + 1][j], table[i][j + 1]);
  }
  const unchanged = new Set();
  let i = 0, j = 0;
  while (i < left.length && j < right.length) {
    if (left[i].text === right[j].text) { unchanged.add(i++); j++; }
    else if (table[i + 1][j] >= table[i][j + 1]) i++;
    else j++;
  }
  return left.map((token, index) => unchanged.has(index) ? null : token);
}

export function renderMarkdownDiffLine(source, other, kind) {
  const changes = changedWords(source, other);
  let output = source;
  const ranges = [];
  for (let index = 0; index < changes.length; index++) {
    const token = changes[index];
    if (!token) continue;
    let { start, end } = token;
    while (index + 1 < changes.length && changes[index + 1]) {
      const next = changes[index + 1];
      const between = source.slice(end, next.start);
      if (!/^\s+$/.test(between)) break;
      end = next.end;
      index++;
    }
    if (ranges.length && /^\s+$/.test(source.slice(ranges.at(-1).end, start))) ranges.at(-1).end = end;
    else ranges.push({ start, end });
  }
  for (let index = ranges.length - 1; index >= 0; index--) {
    const { start, end } = ranges[index];
    output = `${output.slice(0, start)}\uE000${kind}\uE001${output.slice(start, end)}\uE002${output.slice(end)}`;
  }
  return renderMarkdown(output || ' ');
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
