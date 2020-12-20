module.exports = {
    type: 'react-component',
    npm: {
        esModules: false,
        umd: {
            global: 'HostManagement',
            externals: {
                react: 'React'
            }
        }
    },
    webpack: {
        config(config) {
            config.entry = {
                demo: ["./src/index.tsx"]
            }
            config.resolve.extensions = config.resolve.extensions || [
                '.js',
                '.jsx',
            ];
            config.resolve.extensions.push('.ts', '.tsx');
            config.devtool = 'source-map'
            config.module.rules.push({
                "test": /\.tsx?$/,
                "loader": "ts-loader"
            });

            return config;
        }
    },
    devServer: {
        hotOnly: true,
        inline: true,
        hot: true
    }
}
