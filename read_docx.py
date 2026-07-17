import docx
import json

def read_docx(file_path):
    """读取DOCX文档并返回段落内容列表"""
    doc = docx.Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs]
    return paragraphs

def main():
    file_path = r"d:\autotrace\traceai\docs\930接口文档.docx"
    content = read_docx(file_path)
    
    # 保存内容到JSON文件
    output_path = r"d:\autotrace\traceai\docs\api_doc_content.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    print(f"文档内容已保存到: {output_path}")
    # 打印前20个段落的内容
    print("\n文档前20个段落内容:")
    for i, para in enumerate(content[:20]):
        print(f"{i+1}. {para}")

if __name__ == "__main__":
    main()