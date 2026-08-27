# 用户画像分析框架

## 概述

本框架定义了用户画像的分析维度、计算公式和洞察生成逻辑。

---

## 用户画像公式

### 核心公式

```
用户画像得分 = (人口统计学特征 × 3) + (行为偏好 × 2) + (内容偏好 × 1.5) + (地域特征 × 1)
```

### 维度说明

| 维度 | 权重 | 说明 |
|------|------|------|
| 人口统计学特征 | 3 | 年龄、性别、地域等基础属性 |
| 行为偏好 | 2 | 搜索行为、互动行为 |
| 内容偏好 | 1.5 | 内容类型、话题标签偏好 |
| 地域特征 | 1 | 地域分布、城市级别 |

---

## 分析维度

### 1. 年龄分布分析

#### 年龄段划分
```
18-24岁: Z世代，学生/职场新人
25-30岁: 职场青年，消费主力
31-35岁: 职场中坚，家庭阶段
36-40岁: 职场资深，稳定阶段
40+岁: 资深用户，决策层
```

#### 核心年龄段识别
```python
def identify_primary_age(age_distribution):
    max_percentage = max(age_distribution.values())
    primary_age_groups = [
        age for age, pct in age_distribution.items()
        if pct >= max_percentage * 0.8  # 相差不超过 20%
    ]
    return primary_age_groups
```

#### 年龄与内容偏好关联
```
18-24岁 → 娱乐、二次元、游戏
25-30岁 → 职场、情感、生活方式
31-35岁 → 育儿、理财、健康
36-40岁 → 管理、投资、教育
40+岁 → 养生、旅游、时事
```

### 2. 性别分布分析

#### 性别比例判断
```
男性为主: male > 60%
女性为主: female > 60%
相对均衡: 40% <= male <= 60%
```

#### 性别与内容偏好关联
```
男性 → 科技、汽车、财经、体育
女性 → 美妆、时尚、育儿、情感
均衡 → 职场、教育、健康、生活
```

### 3. 地域分布分析

#### 城市级别划分
```
一线城市: 北京、上海、广州、深圳
新一线: 成都、杭州、重庆等15城
二线城市: 30个省会城市及计划单列市
三线城市: 地级市
四线及以下: 县级及以下
```

#### 地域渗透率计算
```
一线城市渗透率 = TOP4 城市占比总和
核心区域集中度 = TOP5 省份占比总和
```

#### 地域与消费能力关联
```
一线城市 → 高消费、快节奏、品质导向
新一线 → 较高消费、生活品质、成长性
二线城市 → 中等消费、性价比、实用主义
三线及以下 → 价格敏感、口碑传播
```

---

## 核心用户群识别

### 识别逻辑

```python
def extract_core_persona(persona_data):
    """
    提取核心用户群
    """
    demographics = persona_data['demographics']

    # 1. 主要年龄段（占比最高的）
    primary_age = max(
        demographics['age'].items(),
        key=lambda x: x[1]
    )[0]

    # 2. 性别主导
    gender_dominant = (
        'male' if demographics['gender']['male'] > 0.6 else
        'female' if demographics['gender']['female'] > 0.6 else
        'balanced'
    )

    # 3. 核心地域（TOP 3）
    top_regions = [
        r['region'] for r in demographics['region'][:3]
    ]

    # 4. 城市级别分布
    city_tier_distribution = calculate_city_tier(
        demographics['region']
    )

    return {
        'primary_age': primary_age,
        'gender_dominant': gender_dominant,
        'top_regions': top_regions,
        'city_tier_distribution': city_tier_distribution,
        'user_profile': generate_profile_description(
            primary_age, gender_dominant, top_regions
        )
    }

def generate_profile_description(age, gender, regions):
    """生成用户画像描述"""
    age_desc = {
        '18-24': 'Z世代年轻用户',
        '25-30': '职场青年群体',
        '31-35': '职场中坚力量',
        '36-40': '资深职场人士',
        '40+': '成熟决策群体'
    }

    gender_desc = {
        'male': '男性为主',
        'female': '女性为主',
        'balanced': '性别均衡'
    }

    region_str = '、'.join(regions[:2])

    return (
        f"{age_desc.get(age, '')}，"
        f"{gender_desc.get(gender, '')}，"
        f"主要集中在{region_str}等地区"
    )
```

---

## 洞察生成规则

### 年龄洞察

```python
def generate_age_insights(age_distribution):
    insights = []

    # 判断主要年龄段
    max_age = max(age_distribution.items(), key=lambda x: x[1])
    insights.append(
        f"核心用户群为 {max_age[0]} 岁，占比 {max_age[1]*100:.1f}%"
    )

    # 判断用户成熟度
    young_pct = age_distribution.get('18-24', 0)
    mature_pct = (
        age_distribution.get('36-40', 0) +
        age_distribution.get('40+', 0)
    )

    if young_pct > 0.4:
        insights.append("用户群体偏年轻，内容应注重视觉化和趣味性")
    elif mature_pct > 0.3:
        insights.append("用户群体较成熟，内容应注重专业性和深度")

    return insights
```

### 地域洞察

