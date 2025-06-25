# 贡献指南

感谢您对 MedicNex File2Markdown 项目的关注！我们热烈欢迎社区贡献，让这个项目变得更好。

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Docker 和 Docker Compose（推荐）
- Git

### 开发环境设置

1. **Fork 并克隆仓库**
```bash
git clone https://github.com/your-username/medicnex-file2md.git
cd medicnex-file2md
```

2. **设置开发环境**
```bash
# 使用Docker（推荐）
./docker-deploy.sh

# 或者本地开发
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **运行项目**
```bash
# Docker方式
docker-compose up -d

# 本地方式
python -m uvicorn app.main:app --reload --port 8080
```

## 🐛 报告问题

我们使用 GitHub Issues 来跟踪问题。在报告新问题之前，请：

1. **搜索现有问题**：确保问题尚未被报告
2. **使用问题模板**：提供所有必要信息
3. **提供详细信息**：
   - 操作系统和版本
   - Python版本
   - 错误的完整堆栈跟踪
   - 重现步骤
   - 预期行为 vs 实际行为

### 问题标签

- `bug`: 软件缺陷
- `enhancement`: 新功能请求
- `documentation`: 文档改进
- `good first issue`: 适合新贡献者
- `help wanted`: 需要社区帮助

## 💡 提出功能建议

我们欢迎新功能建议！请在 Issues 中：

1. **清楚描述用例**：解释为什么需要这个功能
2. **提供详细规范**：描述期望的行为
3. **考虑替代方案**：是否有现有的解决方法
4. **评估影响**：对性能、复杂性的影响

## 🔧 代码贡献

### 工作流程

1. **创建分支**
```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b bugfix/issue-number
```

2. **编写代码**
   - 遵循现有代码风格
   - 添加必要的测试
   - 更新相关文档

3. **提交更改**
```bash
git add .
git commit -m "feat: add support for new file format"
```

4. **推送并创建 PR**
```bash
git push origin feature/your-feature-name
```

### 提交消息规范

我们使用[约定式提交](https://www.conventionalcommits.org/zh-hans/)规范：

- `feat:` 新功能
- `fix:` 错误修复
- `docs:` 文档更新
- `style:` 代码格式（不影响代码运行）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```
feat(parsers): add support for .epub files
fix(docker): resolve PaddleOCR initialization issue
docs(readme): update installation instructions
```

### 代码风格

我们遵循以下代码规范：

- **Python**: PEP 8 风格指南
- **注释**: 中文注释，英文变量名
- **类型注解**: 使用 Python 类型提示
- **文档字符串**: 使用详细的 docstring

### 添加新解析器

如果您想添加对新文件格式的支持：

1. **创建解析器文件**
```python
# app/parsers/your_format.py
from app.parsers.base import BaseParser

class YourFormatParser(BaseParser):
    @classmethod
    def get_supported_extensions(cls):
        return ['.yourext']
    
    async def parse(self, file_path: str) -> str:
        # 实现解析逻辑
        pass
```

2. **注册解析器**
```python
# app/parsers/registry.py
from .your_format import YourFormatParser

# 添加到解析器映射中
```

3. **添加测试**
```python
# tests/test_your_format.py
def test_your_format_parser():
    # 添加测试用例
    pass
```

4. **更新文档**
   - 在 `SUPPORTED_FORMATS.md` 中添加格式说明
   - 更新 README.md 中的支持格式统计

## 🧪 测试

我们重视测试！请为您的贡献添加适当的测试：

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest tests/test_parsers.py

# 运行并生成覆盖率报告
python -m pytest --cov=app tests/
```

### 测试类型

- **单元测试**: 测试单个函数/类
- **集成测试**: 测试解析器和API集成
- **端到端测试**: 测试完整的转换流程

### 测试文件

请在 `tests/` 目录下添加相应的测试文件，并提供测试用的示例文件。

## 📚 文档

文档是项目的重要组成部分：

### 文档类型

- **API文档**: 自动从代码生成
- **用户指南**: README.md 和相关文档
- **开发文档**: 本文件和代码注释

### 文档更新

当您的更改影响到：
- API接口
- 配置选项
- 使用方法
- 支持的文件格式

请相应更新文档。

## 🔍 代码审查

所有代码贡献都需要经过代码审查：

### 审查清单

- [ ] 代码符合项目风格
- [ ] 包含适当的测试
- [ ] 文档已更新
- [ ] 通过所有CI检查
- [ ] 没有引入破坏性变更

### 响应审查

- 及时回应审查评论
- 根据反馈调整代码
- 保持友好和建设性的讨论

## 🏷️ 发布流程

项目维护者负责发布管理：

1. **版本控制**: 使用语义化版本控制
2. **变更日志**: 更新 README.md 中的更新记录
3. **标签发布**: 创建Git标签
4. **Docker镜像**: 构建和推送新的Docker镜像

## 💬 社区

### 沟通渠道

- **GitHub Issues**: 问题报告和功能讨论
- **GitHub Discussions**: 一般讨论和问答
- **Pull Requests**: 代码审查和讨论

### 行为准则

我们期望所有贡献者：

- 保持友好和专业
- 尊重不同观点
- 专注于技术讨论
- 帮助新贡献者

## 🎯 贡献想法

如果您不知道从哪里开始，这里有一些建议：

### 🟢 适合新手
- 修复文档中的错别字
- 改进错误消息
- 添加单元测试
- 更新依赖版本

### 🟡 中等难度
- 添加新的文件格式支持
- 优化现有解析器性能
- 改进Docker配置
- 添加新的配置选项

### 🔴 高难度
- 重构核心架构
- 添加新的API功能
- 实现并发优化
- 添加国际化支持

## ❓ 获取帮助

如果您需要帮助：

1. **查看文档**: README.md 和相关文档
2. **搜索Issues**: 可能已有相似问题
3. **创建讨论**: 在 GitHub Discussions 中提问
4. **联系维护者**: 在相关Issue中@维护者

---

再次感谢您的贡献！每一个贡献，无论大小，都让这个项目变得更好。🙏

## 🎉贡献者

<div align="center">
<a href="https://github.com/MedicNex/medicnex-file2md/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=MedicNex/medicnex-file2md" />
</a>
</div>

**Happy coding!** 🚀 