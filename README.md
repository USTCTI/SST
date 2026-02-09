# Python 系统压力测试工具

一个用于对本机进行暴力压力测试的单文件工具，覆盖 CPU、内存、网络（UDP）以及公网宽带下载压力测试，并在测试结束后自动输出「分析报告」，便于横向对比不同场景下的系统表现。

文件位置：[`stress_test.py`](stress_test.py)

## 功能特性
- CPU 压测：自动检测核心数，开启同等数量进程进行高强度计算负载
- 内存压测：按指定大小分配内存并持续读写，防止被交换到磁盘
- 网络（UDP）压测：向本地环回地址 127.0.0.1 指定端口持续发送随机数据包
- 公网宽带压测：多线程并发下载大文件以占满下载带宽（默认使用 Hetzner 测速文件）
- 分析报告：测试结束自动输出 CPU/内存占用对比和各项测试的总量与速率

## 环境要求
- Python 3.8+（Windows/Linux/macOS）
- 依赖库：`psutil`（用于采集系统指标）

安装依赖：

```bash
pip install psutil
```

## 快速开始

下载或复制本仓库中的 [`stress_test.py`](stress_test.py)，在终端中执行：

```bash
# 全量压测（CPU + 2GB 内存 + UDP + 宽带，持续 60 秒）
python stress_test.py --cpu --mem 2 --net --bw --duration 60
```

完成后终端会输出一份分析报告，包含测试前后系统负载对比与各项测试的产出统计。

## 命令行参数
- `--cpu`：开启 CPU 压力测试
- `--mem <GB>`：开启内存压力测试，并指定占用大小（单位 GB）
- `--net`：开启网络（UDP）压力测试，目标为本地环回 `127.0.0.1`
- `--bw`：开启公网宽带下载压测（通过并发下载占满带宽）
- `--url <URL>`：宽带测试下载地址，默认 `http://speed.hetzner.de/100MB.bin`
- `--threads <N>`：宽带测试并发线程数，默认 `8`
- `--duration <秒>`：测试持续时间（默认 `60` 秒）
- `--net-port <端口>`：UDP 目标端口（默认 `9999`）

## 使用示例

```bash
# 仅测试 CPU（持续 60 秒）
python stress_test.py --cpu --duration 60

# 仅测试内存（分配 4GB）
python stress_test.py --mem 4 --duration 60

# 仅测试公网宽带（16 线程下载，默认 URL）
python stress_test.py --bw --threads 16 --duration 90

# 指定自定义下载地址与端口
python stress_test.py --bw --url "http://speed.hetzner.de/1GB.bin" --threads 32 --duration 120
python stress_test.py --net --net-port 8888 --duration 30
```

## 分析报告说明
测试结束后会显示：
- 系统负载对比：CPU 占用率、内存占用率、已用内存（GB）
- CPU 运算总量及平均速率（ops/sec）
- 内存分配总量（MB/GB）
- UDP 发送总包数、总数据量（MB）与平均速率（MB/s）
- 宽带下载总流量（MB）与平均速率（Mbps）

示例（缩略）：

```text
==================================================
                压力测试分析报告
==================================================
测试持续时间: 60.00 秒

[系统负载对比]
CPU 占用率         |    测试前: 5.2%  |  测试后: 98.5%
内存 占用率          |   测试前: 30.1%  |  测试后: 65.4%
内存 已用           |    测试前: 4.80 GB | 测试后: 10.46 GB

[具体项目产出]
- CPU 运算总量: 1,245,000 次循环 (约 20,750 ops/sec)
- 脚本分配内存: 4096 MB (约 4.00 GB)
- UDP 发送总量: 234.38 MB (约 3.91 MB/s)
- 宽带下载总量: 450.25 MB (约 60.03 Mbps)
==================================================
```

## 注意事项
- 压测会显著占用系统资源，可能导致卡顿或无响应；建议在可控环境运行并提前保存工作
- 宽带压测会消耗真实网络流量，请谨慎选择下载 URL 并确保网络策略允许
- Windows 平台已处理 `multiprocessing` 的入口保护（`if __name__ == "__main__":`）
- 如果需要更高强度的网络/宽带压测，可适当增大 `--threads` 或更换更大的测速文件 URL

