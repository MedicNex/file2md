# MedicNex File2MD 安全指南

## 安全概述

此文档描述了 MedicNex File2MD 项目的安全措施和最佳实践。

## 🔒 已实施的安全措施

### 1. API 密钥安全
- ✅ 移除了所有硬编码的 API 密钥
- ✅ 强制要求通过环境变量设置 API_KEY
- ✅ 提供了 `.env.example` 配置模板
- ✅ 启动脚本会验证必需的环境变量

### 2. 环境变量安全加载
- ✅ 替换了不安全的 `export $(cat .env | xargs)` 模式
- ✅ 实现了安全的环境变量解析
- ✅ 验证环境变量名格式（仅允许字母、数字、下划线）
- ✅ 过滤危险字符和模式

### 3. 外部工具调用安全
- ✅ 为 Pandoc 调用添加了沙箱模式和超时限制
- ✅ 使用绝对路径防止路径遍历攻击
- ✅ 实现文件大小和路径验证
- ✅ 添加了内容长度限制和清理

### 4. ImageMagick/SVG 安全
- ✅ 为 ImageMagick 设置了安全选项
- ✅ 限制图片输出尺寸和分辨率
- ✅ 验证 SVG 内容，移除危险元素
- ✅ 过滤脚本标签和事件处理器

### 5. 内容清理和验证
- ✅ 对 OCR 和 Vision API 结果进行内容清理
- ✅ 防止 Markdown 注入攻击
- ✅ 移除 HTML 脚本和危险标签
- ✅ 限制内容长度和清理控制字符

## 🛠️ 配置指南

### 环境变量配置

1. 复制环境变量模板：
```bash
cp env.example .env
```

2. 编辑 `.env` 文件并设置您的 API 密钥：
```env
API_KEY=your-openai-api-key-here
PORT=8999
MAX_CONCURRENT=10
```

3. 确保文件权限安全：
```bash
chmod 600 .env
```

### 生产环境部署

1. **使用环境特定的配置**：
```bash
# 开发环境
cp env.example .env.dev

# 生产环境
cp env.example .env.prod
```

2. **设置严格的文件权限**：
```bash
# 限制配置文件访问
chmod 600 .env*
chown app:app .env*

# 限制应用目录访问
chmod 750 /path/to/app
```

3. **使用密钥管理服务**（推荐）：
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Kubernetes Secrets

## 🔍 安全验证

### 文件处理限制
- RTF/ODT 文件：最大 50MB
- SVG 文件：最大 10MB
- 图片文件：最大分辨率 2000x2000
- 文本内容：最大 1MB（RTF/ODT），500KB（SVG）

### 支持的安全特性
- 文件类型验证
- 路径遍历防护
- 内容长度限制
- 危险元素过滤
- 沙箱模式执行

## ⚠️ 安全建议

### 1. 定期安全维护
- 定期轮换 API 密钥
- 更新依赖库到最新版本
- 监控安全漏洞公告

### 2. 网络安全
```bash
# 使用防火墙限制访问
ufw allow from trusted_ip to any port 8999

# 设置 HTTPS（生产环境必需）
# 使用 nginx 或 Apache 作为反向代理
```

### 3. 日志监控
```bash
# 监控异常访问模式
tail -f /var/log/medicnex/*.log | grep -E "(ERROR|WARN)"

# 设置日志轮转
logrotate /etc/logrotate.d/medicnex
```

### 4. 容器安全（如使用 Docker）
```dockerfile
# 使用非 root 用户
USER app:app

# 限制容器权限
--cap-drop=ALL
--read-only
--no-new-privileges
```

## 🚨 安全事件响应

### 发现安全问题时的步骤：

1. **立即隔离**：停止相关服务
2. **评估影响**：确定受影响的数据和系统
3. **通知相关方**：通知管理员和用户
4. **修复漏洞**：应用安全补丁
5. **验证修复**：测试安全措施有效性
6. **记录总结**：更新安全文档和流程

## 📞 安全联系信息

如发现安全漏洞，请通过以下方式报告：
- 邮箱：security@medicnex.com
- 加密通信：使用 GPG 密钥
- 内部系统：通过安全事件管理系统

## 🔄 安全更新日志

### v1.1.0 (最新)
- 移除硬编码 API 密钥
- 实现安全的环境变量加载
- 添加文件验证和内容清理
- 增强外部工具调用安全性

### 计划改进
- [ ] 实现速率限制
- [ ] 添加用户认证和授权
- [ ] 集成威胁检测系统
- [ ] 实现安全审计日志

---

**注意**：安全是一个持续的过程。请定期审查和更新安全措施，确保系统始终符合最新的安全标准。 