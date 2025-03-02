import re
from typing import Any, List, Optional, Dict, Union
from pydantic import Field, model_validator
from langchain_core.language_models import BaseLLM
from langchain_core.outputs import LLMResult

class LLMAgent(BaseLLM):
    agent: Any = Field(description="LLM client instance")  # 使用Any类型避免类型校验冲突
    model_name: str = Field(alias="model", description="Model identifier")
    temperature: float = Field(default=0.5, ge=0, le=1, description="Sampling temperature")
    local: bool = Field(default=True, description="Local mode flag")


    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Dict:
        """根据模式初始化客户端"""
        local = values.get("local", True)
        temperature = values.get("temperature", 0.5)

        if local:
            from ollama import Client  # 替换为实际本地客户端导入
            values["agent"] = Client()
            values["model"] = "deepseek-r1"
        else:
            from openai import OpenAI  # 建议使用官方openai库
            values["agent"] = OpenAI(
                api_key=values.get("api_key", "<DeepSeek API Key>"),
                base_url="https://api.deepseek.com"
            )
            values["model"] = "deepseek-reasoner"

        return values

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> str:
        """核心调用逻辑"""
        messages = [{"role": "user", "content": prompt}]
        
        if self.local:
            response = self.agent.chat(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            # 使用更健壮的响应处理
            content = response.get("message", {}).get("content", "")
            return self._clean_content(content)
        else:
            response = self.agent.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=False,
                **kwargs
            )
            return response.choices[0].message.content
    def complete(self, prompt: str, **kwargs) -> str:
        return self._call(prompt, **kwargs)

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """批量生成实现"""
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
            generations.append([{"text": text}])
        
        return LLMResult(generations=generations)

    def _clean_content(self, text: str) -> str:
        """响应内容清洗"""
        return re.sub(r'<think>.*?', '', text, flags=re.DOTALL).strip()

    @property
    def _llm_type(self) -> str:
        return "ollama-deepseek-r1"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """返回标识参数"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "local_mode": self.local
        }