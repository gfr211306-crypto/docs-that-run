# Test Document

這是 docs-that-run v0.1 的測試文件。

```python dtr-run
print("Test 1: Success")
```

```bash dtr-run
echo "Hello from bash" > shared_file.txt
echo "Test 2: Success"
```

```python
# 這段不會執行（沒有 dtr-run）
raise RuntimeError("This block must not run")
```

```python dtr-run
with open("shared_file.txt", "r", encoding="utf-8") as file:
    print("Read from shared file:", file.read().strip())
```

```python dtr-run
import time

time.sleep(0.05)
print("Test 3: After delay")
```
