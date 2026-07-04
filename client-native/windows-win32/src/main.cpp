#include <WebView2.h>
#include <windows.h>
#include <shellapi.h>
#include <wrl.h>

#include <cwchar>
#include <string>

using Microsoft::WRL::Callback;
using Microsoft::WRL::ComPtr;

namespace {
constexpr wchar_t kWindowClassName[] = L"NeuroSimulatorWin32ClientWindow";
constexpr wchar_t kWindowTitle[] = L"Neuro Simulator";
constexpr wchar_t kDefaultUrl[] = L"http://127.0.0.1:8000/";

ComPtr<ICoreWebView2Controller> g_webviewController;
ComPtr<ICoreWebView2> g_webview;

std::wstring GetInitialUrl() {
    int argc = 0;
    LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);
    std::wstring url = kDefaultUrl;

    if (argv != nullptr) {
        for (int index = 1; index < argc; ++index) {
            const std::wstring arg = argv[index];
            constexpr wchar_t prefix[] = L"--url=";
            if (arg.rfind(prefix, 0) == 0 && arg.size() > std::wcslen(prefix)) {
                url = arg.substr(std::wcslen(prefix));
                break;
            }
        }
        LocalFree(argv);
    }

    return url;
}

void ResizeWebView(HWND hwnd) {
    if (!g_webviewController) {
        return;
    }

    RECT bounds{};
    GetClientRect(hwnd, &bounds);
    g_webviewController->put_Bounds(bounds);
}

void InitializeWebView(HWND hwnd) {
    const std::wstring initialUrl = GetInitialUrl();

    CreateCoreWebView2EnvironmentWithOptions(
        nullptr,
        nullptr,
        nullptr,
        Callback<ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler>(
            [hwnd, initialUrl](HRESULT result, ICoreWebView2Environment* environment) -> HRESULT {
                if (FAILED(result) || environment == nullptr) {
                    MessageBoxW(hwnd, L"WebView2 Runtime 初始化失败，请安装 Microsoft Edge WebView2 Runtime。", kWindowTitle, MB_ICONERROR | MB_OK);
                    return result;
                }

                environment->CreateCoreWebView2Controller(
                    hwnd,
                    Callback<ICoreWebView2CreateCoreWebView2ControllerCompletedHandler>(
                        [hwnd, initialUrl](HRESULT controllerResult, ICoreWebView2Controller* controller) -> HRESULT {
                            if (FAILED(controllerResult) || controller == nullptr) {
                                MessageBoxW(hwnd, L"WebView2 控件创建失败。", kWindowTitle, MB_ICONERROR | MB_OK);
                                return controllerResult;
                            }

                            g_webviewController = controller;
                            g_webviewController->get_CoreWebView2(&g_webview);
                            ResizeWebView(hwnd);

                            if (g_webview) {
                                ComPtr<ICoreWebView2Settings> settings;
                                if (SUCCEEDED(g_webview->get_Settings(&settings)) && settings) {
                                    settings->put_AreDefaultContextMenusEnabled(TRUE);
                                    settings->put_AreDevToolsEnabled(TRUE);
                                    settings->put_IsStatusBarEnabled(FALSE);
                                }
                                g_webview->Navigate(initialUrl.c_str());
                            }

                            return S_OK;
                        })
                        .Get());

                return S_OK;
            })
            .Get());
}

LRESULT CALLBACK WindowProc(HWND hwnd, UINT message, WPARAM wparam, LPARAM lparam) {
    switch (message) {
        case WM_CREATE:
            InitializeWebView(hwnd);
            return 0;
        case WM_SIZE:
            ResizeWebView(hwnd);
            return 0;
        case WM_DESTROY:
            g_webview.Reset();
            g_webviewController.Reset();
            PostQuitMessage(0);
            return 0;
        default:
            return DefWindowProcW(hwnd, message, wparam, lparam);
    }
}
}  // namespace

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int showCommand) {
    HRESULT comResult = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    if (FAILED(comResult)) {
        MessageBoxW(nullptr, L"COM 初始化失败。", kWindowTitle, MB_ICONERROR | MB_OK);
        return 1;
    }

    WNDCLASSEXW windowClass{};
    windowClass.cbSize = sizeof(windowClass);
    windowClass.lpfnWndProc = WindowProc;
    windowClass.hInstance = instance;
    windowClass.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    windowClass.hIcon = LoadIconW(nullptr, IDI_APPLICATION);
    windowClass.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_WINDOW + 1);
    windowClass.lpszClassName = kWindowClassName;

    if (RegisterClassExW(&windowClass) == 0) {
        MessageBoxW(nullptr, L"窗口类注册失败。", kWindowTitle, MB_ICONERROR | MB_OK);
        CoUninitialize();
        return 1;
    }

    HWND hwnd = CreateWindowExW(
        0,
        kWindowClassName,
        kWindowTitle,
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        1280,
        800,
        nullptr,
        nullptr,
        instance,
        nullptr);

    if (hwnd == nullptr) {
        MessageBoxW(nullptr, L"主窗口创建失败。", kWindowTitle, MB_ICONERROR | MB_OK);
        CoUninitialize();
        return 1;
    }

    ShowWindow(hwnd, showCommand);
    UpdateWindow(hwnd);

    MSG message{};
    while (GetMessageW(&message, nullptr, 0, 0) > 0) {
        TranslateMessage(&message);
        DispatchMessageW(&message);
    }

    CoUninitialize();
    return static_cast<int>(message.wParam);
}
