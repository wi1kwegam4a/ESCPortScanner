#!/usr/bin/env python3

import socket
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_arguments():
    parser = argparse.ArgumentParser(description="A script to scan open ports on a target IP within a specified range.")
    parser.add_argument("target_ip", help="Target IP address to scan")
    parser.add_argument("-s", "--start_port", type=int, default=1, help="Starting port (default: 1)")
    parser.add_argument("-e", "--end_port", type=int, default=65535, help="Ending port (default: 65535)")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Number of threads to use (default: 100)")
    return parser.parse_args()

def scan_port(ip, port, timeout=5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((ip, port))
            return port, "open"
        except socket.timeout:
            return port, "timeout"
        except socket.error as e:
            if e.errno == socket.errno.ECONNREFUSED:
                return port, "refused"
            return port, "closed"

def main():
    args = parse_arguments()

    # 使用多线程执行端口扫描任务
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        # 为每个端口提交任务
        future_to_port = {executor.submit(scan_port, args.target_ip, port): port for port in range(args.start_port, args.end_port + 1)}

        for future in as_completed(future_to_port):
            port, status = future.result()
            
            # 打印扫描结果
            if status == "open":
                print(f"Port {port} is open with a service")
            elif status == "refused":
                print(f"Port {port} is open but no service")
            # else:
            #     print(f"Port {port} is closed")

    print("Scan completed.")

if __name__ == "__main__":
    main()
