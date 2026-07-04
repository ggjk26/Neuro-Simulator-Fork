# Neuro Simulator Win32 Native Client

这是一个不依赖 Tauri 的 Windows 原生客户端骨架，使用 Win32 API 创建窗口，并通过 Microsoft Edge WebView2 承载 Neuro Simulator 的 Web 客户端页面。

## 功能

- 原生 Win32 桌面窗口。
- WebView2 内嵌客户端页面。
- 默认连接 `http://127.0.0.1:8000/`。
- 支持通过命令行参数覆盖入口地址：

```powershell
neuro-win32.exe --url=http://192.168.1.10:8000/
```

## 前置条件

- Windows 10/11。
- Visual Studio 2022 或 Build Tools for Visual Studio，包含 C++ 桌面开发工具链。
- CMake 3.21 或更新版本。
- Microsoft Edge WebView2 Runtime。

## 构建

```powershell
cmake -S client-native/windows-win32 -B build/win32-client -G "Visual Studio 17 2022" -A x64
cmake --build build/win32-client --config Release
```

构建脚本会下载 `Microsoft.Web.WebView2` NuGet 包，并静态链接 WebView2 loader。

## 运行

先启动 Neuro Simulator 服务端，使 Web 客户端可通过浏览器访问，然后运行：

```powershell
.\build\win32-client\Release\neuro-win32.exe
```

如服务端不在本机默认端口，使用 `--url=` 指定地址。
