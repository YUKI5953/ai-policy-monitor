# main.py
import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header

# 1. 配置参数（这些值会在GitHub Actions中自动替换，无需手动修改）
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
EMAIL_SENDER = os.getenv('EMAIL_SENDER') # 发送方邮箱
EMAIL_AUTH_CODE = os.getenv('EMAIL_AUTH_CODE') # 邮箱SMTP授权码
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER') # 接收方邮箱
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.qq.com') # SMTP服务器

# 2. 定义搜索关键词和站点
search_queries = [
    '"人工智能" site:gov.cn', # 政府网站中带“人工智能”的内容
    '"AI" site:gov.cn',
    '"智能产业" site:gov.cn',
    '"AI补贴"',
    '"人工智能项目申报"'
]

def search_news(query):
    """模拟搜索（这是一个示例，实际应用中你可能需要调用Serper或Bing的API）"""
    # 这里是模拟数据，因为你没有Serper API。
    # 假设我们搜索到了一些结果。
    print(f"正在模拟搜索: {query}")
    mock_results = [
        {
            "title": "关于支持人工智能产业发展的若干政策措施（模拟数据）",
            "link": "https://www.example.gov.cn/2024/05/ai-policy.html",
            "snippet": "为促进本市人工智能产业发展，经研究，制定以下补贴和政策支持...（此为模拟数据，仅用于演示）"
        },
        {
            "title": "2024年度人工智能项目申报指南通知（模拟数据）",
            "link": "https://www.example.gov.cn/2024/05/ai-project-apply.html",
            "snippet": "现将开展2024年度人工智能技术攻关项目申报工作，具体通知如下...（此为模拟数据，仅用于演示）"
        }
    ]
    return mock_results

def is_relevant_with_ai(text, deepseek_api_key):
    """调用DeepSeek API判断信息是否相关"""
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {deepseek_api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    请严格判断以下文本是否属于‘人工智能国家或地方政策’、‘人工智能项目补贴通知’或‘重要人工智能项目新闻’。
    只需回答“是”或“否”。

    文本内容：
    「{text}」
    """

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1  # 低温度，让输出更确定
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        ai_judgment = result['choices'][0]['message']['content'].strip()
        print(f"AI判断结果: {ai_judgment}")
        return "是" in ai_judgment
    except Exception as e:
        print(f"调用DeepSeek API时出错: {e}")
        return False # 如果API调用失败，保守地返回False

def send_email(content, receiver):
    """发送邮件"""
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header(f'AI政策监控机器人 <{EMAIL_SENDER}>', 'utf-8')
    message['To'] = Header(receiver, 'utf-8')
    message['Subject'] = Header('【每日AI政策与项目动态】', 'utf-8')

    try:
        smtp_obj = smtplib.SMTP_SSL(SMTP_SERVER, 465)
        smtp_obj.login(EMAIL_SENDER, EMAIL_AUTH_CODE)
        smtp_obj.sendmail(EMAIL_SENDER, [receiver], message.as_string())
        smtp_obj.quit()
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")

def main():
    """主函数"""
    print("开始执行AI政策监控任务...")
    all_relevant_news = []

    # 遍历所有搜索查询
    for query in search_queries:
        print(f"\n--- 执行搜索: '{query}' ---")
        results = search_news(query)
        for item in results:
            # 组合文本用于AI判断
            text_to_judge = f"{item['title']} {item['snippet']}"
            print(f"正在判断: {item['title']}")

            # 调用AI进行判断
            if is_relevant_with_ai(text_to_judge, DEEPSEEK_API_KEY):
                print("✅ 相关！已添加到列表。")
                all_relevant_news.append(item)
            else:
                print("❌ 不相关，跳过。")

    # 准备邮件内容
    if all_relevant_news:
        email_content = "今日监测到的相关AI政策、补贴及项目信息：\n\n"
        for index, news in enumerate(all_relevant_news, 1):
            email_content += f"{index}. 【{news['title']}】\n"
            email_content += f"   摘要: {news['snippet']}\n"
            email_content += f"   链接: {news['link']}\n\n"
    else:
        email_content = "今日未监测到相关的AI政策、补贴或项目信息。"

    print(f"\n最终邮件内容:\n{email_content}")
    # 发送邮件
    send_email(email_content, EMAIL_RECEIVER)

if __name__ == '__main__':
    main()
