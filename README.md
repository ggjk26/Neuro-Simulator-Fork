# Neuro Simulator

> **实验性 Fork 警告**：该分支开发周期不稳定，接口、配置和部署方式都可能变动。如果你需要稳定版本，请优先使用主项目。本 Fork 主要用于学习、实验和快速验证新功能。

Neuro Simulator 是一个模拟 Neuro-sama Just Chatting 直播的项目。它包含服务端、Web 客户端、Web 控制面板、Tauri 客户端、Win32/WebView2 原生客户端骨架，以及基础的 Official Neuro SDK WebSocket 兼容层。

## 当前状态概览

- **推荐启动方式**：`neuro-launcher`，或源码目录下的 `scripts/start.sh` / `scripts/start.ps1`。
- **Web 控制面板**：由 Vedal Studio 服务承载，用于编辑配置、查看日志、管理 Agent 和热重载。
- **Web 客户端**：仿 Twitch 直播间界面，支持直播画面、聊天室、字幕、Highlight Message、离线页等。
- **LLM 支持**：使用 OpenAI-compatible Chat Completions 接口；可接 OpenAI、兼容云服务，也可接本地 Ollama / LM Studio / llama.cpp server 等本地大模型服务。
- **TTS 支持**：当前主要支持 Azure TTS；即使使用本地 LLM，语音合成仍需配置 Azure TTS，除非你只使用不需要 TTS 的调试链路。
- **Official Neuro SDK 兼容**：Neuro Sama 模块提供 `ws://<host>:<port>/ws/neuro-sdk` 基础适配端点，支持动作注册和强制动作选择流程。
- **Windows 原生客户端**：`client-native/windows-win32` 提供 Win32 + WebView2 客户端骨架；它承载现有 Web UI，不依赖 Tauri。

## 功能亮点

- **多客户端连接与广播**：服务端可向多个客户端推送直播阶段、聊天、字幕和互动消息。
- **配置热重载**：通过 Web 控制面板编辑配置并重载服务。
- **内建记忆 Agent**：Neuro Agent 支持系统提示、核心记忆、临时记忆和工具调用流程。
- **仿 Twitch 前端**：包含直播页面、离线主播页、聊天侧栏、直播信息、字幕和互动覆盖层。
- **本地 LLM 友好**：配置模板默认包含 Ollama 的 OpenAI-compatible 示例，API key 可为空或使用占位值。

## 目录结构

```text
Neuro-Simulator-Fork/
├── server/                         # Python 服务端与 Agent 模块
│   └── neuro_simulator/
│       ├── launcher.py             # 便捷启动器入口
│       ├── vedal_studio/           # Web 控制面板承载与配置管理
│       ├── neuro_sama/             # Neuro Agent、API、Neuro SDK 适配
│       └── working_dir/            # 首次运行复制到用户目录的默认配置/记忆模板
├── client/                         # 仿 Twitch Web 客户端与 Tauri 客户端
├── dashboard/                      # Vue/Vuetify Web 控制面板
├── client-native/windows-win32/     # Win32 + WebView2 原生 Windows 客户端骨架
├── scripts/                        # 源码运行启动脚本
├── tests/                          # Python 单元测试
├── docs/                           # 示例和 README 媒体资源
└── pyproject.toml                  # Python 包配置与命令入口
```

## 快速开始：推荐流程

### 1. 准备环境

建议使用 Python 3.10+。前端开发或重新构建 Web UI 时还需要 Node.js / npm；仅运行已构建资源时不一定需要 Node.js。

```bash
python -m venv .venv
source .venv/bin/activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
```

如果只想按服务端依赖运行，也可以使用：

```bash
python -m pip install -r server/requirements.txt
```

### 2. 启动 Web UI 与控制面板

安装包后推荐使用：

```bash
neuro-launcher
```

源码目录下也可以直接运行脚本：

```bash
scripts/start.sh --port 8000
# Windows PowerShell
./scripts/start.ps1 --port 8000
```

常用参数：

```bash
neuro-launcher --dir ~/.config/neuro-simulator --host 127.0.0.1 --port 8000
neuro-launcher --no-browser
neuro-launcher --reload
```

