import importlib
import time
import tracemalloc
from dataclasses import dataclass

import treqna
from treqna.formats.registry import FormatRegistry
from treqna.plugins.discovery import discover_and_register_plugins
from treqna.plugins.registry import PluginRegistry


@dataclass(frozen=True, kw_only=True)
class ProfilingReport:
    startup_time_ms: float
    plugin_discovery_time_ms: float
    registry_lookup_time_ns: float
    planner_lookup_time_ns: float
    transformation_throughput_ops_sec: float
    peak_memory_kb: float
    memory_leak_bytes: int


class TreqnaProfiler:
    def profile_startup_time(self) -> float:
        start = time.perf_counter()
        importlib.reload(treqna)
        duration_ms = (time.perf_counter() - start) * 1000.0
        return duration_ms

    def profile_plugin_discovery(self) -> float:
        plugin_reg = PluginRegistry()
        format_reg = FormatRegistry()
        start = time.perf_counter()
        discover_and_register_plugins(plugin_reg, format_reg)
        duration_ms = (time.perf_counter() - start) * 1000.0
        return duration_ms

    def profile_registry_lookup(self, iterations: int = 10000) -> float:
        plugin_reg = PluginRegistry()
        discover_and_register_plugins(plugin_reg)
        start = time.perf_counter_ns()
        for _ in range(iterations):
            _ = plugin_reg.get_parser("json")
            _ = plugin_reg.get_writer("json")
        duration_ns = (time.perf_counter_ns() - start) / (iterations * 2)
        return duration_ns

    def profile_planner_lookup(self, iterations: int = 10000) -> float:
        start = time.perf_counter_ns()
        for _ in range(iterations):
            _ = treqna.transform("id,name\n1,Alice\n").to("json")
        duration_ns = (time.perf_counter_ns() - start) / iterations
        return duration_ns

    def run_full_profiling(self) -> ProfilingReport:
        tracemalloc.start()
        start_mem, _ = tracemalloc.get_traced_memory()

        startup_ms = self.profile_startup_time()
        discovery_ms = self.profile_plugin_discovery()
        reg_ns = self.profile_registry_lookup()
        plan_ns = self.profile_planner_lookup()

        start_time = time.perf_counter()
        ops = 5000
        sample_csv = "id,name,role\n101,Alice,Engineer\n"
        for _ in range(ops):
            _ = treqna.transform(sample_csv).to("json").execute()
        duration_sec = time.perf_counter() - start_time
        throughput = ops / duration_sec if duration_sec > 0 else 0.0

        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return ProfilingReport(
            startup_time_ms=round(startup_ms, 3),
            plugin_discovery_time_ms=round(discovery_ms, 3),
            registry_lookup_time_ns=round(reg_ns, 2),
            planner_lookup_time_ns=round(plan_ns, 2),
            transformation_throughput_ops_sec=round(throughput, 1),
            peak_memory_kb=round(peak_mem / 1024.0, 2),
            memory_leak_bytes=current_mem - start_mem,
        )

