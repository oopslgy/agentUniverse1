import unittest
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.yfinance_tool import YahooFinanceTool, SearchMode  

class YahooFinanceToolTest(unittest.TestCase):
    """
    Yahoo Finance工具单元测试类
    """

    def setUp(self) -> None:
        """初始化测试环境"""
        self.tool = YahooFinanceTool()

    def test_search_papers(self) -> None:
        """测试股票历史数据查询功能"""
        tool_input = ToolInput({
            'input': 'AAPL',  # 使用苹果公司股票代码进行测试
            'mode': SearchMode.SEARCH.value
        })
        result = self.tool.execute(tool_input)
        self.assertTrue("Recent closing prices" in result, "搜索模式返回结果格式异常")
        self.assertTrue("$" in result, "未找到价格数据")
        self.assertTrue("Volume" in result, "未找到成交量数据")

    def test_get_stock_detail(self) -> None:
        """测试股票详细信息查询功能"""
        tool_input = ToolInput({
            'input': 'MSFT',  # 使用微软股票代码进行测试
            'mode': SearchMode.DETAIL.value
        })
        result = self.tool.execute(tool_input)
        self.assertTrue("Company Name" in result, "公司名称字段缺失")
        self.assertTrue("Current Price" in result, "当前价格字段缺失")
        self.assertTrue("Sector" in result, "行业字段缺失")
        self.assertTrue("Market Cap" in result, "市值字段缺失")
        self.assertTrue("P/E Ratio" in result, "市盈率字段缺失")
        self.assertTrue("Website" in result, "官网链接字段缺失")

    def test_invalid_mode(self) -> None:
        """测试无效模式参数的异常处理"""
        tool_input = ToolInput({
            'input': 'test',
            'mode': 'invalid_mode'
        })
        with self.assertRaises(ValueError, msg="未正确抛出无效模式异常"):
            self.tool.execute(tool_input)

    def test_invalid_stock_code(self) -> None:
        """测试无效股票代码的处理"""
        tool_input = ToolInput({
            'input': 'INVALID_CODE',
            'mode': SearchMode.SEARCH.value
        })
        result = self.tool.execute(tool_input)
        self.assertTrue("No historical data found" in result, 
                      "无效股票代码未正确返回错误信息")

    def test_query_length_limit(self) -> None:
        """测试超长查询字符串的截断处理"""
        long_query = 'A' * 400  # 超过默认300字符限制
        tool_input = ToolInput({
            'input': long_query,
            'mode': SearchMode.SEARCH.value
        })
        processed_query = self.tool._process_query(long_query)
        self.assertLessEqual(len(processed_query), 300, 
                           "查询字符串长度限制失效")
        self.assertTrue(processed_query.endswith('A'), 
                      "查询字符串截断处理异常")

if __name__ == '__main__':
    unittest.main()