import base64
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from pipeline.core.node import Node
from openai import OpenAI

from pipeline.core.rate_limiter import RateLimiter
from pipeline.core.retry import retry

client = OpenAI(
    base_url='https://aihubmix.com/v1',
    api_key='sk-u6nqaTA9V41gl5ah0845FcF690F4442eBa969cF2Bd6d9f90',  # Token
)


def encode_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def get_project_root():
    """
    通过文件系统结构获取项目根目录
    :return: 项目根目录路径
    """
    # 获取当前文件的路径
    current_file = Path(__file__).resolve()

    # 向上遍历目录树，查找常见的项目根标识
    for parent in current_file.parents:
        # 检查是否存在常见的项目根目录标识
        if any([
            (parent / "requirements.txt").exists()
        ]):
            return parent

    # 如果没有找到标识，返回当前文件所在目录的父目录
    return current_file.parent


with open(f"{get_project_root()}\\agent\\vcg-system-prompt.txt", 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()


def build_request(batch):
    content = [{
        "type": "text",
        "text": "Score each image for stock photo commercial value. Return JSON."
    }]

    for path in batch:
        img_base64 = encode_image_to_base64(path)

        content.append({
            "type": "text",
            "text": f"Image: {path}"
        })

        content.append({
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{img_base64}"
        })

    return content


class GPTScoringNode(Node):
    name = "gpt_score"

    def __init__(self, batch_size=5, max_workers=3, rate_limit=3):
        self.batch_size = batch_size
        self.max_workers = max_workers
        # 每秒最多3次请求
        self.limiter = RateLimiter(rate_limit)

    def batch_images(self, images):

        for i in range(0, len(images), self.batch_size):
            yield images[i:i + self.batch_size]

    def score_image_batch(self, batch):
        print("Scoring batch:", len(batch))

        def request():
            chunks = []
            self.limiter.acquire()
            response = client.chat.completions.create(
                model='gpt-4o-free',  #  Model-Id
                messages=[
                    {
                        'role': 'system',
                        'content': SYSTEM_PROMPT
                    },
                    {
                        'role': 'user',
                        'content': build_request(batch)
                    }
                ],
                temperature=0.7,
                max_tokens=8192,
                stream=True
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    # print(chunk.choices[0].delta.content, end='', flush=True)
                    chunks.append(chunk.choices[0].delta.content)
            output_text = "".join(chunks)
            return output_text

        result = retry(request)
        return _parse_response(response_text=result)

    def run(self, ctx):

        scores = {}
        images = ctx.get("images")
        aesthetic_scores = ctx.get("aesthetic_scores")
        batches = list(self.batch_images(images))
        with (ThreadPoolExecutor(max_workers=self.max_workers) as executor):
            futures = {
                executor.submit(self.score_image_batch, batch): batch
                for batch in batches
            }
            for future in as_completed(futures):
                # batch = futures[future]
                result = future.result()
                image_scores = result.get("images")
                for score_json in image_scores:
                    gpt_scores = score_json.get('scores')
                    file_name = score_json.get('file')

                    scores[file_name] = {
                        **gpt_scores,
                        'aesthetic_score': aesthetic_scores.get(file_name)
                    }

        ctx.set("scores", scores)


def _fix_json_string(json_str: str) -> str:
    """修复常见的 JSON 格式问题"""
    import re

    # 移除注释
    json_str = re.sub(r'//.*?\n', '\n', json_str)
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)

    # 修复尾随逗号
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)

    # 确保布尔值是小写
    json_str = json_str.replace('True', 'true').replace('False', 'false')

    return json_str


def _parse_response(response_text: str):
    """
    尝试从响应中提取 JSON 格式的分析结果
    如果解析失败，尝试智能提取或返回默认结果
    """
    try:
        # 清理响应文本：移除 markdown 代码块标记
        cleaned_text = response_text
        if '```json' in cleaned_text:
            cleaned_text = cleaned_text.replace('```json', '').replace('```', '')
        elif '```' in cleaned_text:
            cleaned_text = cleaned_text.replace('```', '')

        # 尝试找到 JSON 内容
        json_start = cleaned_text.find('{')
        json_end = cleaned_text.rfind('}') + 1

        if 0 <= json_start < json_end:
            json_str = cleaned_text[json_start:json_end]

            # 尝试修复常见的 JSON 问题
            json_str = _fix_json_string(json_str)

            data = json.loads(json_str)

            # 解析所有字段，使用默认值防止缺失
            return data
        else:
            # 没有找到 JSON，尝试从纯文本中提取信息
            print(f"无法从响应中提取 JSON，使用原始文本分析")

    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}，尝试从文本提取")
