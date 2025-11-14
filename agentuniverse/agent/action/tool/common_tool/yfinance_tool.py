
from typing import Optional, Any, List
from dataclasses import dataclass
from enum import Enum
from pydantic import Field
from agentuniverse.base.annotation.retry import retry
from agentuniverse.agent.action.tool.tool import Tool, ToolInput

class SearchMode(Enum):
    """搜索模式枚举类"""
    SEARCH = "search"   
    DETAIL = "detail"  

class YahooFinanceTool(Tool):
    """Yahoo Finance工具类，支持股票信息搜索和详情查询"""
    
    MAX_QUERY_LENGTH: int = Field(default=300, description="查询字符串最大长度")
    
    def execute(self, tool_input: ToolInput):
        """执行工具逻辑"""
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError("yfinance is required. Install with: pip install yfinance")

        mode = tool_input.get_data('mode')
        if mode not in [m.value for m in SearchMode]:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {[m.value for m in SearchMode]}")

        query = tool_input.get_data("input")
        processed_query = self._process_query(query)

        return (self.get_stock_history(processed_query) if mode == SearchMode.SEARCH.value
                else self.get_stock_details(processed_query))

    def _process_query(self, query: str) -> str:
        """处理查询字符串，限制最大长度"""
        if len(query) <= self.MAX_QUERY_LENGTH:
            return query

        words = query.split()
        processed_words = []
        current_length = 0
        for word in words:
            word_length = len(word) + 1 
            if current_length + word_length <= self.MAX_QUERY_LENGTH:
                processed_words.append(word)
                current_length += word_length
            else:
                break
        return ' '.join(processed_words)

    @retry(3, 1.0)
    def get_stock_history(self, symbol: str) -> str:
        """获取股票历史价格数据"""
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError("yfinance is required.")
            
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")  # 获取最近5个交易日的数据
        
        if hist.empty:
            return f"No historical data found for {symbol}."
            
        # 格式化输出最近收盘价
        result = f"Recent closing prices for {symbol}:\n"
        for date, row in hist[-5:].iterrows():
            result += f"{date.strftime('%Y-%m-%d')}: ${row['Close']:.2f} (Volume: {row['Volume']})\n"
        return result

    @retry(3, 1.0)
    def get_stock_details(self, symbol: str) -> str:
        """获取股票详细信息"""
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError("yfinance is required.")
            
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info:
            return f"No details found for {symbol}."
            
        # 提取关键财务指标
        details = (
            f"Company Name: {info.get('shortName', 'N/A')}\n"
            f"Current Price: ${info.get('currentPrice', 'N/A')} USD\n"
            f"Previous Close: ${info.get('previousClose', 'N/A')}\n"
            f"Day Range: ${info.get('dayLow', 'N/A')} - ${info.get('dayHigh', 'N/A')}\n"
            f"52 Week Range: ${info.get('fiftyTwoWeekLow', 'N/A')} - ${info.get('fiftyTwoWeekHigh', 'N/A')}\n"
            f"Market Cap: {info.get('marketCap', 'N/A')}\n"
            f"P/E Ratio: {info.get('forwardPE', 'N/A')}\n"
            f"EPS (Forward): {info.get('forwardEps', 'N/A')}\n"
            f"Dividend Yield: {info.get('dividendYield', 'N/A')}\n"
            f"Volume: {info.get('volume', 'N/A')}\n"
            f"Average Volume: {info.get('averageVolume', 'N/A')}\n"
            f"Sector: {info.get('sector', 'N/A')}\n"
            f"Industry: {info.get('industry', 'N/A')}\n"
            f"Website: {info.get('website', 'N/A')}\n"
        )
        return details
