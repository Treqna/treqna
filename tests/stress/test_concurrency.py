from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest

import treqna


def worker_task(worker_id: int) -> bool:
    csv_payload = f"id,worker,val\n{worker_id},worker_{worker_id},{worker_id * 10}\n"
    res_json = treqna.transform(csv_payload).to("json").execute()
    if not res_json.success:
        return False
    res_xml = treqna.transform(res_json.output).to("xml").execute()
    if not res_xml.success:
        return False
    res_yaml = treqna.transform(res_xml.output).to("yaml").execute()
    if not res_yaml.success:
        return False
    res_csv = treqna.transform(res_yaml.output).to("csv").execute()
    return res_csv.success


def test_concurrency_1000_workers() -> None:
    num_workers = 1000
    max_threads = 50

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(worker_task, i) for i in range(num_workers)]
        results = [f.result() for f in as_completed(futures)]

    assert len(results) == num_workers
    assert all(results)

