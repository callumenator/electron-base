const Webpack = require('webpack');
const WebpackDevServer = require('webpack-dev-server');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin');

const nodemon = require('nodemon');

const devServerPort = 3001;
const devServerAddress = '127.0.0.1';
const mode = 'development';
const devtool = 'eval-cheap-module-source-map';

const tsRule = ({ babel = false } = {}) => ({
    test: /\.tsx?$/,
    use: [
        // Need babel loader for fast refresh
        babel && {
            loader: 'babel-loader',
            options: { plugins: ['react-refresh/babel'] },
        },
        {
            loader: 'ts-loader',
            options: {
                // ts-loader will look for this in each entry point's containing folder
                configFile: 'tsconfig.json',
            },
        },
    ].filter(Boolean),
});

const commonDefines = new Webpack.DefinePlugin({
    DEVSERVER_PORT: JSON.stringify(devServerPort),
    DEVSERVER_ADDRESS: JSON.stringify(devServerAddress),
});

const mainConfig = {
    mode,
    devtool,
    name: 'main',
    target: 'electron-main',
    entry: './src/main/index.ts',
    output: {
        filename: 'main.js',
    },
    resolve: {
        extensions: ['.ts', '.js'],
    },
    module: {
        rules: [tsRule()],
    },
    plugins: [
        commonDefines,
    ],
};

const preloadConfig = {
    mode,
    devtool,
    name: 'preload',
    target: 'electron-preload',
    entry: './src/main/preload-internal.ts',
    output: {
        filename: 'preload-internal.js',
    },
    resolve: {
        extensions: ['.ts', '.js'],
    },
    module: {
        rules: [tsRule()],
    },
    plugins: [
        commonDefines,
    ],
};

const rendererConfig = {
    mode,
    devtool,
    name: 'renderer',
    target: 'web',
    entry: './src/renderer/index.tsx',
    output: {
        filename: 'renderer.js',
    },
    resolve: {
        extensions: ['.ts', '.tsx', '.js'],
    },
    module: {
        rules: [tsRule({ babel: true })],
    },
    plugins: [
        commonDefines,
        new ReactRefreshWebpackPlugin(),
        new HtmlWebpackPlugin({
            template: './src/renderer/index.ejs',
        }),
    ],
};

const compiler = Webpack([mainConfig, preloadConfig, rendererConfig]);

// ---- Main process ---- //

let mainStarted = false;
const mainWatcher = compiler.compilers[0].watch({}, (err, stats) => {
    console.log(stats.toString());

    if (!mainStarted) {
        mainStarted = true;
        nodemon({
            script: 'dist/main.js',
            execMap: {
                js: 'electron',
            },
            watch: ['dist/main*.js', 'dist/preload-internal*.js'],
        });
    }
});
const preloadWatcher = compiler.compilers[1].watch({}, (err, stats) => {
    console.log(stats.toString());
});

// ---- Renderer process ---- //

const rendererDevServer = new WebpackDevServer(compiler.compilers[2], {
    hot: true,
}).listen(devServerPort, devServerAddress, () => {
    // Dev server now listening...
});

process.on('SIGINT', function () {
    console.log('\nGracefully shutting down from SIGINT (Ctrl-C)');
    mainWatcher.close();
    preloadWatcher.close();
    rendererDevServer.close();
    process.exit(1);
});
