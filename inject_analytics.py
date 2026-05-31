import os

index_path = os.path.join("build", "web", "index.html")

if not os.path.exists(index_path):
    print("Error: index.html not found!")
    exit(1)

with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

analytics_script = """
<!-- Vercel Analytics -->
<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>
<script defer src="/_vercel/insights/script.js"></script>
"""

if "</body>" in content:
    content = content.replace("</body>", f"{analytics_script}\n</body>")
else:
    content += analytics_script

with open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Injected Vercel Analytics into index.html")
