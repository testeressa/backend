import os
import re
import json
from collections import defaultdict
import argparse
from datetime import datetime


def parse_log_line(line):
    pattern = r'^(\S+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)" (\d+)$'
    match = re.match(pattern, line)
    if not match:
        return None

    ip = match.group(1)
    timestamp = match.group(2)
    request = match.group(3)
    status = match.group(4)
    bytes_sent = match.group(5)
    referer = match.group(6)
    user_agent = match.group(7)
    duration = int(match.group(8))

    request_parts = request.split()
    method = request_parts[0] if len(request_parts) > 0 else ''
    url = request_parts[1] if len(request_parts) > 1 else ''

    try:
        dt = datetime.strptime(timestamp, "%d/%b/%Y:%H:%M:%S %z")
    except ValueError:
        dt = None

    return {
        'ip': ip,
        'timestamp': timestamp,
        'datetime': dt,
        'method': method,
        'url': url,
        'status': status,
        'bytes_sent': bytes_sent,
        'referer': referer,
        'user_agent': user_agent,
        'duration': duration
    }


def analyze_log_file(file_path):
    total_requests = 0
    methods_count = defaultdict(int)
    ip_counts = defaultdict(int)
    slow_requests = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            total_requests += 1
            parsed = parse_log_line(line.strip())
            if not parsed:
                continue

            method = parsed['method']
            if method:
                methods_count[method] += 1

            ip = parsed['ip']
            ip_counts[ip] += 1

            slow_requests.append((
                parsed['duration'],
                parsed['method'],
                parsed['url'],
                parsed['ip'],
                parsed['timestamp'],
                parsed['datetime']
            ))

    top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    slow_requests_sorted = sorted(slow_requests, key=lambda x: x[0], reverse=True)
    top_slow_requests = []
    for req in slow_requests_sorted[:3]:
        top_slow_requests.append({
            'method': req[1],
            'url': req[2],
            'ip': req[3],
            'duration': req[0],
            'timestamp': req[4],
            'datetime': req[5].isoformat() if req[5] else None
        })

    result = {
        'total_requests': total_requests,
        'methods': dict(methods_count),
        'top_ips': [{'ip': ip, 'count': count} for ip, count in top_ips],
        'top_slow_requests': top_slow_requests,
        'file': os.path.basename(file_path)
    }

    return result


def save_to_json(data, output_dir):
    filename = f"stats_{data['file']}.json"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, filename)

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    return filename


def print_stats(data):
    print(f"\nStatistics for file: {data['file']}")
    print(f"Total requests: {data['total_requests']}")

    print("\nHTTP methods:")
    for method, count in data['methods'].items():
        print(f"{method}: {count}")

    print("\nTop 3 IPs:")
    for i, item in enumerate(data['top_ips'], 1):
        print(f"{i}. {item['ip']} - {item['count']} requests")

    print("\nTop 3 slowest requests:")
    for i, req in enumerate(data['top_slow_requests'], 1):
        print(f"{i}. Method: {req['method']}, URL: {req['url']}, "
              f"IP: {req['ip']}, Duration: {req['duration']} ms, "
              f"Time: {req['timestamp']}")


def process_logs(input_path, output_dir=None):
    if os.path.isfile(input_path):
        files = [input_path]
    elif os.path.isdir(input_path):
        files = [os.path.join(input_path, f) for f in os.listdir(input_path)
                 if os.path.isfile(os.path.join(input_path, f))]
    else:
        print(f"Error: {input_path} is neither a file nor a directory")
        return

    for file_path in files:
        print(f"\nProcessing file: {file_path}")
        stats = analyze_log_file(file_path)
        json_file = save_to_json(stats, output_dir)
        print(f"Statistics saved to: {json_file}")
        print_stats(stats)


def main():
    parser = argparse.ArgumentParser(description='Analyze access.log files')
    parser.add_argument('input', help='Input file or directory containing log files')
    parser.add_argument('-o', '--output', help='Output directory for JSON files')
    args = parser.parse_args()

    process_logs(args.input, args.output)


main()
