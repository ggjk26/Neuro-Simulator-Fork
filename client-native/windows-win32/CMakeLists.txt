cmake_minimum_required(VERSION 3.21)

project(NeuroSimulatorWin32Client LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT WIN32)
  message(FATAL_ERROR "The native Win32 client can only be built on Windows.")
endif()

set(WEBVIEW2_VERSION "1.0.3537.50" CACHE STRING "Microsoft.Web.WebView2 NuGet package version")
set(WEBVIEW2_NUGET_URL "https://www.nuget.org/api/v2/package/Microsoft.Web.WebView2/${WEBVIEW2_VERSION}")
set(WEBVIEW2_PACKAGE "${CMAKE_BINARY_DIR}/Microsoft.Web.WebView2.${WEBVIEW2_VERSION}.nupkg")
set(WEBVIEW2_DIR "${CMAKE_BINARY_DIR}/webview2")

if(NOT EXISTS "${WEBVIEW2_DIR}/build/native/include/WebView2.h")
  file(DOWNLOAD "${WEBVIEW2_NUGET_URL}" "${WEBVIEW2_PACKAGE}" SHOW_PROGRESS STATUS WEBVIEW2_DOWNLOAD_STATUS)
  list(GET WEBVIEW2_DOWNLOAD_STATUS 0 WEBVIEW2_DOWNLOAD_CODE)
  if(NOT WEBVIEW2_DOWNLOAD_CODE EQUAL 0)
    message(FATAL_ERROR "Failed to download Microsoft.Web.WebView2 NuGet package: ${WEBVIEW2_DOWNLOAD_STATUS}")
  endif()
  file(ARCHIVE_EXTRACT INPUT "${WEBVIEW2_PACKAGE}" DESTINATION "${WEBVIEW2_DIR}")
endif()

add_executable(neuro-win32 WIN32
  src/main.cpp
)

target_compile_definitions(neuro-win32 PRIVATE
  UNICODE
  _UNICODE
  NOMINMAX
)

target_include_directories(neuro-win32 PRIVATE
  "${WEBVIEW2_DIR}/build/native/include"
)

target_link_libraries(neuro-win32 PRIVATE
  user32
  shell32
  ole32
  shlwapi
  version
)

if(CMAKE_SIZEOF_VOID_P EQUAL 8)
  set(WEBVIEW2_ARCH "x64")
else()
  set(WEBVIEW2_ARCH "x86")
endif()

set(WEBVIEW2_LOADER_LIB "${WEBVIEW2_DIR}/build/native/${WEBVIEW2_ARCH}/WebView2LoaderStatic.lib")
if(EXISTS "${WEBVIEW2_LOADER_LIB}")
  target_link_libraries(neuro-win32 PRIVATE "${WEBVIEW2_LOADER_LIB}")
else()
  message(FATAL_ERROR "WebView2 loader library not found: ${WEBVIEW2_LOADER_LIB}")
endif()
