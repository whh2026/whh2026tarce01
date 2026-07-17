# 测试报告邮件发送功能

## 功能说明

测试完成后，系统会自动发送包含测试结果的邮件到指定邮箱。

## 配置步骤

### 1. 复制配置文件

```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

填写实际的邮件配置信息：

```env
# SMTP服务器配置
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USE_TLS=true

# 发件人配置
SENDER_EMAIL=your_email@qq.com
SENDER_PASSWORD=your_smtp_password
SENDER_NAME=测试报告系统

# 收件人配置
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com
```

### 3. 获取SMTP授权码

#### QQ邮箱
1. 登录QQ邮箱网页版
2. 进入"设置" -> "账户"
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"SMTP服务"
5. 生成授权码（不是QQ密码）
6. 将授权码填入 `SENDER_PASSWORD`

#### 163邮箱
1. 登录163邮箱网页版
2. 进入"设置" -> "POP3/SMTP/IMAP"
3. 开启"SMTP服务"
4. 获取授权码
5. 将授权码填入 `SENDER_PASSWORD`

#### Gmail
1. 登录Google账户
2. 进入"安全性" -> "两步验证"
3. 开启"应用专用密码"
4. 生成应用专用密码
5. 将专用密码填入 `SENDER_PASSWORD`

## 使用方法

### 运行测试并发送邮件

```bash
python run_test.py
```

测试完成后，系统会自动：
1. 解析测试结果
2. 生成HTML格式的测试报告邮件
3. 附加测试报告文件
4. 发送到配置的收件人邮箱

### 验证邮件配置

```bash
python -c "from tests.api_tests.utils.email_config import EmailConfig; EmailConfig.print_config_status()"
```

## 邮件内容

### 邮件主题

```
【测试报告】20260305_111356 - API自动化测试结果
```

### 邮件正文

- 📊 测试统计（总测试数、通过、失败、跳过、错误、通过率）
- 📈 进度条（可视化显示通过率）
- 📋 测试详情（执行时间、报告目录、测试时间）
- 📎 附件说明（report.html、test_output.txt）

### 邮件附件

1. **report.html** - 完整的HTML测试报告
2. **test_output.txt** - 测试输出日志

## 测试结果示例

```
=== 解析测试结果 ===
总测试数: 48
通过: 32
失败: 10
跳过: 1
错误: 6
通过率: 66.7%
执行时间: 7.76秒

=== 发送测试报告邮件 ===
已添加附件: report.html (text/html)
已添加附件: test_output.txt (text/plain)

正在连接SMTP服务器: smtp.qq.com:587
已启用TLS加密
正在登录: your_email@qq.com
登录成功
正在发送邮件到: recipient1@example.com, recipient2@example.com
✅ 邮件发送成功！
```

## 常见问题

### Q: 邮件发送失败怎么办？

A: 检查以下几点：
1. SMTP服务器地址和端口是否正确
2. 发件人邮箱是否开启了SMTP服务
3. SMTP授权码是否正确（不是邮箱密码）
4. 网络连接是否正常
5. 防火墙是否阻止了SMTP连接

### Q: 如何不发送邮件？

A: 有两种方式：
1. 不配置 `.env` 文件，系统会跳过邮件发送
2. 注释掉 `run_test.py` 中的邮件发送代码

### Q: 可以发送给多个收件人吗？

A: 可以，在 `.env` 文件中使用逗号分隔多个邮箱：
```env
RECIPIENT_EMAILS=user1@example.com,user2@example.com,user3@example.com
```

### Q: 邮件正文可以自定义吗？

A: 可以，修改 `tests/api_tests/utils/email_sender.py` 中的 `_build_test_report_body` 方法。

## 技术支持

如有问题，请联系测试团队。
