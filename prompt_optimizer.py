# -*- coding: utf-8 -*-
"""
提示词优化模块
基于Google Gemini API实现提示词优化功能
"""

import os
from typing import Optional
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class PromptOptimizer:
    """提示词优化器类"""
    
    def __init__(self):
        """初始化优化器"""
        # 加载环境变量
        load_dotenv()
        
        # 获取配置
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.2'))
        self.top_p = float(os.getenv('GEMINI_TOP_P', '0.8'))
        self.max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '1000'))
        self.thinking_budget = int(os.getenv('GEMINI_THINKING_BUDGET', '512'))
        self.include_thoughts = os.getenv('GEMINI_INCLUDE_THOUGHTS', 'false').lower() == 'true'
        self.system_instruction = os.getenv('GEMINI_SYSTEM_INSTRUCTION', 
            '你是提示词优化专家。将用户的简单提示词优化为更清晰、具体、有效的提示词。'
            '优化原则：1. 保持原始意图不变 2. 增加必要的细节和描述 3. 使语言更准确和逻辑性强 '
            '4. 输出简洁明了 5. 适用于各种领域和场景。直接输出优化后的提示词，不要添加额外说明。')
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> bool:
        """初始化Gemini客户端"""
        if not GENAI_AVAILABLE:
            return False

        if not self.api_key or self.api_key == 'your_api_key_here':
            return False

        try:
            self.client = genai.Client(api_key=self.api_key)
            return True
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """检查优化器是否可用"""
        return GENAI_AVAILABLE and self.client is not None
    
    def get_status_message(self) -> str:
        """获取状态消息"""
        if not GENAI_AVAILABLE:
            return "❌ 需要安装google-genai库"
        elif not self.api_key or self.api_key == 'your_api_key_here':
            return "❌ 请在.env文件中配置GEMINI_API_KEY"
        elif self.client is None:
            return "❌ API客户端初始化失败"
        else:
            return "✅ 提示词优化功能已就绪"
    
    def optimize_prompt(self, original_prompt: str) -> str:
        """
        优化提示词
        
        Args:
            original_prompt: 原始提示词
            
        Returns:
            优化后的提示词
            
        Raises:
            Exception: 优化过程中的错误
        """
        if not original_prompt or not original_prompt.strip():
            raise ValueError("输入的提示词不能为空")
        
        if not self.is_available():
            raise RuntimeError(self.get_status_message())
        
        # 创建生成配置
        generation_config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            temperature=self.temperature,
            top_p=self.top_p,
            max_output_tokens=self.max_tokens,
            thinking_config={
                "thinking_budget": self.thinking_budget,
                "include_thoughts": self.include_thoughts
            }
        )

        # 调用API进行优化
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=f"请优化这个提示词：{original_prompt.strip()}",
            config=generation_config
        )

        return response.text.strip() if response and response.text else ""

# 全局优化器实例
_optimizer_instance = None

def get_optimizer() -> PromptOptimizer:
    """获取全局优化器实例"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = PromptOptimizer()
    return _optimizer_instance

def optimize_prompt(text: str) -> str:
    """
    便捷的提示词优化函数
    
    Args:
        text: 要优化的提示词
        
    Returns:
        优化后的提示词
    """
    optimizer = get_optimizer()
    return optimizer.optimize_prompt(text)

def is_optimizer_available() -> bool:
    """检查优化器是否可用"""
    optimizer = get_optimizer()
    return optimizer.is_available()

def get_optimizer_status() -> str:
    """获取优化器状态信息"""
    optimizer = get_optimizer()
    return optimizer.get_status_message()

if __name__ == "__main__":
    # 测试代码
    optimizer = PromptOptimizer()
    print(f"优化器状态: {optimizer.get_status_message()}")
    
    if optimizer.is_available():
        test_prompt = "写一个关于AI的文章"
        try:
            result = optimizer.optimize_prompt(test_prompt)
            print(f"原始提示词: {test_prompt}")
            print(f"优化结果: {result}")
        except Exception as e:
            print(f"测试失败: {e}")
    else:
        print("优化器不可用，请检查配置")
