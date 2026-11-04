# Hello Station

一个待办事项 HTTP API：FastAPI + SQLite + Docker Compose + GitHub Actions。

## 本地开发

需要 Python 3.12。创建虚拟环境后执行：

```bash
python -m pip install -e '.[dev]'
ruff check .
pytest -q
uvicorn app.main:app --reload
```

首页 http://127.0.0.1:8000 就是待办网页，交互式文档在 http://127.0.0.1:8000/docs 。数据库默认位于 `data/tasks.db`，可通过 `DATABASE_PATH` 修改。

## 前端页面

`app/static/index.html` 是单文件页面（原生 HTML/CSS/JS，无构建步骤、不依赖 CDN），由 FastAPI 在 `/` 直接返回，可选静态资源挂在 `/static`。功能：新增待办、勾选完成、删除、按全部/未完成/已完成筛选、显示剩余数量与接口连通状态。页面只调用 `/api/tasks`，所以后端改端口或加反代都不需要动前端。修改后刷新浏览器即可，Docker 镜像会自动带上该文件。

## 接口

`GET /health`；`POST /api/tasks`（JSON `{"title":"待办"}`）；`GET /api/tasks`；`GET /api/tasks/{id}`；`PATCH /api/tasks/{id}`（如 `{"done":true}`）；`DELETE /api/tasks/{id}`。`GET /` 返回网页，`GET /info` 返回文档和健康检查地址。

这是公开演示服务，没有用户认证；能访问接口的人都可以读取、修改和删除待办事项。不要存放敏感数据。

## 服务器一次性准备

准备一台可公网访问的 Linux 服务器（例如 39.106.226.254），安装 Docker Engine、Compose 插件及 curl；部署账户必须能无交互执行 `docker compose`。配置防火墙和云安全组允许 TCP 8000 供用户访问，SSH 端口只向适当来源开放。确认磁盘有足够空间，GitHub Actions 能通过 SSH 访问服务器。Docker 权限等同于较高的主机权限，应使用专用部署账户和专用服务器或隔离环境。

创建专用 Ed25519 密钥，将公钥添加到该部署账户的 `~/.ssh/authorized_keys`。在可信渠道核对服务器 SSH 主机密钥指纹后，把完整的 known_hosts 行配置到仓库 Secrets；不要在未核对指纹的情况下信任 `ssh-keyscan` 输出。GitHub 仓库 Settings → Secrets and variables → Actions 中设置：

- `DEPLOY_HOST`：服务器 IP 或域名。
- `DEPLOY_USER`：SSH 登录用户名。
- `DEPLOY_SSH_KEY`：专用私钥完整内容。
- `DEPLOY_KNOWN_HOSTS`：经核对的服务器主机公钥行。

确保默认分支为 `main`，且仓库启用了 Actions。推送到 `main` 后，Actions 先执行 Ruff、pytest 和 Docker 构建，再构建版本镜像并通过 SSH 将镜像和该提交上传至服务器启动。Pull Request 只运行检查。部署到 `~/hello-station/releases/<提交号>`，并通过 `/health` 验证；失败时尽力恢复上一次成功运行的版本。单机更新可能短暂中断。`workflow_dispatch` 仅运行测试；部署由推送 main 触发。

部署后访问 `http://39.106.226.254:8000/` 使用网页，`/docs` 查看接口文档。如需 HTTPS，配置域名和反向代理、证书。检查 Actions 日志及服务器上的 `docker compose -p hello-station ps` 排障。

## 数据和维护

Compose 命名卷 `hello-station_station-data` 保存 SQLite 数据，容器重建不会删除它。定期使用 SQLite 在线备份方式备份数据库并测试恢复；不要执行 `docker compose down -v`，否则会删除数据卷。备份、服务器安全更新、监控和清理旧 releases/镜像需要另行安排。回滚镜像不能自动撤销数据库结构变更，今后引入迁移时应设计兼容和备份方案。
