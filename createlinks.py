# 从内容片段中，提取年份，并在对应的所以文件中增加链接。

import os
import re
import math
import functools

# 国家列表
COUNTRIES = ["周", "鲁", "宋", "卫", "陈", "蔡", "曹", "郑", "燕", "吴", "楚", "秦", "齐", "赵", "晋", "赵", "魏", "韩"]



project_folder = os.path.dirname(os.path.realpath(__file__))
# print(project_folder)


class ContentDetail():
    """
    内容片段详细信息
    """


    # 文件路径
    path:str = None

    # title
    title:str = None

    # 公元年份，公元前为负数
    year:int = None
    # 公元年链接
    year_path:str = None

    # 国家
    country:str = None
    # 朝代，比如安王、威烈王
    era:str = None
    # 朝代年份
    era_year:str = None


    def __init__(self, file_path:str):
        # if "三壮士" not in file_path:
        #     return

        # 敖，特为楚郏敖匹配
        re_v = re.compile("([" + ''.join(COUNTRIES) + "])(.{1,2}[公王侯敖])([元一二三四五六七八九十]+年).*?(前?\d+)年.*")

        md_file = open(file_path, "r")
        for i in range(5):
            # 第一行，会记录年份
            line_v:str = md_file.readline()
            # print(i, line_v)

            # g = re.search(r'([周晋])(.{1,2}[公王侯])([元一二三四五六七八九十]+年).*?(前?\d+)年.*', line_v)
            g = re_v.search(line_v)
            if g is not None:
                self.title = os.path.basename(file_path).replace(".md", "")
                self.path = file_path.replace(project_folder + "/", "")

                self.year = int(g.group(4).replace("前", '-'))
                # 公元年的目录文件，以每50年汇总为一个文件，以便查阅
                from_year:int = math.floor(self.year / 50) * 50
                to_year:int = from_year + 49
                self.year_path = f"{from_year}年~{to_year}年".replace("-", "前")

                self.country = g.group(1)
                self.era = g.group(2)
                self.era_year = g.group(3)
                break
        
        md_file.close()

        if self.title is None:
            print(f"未检测到链接信息：{file_path}")
    
    def __str__(self) -> str:
        return self.title
        


def compare_detail(detail1:ContentDetail, detail2:ContentDetail):
    """
    对比年代大小
    """

    if detail1.year > detail2.year:
        return 1
    elif detail1.year < detail2.year:
        return -1
    
    era_index1:int = COUNTRIES.index(detail1.country)
    era_index2:int = COUNTRIES.index(detail2.country)

    if era_index1 > era_index2:
        return 1
    elif era_index1 < era_index2:
        return -1
    
    return 0

    

def get_all_links_detail() -> list:
    """
    获取所以内容片段的信息
    """

    details:list[ContentDetail] = []

    # 排除目录
    exclude_folders:list = ["node_modules"]

    # 一级目录，周、鲁
    level1_folders = os.listdir(project_folder)
    for level1_folder in level1_folders:
        # 排除目录
        if level1_folder in exclude_folders:
            continue

        level1_path = os.path.join(project_folder, level1_folder)
        if not os.path.isdir(level1_path):
            continue

        # 二级目录，比如平王、安王等
        level2_folders = os.listdir(level1_path)
        for level2_folder in level2_folders:
            level2_path = os.path.join(level1_path, level2_folder)
            if not os.path.isdir(level2_path):
                continue
            
            # 排除目录
            if level2_folder in exclude_folders:
                continue

            # md 文件列表
            md_files = os.listdir(level2_path)
            for a_md in md_files:
                if not a_md.endswith(".md"):
                    continue
                
                a_md_path = os.path.join(level2_path, a_md)
                # print(a_md)

                detail:ContentDetail = ContentDetail(a_md_path)
                if detail.title is not None:
                    print(detail)
                    details.append(detail)

    return details


def add_links_to_era(era_name1:str, era_name2:str, details:list):
    """
    添加索引至朝代
    """
    index_file_path:str = os.path.join(project_folder, era_name1, era_name2) + ".md"
    os.makedirs(os.path.dirname(index_file_path), exist_ok=True)

    index_content:str = ""

    if os.path.exists(index_file_path):
        index_file = open(index_file_path, "r")
        index_content = index_file.read()
        index_file.close()
    
    index_file = open(index_file_path, "w+")
    
    # print(index_content)

    # 索引文件内容
    index_content = re.sub(r"-\s.*", "", index_content)
    index_content = re.sub(r"[\r\n\s]+", "\r\n", index_content)

    # 年份排序
    # details = sorted(details, key=lambda _:_.year)
    details = sorted(details, key=functools.cmp_to_key(compare_detail))
    
    # 当前朝代年份，比如十五年
    crt_era_year = None
    for _ in details:
        # print("\t", _)
        era_year = _.era_year
        if era_year != crt_era_year:
            crt_era_year = era_year
            year_label:str = str(_.year).replace("-", "前")
            index_content += f"\r\n- {crt_era_year}，[{year_label}](公元/{_.year_path}.md)"
        
        index_content += f"\r\n  - [{_.title}]({_.path})"

    # 写入文件
    index_file.write(index_content)
    index_file.close()

def add_links_to_year(year_label:str, details:list):
    """
    添加索引至公元年。
    """
    index_file_path:str = os.path.join(project_folder, "公元", year_label) + ".md"
    os.makedirs(os.path.dirname(index_file_path), exist_ok=True)

    index_content:str = ""
    
    # print(index_content)

    # 年份排序
    # details = sorted(details, key=lambda _:_.year)
    details = sorted(details, key=functools.cmp_to_key(compare_detail))
    
    # 当前年份，比如-605年
    crt_year = None
    # 当前朝代，比如晋灵公
    crt_era_info = None
    for _ in details:
        # print("\t", _)
        year = _.year
        if year != crt_year:
            crt_year = year
            year_label:str = str(_.year).replace("-", "前")
            index_content += f"\r\n\r\n## {year_label}"

        # 当前朝代
        era_info = f"{_.country}{_.era}{_.era_year}"
        if era_info != crt_era_info:
            crt_era_info = era_info
            index_content += f"\r\n- [{crt_era_info}]({_.country}/{_.era}.md)"
        
        
        index_content += f"\r\n  - [{_.title}]({_.path})"

    # 写入文件
    index_file = open(index_file_path, "w+")
    index_file.write(index_content)
    index_file.close()

#replace all occurrenc


link_details:list = get_all_links_detail()

# 朝代数据
era_map = {}
# 公元年数据
year_map = {}
for _ in link_details:
    # 朝代
    ear_name:str = f"{_.country}_{_.era}"
    if ear_name not in era_map:
        era_map[ear_name] = []
    era_map[ear_name].append(_)

    # 公元年的目录文件，以每50年汇总为一个文件，以便查阅
    if _.year_path not in year_map:
        year_map[_.year_path] = []
    year_map[_.year_path].append(_)


# 添加朝代索引
for _ in era_map:
    country:str = _.split("_")[0]
    era:str = _.split("_")[1]
    add_links_to_era(country, era, era_map[_])

# 添加公元年索引
for _ in year_map:
    add_links_to_year(_, year_map[_])


     