## 目录结构
本项目为单文件工具：
```
stress_test.py   # 压力测试脚本（CPU/内存/UDP/宽带 + 分析报告）
```

## 许可
可自由用于学习、测试与研究用途。若用于生产环境，请进行充分评估并自担风险。

---

# Python System Stress Test Tool (English)

A single-file tool for aggressive stress testing on a local machine, covering CPU, Memory, Network (UDP), and Public Bandwidth (download) tests. It automatically prints a summary report after each run, making it easy to compare system behavior under different scenarios.

File: [`stress_test.py`](stress_test.py)

## Features
- CPU load: Detects core count and spawns equal processes for intensive computation
- Memory load: Allocates memory by given size and keeps it hot with continuous read/write
- Network (UDP) load: Sends random datagrams to loopback 127.0.0.1 with a target port
- Public bandwidth load: Multi-threaded large file download to saturate downstream bandwidth (default Hetzner speed test file)
- Report: Prints CPU/Memory usage comparison and totals/rates for each test item

## Requirements
- Python 3.8+ (Windows/Linux/macOS)
- Dependency: `psutil` (system metrics collection)

Install:

```bash
pip install psutil
```

## Quick Start

Download or copy [`stress_test.py`](stress_test.py), then run:

```bash
# Full stress (CPU + 2GB Memory + UDP + Bandwidth, 60 seconds)
python stress_test.py --cpu --mem 2 --net --bw --duration 60
```

The program prints a summary report after completion, including pre/post system load and per-test totals.

## CLI Options
- `--cpu`: Enable CPU stress test
- `--mem <GB>`: Enable memory stress; specify size in GB
- `--net`: Enable UDP network stress to loopback `127.0.0.1`
- `--bw`: Enable public bandwidth download stress (multi-threaded)
- `--url <URL>`: Download URL for bandwidth test, default `http://speed.hetzner.de/100MB.bin`
- `--threads <N>`: Number of concurrent download threads, default `8`
- `--duration <seconds>`: Test duration (default `60`)
- `--net-port <port>`: UDP target port (default `9999`)

## Examples

```bash
# CPU-only (60 seconds)
python stress_test.py --cpu --duration 60

# Memory-only (allocate 4GB)
python stress_test.py --mem 4 --duration 60

# Bandwidth-only (16 threads, default URL)
python stress_test.py --bw --threads 16 --duration 90

# Custom download URL and port
python stress_test.py --bw --url "http://speed.hetzner.de/1GB.bin" --threads 32 --duration 120
python stress_test.py --net --net-port 8888 --duration 30
```

## Report
After finishing, the report includes:
- System load comparison: CPU usage, Memory usage, Used memory (GB)
- CPU total operations and average rate (ops/sec)
- Memory allocated total (MB/GB)
- UDP sent packets, total payload (MB), and average rate (MB/s)
- Bandwidth downloaded total (MB) and average rate (Mbps)

Example (short):

```text
==================================================
                Stress Test Report
==================================================
Duration: 60.00 s

[System Load Comparison]
CPU Usage          |   Before: 5.2%  |  After: 98.5%
Memory Usage       |   Before: 30.1% |  After: 65.4%
Memory Used        |   Before: 4.80 GB | After: 10.46 GB

[Per-Item Output]
- CPU total ops: 1,245,000 (≈ 20,750 ops/sec)
- Memory allocated: 4096 MB (≈ 4.00 GB)
- UDP total: 234.38 MB (≈ 3.91 MB/s)
- Bandwidth total: 450.25 MB (≈ 60.03 Mbps)
==================================================
```

## Notes
- Stress tests can heavily consume resources and cause lag or unresponsiveness; run in a controlled environment and save work beforehand
- Bandwidth tests use real network traffic; choose URL carefully and ensure policies allow it
- Windows has `multiprocessing` entry guard handled (`if __name__ == "__main__":`)
- For stronger network/bandwidth stress, increase `--threads` or use larger speed test URLs

## Structure
Single-file utility:
```
stress_test.py   # CPU/Memory/UDP/Bandwidth + Report
```

## License
Free for learning, testing, and research. For production use, assess thoroughly and proceed at your own risk.
