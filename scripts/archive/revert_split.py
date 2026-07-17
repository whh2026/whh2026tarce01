with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到四个方法的位置
# fill_basic_info: 692-779
# fill_detail_info: 780-1081
# fill_shelf_info: 1082-1484
# confirm_and_publish: 1486-1596

# 删除四个方法（行号从0开始）
# 保留 create_data_product 方法（618-690行），然后删除后面的四个方法

# 需要保留的行: 0-690
# 需要删除的行: 691-1596
# 需要保留的行: 1597-末尾

new_lines = lines[:691] + lines[1597:]

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Deleted {1596 - 691 + 1} lines")
print(f"New file has {len(new_lines)} lines")
