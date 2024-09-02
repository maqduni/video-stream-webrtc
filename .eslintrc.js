module.exports = {
    extends: [
        // add more generic rule sets here, such as:
        'eslint:recommended',
        // 'plugin:vue/vue3-recommended',
        'plugin:vue/recommended', // Use this if you are using Vue.js 2.x.
    ],
    plugins: ['import'],
    rules: {
        // override/add rules settings here, such as:
        // 'prettier/prettier': 'error',
        'import/order': [
            'error',
            {
                groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
                'newlines-between': 'always',
                alphabetize: {
                    order: 'asc',
                    caseInsensitive: true,
                },
            },
        ],
        'import/prefer-default-export': 'off',
        curly: 'error',
        'eol-last': 'error',
        'id-length': 'error',
        'no-duplicate-imports': 'error',
        'no-trailing-spaces': 'error',
        'no-multiple-empty-lines': ['error', { 'max': 1, 'maxEOF': 1 }],
        'require-await': 'error',
        'comma-dangle': [
            'error',
            {
                arrays: 'always-multiline',
                objects: 'always-multiline',
                imports: 'always-multiline',
                exports: 'always-multiline',
                functions: 'never',
            },
        ],
        'quotes': ['error', 'single', { 'avoidEscape': true }],
        'object-curly-spacing': ['error', 'always'],
        'semi': ['error', 'always'],
        'vue/no-unused-vars': 'error',
        'vue/require-prop-types': 'warn',
        'vue/html-indent': ['error', 4, {
            'attribute': 1,
            'baseIndent': 1,
            'closeBracket': 0,
            'alignAttributesVertically': true,
            'ignores': [],
        }],
        'vue/html-closing-bracket-newline': ['error', {
            'singleline': 'never',
            'multiline': 'never',
        }],
        'vue/script-indent': ['error', 4, {
            'baseIndent': 1,
            'switchCase': 0,
            'ignores': [],
        }],
    },
    env: {
        'browser': true,
        'commonjs': true,
        'es6': true,
        'jquery': true,
    },
    globals: {
        'Mousetrap': true,
        'app': true,
        'Vue': true,
        'axios': true,
    },
};
