import test from 'node:test';
import assert from 'node:assert/strict';
import { renderMarkdownDiffLine } from './markdown.js';

test('diff line marks only removed words and preserves markdown formatting', () => {
  const html = renderMarkdownDiffLine('The **old label** stays', 'The **new label** stays', 'removed');
  assert.match(html, /<strong><span class="diff-text removed">old<\/span> label<\/strong>/);
  assert.doesNotMatch(html, /diff-text removed[^<]*label/);
});

test('diff line marks added words in green-side markup', () => {
  const html = renderMarkdownDiffLine('The new label stays', 'The old label stays', 'added');
  assert.match(html, /<span class="diff-text added">new<\/span>/);
  assert.doesNotMatch(html, /diff-text added[^<]*label/);
});

test('diff line keeps spaces inside a contiguous changed phrase highlight', () => {
  const html = renderMarkdownDiffLine('The old blue label stays', 'The new green label stays', 'removed');
  assert.match(html, /<span class="diff-text removed">old blue<\/span>/);
});
