# Redis缓存功能使用指南

## 概述

本项目集成了Redis缓存功能，通过文件内容的MD5哈希来识别已处理过的文件，避免重复解析相同内容的文件，从而提高解析效率。

## 功能特点

- **智能缓存**：基于文件内容MD5哈希进行缓存，而非文件名
- **自动过期**：缓存数据默认保存1天（可配置）
- **高性能**：Redis内存存储，毫秒级响应
- **透明使用**：对API用户完全透明，自动命中缓存
- **缓存管理**：提供API查看缓存统计和清理缓存

## 配置说明

### 环境变量配置

在`.env`文件中添加以下Redis相关配置：

```bash
# Redis缓存配置
REDIS_HOST=localhost                # Redis服务器地址
REDIS_PORT=6379                     # Redis端口
REDIS_PASSWORD=                     # Redis密码（可选）
REDIS_DB=0                         # Redis数据库编号
REDIS_CACHE_ENABLED=true           # 是否启用缓存
REDIS_CACHE_TTL=86400              # 缓存保存时间（秒），默认1天
REDIS_CONNECTION_TIMEOUT=5.0       # 连接超时时间
REDIS_MAX_CONNECTIONS=20           # 最大连接数
```

### Redis服务部署

#### 使用Docker部署Redis

```bash
# 启动Redis容器
docker run -d \
  --name file2md-redis \
  -p 6379:6379 \
  redis:7-alpine redis-server --appendonly yes

# 带密码的Redis
docker run -d \
  --name file2md-redis \
  -p 6380:6379 \
  redis:7-alpine redis-server --appendonly yes --requirepass 'your-password'
```

#### 系统安装Redis

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install redis-server

# CentOS/RHEL
sudo yum install redis

# macOS
brew install redis

# 启动Redis服务
sudo systemctl start redis
# 或
redis-server
```

## 使用方式

### 自动缓存

缓存功能对用户完全透明：

1. **首次上传**：文件被解析并缓存结果
2. **相同文件再次上传**：自动从缓存返回结果，大幅提高响应速度
3. **不同文件名但内容相同**：依然能命中缓存

### API响应字段

启用缓存后，API响应会包含额外字段：

```json
{
  "filename": "document.pdf",
  "size": 1024000,
  "content_type": "application/pdf",
  "content": "# 文档内容...",
  "duration_ms": 50,
  "from_cache": true,
  "cache_hit_time": 1640995200000,
  "cache_duration_ms": 5
}
```

字段说明：
- `from_cache`: 是否来自缓存
- `cache_hit_time`: 缓存命中时间戳
- `cache_duration_ms`: 缓存查询耗时

### 缓存管理API

#### 查看缓存统计

```bash
GET /v1/cache/stats
```

响应示例：
```json
{
  "enabled": true,
  "cache_count": 15,
  "redis_version": "7.0.0",
  "used_memory_human": "2.50M",
  "connected_clients": 3,
  "total_commands_processed": 1250,
  "cache_ttl_hours": 24
}
```

#### 清理缓存

```bash
POST /v1/cache/clear
```

响应示例：
```json
{
  "message": "成功清除 15 条缓存记录",
  "cleared_count": 15
}
```

## 工作原理

### 缓存键生成

1. 计算文件内容的MD5哈希
2. 生成缓存键：`file2md:cache:{md5_hash}`
3. 使用Redis存储解析结果

### 缓存流程

```
文件上传 → 计算MD5 → 检查缓存 → [命中] 返回缓存结果
                              ↓ [未命中]
                            解析文件 → 保存缓存 → 返回结果
```

### 数据结构

缓存存储的数据结构：
```json
{
  "filename": "原始文件名",
  "content": "解析后的Markdown内容",
  "size": "文件大小",
  "content_type": "文件类型",
  "duration_ms": "解析耗时",
  "cached_time": "缓存时间戳",
  "file_hash": "文件MD5哈希"
}
```

## 性能优化

### 缓存命中率优化

1. **合理设置TTL**：根据业务需求调整缓存过期时间
2. **监控缓存统计**：定期检查缓存命中率
3. **内存管理**：控制Redis内存使用，避免内存不足

### 推荐配置

#### 开发环境
```bash
REDIS_CACHE_TTL=3600        # 1小时
REDIS_MAX_CONNECTIONS=10    # 较少连接数
```

#### 生产环境
```bash
REDIS_CACHE_TTL=86400       # 1天
REDIS_MAX_CONNECTIONS=50    # 更多连接数
```

## 监控和维护

### 健康检查

缓存状态包含在健康检查端点中：

```bash
GET /v1/health
```

### 日志监控

关注以下日志：
- `缓存命中`: 表示成功从缓存获取结果
- `缓存已保存`: 表示新结果已缓存
- `Redis连接失败`: 需要检查Redis服务状态

### 故障处理

#### Redis连接失败

1. 检查Redis服务是否运行
2. 验证网络连接
3. 检查认证配置

如果Redis不可用，应用会自动降级到无缓存模式，不影响正常功能。

## 测试验证

使用提供的测试脚本验证缓存功能：

```bash
python test_cache.py
```

## 安全注意事项

1. **Redis密码**：生产环境务必设置Redis密码
2. **网络隔离**：Redis应在内网环境，不对外暴露
3. **数据加密**：敏感环境可考虑启用Redis TLS
4. **访问控制**：限制Redis访问权限

## 常见问题

### Q: 缓存未生效？
A: 检查以下配置：
- `REDIS_CACHE_ENABLED=true`
- Redis服务是否正常运行
- 网络连接是否正常

### Q: 如何清理过期缓存？
A: Redis会自动清理过期数据，也可手动调用清理API

### Q: 缓存占用内存过多？
A: 可以：
- 减少TTL时间
- 定期清理缓存
- 增加Redis内存限制

### Q: 相同文件但文件名不同，能命中缓存吗？
A: 可以。缓存基于文件内容MD5，与文件名无关。 