```python
def generate_region_insights(region_distribution):
    insights = []

    # 计算一线城市占比
    tier_1_regions = ['北京', '上海', '广州', '深圳']
    tier_1_pct = sum(
        r['percentage'] for r in region_distribution
        if r['region'] in tier_1_regions
    )

    if tier_1_pct > 0.5:
        insights.append(
            f"一线城市用户占比高达 {tier_1_pct*100:.1f}%，"
            "用户消费能力强，可推荐高客单价产品"
        )

    # 判断地域集中度
    top_3_pct = sum(r['percentage'] for r in region_distribution[:3])
    if top_3_pct > 0.5:
        insights.append(
            f"TOP3 地域占比 {top_3_pct*100:.1f}%，"
            "用户地域高度集中，可进行区域化营销"
        )

    return insights
```

---

## 内容策略建议生成

### 基于年龄的内容策略

```python
def get_content_strategy_by_age(primary_age):
    strategies = {
        '18-24': {
            'tone': '轻松、幽默、互动性强',
            'format': '短视频、图文、表情包',
            'topics': ['娱乐', '二次元', '游戏', '潮流'],
            'length': '短视频<30秒，图文<500字',
            'platforms': ['抖音', 'B站', '小红书'],
            'keywords': ['好看', '有趣', '推荐', '必看']
        },
        '25-30': {
            'tone': '共鸣、实用、有态度',
            'format': '中长视频、深度图文',
            'topics': ['职场', '情感', '生活方式', '个人成长'],
            'length': '视频3-5分钟，图文800-1500字',
            'platforms': ['知乎', '公众号', 'B站'],
            'keywords': ['干货', '分享', '经验', '指南']
        },
        '31-35': {
            'tone': '专业、理性、有价值',
            'format': '深度图文、课程、直播',
            'topics': ['育儿', '理财', '健康', '职业发展'],
            'length': '视频5-10分钟，图文1500-3000字',
            'platforms': ['公众号', '知乎', '得到'],
            'keywords': ['方法', '技巧', '攻略', '解析']
        },
        '36-40': {
            'tone': '权威、深度、有洞见',
            'format': '深度文章、案例分析',
            'topics': ['管理', '投资', '教育', '行业洞察'],
            'length': '视频10-20分钟，图文3000字以上',
            'platforms': ['公众号', '知乎', '领英'],
            'keywords': ['趋势', '分析', '研究', '报告']
        },
        '40+': {
            'tone': '稳重、可信、有温度',
            'format': '长文、音频、视频',
            'topics': ['养生', '旅游', '时事', '家庭'],
            'length': '灵活，注重质量',
            'platforms': ['公众号', '今日头条', '音频平台'],
            'keywords': ['健康', '享受', '品质', '生活']
        }
    }
    return strategies.get(primary_age, strategies['25-30'])
```

### 基于地域的平台策略

```python
def get_platform_strategy_by_region(top_regions):
    """
    根据地域分布推荐平台策略
    """
    # 一线城市用户偏好的平台
    tier_1_platforms = {
        '知识类': ['知乎', 'B站', '公众号'],
        '职场类': ['领英', '脉脉', '知乎'],
        '生活类': ['小红书', '大众点评'],
    }

    # 二三线城市用户偏好的平台
    tier_23_platforms = {
        '生活类': ['快手', '抖音'],
        '资讯类': ['今日头条', '腾讯新闻'],
        '社交类': ['微信', 'QQ'],
    }

    # 根据地域分布推荐
    tier_1_pct = calculate_tier_1_percentage(top_regions)

    if tier_1_pct > 0.6:
        return tier_1_platforms
    else:
        # 综合推荐
        return {**tier_1_platforms, **tier_23_platforms}
```

---

## 数据解读指南

### 年龄分布解读

#### 集中分布（某年龄段 >60%）
- **特征**：用户群体特征明显
- **策略**：专注该年龄段需求，精准投放
- **风险**：受众范围窄，增长受限

#### 分散分布（最大占比 <40%）
- **特征**：用户群体多元化
- **策略**：分层运营，满足不同需求
- **机会**：受众范围广，增长潜力大

### 性别分布解读

#### 明确偏向（某性别 >70%）
- **特征**：性别偏好强烈
- **策略**：内容风格明确调整
- **注意**：避免刻板印象

#### 相对均衡（40%-60%）
- **特征**：性别差异不大
- **策略**：保持中性风格
- **机会**：覆盖面更广

### 地域分布解读

#### 高度集中（TOP3 >50%）
- **特征**：地域性强
- **策略**：区域化营销，本地化内容
- **风险**：地域扩张困难

#### 广泛分布（TOP3 <30%）
- **特征**：全国性分布
- **策略**：全国统一策略
- **机会**：规模化扩张

---

## 常见分析场景

### 场景 1：新产品定位
```
输入：产品关键词
分析：目标用户画像
输出：产品定位建议
```

### 场景 2：内容创作
```
输入：内容主题关键词
分析：受众特征
输出：内容策略建议
```

### 场景 3：广告投放
```
输入：广告关键词
分析：目标受众
输出：投放平台和地域建议
```

### 场景 4：竞品分析
```
输入：竞品关键词
分析：竞品用户画像
输出：差异化策略
```

---

## 注意事项

1. **数据时效性**：用户画像会随时间变化，建议定期更新
2. **样本偏差**：不同数据源的用户群体可能有偏差
3. **业务结合**：画像分析需结合实际业务场景
4. **避免刻板印象**：画像仅供参考，避免过度标签化
5. **持续优化**：根据效果反馈不断优化分析策略
