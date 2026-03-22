# 实验室器件局域网共享管理系统

一个面向实验室内部局域网使用的轻量网站系统。部署在一台长期开机的 Linux 电脑上后，实验室成员可通过浏览器访问同一地址，查看和维护同一份器件数据。

本项目第一版重点是：

- 简单
- 稳定
- 容易维护
- 不依赖复杂中间件
- 默认使用 SQLite，部署门槛低
- 代码结构预留后续切换 MySQL 的空间

## 1. 技术方案

为了满足“局域网共享访问、多人共用同一份数据、非专业开发者容易维护”这三个核心目标，本项目采用以下轻量方案：

- 后端：FastAPI
- 页面渲染：Jinja2 模板
- 数据库：SQLite
- ORM：SQLAlchemy
- 前端：服务端渲染 + 原生 HTML/CSS

为什么这样选：

- 不做前后端完全分离，部署最简单
- 不引入 Redis、消息队列等额外复杂组件
- 只有一个 Python 服务，后续维护和迁移都更容易
- 数据直接落到 SQLite 文件，备份就是复制数据库文件
- 不依赖 Docker 也能直接运行，同时已经提供 Docker 镜像部署方案

## 2. 功能说明

已实现功能：

- 器件列表页
- 分页显示
- 按名称、型号、类别、功能关键词搜索
- 按类别筛选
- 器件详情页
- 新增器件
- 编辑器件
- 删除器件
- 分类管理
- 分类新增、编辑、删除
- 分类数据保存在数据库，不写死在代码里
- 数量字段可编辑并在列表中醒目展示
- 服务首次启动时自动初始化数据库
- 提供示例数据，启动后可直接看到效果

## 3. 项目目录结构

```text
LAB/
├─ app/
│  ├─ routers/                # 路由
│  ├─ services/               # 业务逻辑
│  ├─ static/css/             # 页面样式
│  ├─ templates/              # Jinja2 页面模板
│  ├─ config.py               # 配置
│  ├─ database.py             # 数据库连接
│  ├─ dependencies.py         # 依赖注入
│  ├─ main.py                 # FastAPI 入口
│  ├─ models.py               # 数据模型
│  └─ seed.py                 # 建表与示例数据初始化
├─ data/                      # SQLite 数据库文件目录
├─ .dockerignore
├─ Dockerfile                 # Docker 镜像构建文件
├─ docker-compose.yml         # Docker Compose 部署文件
├─ scripts/
│  └─ init_db.py              # 手动初始化数据库脚本
├─ requirements.txt
└─ README.md
```

## 4. 数据库设计说明

本项目当前包含 2 张核心表。

### 4.1 categories 分类表

字段说明：

- `id`：主键
- `name`：分类名称，唯一
- `description`：分类说明
- `created_at`：创建时间
- `updated_at`：更新时间

用途：

- 管理所有器件分类
- 分类不是写死在代码中的，后续可以直接在页面中扩展

### 4.2 items 器件表

字段说明：

- `id`：主键
- `name`：名称
- `model`：型号
- `category_id`：所属分类 ID，关联 `categories.id`
- `quantity`：数量
- `key_specifications`：关键指标
- `function_description`：功能
- `remarks`：备注
- `location`：存放位置
- `created_at`：创建时间
- `updated_at`：更新时间

设计考虑：

- 字段命名使用英文，页面展示使用中文，后续扩展更方便
- 文字说明字段使用 `Text`，方便后续记录更多内容
- 未来如需增加图片、数据手册链接、厂商等字段，可直接在 `Item` 模型中扩展
- 未来如需增加用户、角色、登录权限，也可以继续新增表而不影响现有核心结构

## 5. 环境要求

建议环境：

- Linux：Ubuntu 22.04 / Debian 12 / CentOS Stream 等均可
- Python：3.10 及以上

本项目也可以在 Windows 上本地开发测试，但正式部署建议使用 Linux。

## 6. 安装步骤

以下步骤以 Linux 为例。

### 6.1 进入项目目录

```bash
cd /你的项目目录/LAB
```

### 6.2 创建虚拟环境

```bash
python3 -m venv .venv
```

### 6.3 激活虚拟环境

```bash
source .venv/bin/activate
```

### 6.4 安装依赖

```bash
pip install -r requirements.txt
```

## 7. 初始化数据库

项目支持两种方式初始化数据库。

### 方式一：手动初始化

```bash
python scripts/init_db.py
```

### 方式二：直接启动服务时自动初始化

第一次启动服务时，系统会自动：

- 创建数据库文件
- 创建表结构
- 写入示例分类和示例器件

默认数据库文件位置：

```text
data/lab_inventory.db
```

## 8. 运行步骤

### 8.1 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

说明：

