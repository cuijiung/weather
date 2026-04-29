# 天气查询 MCP 服务器

基于 [wttr.in](https://wttr.in) 免费 API 的天气查询 MCP 服务器，**无需注册，无需 API Key，开箱即用**。

## 功能

| 工具 | 描述 |
|------|------|
| `get_current_weather` | 查询指定城市当前天气 |
| `get_weather_forecast` | 查询指定城市未来 1-3 天天气预报 |
| `get_weather_by_coordinates` | 根据经纬度查询当前天气 |

## 安装

```bash
pip install -r requirements.txt
```

## 配置到 Cursor

将 `mcp.json` 中的内容复制到 Cursor 的 MCP 设置中，或直接在项目根目录使用此 `mcp.json`。

路径参考（按实际安装位置修改）：
- **Cursor 全局配置**：`%APPDATA%\Cursor\User\globalStorage\cursor.mcp\mcp.json`
- **项目级配置**：`.cursor/mcp.json`

## 使用示例

配置完成后，在 Cursor 对话中直接提问：

- "北京今天天气怎么样？"
- "查询上海未来三天的天气预报"
- "帮我看看经纬度 31.2, 121.5 的天气"

## 本地测试

```bash
python weather_server.py
```

## 支持的城市名格式

- 中文：`北京`、`上海`、`广州`
- 英文：`Beijing`、`Shanghai`、`London`
- 拼音：`beijing`、`shanghai`
- 国际城市均支持

## 数据来源

- API：[wttr.in](https://wttr.in) — 开源免费天气服务
- 数据更新频率：约每小时更新一次
