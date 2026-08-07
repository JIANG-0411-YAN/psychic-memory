# QQ音乐 MCP Server

MCP服务，提供QQ音乐搜索歌曲和获取歌词功能。

## 安装

```bash
pip install -r requirements.txt
```

## MCP 客户端配置

在你的MCP客户端配置文件中添加：

```json
{
  "mcpServers": {
    "qqmusic": {
      "command": "python",
      "args": ["/你的路径/qqmusic-mcp/server.py"]
    }
  }
}
```

## 工具列表

| 工具 | 功能 |
|------|------|
| `search_song` | 搜索歌曲，返回歌名、歌手、专辑、songmid |
| `get_lyric` | 根据 songmid 获取完整歌词 |

## 使用示例

在支持MCP的客户端中：

- "帮我搜周杰伦的晴天"
- "获取这首歌的歌词"
