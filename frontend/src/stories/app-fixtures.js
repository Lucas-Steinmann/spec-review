const localRepository = {
  id: 'local:/home/reviewer/projects/companion_app:spec',
  source: 'local',
  root: '/home/reviewer/projects/companion_app',
  spec_dir: 'spec',
  base: 'main',
};

const githubRepository = {
  id: 'optograph/spec-review',
  source: 'gh',
  full_name: 'optograph/spec-review',
  default_branch: 'main',
};

const localOverview = {
  root: localRepository.root,
  spec_dir: 'spec',
  is_git: true,
  default_base: 'main',
  branches: ['main', 'release'],
  worktrees: [
    { path: localRepository.root, branch: 'main', head: 'a19cdb8f0123', subject: 'Update specification', available: true, bare: false },
    { path: '/home/reviewer/worktrees/browser-review', branch: 'agent/browser-review', head: 'c9e21a4b4567', subject: 'Refine review navigation', available: true, bare: false },
    { path: '/home/reviewer/worktrees/diagram-review', branch: '', head: 'd64b0f285678', subject: 'Render diagrams', available: true, bare: false },
  ],
};

const baseDocument = {
  id: 'REQ-034',
  type: 'requirement',
  title: 'Browse and compare specifications in a WebUI',
  path: 'spec/artifacts/requirements/REQ-034.yaml',
  fields: {
    statement: 'Provide a browser overview with the selected local repository in a left sidebar. Let the reviewer choose Review or Compare before selecting a target revision.',
    derived_from: ['UC-008'],
  },
};

const targetDocument = {
  ...baseDocument,
  fields: {
    ...baseDocument.fields,
    statement: 'Provide a browser overview with the selected local repository in a left sidebar. Let the reviewer choose a revision mode in the workspace before selecting a target revision.',
  },
};

const baseSnapshot = {
  revision: 'e06d17c82abc',
  documents: { 'REQ-034': baseDocument },
  diagnostics: [],
  unavailable_ids: [],
  categories: { requirement: 'Requirement' },
};

const targetSnapshot = {
  revision: 'Working tree',
  documents: { 'REQ-034': targetDocument },
  diagnostics: [],
  unavailable_ids: [],
  categories: { requirement: 'Requirement' },
};

const diffSections = (document, statement) => [
  { heading: 'STATEMENT', blocks: [{ kind: 'markdown', text: statement }] },
  { heading: 'DERIVED FROM', blocks: [{ kind: 'markdown', text: '[UC-008 · Review in the browser](UC-008)' }] },
];

function response(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export function installApplicationFixture(kind = 'empty', theme = 'paper') {
  const selected = kind === 'github' ? githubRepository : localRepository;
  const repositories = kind === 'empty' ? [] : kind === 'github' ? [githubRepository] : [localRepository];
  const githubPulls = [
    { number: 42, title: 'Refine the browser review workspace', head_ref: 'feature/browser-diff', base_ref: 'main', head: 'pr-42', base: 'main', checks: 'success' },
    { number: 39, title: 'Render diagrams locally', head_ref: 'feature/diagram-cache', base_ref: 'main', head: 'pr-39', base: 'main', checks: 'in_progress' },
    { number: 36, title: 'Update artifact source display', head_ref: 'fix/source-references', base_ref: 'main', head: 'pr-36', base: 'main', checks: 'unavailable' },
  ];

  localStorage.clear();
  localStorage.setItem('spec-review-theme', theme === 'dark' ? 'dark' : 'paper');
  localStorage.setItem('spec-review-selected-source', selected.id);
  if (kind === 'review') localStorage.setItem('spec-review-mode', 'compare');

  window.fetch = async (input, options = {}) => {
    const url = new URL(input, window.location.href);
    const { pathname, searchParams } = url;
    if (pathname === '/api/status') return response({ repo: null, spec_dir: 'spec' });
    if (pathname === '/api/sources') {
      if (options.method === 'POST') {
        const body = JSON.parse(options.body || '{}');
        return response({ repositories: body.repositories || repositories, selected: body.selected || selected.id });
      }
      return response({ repositories, selected: selected.id });
    }
    if (pathname === '/api/local/overview') return response(localOverview);
    if (pathname === '/api/gh/overview') return response(githubPulls);
    if (pathname === '/api/local/commits') return response({
      ...localOverview,
      commits: [
        { sha: 'e06d17c82abc', date: '2026-10-10T10:00:00Z', subject: 'Update specification' },
        { sha: '9ac411d3cdef', date: '2026-10-09T10:00:00Z', subject: 'Refine browser navigation' },
      ],
    });
    if (pathname === '/api/local/compare') return response({
      base: baseSnapshot,
      target: targetSnapshot,
      changes: { 'REQ-034': { id: 'REQ-034', status: 'changed', old: baseDocument, new: targetDocument } },
    });
    if (pathname === '/api/local/document') {
      const isBase = searchParams.get('ref') === baseSnapshot.revision;
      const document = isBase ? baseDocument : targetDocument;
      return response({
        document,
        revision: isBase ? baseSnapshot.revision : targetSnapshot.revision,
        sections: diffSections(document, document.fields.statement),
      });
    }
    if (pathname === '/api/gh/branches') return response([{ name: 'main', sha: 'main' }]);
    if (pathname === '/api/gh/pulls') return response(githubPulls);
    if (pathname === '/api/gh/commits') return response([{ sha: 'main', subject: 'Update specification' }]);
    if (pathname === '/api/gh/snapshot') return response({ ...targetSnapshot, revision: 'main' });
    return response({ error: `No Storybook fixture for ${pathname}` }, 404);
  };
}
