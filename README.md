# Call DK MCP

> Call DK MCP服务器 - 为AI辅助开发提供用户call dk功能

## 项目概述

Call DK MCP 是一个基于 Model Context Protocol (MCP) 的服务器，专为AI辅助开发场景设计。它提供了一个图形用户界面，允许用户进行交互式call dk。

**许可证**: MIT License

## 核心功能

### 🎯 主要特性

- **交互式call dk系统**: 通过GUI界面收集用户的call dk
- **🚀 提示词优化功能**: 集成Google Gemini AI，智能优化用户输入的提示词
- **现代化UI**: 基于PySide6构建，支持暗色主题
- **跨平台兼容**: 支持Windows、macOS和Linux
- **MCP协议集成**: 完全兼容Model Context Protocol标准

### 🛠️ 技术实现

#### 架构设计

```
call-dk-mcp/
├── server.py          # MCP服务器主文件
├── calldk_ui.py       # GUI用户界面实现
├── test_server.py     # 测试文件
└── images/           # 界面资源文件
```

## MCP配置

在Claude Desktop或其他MCP客户端中添加以下配置：

```json
{
  "mcpServers": {
    "call-dk-mcp": {
      "command": "python",
      "args": [
        "G:\\docker\\McpApi\\call-dk-mcp\\server.py"
      ],
      "cwd": "G:\\docker\\McpApi\\call-dk-mcp"
    }
  }
}
```

**注意**: 请将路径 `G:\\docker\\McpApi\\call-dk-mcp` 替换为你的实际项目路径。

#### 核心组件

1. **MCP服务器 (server.py)**
   - 基于FastMCP框架构建
   - 提供`call_dk`工具接口
   - 无需参数，直接调用
   - 管理GUI进程的启动和结果收集

2. **GUI界面 (calldk_ui.py)**
   - 使用PySide6构建现代化界面
   - 支持Windows暗色标题栏
   - 提供用户call dk输入功能
   - 支持图片上传功能

3. **配置管理**
   - 保存用户界面设置
   - 项目特定的配置存储

## 技术栈

### 依赖项

- **Python**: >=3.11
- **fastmcp**: >=2.0.0 (MCP协议实现)
- **pyside6**: >=6.8.2.1 (GUI框架)
- **pillow**: >=10.0.0 (图片处理)
- **google-genai**: >=1.25.0 (Google Gemini AI API)
- **python-dotenv**: >=1.1.1 (环境变量管理)

### 开发工具

- **pip**: Python包管理器
- **pytest**: 测试框架
- **Git**: 版本控制

## 使用说明

### 环境要求

- Python >= 3.11
- 支持的操作系统：Windows、macOS、Linux

### 快速开始

#### 1. 克隆项目
```bash
git clone <repository-url>
cd call-dk-mcp
```

#### 2. 创建虚拟环境
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # Linux/Mac
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量
```bash
# 复制环境变量模板
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac

# 编辑.env文件，配置你的Google Gemini API密钥
```

#### 5. 运行项目
```bash
# 作为MCP服务器运行
python server.py

# 或直接运行GUI界面测试
python calldk_ui.py
```

### MCP工具使用

服务器提供一个主要工具：

```python
call_dk() -> List[Union[str, Image]]
```

**返回值**:
- 文本内容：用户call dk内容
- 图片内容：用户上传的图片

## 项目结构

```
call-dk-mcp/
├── images/                  # 界面资源
│   ├── attribution.txt
│   └── feedback.png
├── venv/                   # 虚拟环境
├── README.md               # 项目文档
├── calldk_ui.py            # GUI界面实现
├── server.py               # MCP服务器
├── test_server.py          # 测试文件
├── prompt_optimizer.py     # 提示词优化模块
├── .env                    # 环境配置文件
└── 参考文件/               # 参考实现文件
```

## 开发特性

### 代码质量

- **类型注解**: 完整的Python类型提示
- **错误处理**: 健壮的异常处理机制
- **进程管理**: 安全的子进程启动和清理
- **跨平台支持**: Windows特定优化和通用兼容性

### 用户体验

