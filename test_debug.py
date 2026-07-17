import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # 访问登录页面
    page.goto('http://192.168.0.183:30001/login')
    page.wait_for_load_state('networkidle')
    
    # 登录
    page.fill('input[placeholder*="用户"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.fill('input[placeholder*="验证"]', '987423')
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    # 访问发布页面
    page.goto('http://192.168.0.183:30001/registration/product/release')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print('=== 基础配置页面 ===')
    
    # 填写中文名称
    name_input = page.locator('label:has-text("数据产品名称") ~ div .el-input__inner')
    if name_input.count() > 0:
        name_input.fill('TestProduct')
        print('✓ 已填写中文名称')
    
    # 填写英文名称
    en_name_input = page.locator('label:has-text("数据产品英文名称") + div >> input')
    if en_name_input.count() > 0:
        en_name_input.fill('TestProductEn')
        print('✓ 已填写英文名称')
    
    # 填写产品介绍
    desc_textarea = page.locator('textarea[placeholder*="说明数据产品的基本信息"]')
    if desc_textarea.count() > 0:
        desc_textarea.fill('这是测试产品介绍')
        print('✓ 已填写产品介绍')
    
    # 填写使用限制
    limit_textarea = page.locator('textarea[placeholder*="说明数据产品在使用过程中的任何限制"]')
    if limit_textarea.count() > 0:
        limit_textarea.fill('无使用限制')
        print('✓ 已填写使用限制')
    
    # 填写其他说明
    other_textarea = page.locator('textarea[placeholder*="请输入其他说明"]')
    if other_textarea.count() > 0:
        other_textarea.fill('其他说明')
        print('✓ 已填写其他说明')
    
    # 填写产品标签
    tags_input = page.locator('label:has-text("数据产品标签") + div >> input')
    if tags_input.count() > 0:
        tags_input.fill('测试, 自动化')
        print('✓ 已填写产品标签')
    
    # 选择行业分类
    print('正在选择行业分类...')
    industry_select = page.locator('label:has-text("行业分类") + div')
    if industry_select.count() > 0:
        industry_select.click()
        time.sleep(0.5)
        page.locator('li:has-text("采矿业")').first.click()
        print('✓ 已选择行业分类: 采矿业')
        time.sleep(0.5)
    
    # 选择产品类型
    print('正在选择产品类型...')
    type_select = page.locator('label:has-text("产品类型") + div')
    if type_select.count() > 0:
        type_select.click()
        time.sleep(0.5)
        page.locator('li:has-text("数据接口")').first.click()
        print('✓ 已选择产品类型: 数据接口')
        time.sleep(0.5)
    
    # 选择产品小类
    print('正在选择产品小类...')
    subtype_select = page.locator('label:has-text("产品小类") + div')
    if subtype_select.count() > 0:
        subtype_select.click()
        time.sleep(0.5)
        page.locator('li:has-text("API接口")').first.click()
        print('✓ 已选择产品小类: API接口')
        time.sleep(0.5)
    
    # 选择地域分类
    print('正在选择地域分类...')
    region_select = page.locator('label:has-text("地域分类") + div')
    if region_select.count() > 0:
        region_select.click()
        time.sleep(0.5)
        page.locator('li:has-text("北京市")').first.click()
        print('✓ 已选择地域分类: 北京市')
        time.sleep(0.5)
    
    # 点击下一步
    print('正在点击下一步...')
    next_btn = page.locator('button:has-text("下一步")')
    if next_btn.is_visible():
        next_btn.click()
        print('✓ 已点击下一步')
        page.wait_for_load_state('networkidle')
        time.sleep(3)
    
    print(f'\n=== 详细信息页面 ===')
    print(f'当前URL: {page.url}')
    
    # 填写接口名称
    接口名称输入 = page.locator('label:has-text("接口名称") + * input').first
    if 接口名称输入.is_visible():
        接口名称输入.fill('测试接口')
        print('✓ 已填写接口名称')
    
    # 填写正式接口地址
    正式接口 = page.locator('label:has-text("正式接口地址") ~ div .el-input__inner')
    if 正式接口.count() > 0 and 正式接口.is_visible():
        正式接口.fill('http://192.168.0.152:31080/api/mock/prod/cbdt')
        print('✓ 已填写正式接口地址')
    
    # 填写测试接口地址
    测试接口 = page.locator('label:has-text("测试接口地址") ~ div .el-input__inner')
    if 测试接口.count() > 0 and 测试接口.is_visible():
        测试接口.fill('http://192.168.0.152:31080/api/mock/prod/cbdt')
        print('✓ 已填写测试接口地址')
    
    # 向下滚动
    page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
    time.sleep(1)
    
    # 查找入参信息字段
    print('\n=== 查找入参信息字段 ===')
    入参表单 = page.locator('.el-form-item:has(label:has-text("入参信息"))')
    if 入参表单.count() > 0:
        print(f'找到入参信息表单，数量: {入参表单.count()}')
        入参输入框 = 入参表单.locator('.el-input__inner')
        print(f'入参输入框数量: {入参输入框.count()}')
        
        # 填写入参字段
        入参值 = ['a', 'b', 'c', 'date']
        for i in range(min(4, 入参输入框.count())):
            try:
                入参输入框.nth(i).fill(入参值[i])
                print(f'✓ 已填写第{i+1}个入参字段: {入参值[i]}')
            except Exception as e:
                print(f'填写第{i+1}个入参字段失败: {e}')
    
    # 查找"是否需要授权"选项
    print('\n=== 查找是否需要授权选项 ===')
    授权选项 = page.locator('label:has-text("是否需要授权") ~ div .el-radio')
    print(f'找到授权选项数量: {授权选项.count()}')
    
    for i in range(授权选项.count()):
        选项文本 = 授权选项.nth(i).text_content()
        print(f'  选项{i}: {选项文本}')
    
    # 点击"是"选项
    是选项 = page.locator('label:has-text("是否需要授权") ~ div .el-radio:has-text("是")')
    if 是选项.count() > 0:
        是选项.click()
        print('✓ 已点击是否需要授权: 是')
        time.sleep(5)
        
        # 查找精准授权字段
        print('\n=== 查找精准授权字段 ===')
        
        # 使用JavaScript获取页面结构
        result = page.evaluate('''
(function() {
    // 查找包含"企业名称"的label
    var labels = document.querySelectorAll('label, .el-form-item__label');
    var result = [];
    for (var i = 0; i < labels.length; i++) {
        var text = labels[i].textContent || '';
        if (text.includes('企业名称') || text.includes('统一社会信用代码') || text.includes('企业扩展字段') || text.includes('日期')) {
            var parent = labels[i].closest('.el-form-item');
            if (parent) {
                var input = parent.querySelector('input, .el-input__inner');
                if (input) {
                    result.push({
                        label: text.trim(),
                        tagName: input.tagName,
                        type: input.type || 'text',
                        placeholder: input.placeholder || ''
                    });
                }
            }
        }
    }
    return JSON.stringify(result);
})()
        ''')
        import json
        fields = json.loads(result)
        print(f'找到{len(fields)}个精准授权相关字段:')
        for f in fields:
            print(f'  - {f}')
    
    browser.close()
    print('\n调试完成')