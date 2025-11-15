// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
    title: 'SecretOn API Client',
    tagline: 'Python client library for SecretOn API',
    favicon: 'img/favicon.ico',

    // Set the production url of your site here
    url: 'https://klukvaofficial.github.io',
    // Set the /<baseUrl>/ pathname under which your site is served
    // For GitHub pages deployment, it is often '/<projectName>/'
    baseUrl: '/secreton_api_client_draft/',
    trailingSlash: false,

    // GitHub pages deployment config.
    // If you aren't using GitHub pages, you don't need these.
    organizationName: 'klukvaofficial', // Usually your GitHub org/user name.
    projectName: 'secreton_api_client_draft', // Usually your repo name.

    onBrokenLinks: 'throw',
    onBrokenMarkdownLinks: 'warn',

    // Even if you don't use internalization, you can use this field to set useful
    // metadata like html lang. For example, if your site is Chinese, you may want
    // to replace "en" with "zh-Hans".
    i18n: {
        defaultLocale: 'en',
        locales: ['en'],
    },

    presets: [
        [
            'classic',
            /** @type {import('@docusaurus/preset-classic').Options} */
            ({
                docs: {
                    sidebarPath: require.resolve('./sidebars.js'),
                },
                blog: false,
                theme: {
                    customCss: require.resolve('./src/css/custom.css'),
                },
            }),
        ],
    ],

    themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
        ({
        // Replace with your project's social card
        image: 'img/docusaurus-social-card.jpg',
        navbar: {
            title: 'SecretOn API Client',
            logo: {
                alt: 'SecretOn API Client Logo',
                src: 'img/logo.svg',
                srcDark: 'img/logo.svg',
            },
            hideOnScroll: false,
            items: [{
                    type: 'docSidebar',
                    sidebarId: 'tutorialSidebar',
                    position: 'left',
                    label: 'Documentation',
                },
                {
                    href: 'https://github.com/klukvaofficial/secreton_api_client_draft',
                    label: 'GitHub',
                    position: 'right',
                },
            ],
        },
        footer: {
            style: 'dark',
            links: [{
                    title: 'Docs',
                    items: [{
                            label: 'Getting Started',
                            to: '/docs/getting-started/installation',
                        },
                        {
                            label: 'API Reference',
                            to: '/docs/api-reference/client',
                        },
                    ],
                },
                {
                    title: 'Community',
                    items: [{
                        label: 'GitHub',
                        href: 'https://github.com/klukvaofficial/secreton_api_client_draft',
                    }, ],
                },
            ],
            copyright: `Copyright © ${new Date().getFullYear()} SecretOn API Client. Built with Docusaurus.`,
        },
        prism: {
            theme: lightCodeTheme,
            darkTheme: darkCodeTheme,
            additionalLanguages: ['python', 'bash'],
        },
        colorMode: {
            defaultMode: 'light',
            disableSwitch: false,
            respectPrefersColorScheme: true,
        },
    }),
};

module.exports = config;