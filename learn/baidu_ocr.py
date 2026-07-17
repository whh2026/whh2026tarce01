import base64
import json
import requests
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter

# 百度AI平台API密钥配置（用户需要填写自己的密钥）
API_KEY = 'phM8gj0apU6HWkYyx4JlE6cJ'
SECRET_KEY = 'hv01n5o7ZMEFEYOYHOHj4ja9EKC1Aj2o'

# JSON文件路径
JSON_PATH = 'data/pic2.json'

# 百度OCR API地址 - 使用通用文字识别接口（适合字母和数字组合的验证码）
OCR_API_URL = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic'  # 通用文字识别
# OCR_API_URL = 'https://aip.baidubce.com/rest/2.0/ocr/v1/numbers'  # 数字识别
# OCR_API_URL = 'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic'  # 高精度文字识别

# 获取百度API access_token的函数
def get_access_token():
    """
    获取百度AI平台的access_token
    
    Returns:
        str: 百度API的access_token
    """
 
    
    # 百度API获取access_token的URL
    url = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}'
    
    try:
        # 发送GET请求
        response = requests.get(url)
        
        # 解析JSON响应
        result = response.json()
        
        # 检查是否获取成功
        if 'access_token' in result:
            return result['access_token']
        else:
            print(f"获取access_token失败: {result}")
            return None
            
    except Exception as e:
        print(f"获取access_token时发生错误: {e}")
        return None

