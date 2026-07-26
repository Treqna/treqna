# Frequently Asked Questions (FAQ)

### What makes Treqna different from existing format converters?
Treqna NEVER performs direct format-to-format conversion. By routing all data through an intermediate Universal Data Model (UDM), Treqna reduces $O(N^2)$ converter complexity to $O(N)$ decoupled parsers and writers.

### Does Treqna require external C dependencies?
No. Treqna is built directly on Python standard library primitives for maximum portability and zero runtime dependency friction.

### Which Python versions are supported?
Treqna supports Python 3.11, 3.12, and 3.13.

### Can I write custom plugins for my proprietary file formats?
Yes. Implement `ParserPluginInterface` or `WriterPluginInterface` and register your plugin with `PluginRegistry`.
