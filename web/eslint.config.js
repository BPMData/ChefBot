import reactHooks from 'eslint-plugin-react-hooks';
import tseslint from 'typescript-eslint';

// Only the two React Hooks rules. Style belongs to Prettier; type errors belong to tsc.
export default [
  { ignores: ['dist/', 'node_modules/', 'playwright-report/', 'test-results/'] },
  {
    files: ['src/**/*.{ts,tsx}'],
    languageOptions: { parser: tseslint.parser },
    plugins: { 'react-hooks': reactHooks },
    rules: {
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
    },
  },
];
