import multiprocessing
import time
import socket
import os
import argparse
import sys
import array
import urllib.request
import psutil
from threading import Thread

def cpu_stress_worker(stop_event, counter):
    """CPU 压力测试工作进程：执行密集的数学运算"""
    # print(f"CPU 工作进程 {os.getpid()} 启动")
    local_count = 0
    while not stop_event.is_set():
        # 执行密集的数学运算
        _ = [x**2 for x in range(1000)]
        local_count += 1
        if local_count >= 100:
            with counter.get_lock():
                counter.value += local_count
            local_count = 0

def memory_stress_worker(stop_event, size_gb, counter):
    """内存压力测试工作进程：分配并持续访问大块内存"""
    try:
        # 分配内存
        # 每个 float 占 8 字节，128KB chunk 包含 16384 个 float
        chunk_elements = 16384 
        chunk_size_mb = (chunk_elements * 8) / (1024 * 1024) # 0.125 MB
        target_mb = size_gb * 1024
        num_chunks = int(target_mb / chunk_size_mb)
        
        data_blocks = []
        for i in range(num_chunks):
            if stop_event.is_set():
                break
            data_blocks.append(array.array('d', [1.0] * chunk_elements))
            if i % 8 == 0: # 每 1MB 更新一次计数器
                with counter.get_lock():
                    counter.value += 1 
        
        while not stop_event.is_set():
            for block in data_blocks:
                if stop_event.is_set():
                    break
                block[0] = block[0] + 0.1
                _ = block[-1]
            time.sleep(0.1)
            
    except MemoryError:
        print("错误: 内存不足，无法分配请求的内存大小。")
    except Exception as e:
        print(f"内存测试出错: {e}")

def network_stress_worker(stop_event, target_ip, target_port, counter):
    """网络压力测试工作进程：发送 UDP 数据包"""
    # print(f"网络工作进程 {os.getpid()} 启动，目标: {target_ip}:{target_port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = os.urandom(1024) # 1KB 的随机数据
    
    local_count = 0
    while not stop_event.is_set():
        try:
            sock.sendto(data, (target_ip, target_port))
            local_count += 1
            if local_count >= 1000:
                with counter.get_lock():
                    counter.value += local_count
                local_count = 0
        except Exception:
            pass

def bandwidth_stress_worker(stop_event, url, num_threads, counter):
    """宽带压力测试工作进程：通过多线程下载大文件来消耗带宽"""
    # print(f"宽带工作进程 {os.getpid()} 启动，目标 URL: {url}")
    
    def downloader():
        error_logged = False
        while not stop_event.is_set():
            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    while not stop_event.is_set():
                        chunk = response.read(128 * 1024) # 128KB chunks
                        if not chunk:
                            break
                        with counter.get_lock():
                            counter.value += len(chunk)
            except Exception as e:
                if not error_logged:
                    # print(f"下载进程 {os.getpid()} 出错 (可能网络不通): {e}")
                    error_logged = True
                time.sleep(2)

    threads = []
    for i in range(num_threads):
        t = Thread(target=downloader)
        t.daemon = True
        t.start()
        threads.append(t)
    
    while not stop_event.is_set():
        time.sleep(0.5)

