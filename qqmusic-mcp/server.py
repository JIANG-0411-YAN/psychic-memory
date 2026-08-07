"""
QQ音乐 MCP Server
提供搜索歌曲、获取歌词功能
"""

import asyncio
import json
import base64
import urllib.request
import urllib.parse
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("qqmusic-mcp")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
REFERER = "https://y.qq.com"


def _fetch(url: str) -> dict:
    """发送HTTP GET请求，返回JSON"""
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Referer": REFERER,
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_song",
            description="搜索QQ音乐歌曲，返回匹配的歌曲列表（歌名、歌手、专辑、songmid）",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词，如歌名、歌手名",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量，默认10，最大30",
                        "default": 10,
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="get_lyric",
            description="根据songmid获取歌曲歌词",
            inputSchema={
                "type": "object",
                "properties": {
                    "songmid": {
                        "type": "string",
                        "description": "歌曲的songmid，从search_song结果中获取",
                    },
                },
                "required": ["songmid"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "search_song":
        keyword = arguments.get("keyword", "")
        limit = min(int(arguments.get("limit", 10)), 30)

        params = urllib.parse.urlencode({
            "format": "json",
            "w": keyword,
            "n": limit,
            "p": 1,
        })
        url = f"https://c.y.qq.com/soso/fcgi-bin/client_search_cp?{params}"
        data = _fetch(url)

        songs = data.get("data", {}).get("song", {}).get("list", [])
        if not songs:
            return [TextContent(type="text", text=f"未找到与「{keyword}」相关的歌曲")]

        lines = [f"🔍 「{keyword}」搜索结果：\n"]
        for i, s in enumerate(songs, 1):
            songname = s.get("songname", "未知")
            singer = s.get("singer", [{}])[0].get("name", "未知")
            album = s.get("albumname", "未知")
            songmid = s.get("songmid", "")
            interval = int(s.get("interval", 0))
            mins, secs = divmod(interval, 60)
            lines.append(
                f"{i}. {songname} - {singer} | 专辑：{album} | {mins}:{secs:02d}\n"
                f"   songmid: `{songmid}`"
            )

        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "get_lyric":
        songmid = arguments.get("songmid", "")
        if not songmid:
            return [TextContent(type="text", text="请提供 songmid 参数")]

        params = urllib.parse.urlencode({
            "songmid": songmid,
            "format": "json",
        })
        url = f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?{params}"
        data = _fetch(url)

        lyric_b64 = data.get("lyric", "") if isinstance(data, dict) else ""
        if not lyric_b64:
            return [TextContent(type="text", text="未找到歌词")]

        lyric_text = base64.b64decode(lyric_b64).decode("utf-8")
        return [TextContent(type="text", text=lyric_text)]

    else:
        return [TextContent(type="text", text=f"未知工具: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