- **响应式界面**: 流畅的用户交互体验
- **暗色主题**: 现代化的视觉设计
- **实时反馈**: 命令执行状态的实时显示
- **配置持久化**: 用户设置的自动保存

## 工作流程

1. **AI代理调用**: AI助手通过MCP协议调用`call_dk`工具
2. **GUI启动**: 系统启动图形界面，标题为"call dk"
3. **用户交互**: 用户输入call dk内容，可选择上传图片
4. **结果返回**: 系统收集用户call dk和图片，返回给AI代理
5. **流程完成**: AI代理基于call dk继续后续操作

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系方式

- **项目**: Call DK MCP
- **许可证**: MIT License

---

## 🚀 提示词优化功能

### 功能概述
集成了基于Google Gemini 2.5 Flash模型的智能提示词优化功能，能够将用户输入的简单提示词优化为更清晰、具体、有效的提示词。

### 配置步骤

1. **获取Google Gemini API密钥**
   - 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
   - 创建新的API密钥
   - 复制生成的API密钥

2. **配置环境变量**
   - 编辑项目根目录下的 `.env` 文件
   - 将 `GEMINI_API_KEY=your_api_key_here` 中的 `your_api_key_here` 替换为你的实际API密钥

   ```env
   # Google Gemini API配置
   GEMINI_API_KEY=AIzaSyC_your_actual_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   GEMINI_TEMPERATURE=0.2
   GEMINI_MAX_TOKENS=1000
   ```

3. **安装依赖**
   ```bash
   # 激活虚拟环境
   venv\Scripts\activate  # Windows

   # 安装提示词优化相关依赖
   pip install google-genai python-dotenv
   ```

### 使用方法

1. **启动GUI界面**
   ```bash
   python calldk_ui.py
   ```

2. **使用提示词优化**
   - 在文本输入框中输入原始提示词
   - 点击 "🚀 提示词优化 (Ctrl+Q)" 按钮或按快捷键 `Ctrl+Q`
   - 等待AI处理完成（按钮会显示"🧠 优化中..."）
   - 优化后的提示词会自动替换输入框中的内容
   - 如需撤销优化，按 `Ctrl+Z` 恢复原始内容

### 优化示例

**原始提示词：**
```
写一个关于AI的文章
```

**优化后的提示词：**
```
请撰写一篇关于人工智能技术发展现状与未来趋势的深度分析文章。文章应包含：
1. AI技术的历史发展脉络
2. 当前主流AI技术及其应用领域
3. AI对社会经济的影响分析
4. 未来AI发展的机遇与挑战
5. 对AI伦理和监管的思考
文章字数控制在2000-3000字，语言专业但易懂，适合技术爱好者阅读。
```

### 功能特点

- **智能优化**: 基于Google Gemini 2.5 Flash模型的AI思考能力
- **保持原意**: 优化过程中保持用户原始意图不变
- **增强细节**: 自动添加必要的细节和具体要求
- **多领域适用**: 适用于各种领域和场景的提示词优化
- **快捷键支持**: `Ctrl+Q` 快速优化，`Ctrl+Z` 撤销操作
- **无干扰体验**: 优化完成后无弹窗提示，保持流畅操作
- **撤销功能**: 支持一键撤销优化，恢复原始输入内容

### 故障排除

**问题：提示词优化按钮显示为灰色不可用**
- 检查 `.env` 文件中的API密钥是否正确配置
- 确认已安装 `google-genai` 依赖包
- 验证网络连接是否正常

**问题：优化失败提示API错误**
- 检查API密钥是否有效且有足够的配额
- 确认API密钥有访问Gemini模型的权限
- 检查网络连接和防火墙设置

---

## 功能特性

### 图片上传功能

#### 功能概述
为call dk系统增加图片上传功能，允许用户在call dk中包含图像内容，提升AI助手对用户需求的理解能力。

#### 实现思路

**1. 用户界面增强**
- 在call dk文本框旁边添加"添加图片"按钮
- 支持点击按钮选择本地图片文件（支持常见格式：PNG、JPG、JPEG、GIF等）
- 添加"清除所有图片"按钮，允许用户移除已选择的图片
- 在界面中显示已选择图片的缩略图预览
- 支持单个图片删除功能

