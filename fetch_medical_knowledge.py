# -*- coding: utf-8 -*-
"""
医学知识API调用脚本
从各个公开医学API获取实际的知识案例数据
"""

import requests
import pandas as pd
import json
import time
from urllib.parse import quote

# 设置请求头，遵循API使用政策
HEADERS = {
    'User-Agent': 'MedicalKnowledgeAPI/1.0 (research; contact@example.com)',
    'Accept': 'application/json'
}

def fetch_who_gho_example():
    """
    WHO GHO OData API - 获取全球健康统计数据示例
    https://www.who.int/data/gho/info/gho-odata-api
    """
    try:
        # 获取HIV新感染病例指标数据
        url = "https://ghoapi.azureedge.net/api/HIV_0000000001?$top=5"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if 'value' in data and len(data['value']) > 0:
                item = data['value'][0]
                return f"WHO GHO示例 - HIV新感染数据: 国家={item.get('SpatialDim', 'N/A')}, 年份={item.get('TimeDim', 'N/A')}, 数值={item.get('NumericValue', 'N/A')}"
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"

def fetch_ncbi_pubmed_example():
    """
    NCBI E-utilities / PubMed API - 获取生物医学文献示例
    https://www.ncbi.nlm.nih.gov/home/develop/api/
    """
    try:
        # 搜索关于COVID-19的文献
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=COVID-19+vaccine&retmax=1&retmode=json"
        resp = requests.get(search_url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                pmid = data['esearchresult']['idlist'][0] if data['esearchresult']['idlist'] else None
                if pmid:
                    # 获取文献摘要
                    summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
                    resp2 = requests.get(summary_url, headers=HEADERS, timeout=30)
                    if resp2.status_code == 200:
                        summary = resp2.json()
                        result = summary.get('result', {})
                        if pmid in result:
                            article = result[pmid]
                            title = article.get('title', 'N/A')[:100]
                            return f"PubMed示例 - PMID:{pmid}, 标题: {title}..."
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"

def fetch_clinicaltrials_example():
    """
    ClinicalTrials.gov v2 API - 获取临床试验信息示例
    https://clinicaltrials.gov/api/v2/studies
    """
    try:
        url = "https://clinicaltrials.gov/api/v2/studies?query.term=diabetes&pageSize=1"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if 'studies' in data and len(data['studies']) > 0:
                study = data['studies'][0]
                protocol = study.get('protocolSection', {})
                identification = protocol.get('identificationModule', {})
                nct_id = identification.get('nctId', 'N/A')
                title = identification.get('briefTitle', 'N/A')[:80]
                return f"ClinicalTrials示例 - {nct_id}: {title}..."
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"

def fetch_openfda_example():
    """
    openFDA API - 获取药品标签信息示例
    https://open.fda.gov/apis/
    """
    try:
        url = "https://api.fda.gov/drug/label.json?search=aspirin&limit=1"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if 'results' in data and len(data['results']) > 0:
                drug = data['results'][0]
                brand_name = drug.get('openfda', {}).get('brand_name', ['N/A'])[0]
                purpose = drug.get('purpose', ['N/A'])[0][:100] if drug.get('purpose') else 'N/A'
                return f"openFDA示例 - 药品: {brand_name}, 用途: {purpose}..."
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"

def fetch_bioportal_example():
    """
    BioPortal REST API - 需要API Key，返回示例说明
    """
    return "需要API Key - 可查询SNOMED CT、ICD、MeSH等医学本体概念与映射关系"

def fetch_medqa_example():
    """
    MedQA (Hugging Face) - 数据集下载，返回示例说明
    """
    return "Hugging Face数据集 - 包含USMLE风格医学问答，如：'哪种药物可用于治疗社区获得性肺炎？' 选项:A.阿莫西林, B.万古霉素..."

def fetch_europepmc_example():
    """
    Europe PMC API - 获取生命科学文献示例
    https://europepmc.org/RestfulWebService
    """
    try:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=cancer%20therapy&format=json&pageSize=1"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if 'resultList' in data and 'result' in data['resultList']:
                results = data['resultList']['result']
                if results:
                    article = results[0]
                    pmid = article.get('pmid', 'N/A')
                    title = article.get('title', 'N/A')[:80]
                    return f"Europe PMC示例 - PMID:{pmid}, 标题: {title}..."
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"

def fetch_ema_example():
    """
    EMA Open Data - 需要申请，返回示例说明
    """
    return "需EU API Store申请 - 提供欧盟药品上市授权、EPAR评估报告等数据"

def fetch_nhs_example():
    """
    NHS APIs - 需要开发者账号，返回示例说明
    """
    return "需NHS开发者账号 - 提供NHS健康内容、疾病症状、药品信息、服务目录等"

def fetch_ncbi_blast_pubchem_example():
    """
    NCBI BLAST & PubChem - 返回示例说明
    """
    try:
        # PubChem简单查询示例
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/property/MolecularFormula,MolecularWeight/JSON"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if 'PropertyTable' in data and 'Properties' in data['PropertyTable']:
                props = data['PropertyTable']['Properties'][0]
                formula = props.get('MolecularFormula', 'N/A')
                weight = props.get('MolecularWeight', 'N/A')
                return f"PubChem示例 - 阿司匹林: 分子式={formula}, 分子量={weight}"
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"

def fetch_nhc_example():
    """
    国家卫健委 - 无公开API，需爬取
    """
    return "无公开API - 可通过爬取获取卫生健康政策文件、诊疗规范、诊断标准等"

def fetch_nmpa_example():
    """
    国家药监局 - 无统一公开API
    """
    return "无统一公开API - 可查询药品、医疗器械注册审批信息、说明书、召回信息等"

def fetch_nmpa_udi_example():
    """
    NMPA UDI系统 API - 需要访问令牌
    """
    return "需要访问令牌 - 提供医疗器械唯一标识(UDI)与产品信息查询"

def fetch_chictr_example():
    """
    中国临床试验注册中心 - 无公开REST API
    """
    return "无公开REST API - 可通过Web检索中国临床试验注册信息"

def fetch_cma_guidelines_example():
    """
    中华医学会指南 - 无统一API
    """
    return "无统一API - 包含各专科临床指南、专家共识，需下载PDF后本地处理"

def fetch_cnki_example():
    """
    中国知网 - 无公开API
    """
    return "无公开API - 中文期刊论文、学位论文等，需机构账号，有第三方封装如MagicCNKI"

def fetch_wanfang_example():
    """
    万方数据 - 需申请开放平台
    """
    return "需万方开放平台申请 - 提供文献查询、选题API等接口"

def fetch_huatuo26m_example():
    """
    Huatuo-26M - 数据集下载
    """
    return "数据集下载 - 约2600万条中文医疗问答，如：'Q:高血压的症状有哪些？A:头痛、头晕、心悸、耳鸣...'"

def fetch_huatuo_kgqa_example():
    """
    huatuo_knowledge_graph_qa - 数据集下载
    """
    return "数据集下载 - 约79.8万条基于知识图谱的医疗问答"

def fetch_disease_ontology_example():
    """
    Disease Ontology API - 获取疾病本体示例
    https://disease-ontology.org/do-kb/api_doc
    """
    try:
        url = "https://www.disease-ontology.org/api/metadata/DOID:4"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            name = data.get('name', 'N/A')
            definition = data.get('definition', 'N/A')[:100] if data.get('definition') else 'N/A'
            return f"Disease Ontology示例 - DOID:4 ({name}): {definition}..."
        return "API调用成功但无数据返回"
    except Exception as e:
        return f"调用失败: {str(e)}"

def fetch_orphanet_example():
    """
    Orphanet ORDO - SPARQL端点
    """
    return "SPARQL端点可用 - 罕见病本体，包含疾病与基因、表型、流行病学信息"

def fetch_drugcentral_example():
    """
    DrugCentral - 需自建数据库
    """
    return "需自建数据库 - 提供药物活性成分、适应症、靶点、相互作用等数据"

def fetch_primekg_example():
    """
    PrimeKG - 需自建SPARQL端点
    """
    return "需自建SPARQL端点 - 精准医学知识图谱，整合约20个生物医学数据库"

def fetch_umls_example():
    """
    UMLS Terminology Services - 需要API Key
    """
    return "需UMLS License和API Key - 整合SNOMED CT、MeSH、LOINC、ICD-10、RxNorm等术语"

def fetch_cmekg_example():
    """
    CMeKG中文医学知识图谱 - 需下载导入
    """
    return "需下载导入Neo4j - 中文医学知识图谱，包含疾病、症状、药品、检查等实体关系"

def fetch_peking_cmekg_example():
    """
    医学知识图谱数据集(协和医院+CMeKG) - 需申请
    """
    return "需通过平台申请 - 融合协和医院电子病历的结构化知识图谱"

def fetch_cmkg_example():
    """
    CMKG中文医学知识图谱 - GitHub开源
    """
    return "GitHub开源数据 - 多模态中文医学知识图谱，基于公开医学网页数据"


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
    print("正在读取Excel文件...")
    df = pd.read_excel(r'd:\now\20251215-20251221\医学API\公开医学知识API.xlsx')
    
    # 清理列名
    df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
    
    # 获取API名称列（第二列）
    name_col = df.columns[1]
    
    # 新建知识案例列
    examples = []
    
    print(f"共有 {len(df)} 个API需要处理\n")
    
    for idx, row in df.iterrows():
        api_name = str(row[name_col]).strip()
        print(f"[{idx+1}/{len(df)}] 处理: {api_name[:50]}...")
        
        # 查找对应的函数
        func = None
        for key, fn in API_FUNCTIONS.items():
            if key in api_name or api_name in key:
                func = fn
                break
        
        if func:
            result = func()
            print(f"  -> {result[:80]}...")
        else:
            result = "未找到对应的API调用函数"
            print(f"  -> {result}")
        
        examples.append(result)
        
        # 添加延迟，避免请求过快
        time.sleep(0.5)
    
    # 添加新列
    df['知识案例'] = examples
    
    # 保存结果
    output_path = r'd:\now\20251215-20251221\医学API\公开医学知识API_带案例.xlsx'
    df.to_excel(output_path, index=False)
    print(f"\n完成！结果已保存到: {output_path}")
    
    return df


if __name__ == "__main__":
    main()
