import os, re

apps_dir = "/home/frappe/frappe-bench/apps"

files_to_check = []
for root, dirs, files in os.walk(apps_dir):
    if "node_modules" in dirs:
        dirs.remove("node_modules")
    for file in files:
        if file in ("Home.vue", "Launcher.vue"):
            files_to_check.append(os.path.join(root, file))

GOOD_HEADER_BLOCK = '''      <div class="flex items-center gap-3">
        <Button variant="subtle" @click="goPortal" class="flex items-center gap-1">
          <FeatherIcon name="arrow-left" class="h-4 w-4" />
          <span>Cổng</span>
        </Button>
        <div class="h-4 w-[1px] bg-gray-200"></div>
        <span class="text-sm text-gray-600 font-medium">{{ user?.full_name || 'Administrator' }}</span>
        <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600 hover:text-red-700">
          Đăng xuất
        </Button>
      </div>'''

for path in files_to_check:
    try:
        content = open(path, encoding="utf-8").read()
    except:
        continue

    # Count how many times "Đăng xuất" appears in the template section only
    template_end = content.find("</template>")
    if template_end == -1:
        template_end = len(content)
    template_section = content[:template_end]
    
    count = template_section.count("Đăng xuất")
    if count > 1:
        print(f"DUPLICATE FOUND: {path} ({count} occurrences)")
        
        # Strategy: find the </header> and check what's before it
        # Remove any nested duplicate header closing divs
        # We expect: outer div.flex.items-center.gap-3 containing the button block ONCE
        
        # Pattern to find duplicate: two adjacent user/logout blocks
        # Remove the second one by normalizing
        
        # Simple approach: collapse duplicate Đăng xuất button patterns
        # Find pattern where we have nested divs with same content
        bad_pattern = re.compile(
            r'(<div class="flex items-center gap-3">)\s*'
            r'(<div class="flex items-center gap-3">)\s*'
            r'(.*?Đăng xuất.*?</Button>\s*</div>)\s*'  # inner block
            r'(.*?Đăng xuất.*?</Button>)\s*'           # outer block 
            r'(\s*</div>)',
            re.DOTALL
        )
        
        # Simpler: just remove the duplicate lines
        # Find all occurrences of the user+logout pattern
        logout_pattern = re.compile(
            r'\s*<div class="h-4 w-\[1px\] bg-gray-200"></div>\s*'
            r'<span class="text-sm text-gray-600 font-medium">.*?</span>\s*'
            r'<Button[^>]*loggingOut[^>]*>\s*Đăng xuất\s*</Button>',
            re.DOTALL
        )
        
        matches = list(logout_pattern.finditer(template_section))
        print(f"  Found {len(matches)} logout patterns in template")
        
        if len(matches) >= 2:
            # Remove the last one (the duplicate)
            last_match = matches[-1]
            content = content[:last_match.start()] + content[last_match.end():]
            
            # Also clean up orphan closing div if any
            # Check for double </div> before </header>
            content = re.sub(r'</div>\s*</div>\s*</header>', '</div>\n    </header>', content)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Fixed!")
        
    else:
        print(f"OK ({count}x): {path}")

print("Done.")
