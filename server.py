# dk call mcp
import os
import sys
import json
import tempfile
import subprocess

from typing import List, Union
import base64

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

# log_level 对于 Cline 的正常工作是必需的：https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("dk call mcp", log_level="ERROR")

def launch_calldk_ui(project_directory: str, summary: str) -> List[Union[str, Image]]:
    # 为call dk结果创建临时文件
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    try:
        # 获取相对于此脚本的 calldk_ui.py 路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        calldk_ui_path = os.path.join(script_dir, "calldk_ui.py")

        # 作为单独进程运行 calldk_ui.py
        # 注意：uv 中似乎存在一个错误，所以我们需要
        # 传递一些特殊标志来使其正常工作
        args = [
            sys.executable,
            "-u",
            calldk_ui_path,
            "--project-directory", project_directory,
            "--prompt", summary,
            "--output-file", output_file
        ]
        result = subprocess.run(
            args,
            check=False,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True
        )
        if result.returncode != 0:
            raise Exception(f"启动call dk界面失败: {result.returncode}")

        # 从临时文件读取结果
        with open(output_file, 'r') as f:
            result = json.load(f)
        os.unlink(output_file)

        # 处理结果以创建内容列表
        content_list = []

        # 如果有文本call dk则添加
        calldk_text = result.get('interactive_calldk', '').strip()
        command_logs = result.get('command_logs', '').strip()

        # 将call dk和日志合并为单个文本响应
        combined_text = ""
        if calldk_text:
            combined_text += f"用户call dk: {calldk_text}\n\n"
        if command_logs:
            combined_text += f"命令日志: {command_logs}"

        if combined_text.strip():
            content_list.append(combined_text.strip())

        # 如果有图片则添加
        images = result.get('images', [])
        for image_data in images:
            try:
                # 将base64数据转换回字节
                image_bytes = base64.b64decode(image_data['data'])
                
                # 从mime_type中提取格式，例如从'image/jpeg'提取'jpeg'，从'image/png'提取'png'
                format_type = image_data['mime_type'].split('/')[-1]

                # 处理特殊格式
                if format_type == 'jpg':
                    format_type = 'jpeg'
                elif format_type not in ('jpeg', 'png', 'gif', 'bmp', 'webp'):
                    format_type = 'png'  # 默认使用png格式

                # 创建 fastmcp Image 对象
                img = Image(data=image_bytes, format=format_type)
                content_list.append(img)
            except Exception as e:
                # 如果图片处理失败，添加错误消息
                content_list.append(f"图片处理错误 ({image_data['filename']}): {str(e)}")

        return content_list

    except Exception as e:
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e

def first_line(text: str) -> str:
    return text.split("\n")[0].strip()

@mcp.tool()
def call_dk() -> List[Union[str, Image]]:
    """呼叫dk"""
    return launch_calldk_ui(".", "call dk")

if __name__ == "__main__":
    mcp.run(transport="stdio")
