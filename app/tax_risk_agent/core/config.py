"""应用配置模块

本模块集中定义税务风险诊断系统的运行配置，支持从默认值和 `.env` 文件读取。
API 入口通过 `get_settings()` 获取配置后，用于初始化数据库、报告目录、LLM
客户端、规则向量库等基础依赖。
"""

from functools import lru_cache  # 导入缓存装饰器，避免重复构造配置对象。
from pathlib import Path  # 导入路径类型，用于数据库和报告目录配置。

from pydantic import Field  # 导入字段配置工具，用于隐藏敏感字段展示。
from pydantic_settings import BaseSettings, SettingsConfigDict  

# 定义应用运行配置模型，字段可被环境变量或 .env 覆盖
class Settings(BaseSettings):  
    # 配置读取规则：从项目根目录的 .env 文件读取 UTF-8 配置，忽略未声明的额外字段
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"  # 应用运行环境标识，默认本地环境。
    database_url: Path = Path("data/tax_risk_demo.sqlite")  # SQLite 数据库文件路径
    report_dir: Path = Path("reports_output")  # 诊断报告和图表的输出目录
    llm_provider: str = "offline"  # LLM 提供方，默认使用离线兜底摘要
    llm_base_url: str = "http://127.0.0.1:8001/v1"  # OpenAI-compatible 模型服务地址
    llm_model: str = "Qwen2.5-14B-Instruct"  # 在线摘要使用的模型名称
    llm_api_key: str = Field(default="local-key", repr=False)  # 模型服务 API Key，repr=False 避免日志或调试输出泄露
    milvus_uri: str = "http://127.0.0.1:19530"  # Milvus 或兼容向量库服务地址
    milvus_collection: str = "tax_rules"  # 存放税务规则向量的集合名称
    max_tool_rounds: int = 8  # Agent 工具调用轮数上限，用于限制诊断流程复杂度


@lru_cache  # 缓存配置对象，确保一次进程内多次调用复用同一份设置。
def get_settings() -> Settings:  # 对外提供统一配置读取入口
    return Settings()  # 构造并返回 Settings，首次调用时读取默认值、环境变量和 .env
