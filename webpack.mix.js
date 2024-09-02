/*
 * Fix for the error
 * https://github.com/JeffreyWay/laravel-mix/issues/504
 */
const path = require('path');

const mix = require('laravel-mix');

/*
 |--------------------------------------------------------------------------
 | Mix Asset Management
 |--------------------------------------------------------------------------
 |
 | Mix provides a clean, fluent API for defining some Webpack build steps
 | for your Laravel application. By default, we are compiling the Sass
 | file for the application as well as bundling up all the JS files.
 |
 */

mix.setPublicPath('./public');
mix.webpackConfig({
    resolve: {
        alias: {
            // 'bs3': path.resolve(__dirname, 'node_modules/bootstrap-sass/assets/stylesheets/bootstrap')
            '~3pc': path.resolve(__dirname, 'client/3pc'), // third party components
        },
        fallback: {
            'stream': require.resolve('stream-browserify'),
            'http': require.resolve('stream-http'),
            'https': require.resolve('https-browserify'),
            'zlib': require.resolve('browserify-zlib'),
        },
    },
    resolveLoader: {
        alias: {
            svgSprite: path.resolve('./webpack/svgSpriteLoader.js'),
        },
    },
    stats: {
        children: false,
    },
});
mix.autoload({
    jquery: ['$', 'window.jQuery'],
});
mix.options({
    processCssUrls: true,
});

const jsPath = './client/js',
    scssPath = './client/sass';

// non-standard modules
mix.js(`${jsPath}/client.js`, '');
mix.sass(`${scssPath}/client.scss`, '');

if (mix.inProduction()) {
    mix.version();
}
