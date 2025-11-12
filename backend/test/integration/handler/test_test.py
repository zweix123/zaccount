#!/usr/bin/env python3
"""
集成测试：测试 /test 接口
向本地 8080 端口的 /test 接口发送请求并验证返回值
"""

import sys
import urllib.error
import urllib.request


def test_endpoint(url: str = "http://localhost:8080/test") -> bool:
    """
    向 /test 接口发送 GET 请求并处理返回值

    Args:
        url: 测试接口的完整 URL

    Returns:
        bool: 测试是否通过
    """
    try:
        # 创建请求对象，设置超时
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Python Integration Test")

        # 发送 GET 请求
        with urllib.request.urlopen(req, timeout=5) as response:
            # 获取 HTTP 状态码
            status_code = response.getcode()

            # 检查 HTTP 状态码
            if status_code != 200:
                response_text = response.read().decode("utf-8")
                print(f"❌ 请求失败: HTTP {status_code}")
                print(f"响应内容: {response_text}")
                return False

            # 获取响应内容
            response_text = response.read().decode("utf-8")
            print(f"✅ 请求成功: HTTP {status_code}")
            print(f"响应内容: {response_text}")

            # 验证响应内容（根据 handler.go，应该返回 "test success"）
            expected_response = "test success"
            if response_text == expected_response:
                print(
                    f"✅ 响应内容验证通过: '{response_text}' == '{expected_response}'"
                )
                return True
            else:
                print(f"⚠️  响应内容不匹配:")
                print(f"   期望: '{expected_response}'")
                print(f"   实际: '{response_text}'")
                return False

    except urllib.error.URLError as e:
        if isinstance(e.reason, ConnectionRefusedError) or "Connection refused" in str(
            e
        ):
            print(f"❌ 连接失败: 无法连接到 {url}")
            print("   请确保服务器正在运行在 8080 端口")
        else:
            print(f"❌ URL 错误: {e}")
        return False
    except TimeoutError:
        print(f"❌ 请求超时: {url}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {type(e).__name__}: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("开始测试 /test 接口")
    print("=" * 50)

    success = test_endpoint()

    print("=" * 50)
    if success:
        print("✅ 测试通过")
        sys.exit(0)
    else:
        print("❌ 测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