启动器会创建/修复工作目录，读取 `config.json`，启动 Vedal Studio Web UI，并默认打开浏览器。

### 3. 打开控制面板并配置服务

默认访问地址：

- Web 控制面板 / 内置 Web UI：`http://127.0.0.1:8000/`
- Neuro Sama 模块默认端口：`127.0.0.1:8001`

首次运行会在工作目录创建配置，例如：

```text
~/.config/neuro-simulator/config.json
~/.config/neuro-simulator/neuro_sama/prompts/neuro_prompt.txt
~/.config/neuro-simulator/neuro_sama/memory/*.json
```

在控制面板中通常需要确认或填写：

1. `general.llm_services`：添加或编辑 LLM 服务。
2. `general.tts_services`：添加或编辑 Azure TTS 服务。
3. `neuro_sama.llm_service_id`：选择要给 Neuro Agent 使用的 LLM 服务。
4. `neuro_sama.tts_service_id`：选择要给 Neuro Agent 使用的 TTS 服务。
5. 保存配置后重启或热重载相关模块。

## 本地 LLM 配置

本项目通过 OpenAI-compatible Chat Completions 客户端调用 LLM，所以本地服务只要提供 `/v1/chat/completions` 兼容接口即可。

### Ollama 示例

1. 启动 Ollama 并拉取模型：

```bash
ollama pull llama3.1:8b
ollama serve
```

2. 在 `config.json` 或控制面板中配置：

```json
{
  "id": "local_ollama",
  "name": "Local Ollama",
  "provider": "local_openai",
  "url": "http://127.0.0.1:11434/v1",
  "model": "llama3.1:8b",
  "key": "ollama"
}
```

3. 将 `neuro_sama.llm_service_id` 设置为 `local_ollama`。

> 说明：Ollama、LM Studio、llama.cpp server 等本地服务通常不校验 API key。本项目现在允许 LLM service 的 `key` 留空；运行时会自动使用 `OPENAI_API_KEY` 环境变量或 `not-needed` 占位值。

### LM Studio / llama.cpp server 示例

只需要把 `url` 改为对应服务的 OpenAI-compatible 地址，并填写该服务暴露的模型名，例如：

```json
{
  "id": "local_lmstudio",
  "name": "Local LM Studio",
  "provider": "local_openai",
  "url": "http://127.0.0.1:1234/v1",
  "model": "local-model",
  "key": ""
}
```

## Azure TTS 配置

当前语音合成主要依赖 Azure TTS。示例结构如下：

```json
{
  "id": "azure_default",
  "name": "Azure TTS",
  "provider": "azure",
  "key": "<your-azure-speech-key>",
  "region": "eastus",
  "timeout": 10
}
```

然后将 `neuro_sama.tts_service_id` 设置为该服务的 `id`。

## Official Neuro SDK 兼容端点

Neuro Sama 模块提供基础兼容端点：

```text
ws://127.0.0.1:8001/ws/neuro-sdk
```

已支持的基础命令：

- `startup`
- `context`
- `actions/register`
- `actions/unregister`
- `actions/force`
- `action/result`

典型流程是：外部集成连接该 WebSocket，发送 `startup`，注册可用动作；当它发送 `actions/force` 时，模拟器会根据上下文调用当前 LLM，在已注册动作里选择一个并返回 `action` 消息。

## 客户端运行方式

### Web 客户端

启动 Vedal Studio 后，直接打开：

```text
http://127.0.0.1:8000/
```

### Web 客户端开发模式

```bash
cd client
npm install
npm run dev
```

### Dashboard 开发模式

```bash
cd dashboard
npm install
npm run dev
```

### Windows 原生客户端骨架

Win32/WebView2 客户端位于：

```text
client-native/windows-win32/
```

构建需要 Windows、Visual Studio C++ 工具链、CMake 和 WebView2 Runtime。详见 `client-native/windows-win32/README.md`。

## 常见问题

### `neuro`、`vedal` 和 `neuro-launcher` 有什么区别？

- `neuro-launcher`：推荐入口，启动 Vedal Studio Web UI，并默认打开浏览器。
- `vedal`：直接启动 Vedal Studio 中央管理服务。
- `neuro`：直接启动 Neuro Sama 模块，通常用于模块级调试，不是普通用户的推荐入口。

