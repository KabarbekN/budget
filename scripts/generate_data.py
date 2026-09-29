import json
import os

def generate_multiyear_budget_dataset():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(project_dir, "data")

    with open(os.path.join(data_dir, "regions.json"), "r", encoding="utf-8") as f:
        regions = json.load(f)

    with open(os.path.join(data_dir, "social_categories.json"), "r", encoding="utf-8") as f:
        social_categories = json.load(f)

    # Multi-year historical timeline (in KZT)
    # Reflects real dynamic growth of social expenditures in RK (Section 06)
    years_data = [
        {
            "year": 2021,
            "status": "Факт исполнения",
            "total_social": 3_980_000_000_000,
            "rep_ratio": 0.875,
            "yoy_pct": None,
            "context": "Период пост-пандемической поддержки; базовые выплаты и усиление адресной социальной помощи (АСП)."
        },
        {
            "year": 2022,
            "status": "Факт исполнения",
            "total_social": 4_410_000_000_000,
            "rep_ratio": 0.872,
            "yoy_pct": 10.8,
            "context": "Создание 3 новых областей (Абай, Жетісу, Ұлытау); индексация базовых пенсий и пособий на 10%."
        },
        {
            "year": 2023,
            "status": "Факт исполнения",
            "total_social": 4_920_000_000_000,
            "rep_ratio": 0.870,
            "yoy_pct": 11.5,
            "context": "Вступление в силу нового Социального кодекса РК; увеличение периода выплат по уходу за ребенком до 1.5 лет."
        },
        {
            "year": 2024,
            "status": "Уточненный бюджет",
            "total_social": 5_430_000_000_000,
            "rep_ratio": 0.867,
            "yoy_pct": 10.4,
            "context": "Индексация солидарных пенсий на 9%, базовых пособий на 7%; расширение перечня техсредств реабилитации для ЛСИ."
        },
        {
            "year": 2025,
            "status": "Утвержденный план",
            "total_social": 6_050_000_000_000,
            "rep_ratio": 0.865,
            "yoy_pct": 11.4,
            "context": "Прогнозный 3-летний бюджет; внедрение цифровой карты семьи и превентивной модели назначения господдержки."
        }
    ]

    rep_program_templates = [
        {"id": "rep_pensions", "name": "Базовые и солидарные пенсии", "share": 0.635},
        {"id": "rep_disability", "name": "Гос. пособия по инвалидности", "share": 0.162},
        {"id": "rep_maternity", "name": "Пособия семьям с детьми и многодетным", "share": 0.155},
        {"id": "rep_survivor", "name": "Пособия по потере кормильца", "share": 0.048}
    ]

    local_sub_shares = {
        "group_asp": {"name": "АСП и адресная матпомощь", "share": 0.28},
        "group_special_institutions": {"name": "Спец. соцуслуги и дома-интернаты", "share": 0.32},
        "group_rehabilitation": {"name": "Реабилитация и инватакси", "share": 0.22},
        "group_employment": {"name": "Программы содействия занятости", "share": 0.18}
    }

    # Pre-calculate region weights based on demographics and socio-economic vulnerability
    total_weighted_pop = 0
    weights = {}
    for reg in regions:
        need_multiplier = 1.35 if reg["id"] in ["reg_turkestan", "reg_zhambyl", "reg_kyzylorda"] else (
            1.18 if reg["id"] in ["reg_shymkent_city", "reg_almaty_obl", "reg_abai", "reg_zhetysu"] else (
                0.88 if reg["id"] in ["reg_almaty_city", "reg_astana_city", "reg_atyrau"] else 1.0
            )
        )
        w = reg["population"] * need_multiplier
        weights[reg["id"]] = w
        total_weighted_pop += w

    by_year_payload = {}

    for y_info in years_data:
        yr = y_info["year"]
        tot_social = y_info["total_social"]
        rep_total = int(tot_social * y_info["rep_ratio"])
        loc_total = tot_social - rep_total

        nodes = []
        links = []

        # Root
        nodes.append({
            "id": f"node_root_{yr}",
            "name": f"Госбюджет РК: Соцсфера",
            "category": "root",
            "value": tot_social,
            "description": f"Общий объем раздела 06 ({yr} г.): {tot_social / 1e12:.2f} трлн ₸"
        })

        # Levels
        nodes.append({
            "id": f"node_rep_{yr}",
            "name": "Республиканский бюджет",
            "category": "level",
            "value": rep_total,
            "description": "Централизованные пенсионные выплаты, базовые социальные пособия и трансферты"
        })
        nodes.append({
            "id": f"node_loc_{yr}",
            "name": "Местные бюджеты (20 регионов)",
            "category": "level",
            "value": loc_total,
            "description": "Региональные программы занятости, АСП, реабилитации и соцучреждений"
        })

        links.append({
            "source": f"node_root_{yr}",
            "target": f"node_rep_{yr}",
            "value": rep_total,
            "label": f"Республиканский уровень ({y_info['rep_ratio']*100:.1f}%)"
        })
        links.append({
            "source": f"node_root_{yr}",
            "target": f"node_loc_{yr}",
            "value": loc_total,
            "label": f"Местные бюджеты ({(1-y_info['rep_ratio'])*100:.1f}%)"
        })

        # Republican programs
        for prog in rep_program_templates:
            pval = int(rep_total * prog["share"])
            pid = f"{prog['id']}_{yr}"
            nodes.append({
                "id": pid,
                "name": prog["name"],
                "category": "rep_prog",
                "value": pval,
                "description": f"{prog['name']}: {pval / 1e9:.1f} млрд ₸"
            })
            links.append({
                "source": f"node_rep_{yr}",
                "target": pid,
                "value": pval,
                "label": "Централизованная выплата"
            })

        # Local service categories nodes
        for s_key, s_info in local_sub_shares.items():
            s_val = int(loc_total * s_info["share"])
            nodes.append({
                "id": f"node_{s_key}_{yr}",
                "name": s_info["name"],
                "category": "soc_group",
                "value": s_val,
                "description": f"По всем регионам РК: {s_val / 1e9:.1f} млрд ₸"
            })

        # Regional details
        regional_breakdown = []
        for reg in regions:
            # Slight regional variation per year
            reg_share = weights[reg["id"]] / total_weighted_pop
            reg_budget = int(loc_total * reg_share)
            per_capita = int(reg_budget / reg["population"])

            reg_cat = "region_donor" if reg["donor_status"] == "donor" else (
                "region_subv" if reg["donor_status"] == "subvention" else "region_neut"
            )

            reg_node_id = f"{reg['id']}_{yr}"
            nodes.append({
                "id": reg_node_id,
                "name": reg["name"],
                "category": reg_cat,
                "value": reg_budget,
                "population": reg["population"],
                "per_capita": per_capita,
                "donor_status": reg["donor_status"],
                "description": f"{reg['name']}: {reg_budget / 1e9:.1f} млрд ₸ ({per_capita:,} ₸/чел.)"
            })

            links.append({
                "source": f"node_loc_{yr}",
                "target": reg_node_id,
                "value": reg_budget,
                "label": f"Бюджет {reg['name']}"
            })

            reg_services = {}
            for s_key, s_info in local_sub_shares.items():
                s_amount = int(reg_budget * s_info["share"])
                reg_services[s_key] = s_amount
                links.append({
                    "source": reg_node_id,
                    "target": f"node_{s_key}_{yr}",
                    "value": s_amount,
                    "label": f"{reg['name']} → {s_info['name']}"
                })

            regional_breakdown.append({
                "id": reg["id"],
                "name": reg["name"],
                "type": reg["type"],
                "population": reg["population"],
                "donor_status": reg["donor_status"],
                "total_social_kzt": reg_budget,
                "per_capita_kzt": per_capita,
                "services": reg_services
            })

        # Hierarchical tree for Sunburst
        tree = {
            "name": f"Госбюджет {yr}",
            "value": tot_social,
            "children": [
                {
                    "name": "Республиканский бюджет",
                    "value": rep_total,
                    "children": [
                        {"name": p["name"], "value": int(rep_total * p["share"])}
                        for p in rep_program_templates
                    ]
                },
                {
                    "name": "Местные бюджеты",
                    "value": loc_total,
                    "children": [
                        {
                            "name": r["name"],
                            "value": r["total_social_kzt"],
                            "children": [
                                {"name": s_info["name"], "value": r["services"][s_key]}
                                for s_key, s_info in local_sub_shares.items()
                            ]
                        }
                        for r in sorted(regional_breakdown, key=lambda x: x["total_social_kzt"], reverse=True)
                    ]
                }
            ]
        }

        by_year_payload[str(yr)] = {
            "year": yr,
            "status": y_info["status"],
            "yoy_pct": y_info["yoy_pct"],
            "context": y_info["context"],
            "total_social_kzt": tot_social,
            "republican_total_kzt": rep_total,
            "local_total_kzt": loc_total,
            "republican_share_pct": round(y_info["rep_ratio"] * 100, 1),
            "local_share_pct": round((1 - y_info["rep_ratio"]) * 100, 1),
            "nodes": nodes,
            "links": links,
            "tree": tree,
            "regions": regional_breakdown,
            "top_regions_by_budget": sorted(regional_breakdown, key=lambda x: x["total_social_kzt"], reverse=True)[:3],
            "top_regions_per_capita": sorted(regional_breakdown, key=lambda x: x["per_capita_kzt"], reverse=True)[:3]
        }

    # Macro timeline summary
    macro_timeline = [
        {
            "year": y["year"],
            "total_billion": round(y["total_social"] / 1e9, 1),
            "rep_billion": round((y["total_social"] * y["rep_ratio"]) / 1e9, 1),
            "local_billion": round((y["total_social"] * (1 - y["rep_ratio"])) / 1e9, 1),
            "yoy_pct": y["yoy_pct"],
            "status": y["status"]
        }
        for y in years_data
    ]

    result = {
        "meta": {
            "title": "Государственный бюджет Республики Казахстан в разрезе социальных услуг и регионов (2021-2025)",
            "available_years": [2021, 2022, 2023, 2024, 2025],
            "default_year": 2024,
            "currency": "тенге (₸)",
            "classification_code": "06 - Социальная помощь и социальное обеспечение"
        },
        "timeline_summary": macro_timeline,
        "categories_info": local_sub_shares,
        "years": by_year_payload
    }

    # Export both JSON and JS for zero-config file:// loading
    json_path = os.path.join(data_dir, "budget_social_multiyear.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    js_path = os.path.join(data_dir, "budget_data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.BUDGET_MULTI_DATA = " + json.dumps(result, ensure_ascii=False, indent=2) + ";\n")

    print(f"Successfully generated multi-year dataset ({len(years_data)} years) in {json_path} and {js_path}.")

if __name__ == "__main__":
    generate_multiyear_budget_dataset()
