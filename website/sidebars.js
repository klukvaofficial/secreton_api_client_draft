/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    'index',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/authentication',
      ],
    },
    {
      type: 'category',
      label: 'Example Usage',
      items: [
        'examples/examples',
        'examples/telegram-bot',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api-reference/client',
        'api-reference/services',
        'api-reference/models',
        'api-reference/exceptions',
      ],
    },
    {
      type: 'category',
      label: 'User Guide',
      items: [
        'user-guide/error-handling',
      ],
    },
    'CHANGELOG',
  ],
};

module.exports = sidebars;

