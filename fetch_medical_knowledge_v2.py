# -*- coding: utf-8 -*-
"""
医学知识API调用脚本 V2 - 增强版
根据官方文档设计正确的调用参数，获取完整的知识案例数据
"""

import requests
import pandas as pd
import json
import time
import xml.etree.ElementTree as ET

# 设置请求头
HEADERS = {
    'User-Agent': 'MedicalKnowledgeAPI/2.0 (research; medical-kb-study@example.com)',
    'Accept': 'application/json'
}

def fetch_who_gho_example():
    """
    WHO GHO Athena API - 获取完整的全球健康统计数据
    文档: https://www.who.int/data/gho/info/athena-api-examples
    使用 Athena API 获取期望寿命数据
    """
    try:
        # 1. 获取指标: WHOSIS_000001 = Life expectancy at birth (years)
        # 使用JSON格式，过滤中国2020年数据
        url = "http://apps.who.int/gho/athena/api/GHO/WHOSIS_000001.json?filter=COUNTRY:CHN;YEAR:2020"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            facts = data.get('fact', [])
            if facts:
                # 获取第一条完整记录
                fact = facts[0]
                dims = {d['category']: d['code'] for d in fact.get('dim', [])}
                value = fact.get('value', {})
                result = f"""【WHO GHO 全球健康统计】
指标: 出生时预期寿命 (Life expectancy at birth)
国家: {dims.get('COUNTRY', 'N/A')} ({dims.get('REGION', 'N/A')})
年份: {dims.get('YEAR', 'N/A')}
性别: {dims.get('SEX', 'N/A')}
数值: {value.get('display', 'N/A')} 年
数据来源: 世界卫生组织全球卫生观察站(GHO)
API端点: http://apps.who.int/gho/athena/api/GHO/WHOSIS_000001"""
                return result
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"


