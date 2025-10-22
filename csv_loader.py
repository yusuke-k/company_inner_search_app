"""
CSVファイル用のカスタムローダー
社員名簿CSVファイルを1つのドキュメントとして読み込み、検索精度を向上させる
"""

import pandas as pd
from langchain.schema import Document


def custom_csv_loader(path):
    """
    CSVファイルを統合ドキュメントとして読み込むカスタムローダー
    検索精度向上のため、全社員情報を統合しつつ、検索しやすい形式で整理
    """
    # CSVファイルを読み込み
    df = pd.read_csv(path, encoding="utf-8")
    
    # 部署別に社員をグループ化
    dept_groups = df.groupby('部署')
    
    # 統合ドキュメントの内容を構築
    integrated_content = f"""
社員名簿データベース

総社員数: {len(df)}名

"""
    
    # 部署別統計情報を追加
    integrated_content += "部署別統計:\n"
    dept_stats = df['部署'].value_counts()
    for dept, count in dept_stats.items():
        integrated_content += f"- {dept}: {count}名\n"
    
    integrated_content += "\n役職別統計:\n"
    position_stats = df['役職'].value_counts()
    for position, count in position_stats.items():
        integrated_content += f"- {position}: {count}名\n"
    
    integrated_content += "\n従業員区分別統計:\n"
    type_stats = df['従業員区分'].value_counts()
    for emp_type, count in type_stats.items():
        integrated_content += f"- {emp_type}: {count}名\n"
    
    # 部署別の詳細情報を追加
    for dept_name, dept_df in dept_groups:
        integrated_content += f"\n\n=== {dept_name} ({len(dept_df)}名) ===\n"
        
        for _, row in dept_df.iterrows():
            # 検索しやすい形式で社員情報を記述
            employee_entry = f"""
【{row['氏名（フルネーム）']}】
社員ID: {row['社員ID']}
氏名: {row['氏名（フルネーム）']}
性別: {row['性別']}
年齢: {row['年齢']}歳
部署: {row['部署']}
役職: {row['役職']}
従業員区分: {row['従業員区分']}
入社日: {row['入社日']}
スキルセット: {row['スキルセット']}
保有資格: {row['保有資格']}
大学名: {row['大学名']}
学部・学科: {row['学部・学科']}
卒業年月日: {row['卒業年月日']}
メールアドレス: {row['メールアドレス']}

検索キーワード: {row['氏名（フルネーム）']} {row['部署']} {row['役職']} {row['スキルセット']} {row['保有資格']} {row['大学名']} {row['従業員区分']}
-----------------------------------
"""
            integrated_content += employee_entry
    
    # 検索精度向上のための追加セクション
    integrated_content += "\n\n=== 検索用キーワード一覧 ===\n"
    
    # 全社員の氏名一覧
    integrated_content += "\n全社員氏名一覧:\n"
    for _, row in df.iterrows():
        integrated_content += f"- {row['氏名（フルネーム）']} ({row['部署']}, {row['役職']})\n"
    
    # スキル別の社員一覧
    integrated_content += "\nスキル別社員一覧:\n"
    all_skills = set()
    for skills in df['スキルセット'].dropna():
        skill_list = [skill.strip() for skill in str(skills).split(',')]
        all_skills.update(skill_list)
    
    for skill in sorted(all_skills):
        skill_employees = df[df['スキルセット'].str.contains(skill, na=False)]
        if len(skill_employees) > 0:
            employee_names = [f"{row['氏名（フルネーム）']} ({row['部署']})" for _, row in skill_employees.iterrows()]
            integrated_content += f"\n{skill}: {', '.join(employee_names)}\n"
    
    # 資格別の社員一覧
    integrated_content += "\n資格別社員一覧:\n"
    all_qualifications = set()
    for quals in df['保有資格'].dropna():
        qual_list = [qual.strip() for qual in str(quals).split(',')]
        all_qualifications.update(qual_list)
    
    for qualification in sorted(all_qualifications):
        qual_employees = df[df['保有資格'].str.contains(qualification, na=False)]
        if len(qual_employees) > 0:
            employee_names = [f"{row['氏名（フルネーム）']} ({row['部署']})" for _, row in qual_employees.iterrows()]
            integrated_content += f"\n{qualification}: {', '.join(employee_names)}\n"
    
    # 大学別の社員一覧
    integrated_content += "\n大学別社員一覧:\n"
    university_stats = df['大学名'].value_counts()
    for university, count in university_stats.items():
        university_employees = df[df['大学名'] == university]
        employee_names = [f"{row['氏名（フルネーム）']} ({row['部署']})" for _, row in university_employees.iterrows()]
        integrated_content += f"\n{university} ({count}名): {', '.join(employee_names)}\n"
    
    # Documentオブジェクトを作成
    return [Document(
        page_content=integrated_content, 
        metadata={
            "source": path,
            "total_employees": len(df),
            "departments": ", ".join(dept_stats.index),
            "employee_types": ", ".join(type_stats.index)
        }
    )]