**2. 图片处理流程**
- 用户选择图片后，在本地进行预处理（压缩、格式转换等）
- 图片临时存储在内存中，不写入磁盘
- 支持多张图片上传（可设置数量限制，如最多5张）

**2.1 截图功能实现**
- 集成屏幕截图工具，支持区域截图
- 自定义截图快捷键设置（默认可设为Ctrl+Shift+S）
- 截图后自动添加到反馈框的图片预览区域
- 支持截图编辑功能（如标注、裁剪等基础操作）

**3. 数据传输机制**
- 用户点击"发送call dk"时，将图片转换为Base64编码
- 通过MCP协议将图片数据与文字call dk一同传输给AI客户端
- 返回数据结构：
  ```python
  {
      "interactive_calldk": str,
      "images": [
          {
              "filename": str,
              "data": str,  # Base64编码的图片数据
              "mime_type": str  # 图片MIME类型
          }
      ]
  }
  ```

**4. AI处理能力**
- AI助手接收到图片数据后，利用内置的图像识别功能分析图片内容
- 结合文字call dk和图像内容，提供更准确的响应
- 支持图片中的文字识别（OCR）、对象检测、场景理解等

#### 技术实现要点

**前端界面（PySide6）**
- 使用`QFileDialog`实现文件选择
- 使用`QLabel`显示图片缩略图
- 使用`QScrollArea`支持多图片展示
- 图片压缩使用PIL/Pillow库

**数据处理**
- 图片大小限制（如单张不超过5MB）
- 自动压缩大尺寸图片以优化传输
- 支持的图片格式验证

**安全考虑**
- 内存使用优化，防止大图片导致内存溢出

#### 用户体验优化

- **图片预览**：显示已选择图片的缩略图
- **单个删除**：支持删除单个图片
- **错误处理**：友好的错误提示信息
- **格式支持**：支持常见图片格式

---

## 工作进度记录

### 2025-01-27 Call DK功能实现与优化

**实现内容：**
1. **项目重构** - 将所有"feedback"相关字眼替换为"call dk"
2. **文件重命名** - feedback_ui.py重命名为calldk_ui.py
3. **界面优化** - 简化GUI界面，去掉不必要的描述区域
4. **图片功能** - 支持图片上传和预览功能
5. **测试完善** - 添加pytest测试确保功能正常

**技术优化：**
1. **代码清理** - 移除不必要的依赖导入
2. **函数重命名** - 所有函数名从feedback改为calldk
3. **配置更新** - 更新MCP配置为标准Python环境
4. **文档完善** - 更新README.md文档

**当前状态：** 功能实现完成，所有测试通过，GUI界面简洁易用

### 2025-01-27 提示词优化功能集成

**实现内容：**
1. **提示词优化模块** - 基于Google Gemini 2.5 Flash模型的智能优化功能
2. **环境配置管理** - 使用.env文件管理API密钥和模型参数
3. **GUI界面集成** - 在calldk_ui.py中添加"提示词优化"按钮
4. **异步处理** - 使用QThread避免UI阻塞，提供流畅的用户体验
5. **错误处理** - 完善的错误提示和状态反馈机制

**技术实现：**
1. **依赖管理** - 新增google-genai和python-dotenv依赖
2. **模块封装** - 创建独立的prompt_optimizer.py模块
3. **线程处理** - 实现OptimizeThread类处理API调用
4. **配置系统** - 支持多种模型参数和优化选项配置
5. **用户体验** - 一键优化，自动替换输入内容

**功能特点：**
- 🧠 AI思考模式：利用Gemini 2.5的内置思考能力
- 🎯 智能优化：保持原意的同时增强提示词的具体性和有效性
- ⚡ 快速响应：异步处理确保界面流畅不卡顿
- 🔧 灵活配置：支持温度、Token数等参数调整
- 🛡️ 错误处理：友好的错误提示和状态反馈

**当前状态：** 提示词优化功能集成完成，支持一键智能优化用户输入


*本项目旨在改善AI辅助开发的用户体验，通过call dk机制让开发者更好地与AI协作。*