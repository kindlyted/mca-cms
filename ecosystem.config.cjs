const fs = require('fs');
const path = require('path');

// 简单的 .env 文件解析器（不依赖外部包）
function loadEnv(filePath) {
  const env = {};
  if (!fs.existsSync(filePath)) {
    console.warn(`警告: ${filePath} 不存在`);
    return env;
  }

  const content = fs.readFileSync(filePath, 'utf8');
  content.split('\n').forEach(line => {
    line = line.trim();
    if (!line || line.startsWith('#')) return;

    const match = line.match(/^([^=]+)=(.*)$/);
    if (match) {
      const key = match[1].trim();
      let value = match[2].trim();
      // 去除引号
      value = value.replace(/^['"](.*)['"]$/g, '$1');
      env[key] = value;
    }
  });

  return env;
}

// 加载 .env 文件
const envVars = loadEnv(path.join(__dirname, '.env'));

module.exports = {
  apps: [
    {
      name: 'mca-cms',
      script: './.output/server/index.mjs',

      // 合并默认配置和 .env 中的变量
      env: {
        NODE_ENV: 'production',
        HOST: '0.0.0.0',
        NITRO_HOST: '0.0.0.0',
        NITRO_PORT: '3001',
        ...envVars,
      },

      // 实例配置
      instances: 1,
      exec_mode: 'fork',

      // 日志配置
      log_file: './logs/combined.log',
      out_file: './logs/out.log',
      error_file: './logs/error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

      // 自动重启配置
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',

      // 启动配置
      min_uptime: '10s',
      max_restarts: 5,

      // 工作目录 - 生产服务器上的绝对路径 (按部署环境修改)
      cwd: '/www/wwwroot/your-site',
    },
  ],
};