### 使用本地 LLM 还需要 Azure TTS 吗？

需要。LLM 和 TTS 是两套服务。本地 LLM 只负责生成文本和工具调用；如果你要在直播客户端听到声音，仍需配置 Azure TTS，或后续自行接入其他 TTS 实现。

### 为什么本地 LLM 的 API key 可以为空？

很多本地 OpenAI-compatible 服务不校验 API key。为了兼容这些服务，配置层允许 `key` 为空，并在运行时使用 `OPENAI_API_KEY` 环境变量或 `not-needed` 作为占位值。

## 开发计划和已实现功能

- 服务端
  - [x] Neuro Agent 模块
    - [x] 基于 Letta 的 Neuro Agent
    - [x] 内建的 Neuro Agent
      - [x] 基本的对话和上下文功能
      - [x] 自动和手动记忆管理，包括系统提示、核心记忆、临时记忆
      - [x] prompt 完整内容编辑
      - [ ] 工具调用
        - [x] 内建工具及调用
          - [x] 记忆管理
          - [ ] 直播标题修改
          - [x] 对外发言
          - [ ] 发起投票和查看结果
          - [x] 旋转和缩放模型
          - [ ] 调整 TTS 语速
          - [ ] 禁言指定名称用户
          - [ ] 播放音效
        - [ ] 模块化热插拔工具
        - [ ] 连接到 MCP 服务器
        - [x] 兼容 Offical [Neuro SDK](https://github.com/VedalAI/neuro-sdk)（基础 WebSocket 适配）
    - [ ] 拉起 Evil Agent 并进行对话
  - [ ] Evil Agent 模块，~~卖掉了~~ 待 Neuro Agent 完善、有低成本低性能方法实现 Evil 音色模仿的时候加入
  - [ ] 对 Neuroverse 更多成员的 AI Agent 复现，进而允许 Neuro Agent 向其发送 DM（语音聊天可能不太现实）
  - [x] Chatbot 模块
    - [x] 无状态 Chatbot（即将弃用）
      - [x] Username 的自动生成和预置替换补充
      - [x] prompt 编辑
      - [x] 调用 Gemini 和 OpenAI API 格式的LLM
      - [x] 基于 Neuro Agent 的上一句内容而做出 Reaction
      - [ ] ~~在 prompt 中包含直播标题等更多信息~~ 将在更强大的 Chatbot Agent 中实现
      - [x] ~~实现更长的上下文~~ 将在更强大的 Chatbot Agent 中实现
    - [x] Chatbot Agent
      - [x] 更好的用户名生成逻辑
      - [x] 更长的上下文，包括自身输出和 Neuro Agent 内容
      - [ ] 在 prompt 中包含直播标题、Neuro 和 Twitch 相关背景知识等更多信息
      - [x] 类似 Neuro Agent 的记忆系统，实现有状态 Chatbot Agent
  - [ ] 真实的 Filter 模块，取代 Agent prompt 中的自我 Filtered.
  - [x] 对外 API 接口，包括常规的 http 和 ws 端点
  - [x] Twitch Chat 及管理
    - [x] 普通 Chat
      - [x] 随机池机制，从中抽取消息注入 Neuro
    - [x] 醒目留言 Highlight Messages
      - [x] 队列机制，先进先出
      - [ ] 可选的 TTS Guy
    - [ ] Subs 和 Donations 相关机制
    - [ ] 禁言指定名称用户
  - [x] 配置管理和热重载
  - [x] TTS 合成和推送
    - [x] Azure TTS
    - [ ] 待定 TTS
    - [X] 剔除 Emoji 等特殊字符
  - [x] 进行直播和直播环节
    - [x] Just Chatting 单人直播
      - [x] Neuro Stream
      - [ ] Evil Stream
    - [ ] Karaoke 歌回直播
    - [ ] Twin 闲聊或主题直播
    - [ ] 艺术鉴赏直播环节
  - [x] 多客户端连接和广播
    - [ ] 动态推送开场 Starting Soon 视频
    - [x] 直播阶段
      - [x] Starting Soon
      - [x] 神の上升
      - [x] 常规直播
      - [ ] Ending
    - [x] 直播和聊天室内容
    - [x] 醒目留言 Highlight Messages
    - [x] 直播标题和标签等信息
  - [ ] 在非直播的空闲时间自动获取真实世界中 Neuro 的近期直播内容，更新完善记忆内容（不是微调训练）
  - [x] 支持 Ollama / LM Studio / llama.cpp server 等本地 OpenAI-compatible LLM
  - [x] 服务端托管管理面板
    - [x] Web 控制面板
    - [ ] 使用 PyInquiry 的命令行面板
- 客户端
  - [ ] 仅包含直播区域的客户端，适用于希望使用 OBS 或其他软件推流画面的用户
  - [x] 可自定义的用户信息和服务端地址
  - [x] 仿 Twitch 直播界面
    - [x] 响应式设计
    - [x] 主要界面元素
    - [ ] 次级页面
    - [x] Twitch Chat 和其他互动
      - [x] 普通聊天的发送和查看
      - [x] 使用 Bits 和 Channel Points 发送醒目留言 Highlight Messages
      - [ ] 表情发送
      - [ ] Bits & Channel Points 逻辑
      - [ ] 小牛最爱的 Subs 和 Donations 相关逻辑
      - [ ] 参与投票
    - [x] 主播和直播信息
      - [x] 头像、名称信息
      - [x] 动态更新的直播标题、分区、标签
      - [x] 动态更新的人数和直播时长
      - [ ] 下滑的更多主播信息
    - [x] 使用 html 模拟的直播场景
      - [x] 仿真字幕样式
        - [x] 字体和描边效果
        - [x] 逐字跳出效果
        - [x] 随内容量的字号调整效果
      - [x] 仿真 Twitch Chat Overlay
      - [x] Neuro 立绘
        - [x] 开场上升
        - [ ] 表情差分
        - [x] 旋转缩放
        - [x] 自然晃动
        - [ ] 音效播放
      - [ ] Evil 立绘
      - [x] 醒目留言 Highlight Messages Overlay
        - [x] 根据来源（Bits 或 Channel Points）显示不同颜色背景
        - [x] 展示用户名和内容
        - [x] 更真实的进入/退出动画
  - [x] 仿 Twitch 离线界面（主播首页）
    - [x] 响应式设计
    - [x] 自动获取最新哔哩哔哩官号回放
    - [ ] 自动获取上一场哔哩哔哩直播回放对应的时间、分区、回放视频链接
    - [ ] 真实的主播首页竖屏模式界面（目前沿用针对竖屏优化过的横屏样式）
    - [ ] 下滑的更多主播信息
    - [ ] 其他次级页面
  - [x] 服务端托管客户端
  - [ ] 更多客户端（若实现原生客户端则弃用 tauri）
    - [x] 可托管的 Web 静态页面
    - [x] Windows 客户端
      - [x] 基于 Tauri
      - [x] 原生（Win32/WebView2 基础客户端）
    - [x] Linux 客户端
      - [x] 基于 Tauri
      - [ ] 原生
    - [ ] Android 客户端
      - [ ] 基于 Tauri
      - [ ] 原生
- Web 控制面板
  - [x] 更加便捷的启动器/启动脚本
  - [x] 指定服务端 URL 进行连接
  - [x] 直播的开始、停止、重启
  - [x] 配置的查看、编辑、热重载
  - [x] 服务端实时日志查看
    - [ ] 按照等级进行日志筛选
  - [x] Agent管理
    - [x] 对话上下文查看
      - [x] 对话方式展现
      - [x] 上下文方式展现
      - [x] 实时更新
      - [ ] 可视化展现 Agent 的详细执行流程
    - [x] 实时日志查看
      - [ ] 按照等级进行日志筛选 
    - [x] 记忆查看和手动管理
    - [x] 工具
      - [x] 简易的内建工具查看
      - [ ] 工具管理取决于服务端开发进度
- 杂项，有一些可能永远不会实现，有一些可能很快就能完成
  - [ ] 一键启动器和整合包，适用于不需要分开部署的情况，或者面向普通小白用户
  - [ ] 基于静态立绘制作的简易Live2D，能动就行
  - [x] 目前不会考虑语音输入


  - [ ] 等待补充…

## 贡献

该fork仅使用codex开发，开发周期不稳定。
