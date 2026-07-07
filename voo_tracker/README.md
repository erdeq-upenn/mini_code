# VOO 每日开盘异动监控

用「今日开盘价 vs 昨日收盘价」的涨跌幅，与过去 N 日波动率（标准差）比较，
超过设定倍数（默认 2σ）就通过 Telegram 推送提醒。全程免费，用 GitHub Actions 定时跑。

## 一、本地测试

```bash
pip install -r requirements.txt
python voo_monitor.py
```

不配置 Telegram 环境变量时，脚本会把要发送的消息直接打印在终端，方便你先验证逻辑对不对。

可调参数（通过环境变量传入，不传则用默认值）：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TICKER` | VOO | 监控的股票代码 |
| `WINDOW` | 20 | 计算波动率基准用的历史天数 |
| `K_MULTIPLIER` | 2.0 | 触发阈值＝K × 历史标准差 |

例如把阈值改严格一点、只看最近10天波动率：

```bash
WINDOW=10 K_MULTIPLIER=1.5 python voo_monitor.py
```

## 二、申请 Telegram Bot（几分钟搞定）

1. 在 Telegram 里搜索 `@BotFather`，发送 `/newbot`，按提示起名字，拿到一个 `TELEGRAM_BOT_TOKEN`（形如 `123456:ABC-xxxx`）。
2. 搜索 `@userinfobot`，发送任意消息，它会回复你的 `chat_id`（一串数字），这就是 `TELEGRAM_CHAT_ID`。
3. 一定要先给你自己的 Bot 发一条消息（比如 `/start`），否则 Bot 无法主动给你推送。

## 三、部署到 GitHub Actions（推荐，全免费、不用自己开电脑）

1. 新建一个 **私有** GitHub 仓库（建议私有，避免持仓/策略信息暴露），把这个文件夹的内容（含 `.github/workflows/voo_monitor.yml`）推送上去。
2. 进入仓库 `Settings → Secrets and variables → Actions → New repository secret`，添加两个 secret：
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. 进入 `Actions` 标签页，找到 `VOO Daily Monitor`，点击 `Run workflow` 手动触发一次，检查日志是否正常、Telegram 是否收到消息（如果当天波动没超阈值，只会在日志里看到"波动在正常范围内"，这是正常的）。
4. 之后它会按 `cron` 设置的时间自动运行，无需你再操作。

### 关于运行时间的说明

美股开盘是纽约时间 9:30，为了兼容夏令时/冬令时切换，工作流设置了两个 cron（13:35 UTC 和 14:35 UTC），
每天都会各跑一次，其中一次会命中"刚开盘"的时间点，另一次因为 Yahoo Finance 还没更新数据（或者 `state.json`
已经记录当天检查过）会自动跳过，不会重复发送。这是脚本里 `state.json` 去重逻辑的作用，你不需要手动处理。

节假日/周末美股不开盘，Yahoo Finance 不会生成当天的行情行，脚本会自动识别并跳过，不会误报。

## 四、想要更实时（不用等开盘价，而是盘中监控）怎么办？

当前设计是"开盘价 vs 昨收"的日级别信号，足够覆盖"隔夜跳空"这类大幅波动。
如果之后想做盘中实时监控（比如每5分钟检查一次当前价格 vs 昨收），思路是一样的，
只需把 `yf.download` 换成取当前最新价（`interval="1m"` 或 `.info["regularMarketPrice"]`），
再配合更频繁的 cron（GitHub Actions 免费额度下最短建议 5-15 分钟一次，避免超额）。
需要的话可以再告诉我，我帮你改造成盘中版本。

## 五、其他备选部署方式

- **本地长期挂机**：用系统自带的 `cron`（Mac/Linux）或"任务计划程序"（Windows）替代 GitHub Actions，逻辑完全一样，缺点是电脑得一直开着。
- **云函数**：AWS Lambda + EventBridge、或 Google Cloud Functions + Cloud Scheduler，适合已经比较熟悉云服务的人，好处是可以顺便扩展更多监控逻辑（比如接交易API自动下单）。