def get_system_stats():
    """获取当前系统 CPU 和 内存 状态"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "mem_percent": psutil.virtual_memory().percent,
        "mem_used_gb": psutil.virtual_memory().used / (1024**3),
        "net_io": psutil.net_io_counters()
    }

def print_report(duration, args, stats_start, stats_end, cpu_ops, mem_mb, net_packets, bw_bytes):
    """打印测试分析报告"""
    print("\n" + "="*50)
    print("                压力测试分析报告")
    print("="*50)
    print(f"测试持续时间: {duration:.2f} 秒")
    
    print("\n[系统负载对比]")
    print(f"{'指标':<15} | {'测试前':<15} | {'测试后':<15}")
    print("-" * 50)
    print(f"{'CPU 占用率':<15} | {stats_start['cpu_percent']:>14.1f}% | {stats_end['cpu_percent']:>14.1f}%")
    print(f"{'内存 占用率':<15} | {stats_start['mem_percent']:>14.1f}% | {stats_end['mem_percent']:>14.1f}%")
    print(f"{'内存 已用':<15} | {stats_start['mem_used_gb']:>12.2f} GB | {stats_end['mem_used_gb']:>12.2f} GB")

    print("\n[具体项目产出]")
    if args.cpu:
        print(f"- CPU 运算总量: {cpu_ops.value:,} 次循环 (约 {cpu_ops.value/duration:,.0f} ops/sec)")
    if args.mem:
        print(f"- 脚本分配内存: {mem_mb.value} MB (约 {mem_mb.value/1024:.2f} GB)")
    if args.net:
        sent_mb = (net_packets.value * 1024) / (1024**2)
        print(f"- UDP 发送总量: {net_packets.value:,} 包 (约 {sent_mb:.2f} MB)")
        print(f"- UDP 发送速率: {sent_mb/duration:.2f} MB/s")
    if args.bw:
        downloaded_mb = bw_bytes.value / (1024**2)
        print(f"- 宽带下载总量: {downloaded_mb:.2f} MB")
        print(f"- 平均下载速率: {(downloaded_mb * 8)/duration:.2f} Mbps")
    
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Python 暴力压力测试工具 (CPU, 内存, 网络)")
    parser.add_argument("--cpu", action="store_true", help="开启 CPU 压力测试")
    parser.add_argument("--mem", type=float, help="开启内存压力测试，并指定大小 (GB)")
    parser.add_argument("--net", action="store_true", help="开启网络压力测试 (针对本地 127.0.0.1)")
    parser.add_argument("--bw", action="store_true", help="开启宽带压力测试 (下载大文件)")
    parser.add_argument("--url", type=str, default="http://speed.hetzner.de/100MB.bin", help="宽带测试下载 URL")
    parser.add_argument("--threads", type=int, default=8, help="宽带测试并发线程数")
    parser.add_argument("--duration", type=int, default=60, help="测试持续时间 (秒)，默认 60 秒")
    parser.add_argument("--net-port", type=int, default=9999, help="网络测试目标端口")
    
    args = parser.parse_args()

    if not (args.cpu or args.mem or args.net or args.bw):
        parser.print_help()
        return

    print("\n--- 正在收集系统初始状态... ---")
    stats_start = get_system_stats()
    
    print("--- 压力测试开始 ---")
    print(f"计划持续时间: {args.duration} 秒")
    
    stop_event = multiprocessing.Event()
    
    # 共享计数器
    cpu_ops = multiprocessing.Value('q', 0)
    mem_mb = multiprocessing.Value('i', 0)
    net_packets = multiprocessing.Value('q', 0)
    bw_bytes = multiprocessing.Value('q', 0)
    
    processes = []

    # 1. CPU 压力测试
    if args.cpu:
        num_cores = multiprocessing.cpu_count()
        print(f"启动 {num_cores} 个 CPU 核心测试进程...")
        for _ in range(num_cores):
            p = multiprocessing.Process(target=cpu_stress_worker, args=(stop_event, cpu_ops))
            p.start()
            processes.append(p)

    # 2. 内存压力测试
    if args.mem:
        print(f"启动内存测试进程，目标 {args.mem}GB...")
        p = multiprocessing.Process(target=memory_stress_worker, args=(stop_event, args.mem, mem_mb))
        p.start()
        processes.append(p)

    # 3. 网络压力测试 (UDP Flood)
    if args.net:
        print(f"启动网络测试进程 (UDP Flood to 127.0.0.1:{args.net_port})...")
        for _ in range(4):
            p = multiprocessing.Process(target=network_stress_worker, args=(stop_event, "127.0.0.1", args.net_port, net_packets))
            p.start()
            processes.append(p)

    # 4. 宽带压力测试
    if args.bw:
        print(f"启动宽带测试进程 (下载: {args.url})...")
        p = multiprocessing.Process(target=bandwidth_stress_worker, args=(stop_event, args.url, args.threads, bw_bytes))
        p.start()
        processes.append(p)

    test_start_time = time.time()
    try:
        while time.time() - test_start_time < args.duration:
            time.sleep(1)
            elapsed = time.time() - test_start_time
            remaining = max(0, int(args.duration - elapsed))
            if remaining % 10 == 0 or remaining < 5:
                print(f"剩余时间: {remaining} 秒...")
    except KeyboardInterrupt:
        print("\n用户手动终止测试。")
    finally:
        actual_duration = time.time() - test_start_time
        print("\n正在停止所有测试进程并收集最终数据...")
        stop_event.set()
        for p in processes:
            p.join(timeout=1)
            if p.is_alive():
                p.terminate()
        
        stats_end = get_system_stats()
        print_report(actual_duration, args, stats_start, stats_end, cpu_ops, mem_mb, net_packets, bw_bytes)
        print("--- 压力测试结束 ---")

if __name__ == "__main__":
    main()