- `--host 0.0.0.0` 表示监听所有网卡，局域网内其他电脑才能访问
- `--port 8000` 表示服务端口为 8000

### 8.2 本机访问

浏览器打开：

```text
http://127.0.0.1:8000
```

### 8.3 局域网访问

先在部署机器上查看 IP 地址，例如：

```bash
ip addr
```

假设部署机器的局域网 IP 是 `192.168.1.50`，那么其他电脑可通过浏览器访问：

```text
http://192.168.1.50:8000
```

如果其他电脑无法访问，请检查：

- Linux 防火墙是否放行了 8000 端口
- 部署机器和访问机器是否在同一局域网
- 启动命令是否确实使用了 `--host 0.0.0.0`

## 9. Linux 部署步骤

### 9.1 最简单部署方式

1. 把整个项目目录复制到 Linux 电脑
2. 安装 Python 3
3. 创建虚拟环境
4. 安装依赖
5. 运行启动命令

完整示例：

```bash
cd /opt/lab-inventory
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 9.2 适合长期运行的直接命令方式

如果只是先快速上线，可以直接在虚拟环境中运行：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

这种方式最简单，但终端关闭后服务也会停止。适合测试或临时运行。

如果想在不退出终端的情况下后台运行，可以用：

```bash
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
```

### 9.3 推荐的 systemd 服务方式

正式长期运行更推荐 `systemd`。

先创建服务文件：

```bash
sudo nano /etc/systemd/system/lab-inventory.service
```

填入以下内容：

```ini
[Unit]
Description=Lab Inventory FastAPI Service
After=network.target

[Service]
User=labuser
Group=labuser
WorkingDirectory=/opt/lab-inventory
Environment="SECRET_KEY=please-change-this-key"
ExecStart=/opt/lab-inventory/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

说明：

- `User` 和 `Group` 改成实际运行用户
- `WorkingDirectory` 改成你的项目实际路径
- `ExecStart` 改成你的虚拟环境中 uvicorn 实际路径
- `SECRET_KEY` 建议改成你自己的随机字符串

然后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl enable lab-inventory
sudo systemctl start lab-inventory
sudo systemctl status lab-inventory
```

查看日志：

```bash
sudo journalctl -u lab-inventory -f
```

### 9.4 Docker 镜像方式

如果你希望在 Debian 上用 Docker 部署，这个项目现在已经支持。

优点：

- 不需要在宿主机手动配置 Python 虚拟环境
- 部署和迁移更标准化
- 容器重建后，只要数据卷还在，数据库就不会丢

#### 9.4.1 构建镜像

在项目根目录执行：

```bash
docker build -t lab-inventory:latest .
```

#### 9.4.2 直接运行容器

```bash
docker run -d \
  --name lab-inventory \
  -p 8000:8000 \
  -e SECRET_KEY=please-change-this-key \
  -e PAGE_SIZE=10 \
  -v /drv2/mysql_docker/bubble:/app/data \
  --restart unless-stopped \
  lab-inventory:latest
```

说明：

- `-p 8000:8000`：把容器 8000 端口映射到宿主机 8000 端口
- `-v /drv2/mysql_docker/bubble:/app/data`：把 Debian 宿主机的 `/drv2/mysql_docker/bubble` 挂载到容器内，确保 SQLite 数据持久化
- `--restart unless-stopped`：宿主机重启后自动拉起容器

启动后访问：

```text
http://宿主机IP:8000
```

#### 9.4.3 使用 Docker Compose

项目已经提供：

```text
docker-compose.yml
```

在 Debian 上推荐直接用：

```bash
mkdir -p /drv2/mysql_docker/bubble
docker compose up -d --build
```

查看运行状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f
```

停止容器：

```bash
docker compose down
```

#### 9.4.4 Debian 上的推荐方式

如果你的目标机器是 Debian，建议流程如下：

1. 安装 Docker Engine 和 Docker Compose 插件
2. 把整个项目目录复制到 Debian
3. 进入项目目录
4. 执行 `docker compose up -d --build`
5. 用浏览器访问 `http://Debian机器IP:8000`

这样宿主机只需要安装 Docker，不需要再单独维护 Python 运行环境。
默认情况下，SQLite 数据库文件会写入：

```text
/drv2/mysql_docker/bubble/lab_inventory.db
```

## 10. 备份说明

当前版本默认使用 SQLite，备份最简单的方法就是备份数据库文件。

数据库文件默认位置：

```text
data/lab_inventory.db
```

如果你使用 Docker 或 Docker Compose，并且按当前配置挂载了 Debian 宿主机目录，那么数据库文件位置会变成：

```text
/drv2/mysql_docker/bubble/lab_inventory.db
```

