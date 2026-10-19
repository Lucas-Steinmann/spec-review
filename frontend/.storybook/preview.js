import '../src/style.css';

const preview = {
  globalTypes: {
    theme: {
      description: 'Application appearance',
      toolbar: {
        title: 'Theme',
        icon: 'paintbrush',
        items: ['paper', 'dark'],
        dynamicTitle: true,
      },
    },
  },
  initialGlobals: { theme: 'paper' },
  decorators: [
    (story, context) => {
      document.documentElement.dataset.theme = context.globals.theme || 'paper';
      return story();
    },
  ],
  parameters: {
    layout: 'centered',
    controls: { expanded: true },
  },
};

export default preview;
