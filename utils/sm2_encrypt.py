"""
SM2 密码加密工具
支持软密钥和硬密钥两种加密模式
"""
import base64
from gmssl import sm2


class SM2Encryptor:
    """SM2 加密工具类"""
    
    @staticmethod
    def is_hardware_key(pubkey: str) -> bool:
        """判断是否为硬密钥（PEM 格式）"""
        return "-----BEGIN PUBLIC KEY-----" in pubkey
    
    @staticmethod
    def convert_pem_to_raw(pubkey: str) -> str:
        """将 PEM 格式公钥转换为裸十六进制格式"""
        if pubkey.startswith("04") and "-----" not in pubkey:
            return pubkey
        
        if SM2Encryptor.is_hardware_key(pubkey):
            b64 = pubkey.replace("-----BEGIN PUBLIC KEY-----", "") \
                        .replace("-----END PUBLIC KEY-----", "") \
                        .replace("\n", "").replace("\r", "")
            der_bytes = base64.b64decode(b64)
            raw_bytes = der_bytes[-65:]
            return raw_bytes.hex()
        
        return pubkey
    
    @staticmethod
    def encrypt_password(plain_password: str, pubkey: str) -> str:
        """
        使用 SM2 加密密码
        
        - 软密钥（04开头的十六进制）：C1C2C3 模式，04前缀 + hex 输出
        - 硬密钥（PEM格式）：C1C3C2 模式，04前缀 + base64 输出
        
        Args:
            plain_password: 明文密码
            pubkey: 公钥（支持 PEM 格式或十六进制格式）
            
        Returns:
            加密后的密码字符串
            
        Raises:
            Exception: 加密失败时抛出异常
        """
        try:
            is_hard = SM2Encryptor.is_hardware_key(pubkey)
            raw_pubkey = SM2Encryptor.convert_pem_to_raw(pubkey)
            
            # gmssl 库需要不带 04 前缀的公钥
            if raw_pubkey.startswith("04"):
                raw_pubkey = raw_pubkey[2:]
            
            if is_hard:
                # 硬密钥：C1C3C2 模式，Base64 输出
                sm2_crypt = sm2.CryptSM2(public_key=raw_pubkey, private_key="", mode=1)
                cipher_bytes = sm2_crypt.encrypt(plain_password.encode())
                cipher_with_prefix = b'\x04' + cipher_bytes
                return base64.b64encode(cipher_with_prefix).decode()
            else:
                # 软密钥：C1C2C3 模式，十六进制输出
                sm2_crypt = sm2.CryptSM2(public_key=raw_pubkey, private_key="", mode=0)
                cipher_bytes = sm2_crypt.encrypt(plain_password.encode())
                return "04" + cipher_bytes.hex()
                
        except Exception as e:
            raise Exception(f"SM2 加密失败: {e}")
    
    @staticmethod
    def encrypt_from_file(password: str, pubkey_file: str) -> str:
        """
        从文件读取公钥并加密密码
        
        Args:
            password: 明文密码
            pubkey_file: 公钥文件路径
            
        Returns:
            加密后的密码字符串
        """
        with open(pubkey_file, 'r', encoding='utf-8') as f:
            pubkey = f.read().strip()
        return SM2Encryptor.encrypt_password(password, pubkey)


def main():
    """命令行入口函数"""
    import sys
    
    if len(sys.argv) < 3:
        print("使用方法:")
        print("  python sm2_encrypt.py <密码> <公钥>")
        print("  python sm2_encrypt.py <密码> <公钥文件>")
        print("\n示例:")
        print("  python sm2_encrypt.py 'mypassword' '04...'")
        print("  python sm2_encrypt.py 'mypassword' 'pubkey.pem'")
        return
    
    password = sys.argv[1]
    pubkey_input = sys.argv[2]
    
    try:
        # 尝试作为文件读取
        with open(pubkey_input, 'r', encoding='utf-8') as f:
            pubkey = f.read().strip()
        print(f"从文件读取公钥: {pubkey_input}")
    except FileNotFoundError:
        # 直接使用输入的公钥
        pubkey = pubkey_input
        print(f"使用输入的公钥: {pubkey[:50]}..." if len(pubkey) > 50 else f"使用输入的公钥: {pubkey}")
    
    try:
        encrypted = SM2Encryptor.encrypt_password(password, pubkey)
        print(f"\n加密结果:")
        print(encrypted)
        
        # 保存到文件
        output_file = "encrypted_password.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(encrypted)
        print(f"\n加密结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
