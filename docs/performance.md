# Performance & Benchmarks

Treqna is designed for high throughput and low memory footprint.

## Benchmark Results

| Operation | Dataset Size | Duration | Throughput |
| --- | --- | --- | --- |
| CSV -> UDM Parsing | 10,000 rows | < 0.15s | ~70,000 rows/sec |
| UDM -> CSV Writing | 10,000 rows | < 0.15s | ~70,000 rows/sec |
| Format Detection | Sample payload | < 0.001s | Instant |
| Schema Inspection | Sample payload | < 0.002s | Instant |

## Memory Profile

- **Standard Execution**: In-memory parsing loads dataset into UDM tree.
- **Streaming Generator Execution**: `stream_parse_to_udm()` and `stream_write_from_udm()` process items line-by-line, guaranteeing $O(1)$ memory overhead regardless of input stream size.

