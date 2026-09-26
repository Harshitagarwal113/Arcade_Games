import os

index_path = os.path.join("build", "web", "index.html")

if not os.path.exists(index_path):
    print("Error: index.html not found!")
    exit(1)

with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Title
content = content.replace("<title>arcade_games-master</title>", "<title>🎮 Retro Arcade Hub</title>")

# 2. Fix Background Color and Theme (replace powderblue)
content = content.replace("background-color:powderblue;", "background-color:#140f23;")
content = content.replace('platform.document.body.style.background = "#7f7f7f"', 'platform.document.body.style.background = "#140f23"')

# 3. Modernize #infobox loading indicator
old_infobox_css = """        #infobox {
            position: fixed; /* center relative to viewport */
            background: green;
            color: blue;
            font-weight: bold;
            padding: 12px 24px;
 /*           display: none; */
            z-index: 999999;
        }"""

new_infobox_css = """        #infobox {
            position: fixed;
            background: rgba(20, 15, 35, 0.95);
            color: #39ff14;
            border: 2px solid #ff1493;
            border-radius: 12px;
            box-shadow: 0 0 25px rgba(57, 255, 20, 0.4), 0 0 10px rgba(255, 20, 147, 0.3);
            font-family: 'Segoe UI', system-ui, sans-serif;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 2px;
            padding: 14px 28px;
            z-index: 999999;
            backdrop-filter: blur(10px);
            animation: arcadeGlow 1.5s infinite alternate ease-in-out;
        }
        @keyframes arcadeGlow {
            0% { box-shadow: 0 0 15px rgba(57, 255, 20, 0.4); transform: scale(1); }
            100% { box-shadow: 0 0 30px rgba(255, 20, 147, 0.7); transform: scale(1.02); }
        }"""

if old_infobox_css in content:
    content = content.replace(old_infobox_css, new_infobox_css)

content = content.replace("Loading, please wait ...", "🎮 LOADING ARCADE HUB...")

# 4. Bypass UME wait loop for direct arcade launch
ume_wait_block = """    # test/wait user media interaction
    if not platform.window.MM.UME:

        # now that apk is mounted we have access to font cache
        # but we need to fill __file__ that is not yet set
        __import__(__name__).__file__ = main

        # now make a prompt
        msg  = "Ready to start ! Please click/touch page"
        platform.window.infobox.innerText = msg
        print("\\n"*4, f"    * Waiting for media user engagement. {msg} *" , "\\n"*4)

        while not platform.window.MM.UME:
            await asyncio.sleep(.1)"""

direct_launch_block = """    # Direct arcade launch: bypass click prompt
    __import__(__name__).__file__ = main
    platform.window.MM.UME = true"""

if ume_wait_block in content:
    content = content.replace(ume_wait_block, direct_launch_block)

# 5. Inject Vercel Analytics
analytics_script = """
<!-- Vercel Analytics -->
<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>
<script defer src="/_vercel/insights/script.js"></script>
"""

if "_vercel/insights/script.js" not in content:
    if "</body>" in content:
        content = content.replace("</body>", f"{analytics_script}\n</body>")
    else:
        content += analytics_script

with open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Injected Vercel Analytics, dark neon styling, and direct arcade auto-start into index.html")
