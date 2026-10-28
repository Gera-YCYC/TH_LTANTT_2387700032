// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'DevSecOps & CI/CD Documentation',
  tagline: 'Tài liệu Thực hành Lập trình An ninh thông tin - Bài 6',
  favicon: 'img/favicon.ico',

  // Cấu hình URL và BaseUrl theo yêu cầu mục 6.2.2 tài liệu Bài 6
  url: 'https://student-hutech.gitlab.io',
  baseUrl: '/my-pipeline-tutorial-project/',

  // GitLab pages deployment config.
  organizationName: 'student-hutech',
  projectName: 'my-pipeline-tutorial-project',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'vi',
    locales: ['vi'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://gitlab.com/student-hutech/my-pipeline-tutorial-project/edit/main/',
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://gitlab.com/student-hutech/my-pipeline-tutorial-project/edit/main/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'DevSecOps Portal',
        logo: {
          alt: 'DevSecOps Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Tài liệu hướng dẫn',
          },
          { to: '/blog', label: 'Bản tin An ninh', position: 'left' },
          {
            href: 'https://gitlab.com/student-hutech/my-pipeline-tutorial-project',
            label: 'GitLab Repo',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Tài liệu',
            items: [
              {
                label: 'Tổng quan DevSecOps',
                to: '/docs/intro',
              },
            ],
          },
          {
            title: 'Cộng đồng',
            items: [
              {
                label: 'OWASP Foundation',
                href: 'https://owasp.org',
              },
              {
                label: 'GitLab CI/CD Docs',
                href: 'https://docs.gitlab.com',
              },
            ],
          },
        ],
        copyright: `Bản quyền © ${new Date().getFullYear()} Lê Đăng Khoa - 2387700032 - HUTECH.`,
      },
    }),
};

module.exports = config;