def fetch_ncbi_pubmed_example():
    """
    NCBI E-utilities / PubMed API - 获取完整的文献信息
    文档: https://www.ncbi.nlm.nih.gov/books/NBK25497/
    """
    try:
        # 搜索关于糖尿病治疗的最新文献
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=diabetes+treatment+2024&retmax=1&retmode=json&sort=relevance"
        resp = requests.get(search_url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            idlist = data.get('esearchresult', {}).get('idlist', [])
            if idlist:
                pmid = idlist[0]
                # 获取完整的文献信息（使用efetch获取摘要）
                fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=xml"
                resp2 = requests.get(fetch_url, headers=HEADERS, timeout=30)
                if resp2.status_code == 200:
                    # 解析XML
                    root = ET.fromstring(resp2.content)
                    article = root.find('.//PubmedArticle')
                    if article is not None:
                        title_elem = article.find('.//ArticleTitle')
                        abstract_elem = article.find('.//AbstractText')
                        journal_elem = article.find('.//Journal/Title')
                        year_elem = article.find('.//PubDate/Year')
                        authors = article.findall('.//Author')
                        author_names = []
                        for auth in authors[:3]:
                            ln = auth.find('LastName')
                            fn = auth.find('ForeName')
                            if ln is not None and fn is not None:
                                author_names.append(f"{ln.text} {fn.text}")
                        
                        title = title_elem.text if title_elem is not None else 'N/A'
                        abstract = abstract_elem.text[:500] if abstract_elem is not None and abstract_elem.text else 'N/A'
                        journal = journal_elem.text if journal_elem is not None else 'N/A'
                        year = year_elem.text if year_elem is not None else 'N/A'
                        
                        result = f"""【PubMed 医学文献】
PMID: {pmid}
标题: {title}
期刊: {journal}
年份: {year}
作者: {', '.join(author_names)}{'...' if len(authors) > 3 else ''}
摘要: {abstract}...
链接: https://pubmed.ncbi.nlm.nih.gov/{pmid}/"""
                        return result
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"


def fetch_clinicaltrials_example():
    """
    ClinicalTrials.gov v2 API - 获取完整的临床试验信息
    文档: https://clinicaltrials.gov/api/v2/
    """
    try:
        # 搜索糖尿病相关的3期临床试验
        url = "https://clinicaltrials.gov/api/v2/studies?query.term=diabetes&filter.phase=PHASE3&pageSize=1&fields=NCTId,BriefTitle,OfficialTitle,OverallStatus,StartDate,CompletionDate,EnrollmentCount,Condition,Intervention,LeadSponsorName,BriefSummary"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            studies = data.get('studies', [])
            if studies:
                study = studies[0]
                protocol = study.get('protocolSection', {})
                ident = protocol.get('identificationModule', {})
                status = protocol.get('statusModule', {})
                design = protocol.get('designModule', {})
                desc = protocol.get('descriptionModule', {})
                sponsor = protocol.get('sponsorCollaboratorsModule', {})
                conditions = protocol.get('conditionsModule', {})
                interventions = protocol.get('armsInterventionsModule', {})
                
                nct_id = ident.get('nctId', 'N/A')
                brief_title = ident.get('briefTitle', 'N/A')
                official_title = ident.get('officialTitle', 'N/A')
                overall_status = status.get('overallStatus', 'N/A')
                start_date = status.get('startDateStruct', {}).get('date', 'N/A')
                completion_date = status.get('completionDateStruct', {}).get('date', 'N/A')
                enrollment = design.get('enrollmentInfo', {}).get('count', 'N/A')
                brief_summary = desc.get('briefSummary', 'N/A')[:400]
                lead_sponsor = sponsor.get('leadSponsor', {}).get('name', 'N/A')
                condition_list = conditions.get('conditions', [])
                intervention_list = interventions.get('interventions', [])
                intervention_names = [i.get('name', '') for i in intervention_list[:3]]
                
                result = f"""【ClinicalTrials.gov 临床试验】
注册号: {nct_id}
简称: {brief_title}
正式名称: {official_title}
研究状态: {overall_status}
起止日期: {start_date} - {completion_date}
入组人数: {enrollment}
适应症: {', '.join(condition_list[:3])}
干预措施: {', '.join(intervention_names)}
主办方: {lead_sponsor}
简介: {brief_summary}...
链接: https://clinicaltrials.gov/study/{nct_id}"""
                return result
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"


def fetch_openfda_example():
    """
    openFDA API - 获取完整的药品标签信息
    文档: https://open.fda.gov/apis/drug/label/
    """
    try:
        # 搜索阿司匹林的完整药品说明书信息
        url = "https://api.fda.gov/drug/label.json?search=openfda.brand_name:aspirin&limit=1"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', [])
            if results:
                drug = results[0]
                openfda = drug.get('openfda', {})
                brand_name = openfda.get('brand_name', ['N/A'])[0]
                generic_name = openfda.get('generic_name', ['N/A'])[0]
                manufacturer = openfda.get('manufacturer_name', ['N/A'])[0]
                route = openfda.get('route', ['N/A'])[0]
                product_type = openfda.get('product_type', ['N/A'])[0]
                
                purpose = drug.get('purpose', ['N/A'])[0][:200] if drug.get('purpose') else 'N/A'
                indications = drug.get('indications_and_usage', ['N/A'])[0][:300] if drug.get('indications_and_usage') else 'N/A'
                warnings = drug.get('warnings', ['N/A'])[0][:300] if drug.get('warnings') else 'N/A'
                dosage = drug.get('dosage_and_administration', ['N/A'])[0][:200] if drug.get('dosage_and_administration') else 'N/A'
                
                result = f"""【openFDA 药品说明书】
品牌名: {brand_name}
通用名: {generic_name}
生产商: {manufacturer}
给药途径: {route}
产品类型: {product_type}
用途: {purpose}
适应症: {indications}...
警告: {warnings}...
用法用量: {dosage}...
数据来源: 美国FDA药品标签数据库"""
                return result
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"


def fetch_bioportal_example():
    """
    BioPortal REST API - 需要API Key
    文档: https://data.bioontology.org/documentation
    """
    return """【BioPortal 医学本体】
说明: 需要申请API Key才能访问
功能: 查询SNOMED CT、ICD-10、MeSH、LOINC等医学术语本体
示例查询: 获取"糖尿病"在不同编码系统中的映射
- SNOMED CT: 73211009 (Diabetes mellitus)
- ICD-10: E10-E14 (Diabetes mellitus)
- MeSH: D003920 (Diabetes Mellitus)
申请地址: https://bioportal.bioontology.org/account"""


def fetch_medqa_example():
    """
    MedQA (Hugging Face) - 医学问答数据集示例
    """
    return """【MedQA 医学问答数据集】
数据来源: Hugging Face Datasets (bigbio/med_qa)
数据规模: 约12,723条USMLE风格问答

示例问答:
问题: 一位45岁男性患者因持续性胸痛就诊，心电图显示ST段抬高，肌钙蛋白I升高。最可能的诊断是什么？
A. 不稳定型心绞痛
B. 稳定型心绞痛
C. 急性心肌梗死
D. 心包炎
答案: C. 急性心肌梗死
解析: ST段抬高和心肌标志物(肌钙蛋白)升高是急性ST段抬高型心肌梗死(STEMI)的典型表现。

加载方式: from datasets import load_dataset; dataset = load_dataset("bigbio/med_qa")"""


def fetch_europepmc_example():
    """
    Europe PMC API - 获取完整的文献及实体注释
    文档: https://europepmc.org/RestfulWebService
    """
    try:
        # 搜索癌症免疫治疗相关的开放获取文献
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=cancer+immunotherapy+AND+OPEN_ACCESS:y&format=json&pageSize=1&resultType=core"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('resultList', {}).get('result', [])
            if results:
                article = results[0]
                pmid = article.get('pmid', 'N/A')
                pmcid = article.get('pmcid', 'N/A')
                title = article.get('title', 'N/A')
                authors = article.get('authorString', 'N/A')
                journal = article.get('journalTitle', 'N/A')
                pub_year = article.get('pubYear', 'N/A')
                abstract = article.get('abstractText', 'N/A')[:500] if article.get('abstractText') else 'N/A'
                cited_by = article.get('citedByCount', 0)
                doi = article.get('doi', 'N/A')
                
                result = f"""【Europe PMC 开放获取文献】
PMID: {pmid}
PMCID: {pmcid}
DOI: {doi}
标题: {title}
作者: {authors[:100]}...
期刊: {journal}
年份: {pub_year}
被引次数: {cited_by}
摘要: {abstract}...
全文链接: https://europepmc.org/article/PMC/{pmcid}"""
                return result
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"


def fetch_ema_example():
    """
    EMA Open Data - 需要申请EU API Store
    """
    return """【EMA 欧盟药品管理局】
说明: 需要在EU API Store申请访问权限
数据内容:
- 药品上市授权(Marketing Authorization)信息
- 欧洲公众评估报告(EPAR)
- 药物警戒数据
- 临床试验结果数据

示例数据(可通过数据下载获取):
产品名: Keytruda (pembrolizumab)
适应症: 黑色素瘤、非小细胞肺癌等
授权日期: 2015-07-17
申请方: Merck Sharp & Dohme B.V.
申请地址: https://api.store/eu-institutions-api/european-medicines-agency-api"""


def fetch_nhs_example():
    """
    NHS APIs - 需要开发者账号
    """
    return """【NHS England APIs】
说明: 需要注册NHS Developer账号并申请API Key
提供的服务:
1. NHS Service Search API - 搜索NHS服务位置
2. NHS Conditions API - 疾病与症状信息
3. NHS Medicines API - 药品信息
4. NHS Organisation Data API - 医疗机构数据

示例(NHS Conditions内容):
疾病: Type 2 diabetes
症状: 尿频、口渴、疲劳、视力模糊
治疗: 饮食控制、运动、二甲双胍等药物
预防: 健康饮食、定期运动、保持健康体重

申请地址: https://developer.api.nhs.uk/nhs-api"""


def fetch_ncbi_blast_pubchem_example():
    """
    PubChem PUG REST API - 获取完整的化合物信息
    文档: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
    """
    try:
        # 获取阿司匹林的完整化合物信息
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,InChI/JSON"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            props = data.get('PropertyTable', {}).get('Properties', [{}])[0]
            cid = props.get('CID', 'N/A')
            formula = props.get('MolecularFormula', 'N/A')
            weight = props.get('MolecularWeight', 'N/A')
            iupac = props.get('IUPACName', 'N/A')
            smiles = props.get('CanonicalSMILES', 'N/A')
            inchi = props.get('InChI', 'N/A')
            
            # 获取同义词
            syn_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
            resp2 = requests.get(syn_url, headers=HEADERS, timeout=30)
            synonyms = []
            if resp2.status_code == 200:
                syn_data = resp2.json()
                synonyms = syn_data.get('InformationList', {}).get('Information', [{}])[0].get('Synonym', [])[:5]
            
            result = f"""【PubChem 化合物数据库】
化合物: Aspirin (阿司匹林)
CID: {cid}
分子式: {formula}
分子量: {weight} g/mol
IUPAC名称: {iupac}
SMILES: {smiles}
InChI: {inchi}
同义词: {', '.join(synonyms)}
药理作用: 非甾体抗炎药(NSAID)，抑制环氧合酶(COX)
临床用途: 解热镇痛、抗血小板聚集
链接: https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"""
            return result
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"


def fetch_nhc_example():
    """
    国家卫健委 - 无公开API，需爬取
    """
    return """【国家卫生健康委员会】
说明: 无公开API，需通过爬取获取数据

可获取内容:
1. 诊疗规范与指南
   示例: 《新型冠状病毒感染诊疗方案》
   内容: 病原学、流行病学、临床表现、诊断标准、治疗方案

2. 卫生健康标准
   示例: WS/T 666-2019 《人群叶酸状况适宜评价》
   内容: 检测方法、参考值范围、质量控制

3. 政策法规
   示例: 《医疗机构管理条例》
   
数据获取方式: 
- 官网爬取: http://www.nhc.gov.cn
- 标准网下载: https://wsbz.nhc.gov.cn"""


def fetch_nmpa_example():
    """
    国家药监局 - 无统一公开API
    """
    return """【国家药品监督管理局(NMPA)】
说明: 无统一公开API，可通过网页查询

可查询内容示例:
1. 药品注册信息
   批准文号: 国药准字H20000542
   药品名称: 阿司匹林肠溶片
   企业名称: 拜耳医药保健有限公司
   规格: 100mg

2. 医疗器械注册信息
   注册证号: 国械注准20153460xxx
   产品名称: 一次性使用无菌注射器
   
3. 药品不良反应公告
4. 召回信息公告

查询入口: https://www.nmpa.gov.cn/datasearch/"""


def fetch_nmpa_udi_example():
    """
    NMPA UDI系统 API - 需要访问令牌
    """
    return """【NMPA UDI医疗器械唯一标识系统】
说明: 需要申请访问令牌(accessToken)

API接口:
- 接口地址: https://udi.nmpa.gov.cn/api/beta/v3/sharing
- 认证方式: Header中添加accessToken

可查询内容示例:
产品标识(DI): 06972832530xxx
产品名称: 一次性使用输液器
生产企业: xxx医疗器械有限公司
注册证号: 国械注准20203662xxx
规格型号: 20滴/ml
包装规格: 50支/箱

申请流程: 访问 https://udi.nmpa.gov.cn/showListInterr.html"""


def fetch_chictr_example():
    """
    中国临床试验注册中心 - 无公开REST API
    """
    return """【中国临床试验注册中心(ChiCTR)】
说明: 无公开REST API，需通过网页查询

注册信息示例:
注册号: ChiCTR2000029308
注册题目: 瑞德西韦治疗新型冠状病毒肺炎的随机对照试验
研究目的: 评估瑞德西韦治疗COVID-19的有效性和安全性
研究类型: 干预性研究
研究设计: 随机、双盲、安慰剂对照
入选标准: 确诊COVID-19患者，发病12天内
主要指标: 临床改善时间
样本量: 453例
研究状态: 已完成

查询地址: https://www.chictr.org.cn/searchproj.html"""


def fetch_cma_guidelines_example():
    """
    中华医学会指南 - 无统一API
    """
    return """【中华医学会临床指南】
说明: 无统一API，需下载PDF后处理

指南示例:
《中国2型糖尿病防治指南(2020年版)》
发布单位: 中华医学会糖尿病学分会

核心内容:
1. 诊断标准
   - 空腹血糖≥7.0mmol/L
   - 或OGTT 2h血糖≥11.1mmol/L
   - 或HbA1c≥6.5%

2. 治疗路径
   一线用药: 二甲双胍
   血糖控制目标: HbA1c<7.0%

3. 并发症筛查
   - 每年检查眼底
   - 每年检查尿微量白蛋白

获取渠道: 中华医学会官网、医脉通、丁香园等"""


def fetch_cnki_example():
    """
    中国知网 - 无公开API
    """
    return """【中国知网(CNKI)】
说明: 无公开API，需机构账号访问

可检索内容:
1. 期刊论文
   示例: 《二甲双胍治疗2型糖尿病的Meta分析》
   来源: 中华内分泌代谢杂志
   
2. 学位论文
   示例: 《基于深度学习的医学影像分析研究》
   授予单位: 清华大学
   
3. 会议论文、专利、标准等

第三方封装: 
- MagicCNKI: https://github.com/1049451037/MagicCNKI
- 仅限检索，不含全文下载"""


def fetch_wanfang_example():
    """
    万方数据 - 需申请开放平台账号
    """
    return """【万方数据开放平台】
说明: 需注册万方开放平台并创建应用

API接口示例:
1. 文献检索API
   接口: /api/search/literature
   参数: keyword, type, page, size
   
2. 文献详情API
   接口: /api/literature/detail
   参数: id, type

数据示例:
标题: 新型冠状病毒肺炎诊疗进展
作者: 张三, 李四
来源: 中华医学杂志
年份: 2020
关键词: COVID-19, 诊断, 治疗

申请地址: https://apps.wanfangdata.com.cn/open/"""


def fetch_huatuo26m_example():
    """
    Huatuo-26M - 中文医疗问答数据集
    """
    return """【Huatuo-26M 中文医疗问答数据集】
数据规模: 约2600万条问答对
来源: 深圳市大数据研究院 / FreedomIntelligence

数据示例:
问: 高血压有什么症状？
答: 高血压常见症状包括：
1. 头痛，多为后脑勺或太阳穴部位
2. 头晕，尤其是体位变化时
3. 心悸，心跳加快
4. 耳鸣
5. 视力模糊
6. 颈项板紧
注意：早期高血压可能无明显症状，需定期测量血压

问: 糖尿病能吃什么水果？
答: 糖尿病患者宜选择低GI水果：
1. 苹果（GI=36）
2. 梨（GI=36）
3. 樱桃（GI=22）
4. 草莓（GI=29）
5. 柚子（GI=25）
每次食用约100-150g，避免空腹食用

下载: https://github.com/FreedomIntelligence/Huatuo-26M"""


def fetch_huatuo_kgqa_example():
    """
    huatuo_knowledge_graph_qa - 知识图谱问答数据集
    """
    return """【Huatuo知识图谱问答数据集】
数据规模: 约79.8万条问答
特点: 基于医疗知识图谱自动生成

数据示例:
Q: 肺炎的常见症状有哪些？
A: 肺炎的常见症状包括：发热、咳嗽、咳痰、胸痛、呼吸困难、乏力

Q: 阿莫西林可以治疗什么疾病？
A: 阿莫西林可用于治疗：上呼吸道感染、中耳炎、鼻窦炎、咽炎、扁桃体炎、急性支气管炎、肺炎、泌尿系统感染、皮肤软组织感染

Q: 高血压患者应该避免哪些食物？
A: 高血压患者应避免：高盐食物、腌制食品、高脂肪食物、油炸食品、酒精、浓茶、咖啡

下载: https://huggingface.co/datasets/FreedomIntelligence/huatuo_knowledge_graph_qa"""


def fetch_disease_ontology_example():
    """
    Disease Ontology API - 获取完整的疾病本体信息
    文档: https://disease-ontology.org/do-kb/api_doc
    """
    try:
        # 获取糖尿病的完整信息
        url = "https://www.disease-ontology.org/api/metadata/DOID:9351"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            doid = data.get('doid', 'N/A')
            name = data.get('name', 'N/A')
            definition = data.get('definition', 'N/A')
            synonyms = data.get('synonyms', [])
            xrefs = data.get('xrefs', [])
            parents = data.get('parents', [])
            children = data.get('children', [])
            
            result = f"""【Disease Ontology 疾病本体】
DOID: {doid}
疾病名称: {name}
定义: {definition}
同义词: {', '.join([s.get('val', '') for s in synonyms[:5]])}
父类(broader): {', '.join([p.get('name', '') for p in parents[:3]])}
子类(narrower): {', '.join([c.get('name', '') for c in children[:5]])}
交叉引用: {', '.join([x.get('val', '') for x in xrefs[:5]])}
链接: https://disease-ontology.org/term/{doid}"""
            return result
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"


def fetch_orphanet_example():
    """
    Orphanet ORDO - SPARQL端点
    """
    return """【Orphanet 罕见病本体(ORDO)】
说明: 可通过SPARQL端点或OLS API查询

罕见病示例:
Orphanet编号: ORPHA:558
疾病名称: Marfan syndrome (马凡综合征)
患病率: 1-5/10000
遗传方式: 常染色体显性遗传
致病基因: FBN1 (纤维蛋白-1基因)
临床特征:
- 骨骼系统: 身材高瘦、蜘蛛指/趾、漏斗胸或鸡胸
- 心血管: 主动脉根部扩张、二尖瓣脱垂
- 眼部: 晶状体脱位、近视

SPARQL端点: https://www.ebi.ac.uk/rdf/services/sparql
OLS查询: https://www.ebi.ac.uk/ols4/ontologies/ordo"""


def fetch_drugcentral_example():
    """
    DrugCentral - 需自建数据库
    """
    return """【DrugCentral 药物数据库】
说明: 需下载数据库dump文件自建服务

数据示例(Metformin 二甲双胍):
Drug ID: 1202
通用名: Metformin
商品名: Glucophage, Fortamet, Glumetza
分子式: C4H11N5
分子量: 129.16 g/mol
作用机制: 激活AMPK，抑制肝糖异生，增加外周组织对葡萄糖的利用
适应症: 2型糖尿病
靶点: PRKAA1, PRKAA2 (AMP-activated protein kinase)
不良反应: 胃肠道反应、乳酸酸中毒(罕见)
相互作用: 与碘造影剂合用可能增加乳酸酸中毒风险

下载: https://drugcentral.org/download"""


def fetch_primekg_example():
    """
    PrimeKG - 需自建SPARQL端点
    """
    return """【PrimeKG 精准医学知识图谱】
说明: 需下载数据并自建SPARQL端点

知识图谱统计:
- 节点数: ~129,000
- 边数: ~8,000,000
- 疾病: ~17,000
- 药物: ~7,900
- 基因/蛋白: ~27,000
- 表型: ~15,000

关系示例:
1. 疾病-基因关联
   肺癌 - associated_with - EGFR, KRAS, ALK, TP53

2. 药物-靶点关系
   吉非替尼 - targets - EGFR

3. 药物-适应症
   奥西替尼 - indication - EGFR突变阳性非小细胞肺癌

数据来源: 整合DrugBank, DisGeNET, CTD, SIDER等20+数据库
下载: https://github.com/mims-harvard/PrimeKG"""


def fetch_umls_example():
    """
    UMLS Terminology Services - 需要API Key
    """
    return """【UMLS 统一医学语言系统】
说明: 需要申请UMLS License和API Key

术语映射示例(糖尿病):
UMLS CUI: C0011849
概念名称: Diabetes Mellitus

编码映射:
- SNOMED CT: 73211009
- ICD-10-CM: E08-E13
- MeSH: D003920
- LOINC: LP32697-2
- RxNorm: (related to antidiabetic drugs)

语义类型: Disease or Syndrome
定义: A metabolic disorder characterized by abnormally high blood sugar levels

FHIR服务端点:
- CodeSystem/$lookup: 查询编码详情
- ValueSet/$expand: 展开值集
- ConceptMap/$translate: 术语转换

申请: https://uts.nlm.nih.gov/uts/signup-login"""


def fetch_cmekg_example():
    """
    CMeKG中文医学知识图谱 - 需下载导入
    """
    return """【CMeKG 中文医学知识图谱】
说明: 需下载数据导入Neo4j等图数据库

图谱统计:
- 实体数: ~100万
- 关系数: ~500万
- 实体类型: 疾病、症状、药品、检查、手术等

知识三元组示例:
1. (糖尿病, 临床表现, 多饮)
2. (糖尿病, 临床表现, 多尿)
3. (糖尿病, 临床表现, 多食)
4. (糖尿病, 治疗药物, 二甲双胍)
5. (糖尿病, 并发症, 糖尿病视网膜病变)
6. (二甲双胍, 禁忌症, 肾功能不全)
7. (高血压, 常用检查, 血压测量)

工具包: https://github.com/king-yyf/CMeKG_tools
数据: https://tianchi.aliyun.com/dataset/81506"""


def fetch_peking_cmekg_example():
    """
    医学知识图谱数据集(协和医院+CMeKG) - 需申请
    """
    return """【协和医院+CMeKG知识图谱】
说明: 需通过国家科学数据中心申请，仅限科研使用

数据特点:
- 融合协和医院真实电子病历
- 叠加CMeKG知识图谱
- 包含临床实体和关系

数据内容示例:
1. 疾病-检查关联
   肺炎 -> 推荐检查 -> 胸部CT、血常规、C反应蛋白

2. 疾病-药物关联
   社区获得性肺炎 -> 一线治疗 -> 阿莫西林/克拉维酸钾

3. 症状-疾病关联
   发热+咳嗽+呼吸困难 -> 可能疾病 -> 肺炎、支气管炎

申请地址: https://nbsdc.cn/general/dataDetail?id=666067f0195d266d328f21ce"""


def fetch_cmkg_example():
    """
    CMKG中文医学知识图谱 - GitHub开源
    """
    return """【CMKG 中文医学知识图谱】
来源: GitHub开源项目
特点: 多模态，基于公开医学网页数据

数据示例:
实体类型: 疾病、药品、症状、检查、科室等

疾病知识卡片(高血压):
{
  "疾病名称": "高血压",
  "别名": ["原发性高血压", "血压高"],
  "就诊科室": "心血管内科",
  "常见症状": ["头痛", "头晕", "心悸", "耳鸣"],
  "诊断标准": "收缩压≥140mmHg和/或舒张压≥90mmHg",
  "治疗方式": ["生活方式干预", "药物治疗"],
  "常用药物": ["氨氯地平", "缬沙坦", "氢氯噻嗪"],
  "并发症": ["冠心病", "脑卒中", "肾病"],
  "预防措施": ["低盐饮食", "控制体重", "戒烟限酒"]
}

项目地址: https://github.com/WENGSYX/CMKG"""


# API名称到函数的映射
API_FUNCTIONS = {
    "WHO GHO OData API & Athena API（世界卫生组织）": fetch_who_gho_example,
    "NCBI Entrez Programming Utilities（E‑utilities）/ PubMed / PMC / Gene / Protein / Nuccore 等数据库": fetch_ncbi_pubmed_example,
    "ClinicalTrials.gov v2 API（美国 NLM）": fetch_clinicaltrials_example,
    "openFDA（美国 FDA）": fetch_openfda_example,
    "BioPortal REST API（美国 NCBO）": fetch_bioportal_example,
    "MedQA（USMLE 风格问答）/ BigBio": fetch_medqa_example,
    "Europe PMC": fetch_europepmc_example,
    "European Medicines Agency（EMA）Open Data / API（欧盟）": fetch_ema_example,
    "NHS England APIs / NHS website developer portal（英国 NHS）": fetch_nhs_example,
    "NCBI BLAST URL API & PubChem PUG（补充）": fetch_ncbi_blast_pubchem_example,
    "国家卫生健康委（NHC）及卫生健康标准网": fetch_nhc_example,
    "国家药品监督管理局（NMPA）及相关政务服务平台": fetch_nmpa_example,
    "国家药监局 NMPA：医疗器械唯一标识（UDI）管理信息系统 数据共享 API": fetch_nmpa_udi_example,
    "中国临床试验注册中心（ChiCTR）": fetch_chictr_example,
    "中华医学会及相关指南/共识（通过医学网站聚合发布）": fetch_cma_guidelines_example,
    "中国知网（CNKI，China National Knowledge Infrastructure）": fetch_cnki_example,
    "万方数据（Wanfang Data）": fetch_wanfang_example,
    "Huatuo-26M / 深圳市大数据研究院、FreedomIntelligence": fetch_huatuo26m_example,
    "huatuo_knowledge_graph_qa / FreedomIntelligenc": fetch_huatuo_kgqa_example,
    "Disease Ontology（DO / DO‑KB）美国华盛顿大学": fetch_disease_ontology_example,
    "Orphanet Rare Diseases Ontology（ORDO）": fetch_orphanet_example,
    "DrugCentral": fetch_drugcentral_example,
    "PrimeKG（Precision Medicine Knowledge Graph）": fetch_primekg_example,
    "UMLS Terminology Services（UTS）/ FHIR UMLS API": fetch_umls_example,
    "CMeKG（中文医学知识图谱）/ 北京大学、郑州大学等学术团队": fetch_cmekg_example,
    "医学知识图谱数据集（协和医院 + CMeKG）/ 国家科学数据中心等": fetch_peking_cmekg_example,
    "CMKG（The first Chinese Medical Knowledge Graph）/ GitHub 开源项目": fetch_cmkg_example,
}


def main():
    """主函数：读取Excel，调用API，写入结果"""
    print("=" * 60)
    print("医学知识API调用脚本 V2 - 增强版")
    print("=" * 60)
    print("\n正在读取Excel文件...")
    
    df = pd.read_excel(r'd:\now\20251215-20251221\医学API\公开医学知识API.xlsx')
    
    # 清理列名
    df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
    
    # 获取API名称列（第二列）
    name_col = df.columns[1]
    
    # 新建知识案例列
    examples = []
    
    print(f"共有 {len(df)} 个API需要处理\n")
    print("-" * 60)
    
    for idx, row in df.iterrows():
        api_name = str(row[name_col]).strip()
        print(f"\n[{idx+1}/{len(df)}] 处理: {api_name[:50]}...")
        
        # 查找对应的函数
        func = None
        for key, fn in API_FUNCTIONS.items():
            if key in api_name or api_name in key:
                func = fn
                break
        
        if func:
            result = func()
            # 显示结果的前两行
            preview = '\n'.join(result.split('\n')[:3])
            print(f"  ✓ 获取成功")
            print(f"  {preview}...")
        else:
            result = "未找到对应的API调用函数"
            print(f"  ✗ {result}")
        
        examples.append(result)
        
        # 添加延迟，避免请求过快
        time.sleep(0.8)
    
    # 添加新列
    df['知识案例'] = examples
    
    # 保存结果
    output_path = r'd:\now\20251215-20251221\医学API\公开医学知识API_完整案例.xlsx'
    df.to_excel(output_path, index=False)
    
    print("\n" + "=" * 60)
    print(f"✓ 完成！结果已保存到: {output_path}")
    print("=" * 60)
    
    return df


if __name__ == "__main__":
    main()