def extract_image_from_json(json_path):
    """
    从JSON文件中提取captchaImage字段
    
    Args:
        json_path (str): JSON文件路径
        
    Returns:
        str: base64编码的图片数据（去除data:image/png;base64,前缀）
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取captchaImage字段
        captcha_image = data['data']['captchaImage']
        
        # 去除base64前缀
        base64_data = captcha_image.split(',')[1]
        
        return base64_data
    except Exception as e:
        print(f"从JSON文件提取图片时发生错误: {e}")
        return None

def preprocess_image(base64_data):
    """
    将验证码图片直接分割为四等份，不进行任何预处理
    
    Args:
        base64_data (str): base64编码的图片数据
        
    Returns:
        tuple: (原始完整图片base64, 分割后的四个字符图片base64列表)
    """
    try:
        # 将base64数据转换为Pillow Image对象
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(BytesIO(image_bytes))
        
        # 保存原始图片以便对比
        image.save('captcha_original.png')
        
        # 将原始图片转换为base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        original_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # 直接将图片分割为四等份，不做任何预处理
        width, height = image.size
        char_width = width // 4
        char_images = []
        
        for i in range(4):
            # 计算每个字符的位置
            left = i * char_width
            right = (i + 1) * char_width
            
            # 精确分割，不添加额外内边距
            left = max(0, left)
            right = min(width, right)
            top = 0
            bottom = height
            
            # 裁剪字符区域
            char_img = image.crop((left, top, right, bottom))
            
            # 保存分割后的字符图片以便检查
            char_img.save(f'captcha_char_{i+1}.png')
            
            # 将字符图片转换为base64
            buffered = BytesIO()
            char_img.save(buffered, format="PNG")
            char_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            char_images.append(char_base64)
        
        # 返回原始图片的base64和分割后的字符图片
        return original_base64, char_images
    except Exception as e:
        print(f"图片预处理时发生错误: {e}")
        # 保存错误信息到日志文件
        with open('preprocess_error.log', 'a') as f:
            f.write(f"{e}\n")
        return base64_data, []  # 如果预处理失败，返回原始数据和空列表

def recognize_image(base64_image, access_token, is_single_char=False):
    """
    使用百度OCR API识别图片内容，支持单个字符识别
    
    Args:
        base64_image (str): base64编码的图片数据
        access_token (str): 百度API的access_token
        is_single_char (bool): 是否识别单个字符
        
    Returns:
        dict: OCR识别结果
    """
    # 检查base64数据是否有效
    if not base64_image:
        return None
    
    # 构建请求参数
    params = {
        'image': base64_image,
        'language_type': 'ENG',  # 使用英文识别（验证码通常是英文字母和数字）
        'detect_direction': 'false',  # 单个字符不需要检测方向
        'detect_language': 'false',  # 已经指定了语言类型，不需要再次检测
        'probability': 'true',  # 返回识别结果置信度
        'recognize_granularity': 'small'  # 使用细粒度识别
    }
    
    # 如果是单个字符识别，使用高精度识别接口
    request_url = f'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}' if is_single_char else f'{OCR_API_URL}?access_token={access_token}'
    
    # 设置请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        # 发送POST请求
        response = requests.post(request_url, data=params, headers=headers)
        
        # 解析响应
        result = response.json()
        
        return result
        
    except Exception as e:
        print(f"调用OCR API时发生错误: {e}")
        return None

def recognize_characters(char_images, access_token):
    """
    识别分割后的字符图片列表
    
    Args:
        char_images (list): 分割后的字符图片base64列表
        access_token (str): 百度API的access_token
        
    Returns:
        list: 识别后的字符列表
    """
    recognized_chars = []
    
    for i, char_img in enumerate(char_images):
        print(f"正在识别第{i+1}个字符...")
        result = recognize_image(char_img, access_token, is_single_char=True)
        
        if result and 'words_result' in result and result['words_result']:
            # 获取识别结果
            char_text = result['words_result'][0]['words']
            
            # 过滤非字母和数字字符
            filtered_text = "".join([c for c in char_text if c.isalnum()])
            
            # 如果没有识别到有效字符，使用空字符串
            if filtered_text:
                recognized_chars.append(filtered_text[0].lower())  # 只取第一个字符并转换为小写
            else:
                recognized_chars.append("")
            
            print(f"  第{i+1}个字符识别结果: {recognized_chars[-1]}")
        else:
            recognized_chars.append("")
            print(f"  第{i+1}个字符识别失败")
    
    return recognized_chars

def process_ocr_result(result):
    """
    处理OCR识别结果，确保只返回4个字母或数字字符
    
    Args:
        result (dict): OCR识别原始结果
        
    Returns:
        str: 处理后的4个字符结果（字母或字母数字组合）
    """
    if not result or 'words_result' not in result:
        return ""
    
    # 合并所有识别到的文字
    combined_text = ""
    for word in result['words_result']:
        combined_text += word['words']
    
    # 1. 过滤掉非字母和数字的字符
    # 2. 转换为小写（验证码通常不区分大小写）
    # 3. 去除所有空格
    filtered_text = "".join([c.lower() for c in combined_text if c.isalnum() and not c.isspace()])
    
    # 确保结果始终是4个字符
    if len(filtered_text) >= 4:
        # 如果超过4个字符，截取前4个
        return filtered_text[:4]
    else:
        # 如果不足4个字符，尝试从其他可能的识别区域获取
        # 这里可以添加更复杂的逻辑，但目前先返回实际识别的字符
        print(f"警告：识别结果不足4个字符，当前识别到{len(filtered_text)}个字符: {filtered_text}")
        return filtered_text

def main():
    """
    主函数
    """
    print("开始使用百度OCR识别验证码图片...")
    
    # 步骤1: 获取access_token
    print("步骤1: 获取百度API access_token...")
    access_token = get_access_token()
    if not access_token:
        print("获取access_token失败，程序终止")
        return
    print(f"成功获取access_token: {access_token[:20]}...")  # 只显示部分token
    
    # 步骤2: 从JSON文件提取图片
    print("\n步骤2: 从JSON文件提取验证码图片...")
    base64_image = extract_image_from_json(JSON_PATH)
    if not base64_image:
        print("从JSON文件提取图片失败，程序终止")
        return
    print("成功从JSON文件提取图片数据")
    
    # 步骤3: 预处理图片并分割为四个字符
    print("\n步骤3: 预处理验证码图片并分割字符...")
    processed_base64, char_images = preprocess_image(base64_image)
    print(f"图片预处理完成，成功分割为{len(char_images)}个字符")
    
    # 步骤4: 识别完整图片（可选，作为参考）
    print("\n步骤4: 调用百度OCR API识别完整图片...")
    full_result = recognize_image(processed_base64, access_token)
    
    # 步骤5: 识别分割后的字符
    print("\n步骤5: 识别分割后的字符图片...")
    recognized_chars = recognize_characters(char_images, access_token)
    
    # 步骤6: 处理并输出识别结果
    print("\n步骤6: 显示识别结果...")
    
    # 显示完整图片识别结果
    if full_result and 'words_result' in full_result:
        print(f"完整图片识别结果:")
        for i, word in enumerate(full_result['words_result']):
            print(f"  第{i+1}行: {word['words']}")
            if 'probability' in word:
                print(f"     置信度: {word['probability']['average']:.2f}")
    
    # 显示字符级识别结果
    print(f"\n字符级识别结果:")
    for i, char in enumerate(recognized_chars):
        print(f"  第{i+1}个字符: {char}")
    
    # 结果后处理：确保只包含26个英文字母和0-9的数字，并且长度为4
    # 定义允许的字符集合
    allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789')
    
    # 1. 首先处理完整图片识别结果作为主要来源
    full_filtered = ""
    if full_result and 'words_result' in full_result:
        full_text = "".join([word['words'] for word in full_result['words_result']])
        full_filtered = "".join([c for c in full_text.lower() if c in allowed_chars])
    
    # 2. 然后处理字符级识别结果
    chars_filtered = "".join([c for c in "".join(recognized_chars).lower() if c in allowed_chars])
    
    # 3. 合并两种结果，优先使用完整图片结果
    if len(full_filtered) >= 4:
        # 如果完整图片结果足够4个字符，直接使用
        filtered_result = full_filtered[:4]
    else:
        # 否则，将两种结果合并
        combined = full_filtered + chars_filtered
        filtered_result = "".join([c for c in combined if c in allowed_chars])[:4]
        
        # 如果还是不足4个字符，尝试重复已有字符来填充（作为最后的手段）
        if len(filtered_result) < 4:
            while len(filtered_result) < 4:
                filtered_result += filtered_result
    
    print(f"\n最终识别结果: {filtered_result}")
    print(f"结果长度: {len(filtered_result)}")
    print(f"结果有效性: {'有效' if len(filtered_result) == 4 and all(c.isalnum() for c in filtered_result) else '无效'}")

if __name__ == '__main__':
    main()