此时备份方式改为直接备份宿主机这个文件。

### 10.1 手动备份

```bash
cp data/lab_inventory.db data/lab_inventory_backup_$(date +%F).db
```

如果你使用 Docker 挂载 `/drv2/closelist`，则使用：

```bash
cp /drv2/mysql_docker/bubble/lab_inventory.db /drv2/mysql_docker/bubble/lab_inventory_backup_$(date +%F).db
```

### 10.2 恢复备份

先停止服务，然后把备份文件覆盖回去：

```bash
cp data/lab_inventory_backup_2026-03-21.db data/lab_inventory.db
```

然后重新启动服务。

如果你使用 Docker 挂载 `/drv2/mysql_docker/bubble`，则恢复方式是：

```bash
cp /drv2/mysql_docker/bubble/lab_inventory_backup_2026-03-21.db /drv2/mysql_docker/bubble/lab_inventory.db
```

## 11. 迁移到另一台 Linux 电脑

迁移步骤非常简单：

1. 复制整个项目目录到新电脑
2. 复制 `data/lab_inventory.db`
3. 在新电脑上重新创建虚拟环境
4. 安装依赖
5. 启动服务

推荐迁移顺序：

```bash
cd /opt/lab-inventory
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

只要 `data/lab_inventory.db` 一起带过去，原有器件数据就不会丢失。

如果你使用 Docker 迁移到另一台 Debian 电脑，流程更简单：

1. 复制整个项目目录
2. 确认 `data/lab_inventory.db` 已复制
3. 在新机器执行 `docker compose up -d --build`

这样容器会重新构建，但数据库文件会继续沿用原有数据。

## 12. 配置说明

本项目当前支持以下环境变量：

- `DATABASE_URL`：数据库连接地址
- `SECRET_KEY`：会话密钥
- `PAGE_SIZE`：列表每页显示数量，默认 `10`

### 12.1 默认 SQLite 配置

如果不设置 `DATABASE_URL`，系统默认使用：

```text
sqlite:///data/lab_inventory.db
```

实际代码中会自动解析为项目目录下的 `data/lab_inventory.db` 文件。

### 12.2 未来切换到 MySQL

当前代码已经把数据库连接配置集中到了 `app/config.py` 和 `app/database.py`，未来切换 MySQL 时只需要：

1. 安装对应驱动，例如 `pymysql`
2. 修改 `DATABASE_URL`
3. 根据需要做一次数据迁移

示例：

```text
mysql+pymysql://user:password@127.0.0.1:3306/lab_inventory?charset=utf8mb4
```

注意：

- 第一版不建议直接上 MySQL
- 对实验室内部使用场景，SQLite 足够简单可靠
- 等后续确实需要更高并发或统一数据库运维时，再切换更合适

## 13. 示例数据说明

首次启动后，如果数据库为空，系统会自动写入一批示例数据，包括：

- 开发板
- 传感器
- 电源模块
- 连接器件

以及多条示例器件记录，方便你启动后直接看到页面效果。

如果你不想保留示例数据，可以直接在页面中删除，或者删除数据库文件后重新初始化。

## 14. 常见维护操作

### 新增一个分类

进入“分类管理”页面，点击“新增分类”。

### 新增一个器件

进入“器件列表”页面，点击“新增器件”。

### 修改数量

进入器件详情页或编辑页，直接修改“数量”字段即可。

### 删除分类失败

如果某个分类下还有器件，系统会阻止删除。这是为了避免误删后导致器件记录失去分类归属。

## 15. 后续扩展建议

后续可以按下面顺序逐步扩展：

1. 增加图片字段，用于上传器件照片
2. 增加数据手册链接字段
3. 增加厂商字段、采购链接字段
4. 增加导入导出 Excel 功能
5. 增加简单登录功能
6. 增加管理员与普通成员权限区分
7. 如果未来有更高并发需求，再切换 MySQL

建议遵循一个原则：

- 每次只增加一个小功能
- 优先保持现有结构清晰
- 不要过早引入复杂组件

## 16. 开发说明

项目采用分层结构：

- `models.py`：数据库模型
- `services/`：数据库读写与业务逻辑
- `routers/`：页面路由和表单处理
- `templates/`：页面模板

这种结构的好处是：

- 后续改字段时位置明确
- 将来要增加 JSON API 也比较容易
- 将来要增加登录权限，不必推翻现有结构

## 17. 启动后你会看到什么

启动成功后，首页会直接进入“器件列表”页面。

你可以立即看到：

- 搜索框
- 分类筛选
- 器件列表
- 数量展示
- 查看 / 编辑 / 删除按钮
- 分类管理入口

这意味着项目已经是一个可直接运行和继续维护的完整第一版，而不是仅供参考的原型代码片段。
