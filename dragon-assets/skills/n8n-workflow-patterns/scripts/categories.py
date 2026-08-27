#!/usr/bin/env python3
"""
n8n Categories Index
列出所有188个n8n集成类别
"""

import sqlite3
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
DB_PATH = SCRIPT_DIR / "index.db"


def list_categories():
    """列出所有分类"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
    SELECT category, COUNT(*) as count
    FROM workflows
    GROUP BY category
    ORDER BY count DESC
    """)

    results = cursor.fetchall()
    conn.close()

    return results


def main():
    categories = list_categories()

    print("\n=== n8n Workflow Categories (188个集成类别) ===\n")

    # 分组显示
    groups = {
        'Communication & Messaging': [],
        'CRM & Sales': [],
        'Database & Storage': [],
        'Marketing & Forms': [],
        'AI & Analytics': [],
        'DevOps & Development': [],
        'Finance & E-commerce': [],
        'Triggers & Automation': [],
        'Other': []
    }

    comm_tools = {'slack', 'telegram', 'discord', 'email', 'gmail', 'twilio', 'whatsapp', 'mattermost', 'mailchimp', 'mailerlite'}
    crm_tools = {'hubspot', 'salesforce', 'jira', 'pipedrive', 'zoho', 'activecampaign', 'affinity', 'copper'}
    db_tools = {'postgresql', 'mysql', 'mongodb', 'supabase', 'googlesheets', 's3', 'elasticsearch', 'grist'}
    mkt_tools = {'mailchimp', 'typeform', 'facebook', 'figma', 'jotform', 'woocommerce', 'shopify'}
    ai_tools = {'openai', 'googleanalytics', 'bigquery', 'posthog', 'coingecko'}
    devops_tools = {'github', 'gitlab', 'netlify', 'docker', 'http', 'code', 'bitbucket'}
    finance_tools = {'paypal', 'shopify', 'woocommerce', 'stripe', 'quickbooks'}
    trigger_tools = {'webhook', 'cron', 'schedule', 'form', 'manual', 'rss'}

    for cat, count in categories:
        cat_lower = cat.lower()
        if any(t in cat_lower for t in comm_tools):
            groups['Communication & Messaging'].append((cat, count))
        elif any(t in cat_lower for t in crm_tools):
            groups['CRM & Sales'].append((cat, count))
        elif any(t in cat_lower for t in db_tools):
            groups['Database & Storage'].append((cat, count))
        elif any(t in cat_lower for t in mkt_tools):
            groups['Marketing & Forms'].append((cat, count))
        elif any(t in cat_lower for t in ai_tools):
            groups['AI & Analytics'].append((cat, count))
        elif any(t in cat_lower for t in devops_tools):
            groups['DevOps & Development'].append((cat, count))
        elif any(t in cat_lower for t in finance_tools):
            groups['Finance & E-commerce'].append((cat, count))
        elif any(t in cat_lower for t in trigger_tools):
            groups['Triggers & Automation'].append((cat, count))
        else:
            groups['Other'].append((cat, count))

    for group_name, items in groups.items():
        if items:
            print(f"\n📁 {group_name} ({len(items)}个)")
            print("-" * 50)
            for name, count in sorted(items, key=lambda x: -x[1]):
                print(f"   {name:<30} {count:>4} workflows")


if __name__ == "__main__":
    main()