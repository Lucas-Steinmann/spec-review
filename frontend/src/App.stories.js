import App from './App.svelte';
import { installApplicationFixture } from './stories/app-fixtures.js';

export default {
  title: 'Application/Browser',
  id: 'browser',
  component: App,
  parameters: { layout: 'fullscreen' },
};

export const EmptyOverview = {
  beforeEach: ({ globals }) => installApplicationFixture('empty', globals.theme),
};

export const GitHubOverview = {
  beforeEach: ({ globals }) => installApplicationFixture('github', globals.theme),
};

export const LocalWorktrees = {
  beforeEach: ({ globals }) => installApplicationFixture('local', globals.theme),
};

export const RevisionComparison = {
  beforeEach: ({ globals }) => installApplicationFixture('review', globals.theme),
  play: async ({ canvas, userEvent }) => {
    await userEvent.click(await canvas.findByRole('button', { name: 'Open review' }));
    await userEvent.click(await canvas.findByRole('button', { name: 'Apply revision' }));
    await userEvent.click(await canvas.findByRole('button', { name: /REQ-034 Browse and compare/ }));
  },
};
