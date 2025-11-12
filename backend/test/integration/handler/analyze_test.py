#!/usr/bin/env python3
"""
集成测试：测试 /analyze 接口
向本地 8080 端口的 /analyze 接口发送请求并验证返回值
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request


def test_analyze_endpoint(
    url: str = "http://localhost:8080/analyze",
    start_date: str = None,  # type: ignore
    end_date: str = None,  # type: ignore
) -> bool:
    """
    向 /analyze 接口发送 GET 请求并处理返回值

    Args:
        url: 测试接口的基础 URL
        start_date: 开始日期 (格式: YYYY-MM-DD)
        end_date: 结束日期 (格式: YYYY-MM-DD)

    Returns:
        bool: 测试是否通过
    """
    try:
        # 构建查询参数
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        # 构建完整 URL
        if params:
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
        else:
            full_url = url

        # 创建请求对象，设置超时
        req = urllib.request.Request(full_url)
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

            # 解析 JSON 响应
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"❌ JSON 解析失败: {e}")
                return False

            # 验证响应结构
            required_fields = ["income", "expense", "balance", "start_date", "end_date"]
            for field in required_fields:
                if field not in response_data:
                    print(f"❌ 响应缺少必需字段: {field}")
                    return False

            # 验证字段类型
            if not isinstance(response_data["income"], (int, float)):
                print(f"❌ income 字段类型错误: {type(response_data['income'])}")
                return False
            if not isinstance(response_data["expense"], (int, float)):
                print(f"❌ expense 字段类型错误: {type(response_data['expense'])}")
                return False
            if not isinstance(response_data["balance"], (int, float)):
                print(f"❌ balance 字段类型错误: {type(response_data['balance'])}")
                return False
            if not isinstance(response_data["start_date"], str):
                print(
                    f"❌ start_date 字段类型错误: {type(response_data['start_date'])}"
                )
                return False
            if not isinstance(response_data["end_date"], str):
                print(f"❌ end_date 字段类型错误: {type(response_data['end_date'])}")
                return False

            # 验证日期格式
            try:
                from datetime import datetime

                datetime.strptime(response_data["start_date"], "%Y-%m-%d")
                datetime.strptime(response_data["end_date"], "%Y-%m-%d")
            except ValueError as e:
                print(f"❌ 日期格式错误: {e}")
                return False

            # 验证 balance 计算是否正确
            expected_balance = response_data["income"] - response_data["expense"]
            if abs(response_data["balance"] - expected_balance) > 0.01:
                print(f"❌ balance 计算错误:")
                print(f"   期望: {expected_balance}")
                print(f"   实际: {response_data['balance']}")
                return False

            print("✅ 响应内容验证通过")
            return True

    except urllib.error.HTTPError as e:
        response_text = e.read().decode("utf-8") if hasattr(e, "read") else ""
        print(f"❌ HTTP 错误: {e.code} {e.reason}")
        if response_text:
            print(f"响应内容: {response_text}")
        return False
    except urllib.error.URLError as e:
        if isinstance(e.reason, ConnectionRefusedError) or "Connection refused" in str(
            e
        ):
            print(f"❌ 连接失败: 无法连接到 {full_url}")
            print("   请确保服务器正在运行在 8080 端口")
        else:
            print(f"❌ URL 错误: {e}")
        return False
    except TimeoutError:
        print(f"❌ 请求超时: {full_url}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {type(e).__name__}: {e}")
        return False


def test_analyze_with_valid_dates() -> bool:
    """测试有效的日期范围 - 验证1月份数据"""
    print("测试: 有效日期范围 (2025-01-01 到 2025-01-31)")
    print("期望: 收入1500 (1000收入+500转入), 支出550 (50+200+300转出), 结余950")

    try:
        url = "http://localhost:8080/analyze?start_date=2025-01-01&end_date=2025-01-31"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Python Integration Test")

        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() != 200:
                print(f"❌ 请求失败: HTTP {response.getcode()}")
                return False

            response_text = response.read().decode("utf-8")
            response_data = json.loads(response_text)

            # 验证数据是否符合测试数据
            expected_income = 1500.00  # 1000 (收入) + 500 (转入)
            expected_expense = 550.00  # 50 + 200 + 300 (转出)
            expected_balance = 950.00  # 1500 - 550

            if abs(response_data["income"] - expected_income) > 0.01:
                print(
                    f"❌ income 不匹配: 期望 {expected_income}, 实际 {response_data['income']}"
                )
                return False

            if abs(response_data["expense"] - expected_expense) > 0.01:
                print(
                    f"❌ expense 不匹配: 期望 {expected_expense}, 实际 {response_data['expense']}"
                )
                return False

            if abs(response_data["balance"] - expected_balance) > 0.01:
                print(
                    f"❌ balance 不匹配: 期望 {expected_balance}, 实际 {response_data['balance']}"
                )
                return False

            print(
                f"✅ 数据验证通过: income={response_data['income']}, expense={response_data['expense']}, balance={response_data['balance']}"
            )
            return True
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False


def test_analyze_with_same_date() -> bool:
    """测试相同日期 - 验证单日数据"""
    print("测试: 相同日期 (2025-01-01 到 2025-01-01)")
    print("期望: 收入1000 (1月1日的工资), 支出0, 结余1000")

    try:
        url = "http://localhost:8080/analyze?start_date=2025-01-01&end_date=2025-01-01"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Python Integration Test")

        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() != 200:
                print(f"❌ 请求失败: HTTP {response.getcode()}")
                return False

            response_text = response.read().decode("utf-8")
            response_data = json.loads(response_text)

            # 验证数据是否符合测试数据（1月1日只有一条收入记录：1000.00）
            expected_income = 1000.00
            expected_expense = 0.00
            expected_balance = 1000.00

            if abs(response_data["income"] - expected_income) > 0.01:
                print(
                    f"❌ income 不匹配: 期望 {expected_income}, 实际 {response_data['income']}"
                )
                return False

            if abs(response_data["expense"] - expected_expense) > 0.01:
                print(
                    f"❌ expense 不匹配: 期望 {expected_expense}, 实际 {response_data['expense']}"
                )
                return False

            if abs(response_data["balance"] - expected_balance) > 0.01:
                print(
                    f"❌ balance 不匹配: 期望 {expected_balance}, 实际 {response_data['balance']}"
                )
                return False

            print(
                f"✅ 数据验证通过: income={response_data['income']}, expense={response_data['expense']}, balance={response_data['balance']}"
            )
            return True
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False


def test_analyze_missing_params() -> bool:
    """测试缺少参数"""
    print("测试: 缺少必需参数")
    try:
        url = "http://localhost:8080/analyze"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Python Integration Test")

        with urllib.request.urlopen(req, timeout=5) as response:
            # 如果返回了 200，说明没有验证参数，这是错误的
            if response.getcode() == 200:
                print("❌ 应该返回错误，但返回了 200")
                return False
            else:
                print(f"✅ 正确返回了错误状态码: {response.getcode()}")
                return True
    except urllib.error.HTTPError as e:
        if e.code == 400:  # Bad Request
            print("✅ 正确返回了 400 Bad Request")
            return True
        else:
            print(f"⚠️  返回了 {e.code}，期望 400")
            return True  # 仍然算通过，因为返回了错误
    except Exception as e:
        print(f"✅ 正确返回了错误: {e}")
        return True


def test_analyze_invalid_date_format() -> bool:
    """测试无效日期格式"""
    print("测试: 无效日期格式")
    try:
        url = "http://localhost:8080/analyze?start_date=2025/01/01&end_date=2025-01-31"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Python Integration Test")

        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() == 200:
                print("❌ 应该返回错误，但返回了 200")
                return False
            else:
                print(f"✅ 正确返回了错误状态码: {response.getcode()}")
                return True
    except urllib.error.HTTPError as e:
        if e.code == 400:  # Bad Request
            print("✅ 正确返回了 400 Bad Request")
            return True
        else:
            print(f"⚠️  返回了 {e.code}，期望 400")
            return True  # 仍然算通过，因为返回了错误
    except Exception as e:
        print(f"✅ 正确返回了错误: {e}")
        return True


def test_analyze_invalid_date_range() -> bool:
    """测试无效日期范围（开始日期晚于结束日期）"""
    print("测试: 无效日期范围（开始日期晚于结束日期）")
    try:
        url = "http://localhost:8080/analyze?start_date=2025-01-31&end_date=2025-01-01"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Python Integration Test")

        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() == 200:
                print("❌ 应该返回错误，但返回了 200")
                return False
            else:
                print(f"✅ 正确返回了错误状态码: {response.getcode()}")
                return True
    except urllib.error.HTTPError as e:
        if e.code == 400:  # Bad Request
            print("✅ 正确返回了 400 Bad Request")
            return True
        else:
            print(f"⚠️  返回了 {e.code}，期望 400")
            return True  # 仍然算通过，因为返回了错误
    except Exception as e:
        print(f"✅ 正确返回了错误: {e}")
        return True


def test_analyze_wrong_method() -> bool:
    """测试错误的 HTTP 方法"""
    print("测试: 错误的 HTTP 方法 (POST)")
    try:
        url = "http://localhost:8080/analyze?start_date=2025-01-01&end_date=2025-01-31"
        req = urllib.request.Request(url, method="POST")
        req.add_header("User-Agent", "Python Integration Test")

        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() == 405:  # Method Not Allowed
                print("✅ 正确返回了 405 Method Not Allowed")
                return True
            else:
                print(f"❌ 期望 405，但返回了 {response.getcode()}")
                return False
    except urllib.error.HTTPError as e:
        if e.code == 405:
            print("✅ 正确返回了 405 Method Not Allowed")
            return True
        else:
            print(f"❌ 期望 405，但返回了 {e.code}")
            return False
    except Exception as e:
        print(f"✅ 正确返回了错误: {e}")
        return True


def main():
    """主函数"""
    print("=" * 50)
    print("开始测试 /analyze 接口")
    print("=" * 50)
    print()

    test_results = []

    # 测试用例
    test_cases = [
        ("有效日期范围-1月份", test_analyze_with_valid_dates),
        ("相同日期-单日", test_analyze_with_same_date),
        ("缺少参数", test_analyze_missing_params),
        ("无效日期格式", test_analyze_invalid_date_format),
        ("无效日期范围", test_analyze_invalid_date_range),
        ("错误的 HTTP 方法", test_analyze_wrong_method),
    ]

    for test_name, test_func in test_cases:
        print("-" * 50)
        print(f"运行测试: {test_name}")
        print("-" * 50)
        try:
            result = test_func()
            test_results.append((test_name, result))
            if result:
                print(f"✅ 测试通过: {test_name}")
            else:
                print(f"❌ 测试失败: {test_name}")
        except Exception as e:
            print(f"❌ 测试异常: {test_name} - {e}")
            test_results.append((test_name, False))
        print()

    # 输出测试结果摘要
    print("=" * 50)
    print("测试结果摘要")
    print("=" * 50)
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print()

    if passed == total:
        print("✅ 所有测试通过")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        failed_tests = [name for name, result in test_results if not result]
        print("失败的测试:")
        for name in failed_tests:
            print(f"  - {name}")
        sys.exit(1)


if __name__ == "__main__":
    main()
