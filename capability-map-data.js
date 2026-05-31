window.CAD_CAPABILITY_MAP_DATA = {
  "schemaVersion": 2,
  "generatedAt": "2026-05-31T15:36:41+00:00",
  "trainingStages": [
    {
      "id": "not_started",
      "label": "未开训",
      "rank": 0,
      "note": "已进入计划视野，但还没有形成可复盘案例。"
    },
    {
      "id": "prompt_defined",
      "label": "目标已声明",
      "rank": 1,
      "note": "已有下一轮训练目标，等待案例验证。"
    },
    {
      "id": "case_training",
      "label": "案例训练中",
      "rank": 2,
      "note": "正在通过真实训练轮次验证 Prompt、规则和链路。"
    },
    {
      "id": "user_feedback_pass",
      "label": "用户反馈通过",
      "rank": 3,
      "note": "用户已认可当前案例效果，但仍不替代表 C 机器证明。"
    },
    {
      "id": "systemized",
      "label": "已沉淀",
      "rank": 4,
      "note": "经验已进入规则、检查器或资产库，可复用到下一轮。"
    }
  ],
  "trainingStageColumns": [
    {
      "id": "raw",
      "label": "标准图库",
      "shortLabel": "图库"
    },
    {
      "id": "knowledge",
      "label": "常识整理",
      "shortLabel": "常识"
    },
    {
      "id": "trained",
      "label": "训练沉淀",
      "shortLabel": "训练"
    },
    {
      "id": "system",
      "label": "自产资产",
      "shortLabel": "自产"
    }
  ],
  "capabilityCatalog": [
    {
      "id": "sofa",
      "name": "沙发",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "priority": "P0",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_repair",
        "pipeline_learning_promoter"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_visual_intent",
          "name": "视觉语义智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        },
        {
          "id": "pipeline_repair",
          "name": "修复回环智能体"
        },
        {
          "id": "pipeline_learning_promoter",
          "name": "训练沉淀智能体"
        }
      ],
      "focus": "方向语义、扶手/靠背/坐垫部件、共享边去重",
      "risks": [
        {
          "id": "sofa_direction_semantics_inverted",
          "label": "方向语义反了",
          "note": "沙发硬背、软靠垫、坐垫的前后语义容易被倒置。"
        },
        {
          "id": "duplicate_shared_edges",
          "label": "共享边重复",
          "note": "相邻部件允许贴合，但同一 CAD 段不能重复生成。"
        }
      ],
      "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
    },
    {
      "id": "tea-table",
      "name": "茶几",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "priority": "P0",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "比例、与沙发组合距离、中心对齐",
      "risks": [
        {
          "id": "retrieval_hit_as_capability",
          "label": "检索命中被当能力",
          "note": "检索到素材只算参考输入，不算系统能力。"
        }
      ],
      "nextTrainingTarget": "补标准尺寸和组合关系检查"
    },
    {
      "id": "dining-table",
      "name": "餐桌",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "priority": "P0",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "桌面尺寸、椅子围合、通行净距",
      "risks": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "训练餐桌+餐椅组合"
    },
    {
      "id": "dining-chair",
      "name": "餐椅",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "priority": "P0",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "focus": "朝向、椅背表达、与桌边关系",
      "risks": [
        {
          "id": "missing_furniture_parts",
          "label": "家具部件缺失",
          "note": "对象必须拆清关键部件，不应只画外轮廓。"
        }
      ],
      "nextTrainingTarget": "补椅背和入座方向规则"
    },
    {
      "id": "bed",
      "name": "床铺",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "priority": "P0",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_visual_intent",
          "name": "视觉语义智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "床头方向、床垫/枕头/床头柜组合",
      "risks": [
        {
          "id": "plan_view_role_direction_errors",
          "label": "平面角色方向错误",
          "note": "平面图方向、入座方向和开门方向需要显式说明。"
        }
      ],
      "nextTrainingTarget": "开卧室组合训练"
    },
    {
      "id": "nightstand",
      "name": "床头柜",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "priority": "P1",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "focus": "成对摆放、床侧净距、比例",
      "risks": [
        {
          "id": "size_only_repair_loop",
          "label": "只靠尺寸修复",
          "note": "视觉语义错时，只调尺寸会进入无效回环。"
        }
      ],
      "nextTrainingTarget": "补床侧组合默认值"
    },
    {
      "id": "wardrobe",
      "name": "衣柜",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "priority": "P1",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "开门净空、贴墙、与床通道",
      "risks": [
        {
          "id": "machine_green_delivery",
          "label": "机器绿但视觉未验",
          "note": "机器审计绿灯不能直接替代用户可见验收。"
        }
      ],
      "nextTrainingTarget": "训练衣柜开门净空 audit"
    },
    {
      "id": "tv-cabinet",
      "name": "电视柜",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "priority": "P1",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "focus": "朝向、墙面关系、电视/柜比例",
      "risks": [
        {
          "id": "clone_reference_fragments",
          "label": "误克隆参考碎片",
          "note": "参考图不能被碎片化克隆为系统资产。"
        }
      ],
      "nextTrainingTarget": "补客厅视线方向规则"
    },
    {
      "id": "desk",
      "name": "书桌",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "priority": "P1",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "focus": "座椅空间、靠窗/靠墙偏好",
      "risks": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "补书桌+椅组合训练"
    },
    {
      "id": "low-cabinet",
      "name": "矮柜",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "priority": "P2",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "focus": "低柜高度语义、墙边摆放",
      "risks": [
        {
          "id": "retrieval_hit_as_capability",
          "label": "检索命中被当能力",
          "note": "检索到素材只算参考输入，不算系统能力。"
        }
      ],
      "nextTrainingTarget": "先补对象默认值"
    },
    {
      "id": "basin",
      "name": "洗手台",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "priority": "P1",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "台盆、柜体、水龙头语义和卫浴墙面关系",
      "risks": [
        {
          "id": "missing_furniture_parts",
          "label": "家具部件缺失",
          "note": "对象必须拆清关键部件，不应只画外轮廓。"
        }
      ],
      "nextTrainingTarget": "训练卫浴对象部件表达"
    },
    {
      "id": "toilet",
      "name": "马桶",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "priority": "P1",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "focus": "朝向、离墙尺寸、检修空间",
      "risks": [
        {
          "id": "machine_size_drift_only",
          "label": "仅尺寸漂移",
          "note": "只盯尺寸漂移会漏掉语义或视觉错误。"
        }
      ],
      "nextTrainingTarget": "补洁具默认净距"
    },
    {
      "id": "stove",
      "name": "灶台",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "priority": "P2",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "focus": "台面、火口、厨房操作三角",
      "risks": [
        {
          "id": "unsupported_or_risky",
          "label": "暂不支持或风险高",
          "note": "高风险或未支持对象应先阻塞并补常识。"
        }
      ],
      "nextTrainingTarget": "先补厨房对象 catalog"
    },
    {
      "id": "fridge",
      "name": "冰箱",
      "kind": "object",
      "kindLabel": "对象能力",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "priority": "P2",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "focus": "门开启方向、散热间距、厨房动线",
      "risks": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "补冰箱门向和净距"
    },
    {
      "id": "wall",
      "name": "墙体绘制",
      "kind": "draw",
      "kindLabel": "绘图能力",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "priority": "P0",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "relatedAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "闭合轮廓、墙厚、图层归类",
      "risks": [
        {
          "id": "duplicate_shared_edges",
          "label": "共享边重复",
          "note": "相邻部件允许贴合，但同一 CAD 段不能重复生成。"
        }
      ],
      "nextTrainingTarget": "强化墙线重复与开口检查"
    },
    {
      "id": "door",
      "name": "门绘制",
      "kind": "draw",
      "kindLabel": "绘图能力",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "priority": "P0",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "relatedAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "门洞、开启弧、门扇方向",
      "risks": [
        {
          "id": "plan_view_role_direction_errors",
          "label": "平面角色方向错误",
          "note": "平面图方向、入座方向和开门方向需要显式说明。"
        }
      ],
      "nextTrainingTarget": "补门向语义训练"
    },
    {
      "id": "window",
      "name": "窗户绘制",
      "kind": "draw",
      "kindLabel": "绘图能力",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "priority": "P0",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "relatedAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "窗洞、窗线层级、墙体嵌入",
      "risks": [
        {
          "id": "machine_green_delivery",
          "label": "机器绿但视觉未验",
          "note": "机器审计绿灯不能直接替代用户可见验收。"
        }
      ],
      "nextTrainingTarget": "补窗洞与墙体关系 audit"
    },
    {
      "id": "door-opening",
      "name": "门洞绘制",
      "kind": "draw",
      "kindLabel": "绘图能力",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "priority": "P1",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "relatedAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "洞口扣减、门套语义、墙段连续",
      "risks": [
        {
          "id": "duplicate_shared_edges",
          "label": "共享边重复",
          "note": "相邻部件允许贴合，但同一 CAD 段不能重复生成。"
        }
      ],
      "nextTrainingTarget": "训练洞口扣减检查"
    },
    {
      "id": "window-opening",
      "name": "窗洞绘制",
      "kind": "draw",
      "kindLabel": "绘图能力",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "priority": "P1",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "relatedAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "窗洞宽度、离地语义、墙内关系",
      "risks": [
        {
          "id": "machine_size_drift_only",
          "label": "仅尺寸漂移",
          "note": "只盯尺寸漂移会漏掉语义或视觉错误。"
        }
      ],
      "nextTrainingTarget": "补窗洞标准语义"
    },
    {
      "id": "room-outline",
      "name": "房间轮廓绘制",
      "kind": "draw",
      "kindLabel": "绘图能力",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "priority": "P1",
      "ownerAgentId": "pipeline_intent",
      "ownerAgentName": "需求拆解智能体",
      "relatedAgentIds": [
        "pipeline_intent",
        "pipeline_context_curator",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_context_curator",
          "name": "上下文整理智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "房间闭合、基点、尺寸约束",
      "risks": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "强化房间轮廓 validate"
    },
    {
      "id": "column",
      "name": "柱子绘制",
      "kind": "draw",
      "kindLabel": "绘图能力",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "priority": "P2",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "relatedAgentIds": [
        "pipeline_execute",
        "pipeline_intent"
      ],
      "relatedAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "focus": "结构柱尺寸、图层、与墙体关系",
      "risks": [
        {
          "id": "retrieval_hit_as_capability",
          "label": "检索命中被当能力",
          "note": "检索到素材只算参考输入，不算系统能力。"
        }
      ],
      "nextTrainingTarget": "补柱子对象规范"
    },
    {
      "id": "furniture-layout",
      "name": "基础家具摆放",
      "kind": "draw",
      "kindLabel": "绘图能力",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "priority": "P2",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "relatedAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_learning_promoter"
      ],
      "relatedAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        },
        {
          "id": "pipeline_learning_promoter",
          "name": "训练沉淀智能体"
        }
      ],
      "focus": "组合关系、通道、朝向和避让",
      "risks": [
        {
          "id": "visual_fail_size_only_repair",
          "label": "视觉失败却只调尺寸",
          "note": "视觉失败时应回到视觉语义智能体。"
        }
      ],
      "nextTrainingTarget": "开客厅/卧室组合训练"
    },
    {
      "id": "dimension",
      "name": "简单尺寸标注",
      "kind": "annotation",
      "kindLabel": "标注能力",
      "group": "标注表达",
      "matrixGroup": "标注表达",
      "priority": "P1",
      "ownerAgentId": "pipeline_delivery",
      "ownerAgentName": "交付汇报智能体",
      "relatedAgentIds": [
        "pipeline_delivery",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "relatedAgents": [
        {
          "id": "pipeline_delivery",
          "name": "交付汇报智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "focus": "标注对象、尺寸线位置、比例和避让",
      "risks": [
        {
          "id": "missing_annotation",
          "label": "标注缺失",
          "note": "标注训练要明确对象、位置、比例和避让。"
        }
      ],
      "nextTrainingTarget": "补尺寸标注检查器"
    },
    {
      "id": "text",
      "name": "简单文字标注",
      "kind": "annotation",
      "kindLabel": "标注能力",
      "group": "标注表达",
      "matrixGroup": "标注表达",
      "priority": "P1",
      "ownerAgentId": "pipeline_delivery",
      "ownerAgentName": "交付汇报智能体",
      "relatedAgentIds": [
        "pipeline_delivery",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "relatedAgents": [
        {
          "id": "pipeline_delivery",
          "name": "交付汇报智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "focus": "文字内容、图层、与对象关联",
      "risks": [
        {
          "id": "missing_annotation",
          "label": "标注缺失",
          "note": "标注训练要明确对象、位置、比例和避让。"
        }
      ],
      "nextTrainingTarget": "训练对象名称标注"
    },
    {
      "id": "layers",
      "name": "基础图层归类",
      "kind": "annotation",
      "kindLabel": "标注能力",
      "group": "标注表达",
      "matrixGroup": "标注表达",
      "priority": "P2",
      "ownerAgentId": "pipeline_audit",
      "ownerAgentName": "机器审计智能体",
      "relatedAgentIds": [
        "pipeline_audit",
        "pipeline_execute",
        "pipeline_delivery"
      ],
      "relatedAgents": [
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_delivery",
          "name": "交付汇报智能体"
        }
      ],
      "focus": "CODEX_PREVIEW、正式图层保护、对象分层",
      "risks": [
        {
          "id": "formal_layer_write_risk",
          "label": "正式图层写入风险",
          "note": "训练默认只写 CODEX_PREVIEW，不碰正式图层。"
        }
      ],
      "nextTrainingTarget": "补图层归类审计"
    }
  ],
  "trainingPrograms": [
    {
      "id": "program-sofa",
      "capabilityId": "sofa",
      "name": "沙发",
      "title": "沙发 · 开一轮沙发方向语义与贴合关系训练",
      "priority": "P0",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_repair",
        "pipeline_learning_promoter"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_visual_intent",
          "name": "视觉语义智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        },
        {
          "id": "pipeline_repair",
          "name": "修复回环智能体"
        },
        {
          "id": "pipeline_learning_promoter",
          "name": "训练沉淀智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_repair",
        "pipeline_learning_promoter"
      ],
      "focus": "方向语义、扶手/靠背/坐垫部件、共享边去重",
      "weaknesses": [
        {
          "id": "sofa_direction_semantics_inverted",
          "label": "方向语义反了",
          "note": "沙发硬背、软靠垫、坐垫的前后语义容易被倒置。"
        },
        {
          "id": "duplicate_shared_edges",
          "label": "共享边重复",
          "note": "相邻部件允许贴合，但同一 CAD 段不能重复生成。"
        }
      ],
      "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练",
      "stageState": {
        "id": "case_training",
        "label": "案例训练中",
        "rank": 2,
        "note": "沙发已有多轮家装训练上下文，本页继续把方向语义、部件和贴合关系作为下一轮目标。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“方向语义、扶手/靠背/坐垫部件、共享边去重”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "training",
          "label": "训练中",
          "note": "下一轮训练目标：开一轮沙发方向语义与贴合关系训练。"
        },
        "system": {
          "state": "planned",
          "label": "计划中",
          "note": "只有经过 promotion gate、证据边界和回归检查后，才允许进入自产资产或通用规则。"
        }
      },
      "trainingObjective": "围绕“方向语义、扶手/靠背/坐垫部件、共享边去重”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-tea-table",
      "capabilityId": "tea-table",
      "name": "茶几",
      "title": "茶几 · 补标准尺寸和组合关系检查",
      "priority": "P0",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "比例、与沙发组合距离、中心对齐",
      "weaknesses": [
        {
          "id": "retrieval_hit_as_capability",
          "label": "检索命中被当能力",
          "note": "检索到素材只算参考输入，不算系统能力。"
        }
      ],
      "nextTrainingTarget": "补标准尺寸和组合关系检查",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补标准尺寸和组合关系检查。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“比例、与沙发组合距离、中心对齐”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补标准尺寸和组合关系检查。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“比例、与沙发组合距离、中心对齐”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-dining-table",
      "capabilityId": "dining-table",
      "name": "餐桌",
      "title": "餐桌 · 训练餐桌+餐椅组合",
      "priority": "P0",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "桌面尺寸、椅子围合、通行净距",
      "weaknesses": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "训练餐桌+餐椅组合",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：训练餐桌+餐椅组合。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“桌面尺寸、椅子围合、通行净距”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：训练餐桌+餐椅组合。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“桌面尺寸、椅子围合、通行净距”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-dining-chair",
      "capabilityId": "dining-chair",
      "name": "餐椅",
      "title": "餐椅 · 补椅背和入座方向规则",
      "priority": "P0",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "朝向、椅背表达、与桌边关系",
      "weaknesses": [
        {
          "id": "missing_furniture_parts",
          "label": "家具部件缺失",
          "note": "对象必须拆清关键部件，不应只画外轮廓。"
        }
      ],
      "nextTrainingTarget": "补椅背和入座方向规则",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补椅背和入座方向规则。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“朝向、椅背表达、与桌边关系”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补椅背和入座方向规则。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“朝向、椅背表达、与桌边关系”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-bed",
      "capabilityId": "bed",
      "name": "床铺",
      "title": "床铺 · 开卧室组合训练",
      "priority": "P0",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_visual_intent",
          "name": "视觉语义智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "床头方向、床垫/枕头/床头柜组合",
      "weaknesses": [
        {
          "id": "plan_view_role_direction_errors",
          "label": "平面角色方向错误",
          "note": "平面图方向、入座方向和开门方向需要显式说明。"
        }
      ],
      "nextTrainingTarget": "开卧室组合训练",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：开卧室组合训练。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“床头方向、床垫/枕头/床头柜组合”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：开卧室组合训练。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“床头方向、床垫/枕头/床头柜组合”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-nightstand",
      "capabilityId": "nightstand",
      "name": "床头柜",
      "title": "床头柜 · 补床侧组合默认值",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "成对摆放、床侧净距、比例",
      "weaknesses": [
        {
          "id": "size_only_repair_loop",
          "label": "只靠尺寸修复",
          "note": "视觉语义错时，只调尺寸会进入无效回环。"
        }
      ],
      "nextTrainingTarget": "补床侧组合默认值",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补床侧组合默认值。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“成对摆放、床侧净距、比例”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补床侧组合默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“成对摆放、床侧净距、比例”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-wardrobe",
      "capabilityId": "wardrobe",
      "name": "衣柜",
      "title": "衣柜 · 训练衣柜开门净空 audit",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "focus": "开门净空、贴墙、与床通道",
      "weaknesses": [
        {
          "id": "machine_green_delivery",
          "label": "机器绿但视觉未验",
          "note": "机器审计绿灯不能直接替代用户可见验收。"
        }
      ],
      "nextTrainingTarget": "训练衣柜开门净空 audit",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：训练衣柜开门净空 audit。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“开门净空、贴墙、与床通道”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：训练衣柜开门净空 audit。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“开门净空、贴墙、与床通道”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-tv-cabinet",
      "capabilityId": "tv-cabinet",
      "name": "电视柜",
      "title": "电视柜 · 补客厅视线方向规则",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "朝向、墙面关系、电视/柜比例",
      "weaknesses": [
        {
          "id": "clone_reference_fragments",
          "label": "误克隆参考碎片",
          "note": "参考图不能被碎片化克隆为系统资产。"
        }
      ],
      "nextTrainingTarget": "补客厅视线方向规则",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补客厅视线方向规则。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“朝向、墙面关系、电视/柜比例”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补客厅视线方向规则。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“朝向、墙面关系、电视/柜比例”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-desk",
      "capabilityId": "desk",
      "name": "书桌",
      "title": "书桌 · 补书桌+椅组合训练",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "座椅空间、靠窗/靠墙偏好",
      "weaknesses": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "补书桌+椅组合训练",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补书桌+椅组合训练。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“座椅空间、靠窗/靠墙偏好”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补书桌+椅组合训练。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“座椅空间、靠窗/靠墙偏好”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-low-cabinet",
      "capabilityId": "low-cabinet",
      "name": "矮柜",
      "title": "矮柜 · 先补对象默认值",
      "priority": "P2",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "focus": "低柜高度语义、墙边摆放",
      "weaknesses": [
        {
          "id": "retrieval_hit_as_capability",
          "label": "检索命中被当能力",
          "note": "检索到素材只算参考输入，不算系统能力。"
        }
      ],
      "nextTrainingTarget": "先补对象默认值",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“低柜高度语义、墙边摆放”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“低柜高度语义、墙边摆放”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-basin",
      "capabilityId": "basin",
      "name": "洗手台",
      "title": "洗手台 · 训练卫浴对象部件表达",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "台盆、柜体、水龙头语义和卫浴墙面关系",
      "weaknesses": [
        {
          "id": "missing_furniture_parts",
          "label": "家具部件缺失",
          "note": "对象必须拆清关键部件，不应只画外轮廓。"
        }
      ],
      "nextTrainingTarget": "训练卫浴对象部件表达",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：训练卫浴对象部件表达。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“台盆、柜体、水龙头语义和卫浴墙面关系”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：训练卫浴对象部件表达。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“台盆、柜体、水龙头语义和卫浴墙面关系”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-toilet",
      "capabilityId": "toilet",
      "name": "马桶",
      "title": "马桶 · 补洁具默认净距",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "朝向、离墙尺寸、检修空间",
      "weaknesses": [
        {
          "id": "machine_size_drift_only",
          "label": "仅尺寸漂移",
          "note": "只盯尺寸漂移会漏掉语义或视觉错误。"
        }
      ],
      "nextTrainingTarget": "补洁具默认净距",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补洁具默认净距。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“朝向、离墙尺寸、检修空间”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补洁具默认净距。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“朝向、离墙尺寸、检修空间”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-stove",
      "capabilityId": "stove",
      "name": "灶台",
      "title": "灶台 · 先补厨房对象 catalog",
      "priority": "P2",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "focus": "台面、火口、厨房操作三角",
      "weaknesses": [
        {
          "id": "unsupported_or_risky",
          "label": "暂不支持或风险高",
          "note": "高风险或未支持对象应先阻塞并补常识。"
        }
      ],
      "nextTrainingTarget": "先补厨房对象 catalog",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“台面、火口、厨房操作三角”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“台面、火口、厨房操作三角”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-fridge",
      "capabilityId": "fridge",
      "name": "冰箱",
      "title": "冰箱 · 补冰箱门向和净距",
      "priority": "P2",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "focus": "门开启方向、散热间距、厨房动线",
      "weaknesses": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "补冰箱门向和净距",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“门开启方向、散热间距、厨房动线”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“门开启方向、散热间距、厨房动线”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-wall",
      "capabilityId": "wall",
      "name": "墙体绘制",
      "title": "墙体绘制 · 强化墙线重复与开口检查",
      "priority": "P0",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "闭合轮廓、墙厚、图层归类",
      "weaknesses": [
        {
          "id": "duplicate_shared_edges",
          "label": "共享边重复",
          "note": "相邻部件允许贴合，但同一 CAD 段不能重复生成。"
        }
      ],
      "nextTrainingTarget": "强化墙线重复与开口检查",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：强化墙线重复与开口检查。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“闭合轮廓、墙厚、图层归类”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：强化墙线重复与开口检查。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“闭合轮廓、墙厚、图层归类”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-door",
      "capabilityId": "door",
      "name": "门绘制",
      "title": "门绘制 · 补门向语义训练",
      "priority": "P0",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "门洞、开启弧、门扇方向",
      "weaknesses": [
        {
          "id": "plan_view_role_direction_errors",
          "label": "平面角色方向错误",
          "note": "平面图方向、入座方向和开门方向需要显式说明。"
        }
      ],
      "nextTrainingTarget": "补门向语义训练",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补门向语义训练。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“门洞、开启弧、门扇方向”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补门向语义训练。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“门洞、开启弧、门扇方向”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-window",
      "capabilityId": "window",
      "name": "窗户绘制",
      "title": "窗户绘制 · 补窗洞与墙体关系 audit",
      "priority": "P0",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "窗洞、窗线层级、墙体嵌入",
      "weaknesses": [
        {
          "id": "machine_green_delivery",
          "label": "机器绿但视觉未验",
          "note": "机器审计绿灯不能直接替代用户可见验收。"
        }
      ],
      "nextTrainingTarget": "补窗洞与墙体关系 audit",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补窗洞与墙体关系 audit。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“窗洞、窗线层级、墙体嵌入”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补窗洞与墙体关系 audit。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“窗洞、窗线层级、墙体嵌入”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-door-opening",
      "capabilityId": "door-opening",
      "name": "门洞绘制",
      "title": "门洞绘制 · 训练洞口扣减检查",
      "priority": "P1",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "洞口扣减、门套语义、墙段连续",
      "weaknesses": [
        {
          "id": "duplicate_shared_edges",
          "label": "共享边重复",
          "note": "相邻部件允许贴合，但同一 CAD 段不能重复生成。"
        }
      ],
      "nextTrainingTarget": "训练洞口扣减检查",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：训练洞口扣减检查。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“洞口扣减、门套语义、墙段连续”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：训练洞口扣减检查。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“洞口扣减、门套语义、墙段连续”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-window-opening",
      "capabilityId": "window-opening",
      "name": "窗洞绘制",
      "title": "窗洞绘制 · 补窗洞标准语义",
      "priority": "P1",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "窗洞宽度、离地语义、墙内关系",
      "weaknesses": [
        {
          "id": "machine_size_drift_only",
          "label": "仅尺寸漂移",
          "note": "只盯尺寸漂移会漏掉语义或视觉错误。"
        }
      ],
      "nextTrainingTarget": "补窗洞标准语义",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补窗洞标准语义。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“窗洞宽度、离地语义、墙内关系”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补窗洞标准语义。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“窗洞宽度、离地语义、墙内关系”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-room-outline",
      "capabilityId": "room-outline",
      "name": "房间轮廓绘制",
      "title": "房间轮廓绘制 · 强化房间轮廓 validate",
      "priority": "P1",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_intent",
      "ownerAgentName": "需求拆解智能体",
      "responsibleAgentIds": [
        "pipeline_intent",
        "pipeline_context_curator",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_context_curator",
          "name": "上下文整理智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_context_curator",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "房间闭合、基点、尺寸约束",
      "weaknesses": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "强化房间轮廓 validate",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：强化房间轮廓 validate。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“房间闭合、基点、尺寸约束”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：强化房间轮廓 validate。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“房间闭合、基点、尺寸约束”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-column",
      "capabilityId": "column",
      "name": "柱子绘制",
      "title": "柱子绘制 · 补柱子对象规范",
      "priority": "P2",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "结构柱尺寸、图层、与墙体关系",
      "weaknesses": [
        {
          "id": "retrieval_hit_as_capability",
          "label": "检索命中被当能力",
          "note": "检索到素材只算参考输入，不算系统能力。"
        }
      ],
      "nextTrainingTarget": "补柱子对象规范",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“结构柱尺寸、图层、与墙体关系”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“结构柱尺寸、图层、与墙体关系”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-furniture-layout",
      "capabilityId": "furniture-layout",
      "name": "基础家具摆放",
      "title": "基础家具摆放 · 开客厅/卧室组合训练",
      "priority": "P2",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_learning_promoter"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        },
        {
          "id": "pipeline_learning_promoter",
          "name": "训练沉淀智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_learning_promoter"
      ],
      "focus": "组合关系、通道、朝向和避让",
      "weaknesses": [
        {
          "id": "visual_fail_size_only_repair",
          "label": "视觉失败却只调尺寸",
          "note": "视觉失败时应回到视觉语义智能体。"
        }
      ],
      "nextTrainingTarget": "开客厅/卧室组合训练",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“组合关系、通道、朝向和避让”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "planned",
          "label": "计划中",
          "note": "只有经过 promotion gate、证据边界和回归检查后，才允许进入自产资产或通用规则。"
        }
      },
      "trainingObjective": "围绕“组合关系、通道、朝向和避让”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-dimension",
      "capabilityId": "dimension",
      "name": "简单尺寸标注",
      "title": "简单尺寸标注 · 补尺寸标注检查器",
      "priority": "P1",
      "kind": "annotation",
      "kindLabel": "标注训练",
      "group": "标注表达",
      "matrixGroup": "标注表达",
      "ownerAgentId": "pipeline_delivery",
      "ownerAgentName": "交付汇报智能体",
      "responsibleAgentIds": [
        "pipeline_delivery",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_delivery",
          "name": "交付汇报智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_delivery"
      ],
      "focus": "标注对象、尺寸线位置、比例和避让",
      "weaknesses": [
        {
          "id": "missing_annotation",
          "label": "标注缺失",
          "note": "标注训练要明确对象、位置、比例和避让。"
        }
      ],
      "nextTrainingTarget": "补尺寸标注检查器",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补尺寸标注检查器。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“标注对象、尺寸线位置、比例和避让”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补尺寸标注检查器。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“标注对象、尺寸线位置、比例和避让”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-text",
      "capabilityId": "text",
      "name": "简单文字标注",
      "title": "简单文字标注 · 训练对象名称标注",
      "priority": "P1",
      "kind": "annotation",
      "kindLabel": "标注训练",
      "group": "标注表达",
      "matrixGroup": "标注表达",
      "ownerAgentId": "pipeline_delivery",
      "ownerAgentName": "交付汇报智能体",
      "responsibleAgentIds": [
        "pipeline_delivery",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_delivery",
          "name": "交付汇报智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_delivery"
      ],
      "focus": "文字内容、图层、与对象关联",
      "weaknesses": [
        {
          "id": "missing_annotation",
          "label": "标注缺失",
          "note": "标注训练要明确对象、位置、比例和避让。"
        }
      ],
      "nextTrainingTarget": "训练对象名称标注",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：训练对象名称标注。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“文字内容、图层、与对象关联”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：训练对象名称标注。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“文字内容、图层、与对象关联”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-layers",
      "capabilityId": "layers",
      "name": "基础图层归类",
      "title": "基础图层归类 · 补图层归类审计",
      "priority": "P2",
      "kind": "annotation",
      "kindLabel": "标注训练",
      "group": "标注表达",
      "matrixGroup": "标注表达",
      "ownerAgentId": "pipeline_audit",
      "ownerAgentName": "机器审计智能体",
      "responsibleAgentIds": [
        "pipeline_audit",
        "pipeline_execute",
        "pipeline_delivery"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_delivery",
          "name": "交付汇报智能体"
        }
      ],
      "pipeline": [
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_delivery"
      ],
      "focus": "CODEX_PREVIEW、正式图层保护、对象分层",
      "weaknesses": [
        {
          "id": "formal_layer_write_risk",
          "label": "正式图层写入风险",
          "note": "训练默认只写 CODEX_PREVIEW，不碰正式图层。"
        }
      ],
      "nextTrainingTarget": "补图层归类审计",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“CODEX_PREVIEW、正式图层保护、对象分层”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“CODEX_PREVIEW、正式图层保护、对象分层”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    }
  ],
  "agentProfiles": [
    {
      "id": "residential",
      "name": "家装场景智能体",
      "sourceName": "residential",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "primary_training",
      "statusLabel": "主训中",
      "trainingRole": "你负责把家装用户的白话需求、房间语境、家具常识和用户反馈，转成流水线可以继续训练的中文场景规则。",
      "roleSummary": "你是家装主训场景智能体，负责把用户的家装白话、房间偏好和家具常识转成可被训练流水线消费的中文规则约束。",
      "promptContractId": "contract-residential",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补客厅视线方向规则"
        },
        {
          "id": "desk",
          "name": "书桌",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补书桌+椅组合训练"
        },
        {
          "id": "low-cabinet",
          "name": "矮柜",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补对象默认值"
        },
        {
          "id": "basin",
          "name": "洗手台",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "toilet",
          "name": "马桶",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补洁具默认净距"
        },
        {
          "id": "stove",
          "name": "灶台",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补厨房对象 catalog"
        },
        {
          "id": "fridge",
          "name": "冰箱",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补冰箱门向和净距"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-tea-table",
          "capabilityId": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "program-dining-table",
          "capabilityId": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "program-dining-chair",
          "capabilityId": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "program-nightstand",
          "capabilityId": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "program-wardrobe",
          "capabilityId": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "program-tv-cabinet",
          "capabilityId": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "nextTrainingTarget": "补客厅视线方向规则"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 100,
        "note": "关联 15 个训练计划项，其中 P0 5 个；表示训练表单覆盖度。",
        "basis": "15 个训练计划 / P0 5 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 68,
        "note": "训练状态：主训中。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：主训中",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 100,
          "note": "关联 15 个训练计划项，其中 P0 5 个；表示训练表单覆盖度。",
          "basis": "15 个训练计划 / P0 5 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 68,
          "note": "训练状态：主训中。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：主训中",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/residential/agent.json",
        "agents/residential/rules.md"
      ],
      "operation": {
        "role": "你负责把家装用户的白话需求、房间语境、家具常识和用户反馈，转成流水线可以继续训练的中文场景规则。",
        "inputs": [
          "用户原话和本轮训练目标",
          "家装场景规则、对象默认值和上轮反馈",
          "当前能力项的风险点和下一轮可验收目标"
        ],
        "outputs": [
          "场景词汇和对象常识约束",
          "家具方向、贴墙、净距、组合关系等可训练偏好",
          "需要交给视觉语义或需求拆解智能体的提示"
        ],
        "passGate": [
          {
            "label": "边界清楚",
            "value": "只声明家装场景规则，不代替执行、审计或真实 CAD 证明。"
          }
        ],
        "mustNot": [
          "不得把场景偏好写成跨场景 Core 规则。",
          "不得把用户一句话脑补成确定尺寸或正式落图结果。"
        ],
        "usesCore": [
          "家装规则读取",
          "对象默认值引用",
          "用户反馈归因",
          "训练目标拆分"
        ],
        "optimizationTips": [
          "把用户指出的家装常识错误沉淀到 rules.md，而不是只改单个案例。",
          "优先补家具方向、贴墙、通行净距和部件语义，因为这些最影响用户观感。",
          "每次训练后检查是否需要新增可机器审计的规则。"
        ]
      }
    },
    {
      "id": "commercial_fitout",
      "name": "商业空间智能体",
      "sourceName": "commercial_fitout",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是商业空间场景智能体，保留零售、接待、会议室和开放办公等规则脚手架，当前不并行主训。",
      "roleSummary": "你是商业空间场景智能体，保留零售、接待、会议室和开放办公等规则脚手架，当前不并行主训。",
      "promptContractId": "contract-commercial_fitout",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/commercial_fitout/agent.json"
      ],
      "operation": {
        "role": "你是商业空间场景智能体，保留零售、接待、会议室和开放办公等规则脚手架，当前不并行主训。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "office",
      "name": "办公场景智能体",
      "sourceName": "office",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是办公场景智能体，保留办公布局、工位和会议空间偏好，当前只作为后续训练候选。",
      "roleSummary": "你是办公场景智能体，保留办公布局、工位和会议空间偏好，当前只作为后续训练候选。",
      "promptContractId": "contract-office",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/office/agent.json"
      ],
      "operation": {
        "role": "你是办公场景智能体，保留办公布局、工位和会议空间偏好，当前只作为后续训练候选。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "restaurant",
      "name": "餐饮场景智能体",
      "sourceName": "restaurant",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是餐饮场景智能体，保留堂食区、服务动线和入口避让常识，当前不并行扩面。",
      "roleSummary": "你是餐饮场景智能体，保留堂食区、服务动线和入口避让常识，当前不并行扩面。",
      "promptContractId": "contract-restaurant",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/restaurant/agent.json"
      ],
      "operation": {
        "role": "你是餐饮场景智能体，保留堂食区、服务动线和入口避让常识，当前不并行扩面。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "exhibition",
      "name": "展陈场景智能体",
      "sourceName": "exhibition",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是展陈场景智能体，保留展台、展墙和参观路线规则，当前不并行主训。",
      "roleSummary": "你是展陈场景智能体，保留展台、展墙和参观路线规则，当前不并行主训。",
      "promptContractId": "contract-exhibition",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/exhibition/agent.json"
      ],
      "operation": {
        "role": "你是展陈场景智能体，保留展台、展墙和参观路线规则，当前不并行主训。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "healthcare",
      "name": "医疗场景智能体",
      "sourceName": "healthcare",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是医疗场景智能体，保留医疗空间脚手架和安全边界，当前不并行主训。",
      "roleSummary": "你是医疗场景智能体，保留医疗空间脚手架和安全边界，当前不并行主训。",
      "promptContractId": "contract-healthcare",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/healthcare/agent.json"
      ],
      "operation": {
        "role": "你是医疗场景智能体，保留医疗空间脚手架和安全边界，当前不并行主训。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "custom",
      "name": "自定义场景智能体",
      "sourceName": "custom",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是自定义场景智能体，用于跨场景或模糊需求占位，默认需要人工确认边界。",
      "roleSummary": "你是自定义场景智能体，用于跨场景或模糊需求占位，默认需要人工确认边界。",
      "promptContractId": "contract-custom",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/custom/agent.json"
      ],
      "operation": {
        "role": "你是自定义场景智能体，用于跨场景或模糊需求占位，默认需要人工确认边界。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "pipeline_context_curator",
      "name": "上下文整理智能体",
      "sourceName": "pipeline_context_curator",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责在训练开始前收束上下文，把当前案例、用户反馈、历史失败和待训练目标整理成干净的输入包。",
      "roleSummary": "你是上下文整理智能体，负责在每一轮训练开始前收束案例状态、用户反馈和历史噪声，避免后续智能体读错上下文。",
      "promptContractId": "contract-pipeline_context_curator",
      "ownedCapabilities": [
        {
          "id": "room-outline",
          "name": "房间轮廓绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化房间轮廓 validate"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-room-outline",
          "capabilityId": "room-outline",
          "name": "房间轮廓绘制",
          "priority": "P1",
          "nextTrainingTarget": "强化房间轮廓 validate"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 33,
        "note": "关联 1 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "1 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 33,
          "note": "关联 1 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "1 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_context_curator/agent.json"
      ],
      "operation": {
        "role": "你负责在训练开始前收束上下文，把当前案例、用户反馈、历史失败和待训练目标整理成干净的输入包。",
        "inputs": [
          "当前案例目录和轮次记录",
          "用户最新反馈",
          "训练计划表单中的能力项与失败类型",
          "已有规则、资产和审计结果"
        ],
        "outputs": [
          "本轮上下文包",
          "本轮必须保留和必须忽略的信息",
          "需要交给后续智能体的阻塞点或缺口"
        ],
        "passGate": [
          {
            "label": "不带旧噪声",
            "value": "过期计划、无关失败和已废弃假设不能继续传下去。"
          }
        ],
        "mustNot": [
          "不得把历史结论当成本轮用户确认。",
          "不得在上下文不足时直接推动执行。"
        ],
        "usesCore": [
          "案例上下文读取",
          "反馈摘要",
          "训练状态过滤",
          "源文件索引"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_asset_retriever",
      "name": "资产检索智能体",
      "sourceName": "pipeline_asset_retriever",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责在落图前检索标准图库、对象默认值、自产资产、常识规则和历史失败，并明确哪些只是参考证据。",
      "roleSummary": "你是资产检索智能体，负责在落图前检索标准图库、常识、自产资产和历史失败，并明确哪些只是参考证据。",
      "promptContractId": "contract-pipeline_asset_retriever",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补客厅视线方向规则"
        },
        {
          "id": "desk",
          "name": "书桌",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补书桌+椅组合训练"
        },
        {
          "id": "low-cabinet",
          "name": "矮柜",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补对象默认值"
        },
        {
          "id": "basin",
          "name": "洗手台",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "toilet",
          "name": "马桶",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补洁具默认净距"
        },
        {
          "id": "stove",
          "name": "灶台",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补厨房对象 catalog"
        },
        {
          "id": "fridge",
          "name": "冰箱",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补冰箱门向和净距"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-tea-table",
          "capabilityId": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "program-dining-table",
          "capabilityId": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "program-dining-chair",
          "capabilityId": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "program-nightstand",
          "capabilityId": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "program-wardrobe",
          "capabilityId": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "program-tv-cabinet",
          "capabilityId": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "nextTrainingTarget": "补客厅视线方向规则"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 100,
        "note": "关联 15 个训练计划项，其中 P0 5 个；表示训练表单覆盖度。",
        "basis": "15 个训练计划 / P0 5 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 100,
          "note": "关联 15 个训练计划项，其中 P0 5 个；表示训练表单覆盖度。",
          "basis": "15 个训练计划 / P0 5 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_asset_retriever/agent.json"
      ],
      "operation": {
        "role": "你负责在落图前检索标准图库、对象默认值、自产资产、常识规则和历史失败，并明确哪些只是参考证据。",
        "inputs": [
          "用户需求和当前能力项",
          "标准图库、原始图库和自产资产入口",
          "对象默认值、场景规则和历史失败记录"
        ],
        "outputs": [
          "资产与常识检索包",
          "命中的参考资料及其可信边界",
          "缺失字段、未知项和不能晋升系统能力的说明"
        ],
        "passGate": [
          {
            "label": "边界声明",
            "value": "命中图库或参考资料只算上游证据，不算 CAD 能力通过。"
          }
        ],
        "mustNot": [
          "不得把检索命中说成能力证明。",
          "不得复制厂商资产几何。",
          "不得跳过视觉部件契约。"
        ],
        "usesCore": [
          "标准图库扫描",
          "参考资产接收",
          "对象默认值检索",
          "历史失败检索"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_orchestrator",
      "name": "流程编排智能体",
      "sourceName": "pipeline_orchestrator",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责决定本轮训练该停在哪个阶段、下一步调用哪个智能体，以及是否需要阻塞、回环或进入沉淀。",
      "roleSummary": "你是流程编排智能体，负责判断当前训练应停在哪个阶段、下一步该调用谁，以及是否需要阻塞或回环。",
      "promptContractId": "contract-pipeline_orchestrator",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_orchestrator/agent.json"
      ],
      "operation": {
        "role": "你负责决定本轮训练该停在哪个阶段、下一步调用哪个智能体，以及是否需要阻塞、回环或进入沉淀。",
        "inputs": [
          "上下文包",
          "训练计划状态",
          "各智能体产物和阻塞说明",
          "证据边界与用户反馈"
        ],
        "outputs": [
          "下一步智能体调用顺序",
          "阻塞原因或回环原因",
          "是否允许进入落图、审计或沉淀的判断"
        ],
        "passGate": [
          {
            "label": "阶段清晰",
            "value": "必须说明当前停在计划、Prompt、案例训练、反馈通过还是已沉淀。"
          }
        ],
        "mustNot": [
          "不得把页面状态当成真实通过。",
          "不得跳过失败归因。"
        ],
        "usesCore": [
          "训练阶段判断",
          "流水线调度",
          "阻塞判定",
          "回环策略"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_visual_intent",
      "name": "视觉语义智能体",
      "sourceName": "pipeline_visual_intent",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责把用户白话、参考图和场景常识拆成部件级视觉契约，重点说明方向、部件、闭合关系和禁止偷懒模式。",
      "roleSummary": "你是视觉语义智能体，负责把白话和参考图拆成部件级视觉契约，尤其要说明方向、部件、闭合关系和禁止偷懒模式。",
      "promptContractId": "contract-pipeline_visual_intent",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 53,
        "note": "关联 2 个训练计划项，其中 P0 2 个；表示训练表单覆盖度。",
        "basis": "2 个训练计划 / P0 2 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 53,
          "note": "关联 2 个训练计划项，其中 P0 2 个；表示训练表单覆盖度。",
          "basis": "2 个训练计划 / P0 2 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_visual_intent/agent.json"
      ],
      "operation": {
        "role": "你负责把用户白话、参考图和场景常识拆成部件级视觉契约，重点说明方向、部件、闭合关系和禁止偷懒模式。",
        "inputs": [
          "用户白话需求",
          "参考截图或目标图",
          "资产与常识检索包",
          "场景规则和对象默认值"
        ],
        "outputs": [
          "部件级视觉契约",
          "方向、层级、闭合状态和贴合关系",
          "必须绘制与禁止绘制的视觉模式"
        ],
        "passGate": [
          {
            "label": "部件可追踪",
            "value": "关键部件要有编号、角色、形状和闭合状态。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得用外框盒子冒充真实部件。",
          "不得把修尺寸当成修视觉语义。"
        ],
        "usesCore": [
          "参考图语义拆解",
          "部件契约生成",
          "方向语义判断",
          "禁止模式生成"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_intent",
      "name": "需求拆解智能体",
      "sourceName": "pipeline_intent",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责把白话和视觉契约整理成可校验的结构化意图，并判断能不能进入 CAD_PLAN。",
      "roleSummary": "你是需求拆解智能体，负责把白话和视觉契约整理成可校验的结构化意图，并决定能否进入 CAD_PLAN。",
      "promptContractId": "contract-pipeline_intent",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补客厅视线方向规则"
        },
        {
          "id": "desk",
          "name": "书桌",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补书桌+椅组合训练"
        },
        {
          "id": "low-cabinet",
          "name": "矮柜",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补对象默认值"
        },
        {
          "id": "basin",
          "name": "洗手台",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "toilet",
          "name": "马桶",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补洁具默认净距"
        },
        {
          "id": "stove",
          "name": "灶台",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补厨房对象 catalog"
        },
        {
          "id": "fridge",
          "name": "冰箱",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补冰箱门向和净距"
        },
        {
          "id": "wall",
          "name": "墙体绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化墙线重复与开口检查"
        },
        {
          "id": "door",
          "name": "门绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补门向语义训练"
        },
        {
          "id": "window",
          "name": "窗户绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞与墙体关系 audit"
        },
        {
          "id": "door-opening",
          "name": "门洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练洞口扣减检查"
        },
        {
          "id": "window-opening",
          "name": "窗洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞标准语义"
        },
        {
          "id": "room-outline",
          "name": "房间轮廓绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化房间轮廓 validate"
        },
        {
          "id": "column",
          "name": "柱子绘制",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补柱子对象规范"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        },
        {
          "id": "dimension",
          "name": "简单尺寸标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补尺寸标注检查器"
        },
        {
          "id": "text",
          "name": "简单文字标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练对象名称标注"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-tea-table",
          "capabilityId": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "program-dining-table",
          "capabilityId": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "program-dining-chair",
          "capabilityId": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "program-nightstand",
          "capabilityId": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "program-wardrobe",
          "capabilityId": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "program-tv-cabinet",
          "capabilityId": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "nextTrainingTarget": "补客厅视线方向规则"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 100,
        "note": "关联 24 个训练计划项，其中 P0 8 个；表示训练表单覆盖度。",
        "basis": "24 个训练计划 / P0 8 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 100,
          "note": "关联 24 个训练计划项，其中 P0 8 个；表示训练表单覆盖度。",
          "basis": "24 个训练计划 / P0 8 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_intent/agent.json"
      ],
      "operation": {
        "role": "你负责把白话和视觉契约整理成可校验的结构化意图，并判断能不能进入 CAD_PLAN。",
        "inputs": [
          "上下文包",
          "视觉契约",
          "场景规则",
          "资产与常识检索结果",
          "本轮训练目标"
        ],
        "outputs": [
          "结构化意图",
          "CAD_PLAN 候选或暂缓说明",
          "审计清单和不可执行原因"
        ],
        "passGate": [
          {
            "label": "意图完整",
            "value": "对象、尺寸、方向、基点、图层和证据边界要能被下一步读取。"
          }
        ],
        "mustNot": [
          "不得把自然语言直接跳到 CAD。",
          "不得省略 validate 和 dry-run 前置条件。"
        ],
        "usesCore": [
          "结构化意图生成",
          "CAD_PLAN 生成前检查",
          "Schema 对齐",
          "审计清单生成"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_execute",
      "name": "落图执行智能体",
      "sourceName": "pipeline_execute",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责把已经声明并校验过的 CAD_PLAN 或 visual_parts 落到 CODEX_PREVIEW，只执行计划内对象，不临场发明。",
      "roleSummary": "你是落图执行智能体，只能按已声明的 CAD_PLAN 或 visual_parts 写入 CODEX_PREVIEW，不临场发明对象。",
      "promptContractId": "contract-pipeline_execute",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补客厅视线方向规则"
        },
        {
          "id": "desk",
          "name": "书桌",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补书桌+椅组合训练"
        },
        {
          "id": "basin",
          "name": "洗手台",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "toilet",
          "name": "马桶",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补洁具默认净距"
        },
        {
          "id": "wall",
          "name": "墙体绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化墙线重复与开口检查"
        },
        {
          "id": "door",
          "name": "门绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补门向语义训练"
        },
        {
          "id": "window",
          "name": "窗户绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞与墙体关系 audit"
        },
        {
          "id": "door-opening",
          "name": "门洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练洞口扣减检查"
        },
        {
          "id": "window-opening",
          "name": "窗洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞标准语义"
        },
        {
          "id": "room-outline",
          "name": "房间轮廓绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化房间轮廓 validate"
        },
        {
          "id": "column",
          "name": "柱子绘制",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补柱子对象规范"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        },
        {
          "id": "dimension",
          "name": "简单尺寸标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补尺寸标注检查器"
        },
        {
          "id": "text",
          "name": "简单文字标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练对象名称标注"
        },
        {
          "id": "layers",
          "name": "基础图层归类",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补图层归类审计"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-tea-table",
          "capabilityId": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "program-dining-table",
          "capabilityId": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "program-dining-chair",
          "capabilityId": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "program-nightstand",
          "capabilityId": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "program-tv-cabinet",
          "capabilityId": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "nextTrainingTarget": "补客厅视线方向规则"
        },
        {
          "id": "program-desk",
          "capabilityId": "desk",
          "name": "书桌",
          "priority": "P1",
          "nextTrainingTarget": "补书桌+椅组合训练"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 100,
        "note": "关联 21 个训练计划项，其中 P0 8 个；表示训练表单覆盖度。",
        "basis": "21 个训练计划 / P0 8 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 100,
          "note": "关联 21 个训练计划项，其中 P0 8 个；表示训练表单覆盖度。",
          "basis": "21 个训练计划 / P0 8 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_execute/agent.json"
      ],
      "operation": {
        "role": "你负责把已经声明并校验过的 CAD_PLAN 或 visual_parts 落到 CODEX_PREVIEW，只执行计划内对象，不临场发明。",
        "inputs": [
          "通过校验的 CAD_PLAN 或 visual_parts",
          "可执行尺寸、基点、图层和对象清单",
          "write guard 与预览图层约束"
        ],
        "outputs": [
          "执行摘要",
          "创建对象、图层和 handles 回读线索",
          "未执行、阻塞或需审计的说明"
        ],
        "passGate": [
          {
            "label": "只写预览",
            "value": "默认只写 CODEX_PREVIEW，不保存或覆盖 DWG。"
          }
        ],
        "mustNot": [
          "不得保存或覆盖 DWG。",
          "不得修改正式图层。",
          "不得跳过 validate / dry-run。",
          "不得绘制未在计划中声明的结构。"
        ],
        "usesCore": [
          "CAD_PLAN 执行入口",
          "CODEX_PREVIEW 写入保护",
          "AutoCAD COM / CAD-MCP 执行桥接",
          "执行摘要回写"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_audit",
      "name": "机器审计智能体",
      "sourceName": "pipeline_audit",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责把机器审计、几何回读、图层、标注和用户可见效果分开判断，指出本轮是否还需要修。",
      "roleSummary": "你是机器审计智能体，负责分开判断几何、语义、图层、标注和用户可见效果，不能把机器绿当成最终验收。",
      "promptContractId": "contract-pipeline_audit",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "basin",
          "name": "洗手台",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "wall",
          "name": "墙体绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化墙线重复与开口检查"
        },
        {
          "id": "door",
          "name": "门绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补门向语义训练"
        },
        {
          "id": "window",
          "name": "窗户绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞与墙体关系 audit"
        },
        {
          "id": "door-opening",
          "name": "门洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练洞口扣减检查"
        },
        {
          "id": "window-opening",
          "name": "窗洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞标准语义"
        },
        {
          "id": "room-outline",
          "name": "房间轮廓绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化房间轮廓 validate"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        },
        {
          "id": "dimension",
          "name": "简单尺寸标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补尺寸标注检查器"
        },
        {
          "id": "layers",
          "name": "基础图层归类",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补图层归类审计"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-tea-table",
          "capabilityId": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "program-dining-table",
          "capabilityId": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "program-wardrobe",
          "capabilityId": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "program-basin",
          "capabilityId": "basin",
          "name": "洗手台",
          "priority": "P1",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "program-wall",
          "capabilityId": "wall",
          "name": "墙体绘制",
          "priority": "P0",
          "nextTrainingTarget": "强化墙线重复与开口检查"
        },
        {
          "id": "program-door",
          "capabilityId": "door",
          "name": "门绘制",
          "priority": "P0",
          "nextTrainingTarget": "补门向语义训练"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 100,
        "note": "关联 15 个训练计划项，其中 P0 7 个；表示训练表单覆盖度。",
        "basis": "15 个训练计划 / P0 7 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 100,
          "note": "关联 15 个训练计划项，其中 P0 7 个；表示训练表单覆盖度。",
          "basis": "15 个训练计划 / P0 7 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_audit/agent.json"
      ],
      "operation": {
        "role": "你负责把机器审计、几何回读、图层、标注和用户可见效果分开判断，指出本轮是否还需要修。",
        "inputs": [
          "执行摘要",
          "handles 回读或截图",
          "CAD_PLAN / visual_parts",
          "成功门槛和不通过边界"
        ],
        "outputs": [
          "机器审计结论",
          "用户可见风险",
          "需要修复的根因和下一步证据要求"
        ],
        "passGate": [
          {
            "label": "不混口径",
            "value": "机器绿、用户认可和表 C 指标必须分开说。"
          }
        ],
        "mustNot": [
          "不得把机器审计通过当最终验收。",
          "不得只报数字不说明用户该看哪里。"
        ],
        "usesCore": [
          "几何回读",
          "截图检查",
          "图层审计",
          "失败归因"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_repair",
      "name": "修复回环智能体",
      "sourceName": "pipeline_repair",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责基于审计根因做最小修复，把修复说明回送执行和审计，而不是无边界重画。",
      "roleSummary": "你是修复回环智能体，负责基于根因做最小修复，并把修复后的结果重新送回执行和审计。",
      "promptContractId": "contract-pipeline_repair",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 3 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 3 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 39,
        "note": "关联 1 个训练计划项，其中 P0 1 个；表示训练表单覆盖度。",
        "basis": "1 个训练计划 / P0 1 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 3 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 3 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 39,
          "note": "关联 1 个训练计划项，其中 P0 1 个；表示训练表单覆盖度。",
          "basis": "1 个训练计划 / P0 1 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_repair/agent.json"
      ],
      "operation": {
        "role": "你负责基于审计根因做最小修复，把修复说明回送执行和审计，而不是无边界重画。",
        "inputs": [
          "审计失败点",
          "原始 CAD_PLAN / visual_parts",
          "可修复范围和禁止改动范围",
          "用户反馈"
        ],
        "outputs": [
          "修复计划",
          "修改后的结构化意图或 CAD_PLAN",
          "需要重新执行与审计的证据清单"
        ],
        "passGate": [
          {
            "label": "最小修复",
            "value": "只改根因相关内容，不扩大范围。"
          }
        ],
        "mustNot": [
          "不得靠反复改尺寸掩盖语义错误。",
          "不得把未验证修复交付给用户。"
        ],
        "usesCore": [
          "失败根因定位",
          "CAD_PLAN 最小修复",
          "回归审计触发"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_delivery",
      "name": "交付汇报智能体",
      "sourceName": "pipeline_delivery",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责用低噪声中文交付本轮训练结论、证据路径、没证明的边界和用户最该验收的位置。",
      "roleSummary": "你是交付汇报智能体，负责用低噪声中文说明本轮结论、证据边界和用户最该验收的位置。",
      "promptContractId": "contract-pipeline_delivery",
      "ownedCapabilities": [
        {
          "id": "dimension",
          "name": "简单尺寸标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补尺寸标注检查器"
        },
        {
          "id": "text",
          "name": "简单文字标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练对象名称标注"
        },
        {
          "id": "layers",
          "name": "基础图层归类",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补图层归类审计"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-dimension",
          "capabilityId": "dimension",
          "name": "简单尺寸标注",
          "priority": "P1",
          "nextTrainingTarget": "补尺寸标注检查器"
        },
        {
          "id": "program-text",
          "capabilityId": "text",
          "name": "简单文字标注",
          "priority": "P1",
          "nextTrainingTarget": "训练对象名称标注"
        },
        {
          "id": "program-layers",
          "capabilityId": "layers",
          "name": "基础图层归类",
          "priority": "P2",
          "nextTrainingTarget": "补图层归类审计"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 49,
        "note": "关联 3 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "3 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 49,
          "note": "关联 3 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "3 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_delivery/agent.json"
      ],
      "operation": {
        "role": "你负责用低噪声中文交付本轮训练结论、证据路径、没证明的边界和用户最该验收的位置。",
        "inputs": [
          "审计结果",
          "截图或回读证据",
          "训练目标",
          "失败沉淀建议",
          "用户反馈入口"
        ],
        "outputs": [
          "本轮结论",
          "相对上一轮变化",
          "证据证明了什么、没证明什么",
          "用户验收重点"
        ],
        "passGate": [
          {
            "label": "先说结论",
            "value": "训练期交付先讲本轮结果，再讲证据和边界。"
          }
        ],
        "mustNot": [
          "不得用表格堆满普通训练交付。",
          "不得暗示真实 CAD 能力已经由训练页证明。"
        ],
        "usesCore": [
          "训练交付模板",
          "证据路径整理",
          "用户验收提示",
          "边界说明"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_learning_promoter",
      "name": "训练沉淀智能体",
      "sourceName": "pipeline_learning_promoter",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责把失败、通过经验和用户反馈分流到案例反馈、场景规则、pipeline 规则、Core 检查器或系统资产库。",
      "roleSummary": "你是训练沉淀智能体，负责把失败和用户反馈分流到案例、场景规则、pipeline、Core 检查器或系统资产库。",
      "promptContractId": "contract-pipeline_learning_promoter",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-furniture-layout",
          "capabilityId": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 47,
        "note": "关联 2 个训练计划项，其中 P0 1 个；表示训练表单覆盖度。",
        "basis": "2 个训练计划 / P0 1 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 47,
          "note": "关联 2 个训练计划项，其中 P0 1 个；表示训练表单覆盖度。",
          "basis": "2 个训练计划 / P0 1 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_learning_promoter/agent.json"
      ],
      "operation": {
        "role": "你负责把失败、通过经验和用户反馈分流到案例反馈、场景规则、pipeline 规则、Core 检查器或系统资产库。",
        "inputs": [
          "审计与用户反馈",
          "失败根因",
          "是否重复出现",
          "可晋升的检查器或资产候选"
        ],
        "outputs": [
          "沉淀位置建议",
          "下一轮 Prompt 调整点",
          "是否允许晋升规则、测试或资产库的判断"
        ],
        "passGate": [
          {
            "label": "先分层",
            "value": "单案例问题留在案例，重复问题才考虑规则或 Core。"
          }
        ],
        "mustNot": [
          "不得把一次失败直接污染通用规则。",
          "不得把参考图库直接晋升自产资产。"
        ],
        "usesCore": [
          "训练错误台账",
          "场景规则沉淀",
          "Core 检查器候选",
          "系统资产晋升判断"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "demand_side_roles",
      "name": "需求侧角色智能体",
      "sourceName": "demand_side_roles",
      "group": "demand",
      "groupLabel": "需求侧角色",
      "status": "data_only",
      "statusLabel": "仅数据角色",
      "trainingRole": "你负责生成更像真实用户的训练需求、角色口吻和 benchmark 场景，只作为输入数据，不参与 CAD 执行。",
      "roleSummary": "你是需求侧角色数据智能体，只负责生成更像真实用户的训练需求和 benchmark，不直接参与 CAD 执行。",
      "promptContractId": "contract-demand_side_roles",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 3 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 3 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 34,
        "note": "训练状态：仅数据角色。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：仅数据角色",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 3 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 3 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 34,
          "note": "训练状态：仅数据角色。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：仅数据角色",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/demand_side_roles/agent.json"
      ],
      "operation": {
        "role": "你负责生成更像真实用户的训练需求、角色口吻和 benchmark 场景，只作为输入数据，不参与 CAD 执行。",
        "inputs": [
          "场景 ID",
          "用户角色",
          "需求焦点",
          "样例请求和验收偏好"
        ],
        "outputs": [
          "自然语言训练需求",
          "用户角色画像",
          "能力目标和验收关注点"
        ],
        "passGate": [
          {
            "label": "用途边界",
            "value": "只生成需求，不直接绘图，也不替代真实用户反馈。"
          }
        ],
        "mustNot": [
          "不得当作执行智能体。",
          "不得替代真实用户反馈。"
        ],
        "usesCore": [
          "需求样本生成",
          "角色口吻生成",
          "benchmark 场景生成"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    }
  ],
  "promptContracts": [
    {
      "id": "contract-residential",
      "agentId": "residential",
      "agentName": "家装场景智能体",
      "sourceName": "residential",
      "promptSummary": "你是家装主训场景智能体，负责把用户的家装白话、房间偏好和家具常识转成可被训练流水线消费的中文规则约束。",
      "roleSetting": "你负责把家装用户的白话需求、房间语境、家具常识和用户反馈，转成流水线可以继续训练的中文场景规则。",
      "responsibilityBoundary": [
        "负责提供场景词汇、对象常识、默认偏好和用户反馈教训。",
        "不直接执行 CAD，也不替代流水线里的审计、修复和交付。",
        "适合训练用户白话到场景规则的映射，例如家具方向、贴墙和净距。"
      ],
      "inputRequirements": [
        "用户原话和本轮训练目标",
        "家装场景规则、对象默认值和上轮反馈",
        "当前能力项的风险点和下一轮可验收目标"
      ],
      "outputFormat": [
        "场景词汇和对象常识约束",
        "家具方向、贴墙、净距、组合关系等可训练偏好",
        "需要交给视觉语义或需求拆解智能体的提示"
      ],
      "hardGates": [
        {
          "label": "边界清楚",
          "value": "只声明家装场景规则，不代替执行、审计或真实 CAD 证明。"
        }
      ],
      "mustNot": [
        "不得把场景偏好写成跨场景 Core 规则。",
        "不得把用户一句话脑补成确定尺寸或正式落图结果。"
      ],
      "callCapabilities": [
        "家装规则读取",
        "对象默认值引用",
        "用户反馈归因",
        "训练目标拆分"
      ],
      "adjustablePromptPoints": [
        "把用户指出的家装常识错误沉淀到 rules.md，而不是只改单个案例。",
        "优先补家具方向、贴墙、通行净距和部件语义，因为这些最影响用户观感。",
        "每次训练后检查是否需要新增可机器审计的规则。"
      ],
      "sourceRefs": [
        {
          "path": "agents/residential/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        },
        {
          "path": "agents/residential/rules.md",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-commercial_fitout",
      "agentId": "commercial_fitout",
      "agentName": "商业空间智能体",
      "sourceName": "commercial_fitout",
      "promptSummary": "你是商业空间场景智能体，保留零售、接待、会议室和开放办公等规则脚手架，当前不并行主训。",
      "roleSetting": "你是商业空间场景智能体，保留零售、接待、会议室和开放办公等规则脚手架，当前不并行主训。",
      "responsibilityBoundary": [
        "负责提供场景词汇、对象常识、默认偏好和用户反馈教训。",
        "不直接执行 CAD，也不替代流水线里的审计、修复和交付。",
        "适合训练用户白话到场景规则的映射，例如家具方向、贴墙和净距。"
      ],
      "inputRequirements": [
        "当前场景规则",
        "用户白话需求",
        "训练计划中的能力项"
      ],
      "outputFormat": [
        "场景词汇解释",
        "对象默认偏好",
        "交给流水线的训练提示"
      ],
      "hardGates": [
        {
          "label": "保持轻量",
          "value": "只补场景差异，不把场景偏好写进 Core。"
        }
      ],
      "mustNot": [
        "不得直接执行 CAD。",
        "不得替代主训家装案例。"
      ],
      "callCapabilities": [
        "场景规则读取",
        "训练需求解释"
      ],
      "adjustablePromptPoints": [
        "补充场景词汇和边界时，先绑定具体案例。",
        "不要和当前家装主训并行抢主线。",
        "只有跨场景重复出现的问题才考虑沉淀到 Core。"
      ],
      "sourceRefs": [
        {
          "path": "agents/commercial_fitout/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-office",
      "agentId": "office",
      "agentName": "办公场景智能体",
      "sourceName": "office",
      "promptSummary": "你是办公场景智能体，保留办公布局、工位和会议空间偏好，当前只作为后续训练候选。",
      "roleSetting": "你是办公场景智能体，保留办公布局、工位和会议空间偏好，当前只作为后续训练候选。",
      "responsibilityBoundary": [
        "负责提供场景词汇、对象常识、默认偏好和用户反馈教训。",
        "不直接执行 CAD，也不替代流水线里的审计、修复和交付。",
        "适合训练用户白话到场景规则的映射，例如家具方向、贴墙和净距。"
      ],
      "inputRequirements": [
        "当前场景规则",
        "用户白话需求",
        "训练计划中的能力项"
      ],
      "outputFormat": [
        "场景词汇解释",
        "对象默认偏好",
        "交给流水线的训练提示"
      ],
      "hardGates": [
        {
          "label": "保持轻量",
          "value": "只补场景差异，不把场景偏好写进 Core。"
        }
      ],
      "mustNot": [
        "不得直接执行 CAD。",
        "不得替代主训家装案例。"
      ],
      "callCapabilities": [
        "场景规则读取",
        "训练需求解释"
      ],
      "adjustablePromptPoints": [
        "补充场景词汇和边界时，先绑定具体案例。",
        "不要和当前家装主训并行抢主线。",
        "只有跨场景重复出现的问题才考虑沉淀到 Core。"
      ],
      "sourceRefs": [
        {
          "path": "agents/office/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-restaurant",
      "agentId": "restaurant",
      "agentName": "餐饮场景智能体",
      "sourceName": "restaurant",
      "promptSummary": "你是餐饮场景智能体，保留堂食区、服务动线和入口避让常识，当前不并行扩面。",
      "roleSetting": "你是餐饮场景智能体，保留堂食区、服务动线和入口避让常识，当前不并行扩面。",
      "responsibilityBoundary": [
        "负责提供场景词汇、对象常识、默认偏好和用户反馈教训。",
        "不直接执行 CAD，也不替代流水线里的审计、修复和交付。",
        "适合训练用户白话到场景规则的映射，例如家具方向、贴墙和净距。"
      ],
      "inputRequirements": [
        "当前场景规则",
        "用户白话需求",
        "训练计划中的能力项"
      ],
      "outputFormat": [
        "场景词汇解释",
        "对象默认偏好",
        "交给流水线的训练提示"
      ],
      "hardGates": [
        {
          "label": "保持轻量",
          "value": "只补场景差异，不把场景偏好写进 Core。"
        }
      ],
      "mustNot": [
        "不得直接执行 CAD。",
        "不得替代主训家装案例。"
      ],
      "callCapabilities": [
        "场景规则读取",
        "训练需求解释"
      ],
      "adjustablePromptPoints": [
        "补充场景词汇和边界时，先绑定具体案例。",
        "不要和当前家装主训并行抢主线。",
        "只有跨场景重复出现的问题才考虑沉淀到 Core。"
      ],
      "sourceRefs": [
        {
          "path": "agents/restaurant/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-exhibition",
      "agentId": "exhibition",
      "agentName": "展陈场景智能体",
      "sourceName": "exhibition",
      "promptSummary": "你是展陈场景智能体，保留展台、展墙和参观路线规则，当前不并行主训。",
      "roleSetting": "你是展陈场景智能体，保留展台、展墙和参观路线规则，当前不并行主训。",
      "responsibilityBoundary": [
        "负责提供场景词汇、对象常识、默认偏好和用户反馈教训。",
        "不直接执行 CAD，也不替代流水线里的审计、修复和交付。",
        "适合训练用户白话到场景规则的映射，例如家具方向、贴墙和净距。"
      ],
      "inputRequirements": [
        "当前场景规则",
        "用户白话需求",
        "训练计划中的能力项"
      ],
      "outputFormat": [
        "场景词汇解释",
        "对象默认偏好",
        "交给流水线的训练提示"
      ],
      "hardGates": [
        {
          "label": "保持轻量",
          "value": "只补场景差异，不把场景偏好写进 Core。"
        }
      ],
      "mustNot": [
        "不得直接执行 CAD。",
        "不得替代主训家装案例。"
      ],
      "callCapabilities": [
        "场景规则读取",
        "训练需求解释"
      ],
      "adjustablePromptPoints": [
        "补充场景词汇和边界时，先绑定具体案例。",
        "不要和当前家装主训并行抢主线。",
        "只有跨场景重复出现的问题才考虑沉淀到 Core。"
      ],
      "sourceRefs": [
        {
          "path": "agents/exhibition/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-healthcare",
      "agentId": "healthcare",
      "agentName": "医疗场景智能体",
      "sourceName": "healthcare",
      "promptSummary": "你是医疗场景智能体，保留医疗空间脚手架和安全边界，当前不并行主训。",
      "roleSetting": "你是医疗场景智能体，保留医疗空间脚手架和安全边界，当前不并行主训。",
      "responsibilityBoundary": [
        "负责提供场景词汇、对象常识、默认偏好和用户反馈教训。",
        "不直接执行 CAD，也不替代流水线里的审计、修复和交付。",
        "适合训练用户白话到场景规则的映射，例如家具方向、贴墙和净距。"
      ],
      "inputRequirements": [
        "当前场景规则",
        "用户白话需求",
        "训练计划中的能力项"
      ],
      "outputFormat": [
        "场景词汇解释",
        "对象默认偏好",
        "交给流水线的训练提示"
      ],
      "hardGates": [
        {
          "label": "保持轻量",
          "value": "只补场景差异，不把场景偏好写进 Core。"
        }
      ],
      "mustNot": [
        "不得直接执行 CAD。",
        "不得替代主训家装案例。"
      ],
      "callCapabilities": [
        "场景规则读取",
        "训练需求解释"
      ],
      "adjustablePromptPoints": [
        "补充场景词汇和边界时，先绑定具体案例。",
        "不要和当前家装主训并行抢主线。",
        "只有跨场景重复出现的问题才考虑沉淀到 Core。"
      ],
      "sourceRefs": [
        {
          "path": "agents/healthcare/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-custom",
      "agentId": "custom",
      "agentName": "自定义场景智能体",
      "sourceName": "custom",
      "promptSummary": "你是自定义场景智能体，用于跨场景或模糊需求占位，默认需要人工确认边界。",
      "roleSetting": "你是自定义场景智能体，用于跨场景或模糊需求占位，默认需要人工确认边界。",
      "responsibilityBoundary": [
        "负责提供场景词汇、对象常识、默认偏好和用户反馈教训。",
        "不直接执行 CAD，也不替代流水线里的审计、修复和交付。",
        "适合训练用户白话到场景规则的映射，例如家具方向、贴墙和净距。"
      ],
      "inputRequirements": [
        "当前场景规则",
        "用户白话需求",
        "训练计划中的能力项"
      ],
      "outputFormat": [
        "场景词汇解释",
        "对象默认偏好",
        "交给流水线的训练提示"
      ],
      "hardGates": [
        {
          "label": "保持轻量",
          "value": "只补场景差异，不把场景偏好写进 Core。"
        }
      ],
      "mustNot": [
        "不得直接执行 CAD。",
        "不得替代主训家装案例。"
      ],
      "callCapabilities": [
        "场景规则读取",
        "训练需求解释"
      ],
      "adjustablePromptPoints": [
        "补充场景词汇和边界时，先绑定具体案例。",
        "不要和当前家装主训并行抢主线。",
        "只有跨场景重复出现的问题才考虑沉淀到 Core。"
      ],
      "sourceRefs": [
        {
          "path": "agents/custom/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-pipeline_context_curator",
      "agentId": "pipeline_context_curator",
      "agentName": "上下文整理智能体",
      "sourceName": "pipeline_context_curator",
      "promptSummary": "你是上下文整理智能体，负责在每一轮训练开始前收束案例状态、用户反馈和历史噪声，避免后续智能体读错上下文。",
      "roleSetting": "你负责在训练开始前收束上下文，把当前案例、用户反馈、历史失败和待训练目标整理成干净的输入包。",
      "responsibilityBoundary": [
        "只负责训练流水线中的本环节判断和产物。",
        "输入不足时必须声明缺口、阻塞或下一步，而不是硬推到 CAD。",
        "输出必须能被下一环节读取，并保留证据边界。"
      ],
      "inputRequirements": [
        "当前案例目录和轮次记录",
        "用户最新反馈",
        "训练计划表单中的能力项与失败类型",
        "已有规则、资产和审计结果"
      ],
      "outputFormat": [
        "本轮上下文包",
        "本轮必须保留和必须忽略的信息",
        "需要交给后续智能体的阻塞点或缺口"
      ],
      "hardGates": [
        {
          "label": "不带旧噪声",
          "value": "过期计划、无关失败和已废弃假设不能继续传下去。"
        }
      ],
      "mustNot": [
        "不得把历史结论当成本轮用户确认。",
        "不得在上下文不足时直接推动执行。"
      ],
      "callCapabilities": [
        "案例上下文读取",
        "反馈摘要",
        "训练状态过滤",
        "源文件索引"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/pipeline_context_curator/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-pipeline_asset_retriever",
      "agentId": "pipeline_asset_retriever",
      "agentName": "资产检索智能体",
      "sourceName": "pipeline_asset_retriever",
      "promptSummary": "你是资产检索智能体，负责在落图前检索标准图库、常识、自产资产和历史失败，并明确哪些只是参考证据。",
      "roleSetting": "你负责在落图前检索标准图库、对象默认值、自产资产、常识规则和历史失败，并明确哪些只是参考证据。",
      "responsibilityBoundary": [
        "只负责训练流水线中的本环节判断和产物。",
        "输入不足时必须声明缺口、阻塞或下一步，而不是硬推到 CAD。",
        "输出必须能被下一环节读取，并保留证据边界。"
      ],
      "inputRequirements": [
        "用户需求和当前能力项",
        "标准图库、原始图库和自产资产入口",
        "对象默认值、场景规则和历史失败记录"
      ],
      "outputFormat": [
        "资产与常识检索包",
        "命中的参考资料及其可信边界",
        "缺失字段、未知项和不能晋升系统能力的说明"
      ],
      "hardGates": [
        {
          "label": "边界声明",
          "value": "命中图库或参考资料只算上游证据，不算 CAD 能力通过。"
        }
      ],
      "mustNot": [
        "不得把检索命中说成能力证明。",
        "不得复制厂商资产几何。",
        "不得跳过视觉部件契约。"
      ],
      "callCapabilities": [
        "标准图库扫描",
        "参考资产接收",
        "对象默认值检索",
        "历史失败检索"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/pipeline_asset_retriever/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-pipeline_orchestrator",
      "agentId": "pipeline_orchestrator",
      "agentName": "流程编排智能体",
      "sourceName": "pipeline_orchestrator",
      "promptSummary": "你是流程编排智能体，负责判断当前训练应停在哪个阶段、下一步该调用谁，以及是否需要阻塞或回环。",
      "roleSetting": "你负责决定本轮训练该停在哪个阶段、下一步调用哪个智能体，以及是否需要阻塞、回环或进入沉淀。",
      "responsibilityBoundary": [
        "只负责训练流水线中的本环节判断和产物。",
        "输入不足时必须声明缺口、阻塞或下一步，而不是硬推到 CAD。",
        "输出必须能被下一环节读取，并保留证据边界。"
      ],
      "inputRequirements": [
        "上下文包",
        "训练计划状态",
        "各智能体产物和阻塞说明",
        "证据边界与用户反馈"
      ],
      "outputFormat": [
        "下一步智能体调用顺序",
        "阻塞原因或回环原因",
        "是否允许进入落图、审计或沉淀的判断"
      ],
      "hardGates": [
        {
          "label": "阶段清晰",
          "value": "必须说明当前停在计划、Prompt、案例训练、反馈通过还是已沉淀。"
        }
      ],
      "mustNot": [
        "不得把页面状态当成真实通过。",
        "不得跳过失败归因。"
      ],
      "callCapabilities": [
        "训练阶段判断",
        "流水线调度",
        "阻塞判定",
        "回环策略"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/pipeline_orchestrator/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-pipeline_visual_intent",
      "agentId": "pipeline_visual_intent",
      "agentName": "视觉语义智能体",
      "sourceName": "pipeline_visual_intent",
      "promptSummary": "你是视觉语义智能体，负责把白话和参考图拆成部件级视觉契约，尤其要说明方向、部件、闭合关系和禁止偷懒模式。",
      "roleSetting": "你负责把用户白话、参考图和场景常识拆成部件级视觉契约，重点说明方向、部件、闭合关系和禁止偷懒模式。",
      "responsibilityBoundary": [
        "只负责训练流水线中的本环节判断和产物。",
        "输入不足时必须声明缺口、阻塞或下一步，而不是硬推到 CAD。",
        "输出必须能被下一环节读取，并保留证据边界。"
      ],
      "inputRequirements": [
        "用户白话需求",
        "参考截图或目标图",
        "资产与常识检索包",
        "场景规则和对象默认值"
      ],
      "outputFormat": [
        "部件级视觉契约",
        "方向、层级、闭合状态和贴合关系",
        "必须绘制与禁止绘制的视觉模式"
      ],
      "hardGates": [
        {
          "label": "部件可追踪",
          "value": "关键部件要有编号、角色、形状和闭合状态。"
        }
      ],
      "mustNot": [
        "不得直接执行 CAD。",
        "不得用外框盒子冒充真实部件。",
        "不得把修尺寸当成修视觉语义。"
      ],
      "callCapabilities": [
        "参考图语义拆解",
        "部件契约生成",
        "方向语义判断",
        "禁止模式生成"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/pipeline_visual_intent/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-pipeline_intent",
      "agentId": "pipeline_intent",
      "agentName": "需求拆解智能体",
      "sourceName": "pipeline_intent",
      "promptSummary": "你是需求拆解智能体，负责把白话和视觉契约整理成可校验的结构化意图，并决定能否进入 CAD_PLAN。",
      "roleSetting": "你负责把白话和视觉契约整理成可校验的结构化意图，并判断能不能进入 CAD_PLAN。",
      "responsibilityBoundary": [
        "只负责训练流水线中的本环节判断和产物。",
        "输入不足时必须声明缺口、阻塞或下一步，而不是硬推到 CAD。",
        "输出必须能被下一环节读取，并保留证据边界。"
      ],
      "inputRequirements": [
        "上下文包",
        "视觉契约",
        "场景规则",
        "资产与常识检索结果",
        "本轮训练目标"
      ],
      "outputFormat": [
        "结构化意图",
        "CAD_PLAN 候选或暂缓说明",
        "审计清单和不可执行原因"
      ],
      "hardGates": [
        {
          "label": "意图完整",
          "value": "对象、尺寸、方向、基点、图层和证据边界要能被下一步读取。"
        }
      ],
      "mustNot": [
        "不得把自然语言直接跳到 CAD。",
        "不得省略 validate 和 dry-run 前置条件。"
      ],
      "callCapabilities": [
        "结构化意图生成",
        "CAD_PLAN 生成前检查",
        "Schema 对齐",
        "审计清单生成"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/pipeline_intent/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-pipeline_execute",
      "agentId": "pipeline_execute",
      "agentName": "落图执行智能体",
      "sourceName": "pipeline_execute",
      "promptSummary": "你是落图执行智能体，只能按已声明的 CAD_PLAN 或 visual_parts 写入 CODEX_PREVIEW，不临场发明对象。",
      "roleSetting": "你负责把已经声明并校验过的 CAD_PLAN 或 visual_parts 落到 CODEX_PREVIEW，只执行计划内对象，不临场发明。",
      "responsibilityBoundary": [
        "只把已声明的 CAD_PLAN 或 visual_parts 落到 CODEX_PREVIEW。",
        "不得临场发明对象、尺寸或正式图层写入行为。",
        "执行结果必须能被 audit 和 repair 回读。"
      ],
      "inputRequirements": [
        "通过校验的 CAD_PLAN 或 visual_parts",
        "可执行尺寸、基点、图层和对象清单",
        "write guard 与预览图层约束"
      ],
      "outputFormat": [
        "执行摘要",
        "创建对象、图层和 handles 回读线索",
        "未执行、阻塞或需审计的说明"
      ],
      "hardGates": [
        {
          "label": "只写预览",
          "value": "默认只写 CODEX_PREVIEW，不保存或覆盖 DWG。"
        }
      ],
      "mustNot": [
        "不得保存或覆盖 DWG。",
        "不得修改正式图层。",
        "不得跳过 validate / dry-run。",
        "不得绘制未在计划中声明的结构。"
      ],
      "callCapabilities": [
        "CAD_PLAN 执行入口",
        "CODEX_PREVIEW 写入保护",
        "AutoCAD COM / CAD-MCP 执行桥接",
        "执行摘要回写"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/pipeline_execute/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-pipeline_audit",
      "agentId": "pipeline_audit",
      "agentName": "机器审计智能体",
      "sourceName": "pipeline_audit",
      "promptSummary": "你是机器审计智能体，负责分开判断几何、语义、图层、标注和用户可见效果，不能把机器绿当成最终验收。",
      "roleSetting": "你负责把机器审计、几何回读、图层、标注和用户可见效果分开判断，指出本轮是否还需要修。",
      "responsibilityBoundary": [
        "负责判断几何、语义、图层、标注和视觉可验收性。",
        "机器绿不能单独等于用户验收通过。",
        "发现重复失败时要给出可晋升检查器的候选。"
      ],
      "inputRequirements": [
        "执行摘要",
        "handles 回读或截图",
        "CAD_PLAN / visual_parts",
        "成功门槛和不通过边界"
      ],
      "outputFormat": [
        "机器审计结论",
        "用户可见风险",
        "需要修复的根因和下一步证据要求"
      ],
      "hardGates": [
        {
          "label": "不混口径",
          "value": "机器绿、用户认可和表 C 指标必须分开说。"
        }
      ],
      "mustNot": [
        "不得把机器审计通过当最终验收。",
        "不得只报数字不说明用户该看哪里。"
      ],
      "callCapabilities": [
        "几何回读",
        "截图检查",
        "图层审计",
        "失败归因"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/pipeline_audit/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-pipeline_repair",
      "agentId": "pipeline_repair",
      "agentName": "修复回环智能体",
      "sourceName": "pipeline_repair",
      "promptSummary": "你是修复回环智能体，负责基于根因做最小修复，并把修复后的结果重新送回执行和审计。",
      "roleSetting": "你负责基于审计根因做最小修复，把修复说明回送执行和审计，而不是无边界重画。",
      "responsibilityBoundary": [
        "只负责训练流水线中的本环节判断和产物。",
        "输入不足时必须声明缺口、阻塞或下一步，而不是硬推到 CAD。",
        "输出必须能被下一环节读取，并保留证据边界。"
      ],
      "inputRequirements": [
        "审计失败点",
        "原始 CAD_PLAN / visual_parts",
        "可修复范围和禁止改动范围",
        "用户反馈"
      ],
      "outputFormat": [
        "修复计划",
        "修改后的结构化意图或 CAD_PLAN",
        "需要重新执行与审计的证据清单"
      ],
      "hardGates": [
        {
          "label": "最小修复",
          "value": "只改根因相关内容，不扩大范围。"
        }
      ],
      "mustNot": [
        "不得靠反复改尺寸掩盖语义错误。",
        "不得把未验证修复交付给用户。"
      ],
      "callCapabilities": [
        "失败根因定位",
        "CAD_PLAN 最小修复",
        "回归审计触发"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/pipeline_repair/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-pipeline_delivery",
      "agentId": "pipeline_delivery",
      "agentName": "交付汇报智能体",
      "sourceName": "pipeline_delivery",
      "promptSummary": "你是交付汇报智能体，负责用低噪声中文说明本轮结论、证据边界和用户最该验收的位置。",
      "roleSetting": "你负责用低噪声中文交付本轮训练结论、证据路径、没证明的边界和用户最该验收的位置。",
      "responsibilityBoundary": [
        "只负责训练流水线中的本环节判断和产物。",
        "输入不足时必须声明缺口、阻塞或下一步，而不是硬推到 CAD。",
        "输出必须能被下一环节读取，并保留证据边界。"
      ],
      "inputRequirements": [
        "审计结果",
        "截图或回读证据",
        "训练目标",
        "失败沉淀建议",
        "用户反馈入口"
      ],
      "outputFormat": [
        "本轮结论",
        "相对上一轮变化",
        "证据证明了什么、没证明什么",
        "用户验收重点"
      ],
      "hardGates": [
        {
          "label": "先说结论",
          "value": "训练期交付先讲本轮结果，再讲证据和边界。"
        }
      ],
      "mustNot": [
        "不得用表格堆满普通训练交付。",
        "不得暗示真实 CAD 能力已经由训练页证明。"
      ],
      "callCapabilities": [
        "训练交付模板",
        "证据路径整理",
        "用户验收提示",
        "边界说明"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/pipeline_delivery/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-pipeline_learning_promoter",
      "agentId": "pipeline_learning_promoter",
      "agentName": "训练沉淀智能体",
      "sourceName": "pipeline_learning_promoter",
      "promptSummary": "你是训练沉淀智能体，负责把失败和用户反馈分流到案例、场景规则、pipeline、Core 检查器或系统资产库。",
      "roleSetting": "你负责把失败、通过经验和用户反馈分流到案例反馈、场景规则、pipeline 规则、Core 检查器或系统资产库。",
      "responsibilityBoundary": [
        "只负责训练流水线中的本环节判断和产物。",
        "输入不足时必须声明缺口、阻塞或下一步，而不是硬推到 CAD。",
        "输出必须能被下一环节读取，并保留证据边界。"
      ],
      "inputRequirements": [
        "审计与用户反馈",
        "失败根因",
        "是否重复出现",
        "可晋升的检查器或资产候选"
      ],
      "outputFormat": [
        "沉淀位置建议",
        "下一轮 Prompt 调整点",
        "是否允许晋升规则、测试或资产库的判断"
      ],
      "hardGates": [
        {
          "label": "先分层",
          "value": "单案例问题留在案例，重复问题才考虑规则或 Core。"
        }
      ],
      "mustNot": [
        "不得把一次失败直接污染通用规则。",
        "不得把参考图库直接晋升自产资产。"
      ],
      "callCapabilities": [
        "训练错误台账",
        "场景规则沉淀",
        "Core 检查器候选",
        "系统资产晋升判断"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/pipeline_learning_promoter/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    },
    {
      "id": "contract-demand_side_roles",
      "agentId": "demand_side_roles",
      "agentName": "需求侧角色智能体",
      "sourceName": "demand_side_roles",
      "promptSummary": "你是需求侧角色数据智能体，只负责生成更像真实用户的训练需求和 benchmark，不直接参与 CAD 执行。",
      "roleSetting": "你负责生成更像真实用户的训练需求、角色口吻和 benchmark 场景，只作为输入数据，不参与 CAD 执行。",
      "responsibilityBoundary": [
        "只生成需求、角色口吻和 benchmark 场景。",
        "不直接绘图，不替代真实用户反馈。",
        "用于让训练输入更像真实白话需求。"
      ],
      "inputRequirements": [
        "场景 ID",
        "用户角色",
        "需求焦点",
        "样例请求和验收偏好"
      ],
      "outputFormat": [
        "自然语言训练需求",
        "用户角色画像",
        "能力目标和验收关注点"
      ],
      "hardGates": [
        {
          "label": "用途边界",
          "value": "只生成需求，不直接绘图，也不替代真实用户反馈。"
        }
      ],
      "mustNot": [
        "不得当作执行智能体。",
        "不得替代真实用户反馈。"
      ],
      "callCapabilities": [
        "需求样本生成",
        "角色口吻生成",
        "benchmark 场景生成"
      ],
      "adjustablePromptPoints": [
        "先明确输入、输出和通过门槛。",
        "把禁止事项写成可检查条款。",
        "重复失败时再晋升为测试或 Core 检查器。"
      ],
      "sourceRefs": [
        {
          "path": "agents/demand_side_roles/agent.json",
          "title": "源文件",
          "kind": "文件",
          "meaning": "用于维护该智能体的中文 Prompt 契约。",
          "changeGuide": "修改后重新生成本页数据并复查页面。"
        }
      ],
      "evidenceBoundary": "本契约只帮助前端展示和训练 Prompt，不代表表 C 真实 CAD 几何通过。"
    }
  ],
  "tableCBoundary": {
    "label": "表 C 真实 CAD 机器快照",
    "generatedAt": "2026-05-28T13:46:40Z",
    "sourcePath": "output/validation_runs/capability-lab/cad_capability_coverage.json",
    "cadProofCoveragePercent": 90.99,
    "cadStrengthIndexPercent": 93.53,
    "sceneFragmentStrengthPercent": 93.62,
    "showcaseReadinessPercent": 90.99,
    "headlinePercent": 90.99,
    "highestProvenLadder": "L4",
    "note": "这是 registry 和 coverage JSON 的机器指标快照，只能说明表 C 口径；不能和训练计划成熟度、智能体 Prompt 成熟度混算。"
  },
  "coverageSnapshot": {
    "label": "表 C 真实 CAD 机器快照",
    "generatedAt": "2026-05-28T13:46:40Z",
    "sourcePath": "output/validation_runs/capability-lab/cad_capability_coverage.json",
    "cadProofCoveragePercent": 90.99,
    "cadStrengthIndexPercent": 93.53,
    "sceneFragmentStrengthPercent": 93.62,
    "showcaseReadinessPercent": 90.99,
    "headlinePercent": 90.99,
    "highestProvenLadder": "L4",
    "note": "这是 registry 和 coverage JSON 的机器指标快照，只能说明表 C 口径；不能和训练计划成熟度、智能体 Prompt 成熟度混算。"
  },
  "stages": [
    {
      "id": "raw",
      "label": "标准图库",
      "shortLabel": "图库"
    },
    {
      "id": "knowledge",
      "label": "常识整理",
      "shortLabel": "常识"
    },
    {
      "id": "trained",
      "label": "训练沉淀",
      "shortLabel": "训练"
    },
    {
      "id": "system",
      "label": "自产资产",
      "shortLabel": "自产"
    }
  ],
  "agents": [
    {
      "id": "residential",
      "name": "家装场景智能体",
      "sourceName": "residential",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "primary_training",
      "statusLabel": "主训中",
      "trainingRole": "你负责把家装用户的白话需求、房间语境、家具常识和用户反馈，转成流水线可以继续训练的中文场景规则。",
      "roleSummary": "你是家装主训场景智能体，负责把用户的家装白话、房间偏好和家具常识转成可被训练流水线消费的中文规则约束。",
      "promptContractId": "contract-residential",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补客厅视线方向规则"
        },
        {
          "id": "desk",
          "name": "书桌",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补书桌+椅组合训练"
        },
        {
          "id": "low-cabinet",
          "name": "矮柜",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补对象默认值"
        },
        {
          "id": "basin",
          "name": "洗手台",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "toilet",
          "name": "马桶",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补洁具默认净距"
        },
        {
          "id": "stove",
          "name": "灶台",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补厨房对象 catalog"
        },
        {
          "id": "fridge",
          "name": "冰箱",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补冰箱门向和净距"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-tea-table",
          "capabilityId": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "program-dining-table",
          "capabilityId": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "program-dining-chair",
          "capabilityId": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "program-nightstand",
          "capabilityId": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "program-wardrobe",
          "capabilityId": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "program-tv-cabinet",
          "capabilityId": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "nextTrainingTarget": "补客厅视线方向规则"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 100,
        "note": "关联 15 个训练计划项，其中 P0 5 个；表示训练表单覆盖度。",
        "basis": "15 个训练计划 / P0 5 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 68,
        "note": "训练状态：主训中。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：主训中",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 100,
          "note": "关联 15 个训练计划项，其中 P0 5 个；表示训练表单覆盖度。",
          "basis": "15 个训练计划 / P0 5 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 68,
          "note": "训练状态：主训中。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：主训中",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/residential/agent.json",
        "agents/residential/rules.md"
      ],
      "operation": {
        "role": "你负责把家装用户的白话需求、房间语境、家具常识和用户反馈，转成流水线可以继续训练的中文场景规则。",
        "inputs": [
          "用户原话和本轮训练目标",
          "家装场景规则、对象默认值和上轮反馈",
          "当前能力项的风险点和下一轮可验收目标"
        ],
        "outputs": [
          "场景词汇和对象常识约束",
          "家具方向、贴墙、净距、组合关系等可训练偏好",
          "需要交给视觉语义或需求拆解智能体的提示"
        ],
        "passGate": [
          {
            "label": "边界清楚",
            "value": "只声明家装场景规则，不代替执行、审计或真实 CAD 证明。"
          }
        ],
        "mustNot": [
          "不得把场景偏好写成跨场景 Core 规则。",
          "不得把用户一句话脑补成确定尺寸或正式落图结果。"
        ],
        "usesCore": [
          "家装规则读取",
          "对象默认值引用",
          "用户反馈归因",
          "训练目标拆分"
        ],
        "optimizationTips": [
          "把用户指出的家装常识错误沉淀到 rules.md，而不是只改单个案例。",
          "优先补家具方向、贴墙、通行净距和部件语义，因为这些最影响用户观感。",
          "每次训练后检查是否需要新增可机器审计的规则。"
        ]
      }
    },
    {
      "id": "commercial_fitout",
      "name": "商业空间智能体",
      "sourceName": "commercial_fitout",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是商业空间场景智能体，保留零售、接待、会议室和开放办公等规则脚手架，当前不并行主训。",
      "roleSummary": "你是商业空间场景智能体，保留零售、接待、会议室和开放办公等规则脚手架，当前不并行主训。",
      "promptContractId": "contract-commercial_fitout",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/commercial_fitout/agent.json"
      ],
      "operation": {
        "role": "你是商业空间场景智能体，保留零售、接待、会议室和开放办公等规则脚手架，当前不并行主训。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "office",
      "name": "办公场景智能体",
      "sourceName": "office",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是办公场景智能体，保留办公布局、工位和会议空间偏好，当前只作为后续训练候选。",
      "roleSummary": "你是办公场景智能体，保留办公布局、工位和会议空间偏好，当前只作为后续训练候选。",
      "promptContractId": "contract-office",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/office/agent.json"
      ],
      "operation": {
        "role": "你是办公场景智能体，保留办公布局、工位和会议空间偏好，当前只作为后续训练候选。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "restaurant",
      "name": "餐饮场景智能体",
      "sourceName": "restaurant",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是餐饮场景智能体，保留堂食区、服务动线和入口避让常识，当前不并行扩面。",
      "roleSummary": "你是餐饮场景智能体，保留堂食区、服务动线和入口避让常识，当前不并行扩面。",
      "promptContractId": "contract-restaurant",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/restaurant/agent.json"
      ],
      "operation": {
        "role": "你是餐饮场景智能体，保留堂食区、服务动线和入口避让常识，当前不并行扩面。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "exhibition",
      "name": "展陈场景智能体",
      "sourceName": "exhibition",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是展陈场景智能体，保留展台、展墙和参观路线规则，当前不并行主训。",
      "roleSummary": "你是展陈场景智能体，保留展台、展墙和参观路线规则，当前不并行主训。",
      "promptContractId": "contract-exhibition",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/exhibition/agent.json"
      ],
      "operation": {
        "role": "你是展陈场景智能体，保留展台、展墙和参观路线规则，当前不并行主训。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "healthcare",
      "name": "医疗场景智能体",
      "sourceName": "healthcare",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是医疗场景智能体，保留医疗空间脚手架和安全边界，当前不并行主训。",
      "roleSummary": "你是医疗场景智能体，保留医疗空间脚手架和安全边界，当前不并行主训。",
      "promptContractId": "contract-healthcare",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/healthcare/agent.json"
      ],
      "operation": {
        "role": "你是医疗场景智能体，保留医疗空间脚手架和安全边界，当前不并行主训。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "custom",
      "name": "自定义场景智能体",
      "sourceName": "custom",
      "group": "scene",
      "groupLabel": "场景智能体",
      "status": "paused",
      "statusLabel": "暂停训练",
      "trainingRole": "你是自定义场景智能体，用于跨场景或模糊需求占位，默认需要人工确认边界。",
      "roleSummary": "你是自定义场景智能体，用于跨场景或模糊需求占位，默认需要人工确认边界。",
      "promptContractId": "contract-custom",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 2 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 20,
        "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：暂停训练",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 2 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 2 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 20,
          "note": "训练状态：暂停训练。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：暂停训练",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/custom/agent.json"
      ],
      "operation": {
        "role": "你是自定义场景智能体，用于跨场景或模糊需求占位，默认需要人工确认边界。",
        "inputs": [
          "当前场景规则",
          "用户白话需求",
          "训练计划中的能力项"
        ],
        "outputs": [
          "场景词汇解释",
          "对象默认偏好",
          "交给流水线的训练提示"
        ],
        "passGate": [
          {
            "label": "保持轻量",
            "value": "只补场景差异，不把场景偏好写进 Core。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得替代主训家装案例。"
        ],
        "usesCore": [
          "场景规则读取",
          "训练需求解释"
        ],
        "optimizationTips": [
          "补充场景词汇和边界时，先绑定具体案例。",
          "不要和当前家装主训并行抢主线。",
          "只有跨场景重复出现的问题才考虑沉淀到 Core。"
        ]
      }
    },
    {
      "id": "pipeline_context_curator",
      "name": "上下文整理智能体",
      "sourceName": "pipeline_context_curator",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责在训练开始前收束上下文，把当前案例、用户反馈、历史失败和待训练目标整理成干净的输入包。",
      "roleSummary": "你是上下文整理智能体，负责在每一轮训练开始前收束案例状态、用户反馈和历史噪声，避免后续智能体读错上下文。",
      "promptContractId": "contract-pipeline_context_curator",
      "ownedCapabilities": [
        {
          "id": "room-outline",
          "name": "房间轮廓绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化房间轮廓 validate"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-room-outline",
          "capabilityId": "room-outline",
          "name": "房间轮廓绘制",
          "priority": "P1",
          "nextTrainingTarget": "强化房间轮廓 validate"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 33,
        "note": "关联 1 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "1 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 33,
          "note": "关联 1 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "1 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_context_curator/agent.json"
      ],
      "operation": {
        "role": "你负责在训练开始前收束上下文，把当前案例、用户反馈、历史失败和待训练目标整理成干净的输入包。",
        "inputs": [
          "当前案例目录和轮次记录",
          "用户最新反馈",
          "训练计划表单中的能力项与失败类型",
          "已有规则、资产和审计结果"
        ],
        "outputs": [
          "本轮上下文包",
          "本轮必须保留和必须忽略的信息",
          "需要交给后续智能体的阻塞点或缺口"
        ],
        "passGate": [
          {
            "label": "不带旧噪声",
            "value": "过期计划、无关失败和已废弃假设不能继续传下去。"
          }
        ],
        "mustNot": [
          "不得把历史结论当成本轮用户确认。",
          "不得在上下文不足时直接推动执行。"
        ],
        "usesCore": [
          "案例上下文读取",
          "反馈摘要",
          "训练状态过滤",
          "源文件索引"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_asset_retriever",
      "name": "资产检索智能体",
      "sourceName": "pipeline_asset_retriever",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责在落图前检索标准图库、对象默认值、自产资产、常识规则和历史失败，并明确哪些只是参考证据。",
      "roleSummary": "你是资产检索智能体，负责在落图前检索标准图库、常识、自产资产和历史失败，并明确哪些只是参考证据。",
      "promptContractId": "contract-pipeline_asset_retriever",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补客厅视线方向规则"
        },
        {
          "id": "desk",
          "name": "书桌",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补书桌+椅组合训练"
        },
        {
          "id": "low-cabinet",
          "name": "矮柜",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补对象默认值"
        },
        {
          "id": "basin",
          "name": "洗手台",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "toilet",
          "name": "马桶",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补洁具默认净距"
        },
        {
          "id": "stove",
          "name": "灶台",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补厨房对象 catalog"
        },
        {
          "id": "fridge",
          "name": "冰箱",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补冰箱门向和净距"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-tea-table",
          "capabilityId": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "program-dining-table",
          "capabilityId": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "program-dining-chair",
          "capabilityId": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "program-nightstand",
          "capabilityId": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "program-wardrobe",
          "capabilityId": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "program-tv-cabinet",
          "capabilityId": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "nextTrainingTarget": "补客厅视线方向规则"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 100,
        "note": "关联 15 个训练计划项，其中 P0 5 个；表示训练表单覆盖度。",
        "basis": "15 个训练计划 / P0 5 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 100,
          "note": "关联 15 个训练计划项，其中 P0 5 个；表示训练表单覆盖度。",
          "basis": "15 个训练计划 / P0 5 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_asset_retriever/agent.json"
      ],
      "operation": {
        "role": "你负责在落图前检索标准图库、对象默认值、自产资产、常识规则和历史失败，并明确哪些只是参考证据。",
        "inputs": [
          "用户需求和当前能力项",
          "标准图库、原始图库和自产资产入口",
          "对象默认值、场景规则和历史失败记录"
        ],
        "outputs": [
          "资产与常识检索包",
          "命中的参考资料及其可信边界",
          "缺失字段、未知项和不能晋升系统能力的说明"
        ],
        "passGate": [
          {
            "label": "边界声明",
            "value": "命中图库或参考资料只算上游证据，不算 CAD 能力通过。"
          }
        ],
        "mustNot": [
          "不得把检索命中说成能力证明。",
          "不得复制厂商资产几何。",
          "不得跳过视觉部件契约。"
        ],
        "usesCore": [
          "标准图库扫描",
          "参考资产接收",
          "对象默认值检索",
          "历史失败检索"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_orchestrator",
      "name": "流程编排智能体",
      "sourceName": "pipeline_orchestrator",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责决定本轮训练该停在哪个阶段、下一步调用哪个智能体，以及是否需要阻塞、回环或进入沉淀。",
      "roleSummary": "你是流程编排智能体，负责判断当前训练应停在哪个阶段、下一步该调用谁，以及是否需要阻塞或回环。",
      "promptContractId": "contract-pipeline_orchestrator",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_orchestrator/agent.json"
      ],
      "operation": {
        "role": "你负责决定本轮训练该停在哪个阶段、下一步调用哪个智能体，以及是否需要阻塞、回环或进入沉淀。",
        "inputs": [
          "上下文包",
          "训练计划状态",
          "各智能体产物和阻塞说明",
          "证据边界与用户反馈"
        ],
        "outputs": [
          "下一步智能体调用顺序",
          "阻塞原因或回环原因",
          "是否允许进入落图、审计或沉淀的判断"
        ],
        "passGate": [
          {
            "label": "阶段清晰",
            "value": "必须说明当前停在计划、Prompt、案例训练、反馈通过还是已沉淀。"
          }
        ],
        "mustNot": [
          "不得把页面状态当成真实通过。",
          "不得跳过失败归因。"
        ],
        "usesCore": [
          "训练阶段判断",
          "流水线调度",
          "阻塞判定",
          "回环策略"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_visual_intent",
      "name": "视觉语义智能体",
      "sourceName": "pipeline_visual_intent",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责把用户白话、参考图和场景常识拆成部件级视觉契约，重点说明方向、部件、闭合关系和禁止偷懒模式。",
      "roleSummary": "你是视觉语义智能体，负责把白话和参考图拆成部件级视觉契约，尤其要说明方向、部件、闭合关系和禁止偷懒模式。",
      "promptContractId": "contract-pipeline_visual_intent",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 53,
        "note": "关联 2 个训练计划项，其中 P0 2 个；表示训练表单覆盖度。",
        "basis": "2 个训练计划 / P0 2 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 53,
          "note": "关联 2 个训练计划项，其中 P0 2 个；表示训练表单覆盖度。",
          "basis": "2 个训练计划 / P0 2 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_visual_intent/agent.json"
      ],
      "operation": {
        "role": "你负责把用户白话、参考图和场景常识拆成部件级视觉契约，重点说明方向、部件、闭合关系和禁止偷懒模式。",
        "inputs": [
          "用户白话需求",
          "参考截图或目标图",
          "资产与常识检索包",
          "场景规则和对象默认值"
        ],
        "outputs": [
          "部件级视觉契约",
          "方向、层级、闭合状态和贴合关系",
          "必须绘制与禁止绘制的视觉模式"
        ],
        "passGate": [
          {
            "label": "部件可追踪",
            "value": "关键部件要有编号、角色、形状和闭合状态。"
          }
        ],
        "mustNot": [
          "不得直接执行 CAD。",
          "不得用外框盒子冒充真实部件。",
          "不得把修尺寸当成修视觉语义。"
        ],
        "usesCore": [
          "参考图语义拆解",
          "部件契约生成",
          "方向语义判断",
          "禁止模式生成"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_intent",
      "name": "需求拆解智能体",
      "sourceName": "pipeline_intent",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责把白话和视觉契约整理成可校验的结构化意图，并判断能不能进入 CAD_PLAN。",
      "roleSummary": "你是需求拆解智能体，负责把白话和视觉契约整理成可校验的结构化意图，并决定能否进入 CAD_PLAN。",
      "promptContractId": "contract-pipeline_intent",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补客厅视线方向规则"
        },
        {
          "id": "desk",
          "name": "书桌",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补书桌+椅组合训练"
        },
        {
          "id": "low-cabinet",
          "name": "矮柜",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补对象默认值"
        },
        {
          "id": "basin",
          "name": "洗手台",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "toilet",
          "name": "马桶",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补洁具默认净距"
        },
        {
          "id": "stove",
          "name": "灶台",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "先补厨房对象 catalog"
        },
        {
          "id": "fridge",
          "name": "冰箱",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补冰箱门向和净距"
        },
        {
          "id": "wall",
          "name": "墙体绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化墙线重复与开口检查"
        },
        {
          "id": "door",
          "name": "门绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补门向语义训练"
        },
        {
          "id": "window",
          "name": "窗户绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞与墙体关系 audit"
        },
        {
          "id": "door-opening",
          "name": "门洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练洞口扣减检查"
        },
        {
          "id": "window-opening",
          "name": "窗洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞标准语义"
        },
        {
          "id": "room-outline",
          "name": "房间轮廓绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化房间轮廓 validate"
        },
        {
          "id": "column",
          "name": "柱子绘制",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补柱子对象规范"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        },
        {
          "id": "dimension",
          "name": "简单尺寸标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补尺寸标注检查器"
        },
        {
          "id": "text",
          "name": "简单文字标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练对象名称标注"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-tea-table",
          "capabilityId": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "program-dining-table",
          "capabilityId": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "program-dining-chair",
          "capabilityId": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "program-nightstand",
          "capabilityId": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "program-wardrobe",
          "capabilityId": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "program-tv-cabinet",
          "capabilityId": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "nextTrainingTarget": "补客厅视线方向规则"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 100,
        "note": "关联 24 个训练计划项，其中 P0 8 个；表示训练表单覆盖度。",
        "basis": "24 个训练计划 / P0 8 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 100,
          "note": "关联 24 个训练计划项，其中 P0 8 个；表示训练表单覆盖度。",
          "basis": "24 个训练计划 / P0 8 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_intent/agent.json"
      ],
      "operation": {
        "role": "你负责把白话和视觉契约整理成可校验的结构化意图，并判断能不能进入 CAD_PLAN。",
        "inputs": [
          "上下文包",
          "视觉契约",
          "场景规则",
          "资产与常识检索结果",
          "本轮训练目标"
        ],
        "outputs": [
          "结构化意图",
          "CAD_PLAN 候选或暂缓说明",
          "审计清单和不可执行原因"
        ],
        "passGate": [
          {
            "label": "意图完整",
            "value": "对象、尺寸、方向、基点、图层和证据边界要能被下一步读取。"
          }
        ],
        "mustNot": [
          "不得把自然语言直接跳到 CAD。",
          "不得省略 validate 和 dry-run 前置条件。"
        ],
        "usesCore": [
          "结构化意图生成",
          "CAD_PLAN 生成前检查",
          "Schema 对齐",
          "审计清单生成"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_execute",
      "name": "落图执行智能体",
      "sourceName": "pipeline_execute",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责把已经声明并校验过的 CAD_PLAN 或 visual_parts 落到 CODEX_PREVIEW，只执行计划内对象，不临场发明。",
      "roleSummary": "你是落图执行智能体，只能按已声明的 CAD_PLAN 或 visual_parts 写入 CODEX_PREVIEW，不临场发明对象。",
      "promptContractId": "contract-pipeline_execute",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补客厅视线方向规则"
        },
        {
          "id": "desk",
          "name": "书桌",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补书桌+椅组合训练"
        },
        {
          "id": "basin",
          "name": "洗手台",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "toilet",
          "name": "马桶",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补洁具默认净距"
        },
        {
          "id": "wall",
          "name": "墙体绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化墙线重复与开口检查"
        },
        {
          "id": "door",
          "name": "门绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补门向语义训练"
        },
        {
          "id": "window",
          "name": "窗户绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞与墙体关系 audit"
        },
        {
          "id": "door-opening",
          "name": "门洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练洞口扣减检查"
        },
        {
          "id": "window-opening",
          "name": "窗洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞标准语义"
        },
        {
          "id": "room-outline",
          "name": "房间轮廓绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化房间轮廓 validate"
        },
        {
          "id": "column",
          "name": "柱子绘制",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补柱子对象规范"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        },
        {
          "id": "dimension",
          "name": "简单尺寸标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补尺寸标注检查器"
        },
        {
          "id": "text",
          "name": "简单文字标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练对象名称标注"
        },
        {
          "id": "layers",
          "name": "基础图层归类",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补图层归类审计"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-tea-table",
          "capabilityId": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "program-dining-table",
          "capabilityId": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "program-dining-chair",
          "capabilityId": "dining-chair",
          "name": "餐椅",
          "priority": "P0",
          "nextTrainingTarget": "补椅背和入座方向规则"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "program-nightstand",
          "capabilityId": "nightstand",
          "name": "床头柜",
          "priority": "P1",
          "nextTrainingTarget": "补床侧组合默认值"
        },
        {
          "id": "program-tv-cabinet",
          "capabilityId": "tv-cabinet",
          "name": "电视柜",
          "priority": "P1",
          "nextTrainingTarget": "补客厅视线方向规则"
        },
        {
          "id": "program-desk",
          "capabilityId": "desk",
          "name": "书桌",
          "priority": "P1",
          "nextTrainingTarget": "补书桌+椅组合训练"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 100,
        "note": "关联 21 个训练计划项，其中 P0 8 个；表示训练表单覆盖度。",
        "basis": "21 个训练计划 / P0 8 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 100,
          "note": "关联 21 个训练计划项，其中 P0 8 个；表示训练表单覆盖度。",
          "basis": "21 个训练计划 / P0 8 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_execute/agent.json"
      ],
      "operation": {
        "role": "你负责把已经声明并校验过的 CAD_PLAN 或 visual_parts 落到 CODEX_PREVIEW，只执行计划内对象，不临场发明。",
        "inputs": [
          "通过校验的 CAD_PLAN 或 visual_parts",
          "可执行尺寸、基点、图层和对象清单",
          "write guard 与预览图层约束"
        ],
        "outputs": [
          "执行摘要",
          "创建对象、图层和 handles 回读线索",
          "未执行、阻塞或需审计的说明"
        ],
        "passGate": [
          {
            "label": "只写预览",
            "value": "默认只写 CODEX_PREVIEW，不保存或覆盖 DWG。"
          }
        ],
        "mustNot": [
          "不得保存或覆盖 DWG。",
          "不得修改正式图层。",
          "不得跳过 validate / dry-run。",
          "不得绘制未在计划中声明的结构。"
        ],
        "usesCore": [
          "CAD_PLAN 执行入口",
          "CODEX_PREVIEW 写入保护",
          "AutoCAD COM / CAD-MCP 执行桥接",
          "执行摘要回写"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_audit",
      "name": "机器审计智能体",
      "sourceName": "pipeline_audit",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责把机器审计、几何回读、图层、标注和用户可见效果分开判断，指出本轮是否还需要修。",
      "roleSummary": "你是机器审计智能体，负责分开判断几何、语义、图层、标注和用户可见效果，不能把机器绿当成最终验收。",
      "promptContractId": "contract-pipeline_audit",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "bed",
          "name": "床铺",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "basin",
          "name": "洗手台",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "wall",
          "name": "墙体绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化墙线重复与开口检查"
        },
        {
          "id": "door",
          "name": "门绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补门向语义训练"
        },
        {
          "id": "window",
          "name": "窗户绘制",
          "priority": "P0",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞与墙体关系 audit"
        },
        {
          "id": "door-opening",
          "name": "门洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练洞口扣减检查"
        },
        {
          "id": "window-opening",
          "name": "窗洞绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补窗洞标准语义"
        },
        {
          "id": "room-outline",
          "name": "房间轮廓绘制",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "强化房间轮廓 validate"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        },
        {
          "id": "dimension",
          "name": "简单尺寸标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补尺寸标注检查器"
        },
        {
          "id": "layers",
          "name": "基础图层归类",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补图层归类审计"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-tea-table",
          "capabilityId": "tea-table",
          "name": "茶几",
          "priority": "P0",
          "nextTrainingTarget": "补标准尺寸和组合关系检查"
        },
        {
          "id": "program-dining-table",
          "capabilityId": "dining-table",
          "name": "餐桌",
          "priority": "P0",
          "nextTrainingTarget": "训练餐桌+餐椅组合"
        },
        {
          "id": "program-bed",
          "capabilityId": "bed",
          "name": "床铺",
          "priority": "P0",
          "nextTrainingTarget": "开卧室组合训练"
        },
        {
          "id": "program-wardrobe",
          "capabilityId": "wardrobe",
          "name": "衣柜",
          "priority": "P1",
          "nextTrainingTarget": "训练衣柜开门净空 audit"
        },
        {
          "id": "program-basin",
          "capabilityId": "basin",
          "name": "洗手台",
          "priority": "P1",
          "nextTrainingTarget": "训练卫浴对象部件表达"
        },
        {
          "id": "program-wall",
          "capabilityId": "wall",
          "name": "墙体绘制",
          "priority": "P0",
          "nextTrainingTarget": "强化墙线重复与开口检查"
        },
        {
          "id": "program-door",
          "capabilityId": "door",
          "name": "门绘制",
          "priority": "P0",
          "nextTrainingTarget": "补门向语义训练"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 100,
        "note": "关联 15 个训练计划项，其中 P0 7 个；表示训练表单覆盖度。",
        "basis": "15 个训练计划 / P0 7 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 100,
          "note": "关联 15 个训练计划项，其中 P0 7 个；表示训练表单覆盖度。",
          "basis": "15 个训练计划 / P0 7 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_audit/agent.json"
      ],
      "operation": {
        "role": "你负责把机器审计、几何回读、图层、标注和用户可见效果分开判断，指出本轮是否还需要修。",
        "inputs": [
          "执行摘要",
          "handles 回读或截图",
          "CAD_PLAN / visual_parts",
          "成功门槛和不通过边界"
        ],
        "outputs": [
          "机器审计结论",
          "用户可见风险",
          "需要修复的根因和下一步证据要求"
        ],
        "passGate": [
          {
            "label": "不混口径",
            "value": "机器绿、用户认可和表 C 指标必须分开说。"
          }
        ],
        "mustNot": [
          "不得把机器审计通过当最终验收。",
          "不得只报数字不说明用户该看哪里。"
        ],
        "usesCore": [
          "几何回读",
          "截图检查",
          "图层审计",
          "失败归因"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_repair",
      "name": "修复回环智能体",
      "sourceName": "pipeline_repair",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责基于审计根因做最小修复，把修复说明回送执行和审计，而不是无边界重画。",
      "roleSummary": "你是修复回环智能体，负责基于根因做最小修复，并把修复后的结果重新送回执行和审计。",
      "promptContractId": "contract-pipeline_repair",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 3 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 3 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 39,
        "note": "关联 1 个训练计划项，其中 P0 1 个；表示训练表单覆盖度。",
        "basis": "1 个训练计划 / P0 1 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 3 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 3 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 39,
          "note": "关联 1 个训练计划项，其中 P0 1 个；表示训练表单覆盖度。",
          "basis": "1 个训练计划 / P0 1 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_repair/agent.json"
      ],
      "operation": {
        "role": "你负责基于审计根因做最小修复，把修复说明回送执行和审计，而不是无边界重画。",
        "inputs": [
          "审计失败点",
          "原始 CAD_PLAN / visual_parts",
          "可修复范围和禁止改动范围",
          "用户反馈"
        ],
        "outputs": [
          "修复计划",
          "修改后的结构化意图或 CAD_PLAN",
          "需要重新执行与审计的证据清单"
        ],
        "passGate": [
          {
            "label": "最小修复",
            "value": "只改根因相关内容，不扩大范围。"
          }
        ],
        "mustNot": [
          "不得靠反复改尺寸掩盖语义错误。",
          "不得把未验证修复交付给用户。"
        ],
        "usesCore": [
          "失败根因定位",
          "CAD_PLAN 最小修复",
          "回归审计触发"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_delivery",
      "name": "交付汇报智能体",
      "sourceName": "pipeline_delivery",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责用低噪声中文交付本轮训练结论、证据路径、没证明的边界和用户最该验收的位置。",
      "roleSummary": "你是交付汇报智能体，负责用低噪声中文说明本轮结论、证据边界和用户最该验收的位置。",
      "promptContractId": "contract-pipeline_delivery",
      "ownedCapabilities": [
        {
          "id": "dimension",
          "name": "简单尺寸标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "补尺寸标注检查器"
        },
        {
          "id": "text",
          "name": "简单文字标注",
          "priority": "P1",
          "stageLabel": "目标已声明",
          "nextTrainingTarget": "训练对象名称标注"
        },
        {
          "id": "layers",
          "name": "基础图层归类",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "补图层归类审计"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-dimension",
          "capabilityId": "dimension",
          "name": "简单尺寸标注",
          "priority": "P1",
          "nextTrainingTarget": "补尺寸标注检查器"
        },
        {
          "id": "program-text",
          "capabilityId": "text",
          "name": "简单文字标注",
          "priority": "P1",
          "nextTrainingTarget": "训练对象名称标注"
        },
        {
          "id": "program-layers",
          "capabilityId": "layers",
          "name": "基础图层归类",
          "priority": "P2",
          "nextTrainingTarget": "补图层归类审计"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 49,
        "note": "关联 3 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "3 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 49,
          "note": "关联 3 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "3 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_delivery/agent.json"
      ],
      "operation": {
        "role": "你负责用低噪声中文交付本轮训练结论、证据路径、没证明的边界和用户最该验收的位置。",
        "inputs": [
          "审计结果",
          "截图或回读证据",
          "训练目标",
          "失败沉淀建议",
          "用户反馈入口"
        ],
        "outputs": [
          "本轮结论",
          "相对上一轮变化",
          "证据证明了什么、没证明什么",
          "用户验收重点"
        ],
        "passGate": [
          {
            "label": "先说结论",
            "value": "训练期交付先讲本轮结果，再讲证据和边界。"
          }
        ],
        "mustNot": [
          "不得用表格堆满普通训练交付。",
          "不得暗示真实 CAD 能力已经由训练页证明。"
        ],
        "usesCore": [
          "训练交付模板",
          "证据路径整理",
          "用户验收提示",
          "边界说明"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "pipeline_learning_promoter",
      "name": "训练沉淀智能体",
      "sourceName": "pipeline_learning_promoter",
      "group": "pipeline",
      "groupLabel": "训练流水线智能体",
      "status": "active",
      "statusLabel": "活跃",
      "trainingRole": "你负责把失败、通过经验和用户反馈分流到案例反馈、场景规则、pipeline 规则、Core 检查器或系统资产库。",
      "roleSummary": "你是训练沉淀智能体，负责把失败和用户反馈分流到案例、场景规则、pipeline、Core 检查器或系统资产库。",
      "promptContractId": "contract-pipeline_learning_promoter",
      "ownedCapabilities": [
        {
          "id": "sofa",
          "name": "沙发",
          "priority": "P0",
          "stageLabel": "案例训练中",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "stageLabel": "未开训",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        }
      ],
      "activeTrainingItems": [
        {
          "id": "program-sofa",
          "capabilityId": "sofa",
          "name": "沙发",
          "priority": "P0",
          "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练"
        },
        {
          "id": "program-furniture-layout",
          "capabilityId": "furniture-layout",
          "name": "基础家具摆放",
          "priority": "P2",
          "nextTrainingTarget": "开客厅/卧室组合训练"
        }
      ],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 82,
        "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 4 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 47,
        "note": "关联 2 个训练计划项，其中 P0 1 个；表示训练表单覆盖度。",
        "basis": "2 个训练计划 / P0 1 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 46,
        "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：活跃",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 82,
          "note": "已显式关联 4 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 4 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 47,
          "note": "关联 2 个训练计划项，其中 P0 1 个；表示训练表单覆盖度。",
          "basis": "2 个训练计划 / P0 1 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 46,
          "note": "训练状态：活跃。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：活跃",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/pipeline_learning_promoter/agent.json"
      ],
      "operation": {
        "role": "你负责把失败、通过经验和用户反馈分流到案例反馈、场景规则、pipeline 规则、Core 检查器或系统资产库。",
        "inputs": [
          "审计与用户反馈",
          "失败根因",
          "是否重复出现",
          "可晋升的检查器或资产候选"
        ],
        "outputs": [
          "沉淀位置建议",
          "下一轮 Prompt 调整点",
          "是否允许晋升规则、测试或资产库的判断"
        ],
        "passGate": [
          {
            "label": "先分层",
            "value": "单案例问题留在案例，重复问题才考虑规则或 Core。"
          }
        ],
        "mustNot": [
          "不得把一次失败直接污染通用规则。",
          "不得把参考图库直接晋升自产资产。"
        ],
        "usesCore": [
          "训练错误台账",
          "场景规则沉淀",
          "Core 检查器候选",
          "系统资产晋升判断"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    },
    {
      "id": "demand_side_roles",
      "name": "需求侧角色智能体",
      "sourceName": "demand_side_roles",
      "group": "demand",
      "groupLabel": "需求侧角色",
      "status": "data_only",
      "statusLabel": "仅数据角色",
      "trainingRole": "你负责生成更像真实用户的训练需求、角色口吻和 benchmark 场景，只作为输入数据，不参与 CAD 执行。",
      "roleSummary": "你是需求侧角色数据智能体，只负责生成更像真实用户的训练需求和 benchmark，不直接参与 CAD 执行。",
      "promptContractId": "contract-demand_side_roles",
      "ownedCapabilities": [],
      "activeTrainingItems": [],
      "promptCompleteness": {
        "percent": 100,
        "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
        "basis": "5/5 类契约已声明",
        "gap": "下一轮可把描述写得更贴近真实训练话术。"
      },
      "callMaturity": {
        "percent": 68,
        "note": "已显式关联 3 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
        "basis": "显式调用 3 项",
        "gap": "缺口：把调用结果和审计证据继续连起来。"
      },
      "trainingCoverage": {
        "percent": 15,
        "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
        "basis": "0 个训练计划 / P0 0 个",
        "gap": "缺口：继续把训练项和失败类型做点对点对应。"
      },
      "evidenceMaturity": {
        "percent": 34,
        "note": "训练状态：仅数据角色。这不是表 C 真实 CAD 机器指标。",
        "basis": "训练状态：仅数据角色",
        "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
      },
      "maturity": {
        "promptCompleteness": {
          "percent": 100,
          "note": "已声明 5/5 类 Prompt 契约：角色、输入、输出、硬门槛、禁止事项。",
          "basis": "5/5 类契约已声明",
          "gap": "下一轮可把描述写得更贴近真实训练话术。"
        },
        "callMaturity": {
          "percent": 68,
          "note": "已显式关联 3 项调用能力；该百分比只表示调用契约成熟度，不表示 CAD 通过率。",
          "basis": "显式调用 3 项",
          "gap": "缺口：把调用结果和审计证据继续连起来。"
        },
        "trainingCoverage": {
          "percent": 15,
          "note": "关联 0 个训练计划项，其中 P0 0 个；表示训练表单覆盖度。",
          "basis": "0 个训练计划 / P0 0 个",
          "gap": "缺口：继续把训练项和失败类型做点对点对应。"
        },
        "evidenceMaturity": {
          "percent": 34,
          "note": "训练状态：仅数据角色。这不是表 C 真实 CAD 机器指标。",
          "basis": "训练状态：仅数据角色",
          "gap": "缺口：需要更多案例证据、用户反馈和可回读产物。"
        }
      },
      "docs": [
        "agents/demand_side_roles/agent.json"
      ],
      "operation": {
        "role": "你负责生成更像真实用户的训练需求、角色口吻和 benchmark 场景，只作为输入数据，不参与 CAD 执行。",
        "inputs": [
          "场景 ID",
          "用户角色",
          "需求焦点",
          "样例请求和验收偏好"
        ],
        "outputs": [
          "自然语言训练需求",
          "用户角色画像",
          "能力目标和验收关注点"
        ],
        "passGate": [
          {
            "label": "用途边界",
            "value": "只生成需求，不直接绘图，也不替代真实用户反馈。"
          }
        ],
        "mustNot": [
          "不得当作执行智能体。",
          "不得替代真实用户反馈。"
        ],
        "usesCore": [
          "需求样本生成",
          "角色口吻生成",
          "benchmark 场景生成"
        ],
        "optimizationTips": [
          "先明确输入、输出和通过门槛。",
          "把禁止事项写成可检查条款。",
          "重复失败时再晋升为测试或 Core 检查器。"
        ]
      }
    }
  ],
  "capabilities": [
    {
      "id": "program-sofa",
      "capabilityId": "sofa",
      "name": "沙发",
      "title": "沙发 · 开一轮沙发方向语义与贴合关系训练",
      "priority": "P0",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_repair",
        "pipeline_learning_promoter"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_visual_intent",
          "name": "视觉语义智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        },
        {
          "id": "pipeline_repair",
          "name": "修复回环智能体"
        },
        {
          "id": "pipeline_learning_promoter",
          "name": "训练沉淀智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_repair",
        "pipeline_learning_promoter"
      ],
      "focus": "方向语义、扶手/靠背/坐垫部件、共享边去重",
      "weaknesses": [
        {
          "id": "sofa_direction_semantics_inverted",
          "label": "方向语义反了",
          "note": "沙发硬背、软靠垫、坐垫的前后语义容易被倒置。"
        },
        {
          "id": "duplicate_shared_edges",
          "label": "共享边重复",
          "note": "相邻部件允许贴合，但同一 CAD 段不能重复生成。"
        }
      ],
      "nextTrainingTarget": "开一轮沙发方向语义与贴合关系训练",
      "stageState": {
        "id": "case_training",
        "label": "案例训练中",
        "rank": 2,
        "note": "沙发已有多轮家装训练上下文，本页继续把方向语义、部件和贴合关系作为下一轮目标。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“方向语义、扶手/靠背/坐垫部件、共享边去重”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "training",
          "label": "训练中",
          "note": "下一轮训练目标：开一轮沙发方向语义与贴合关系训练。"
        },
        "system": {
          "state": "planned",
          "label": "计划中",
          "note": "只有经过 promotion gate、证据边界和回归检查后，才允许进入自产资产或通用规则。"
        }
      },
      "trainingObjective": "围绕“方向语义、扶手/靠背/坐垫部件、共享边去重”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-tea-table",
      "capabilityId": "tea-table",
      "name": "茶几",
      "title": "茶几 · 补标准尺寸和组合关系检查",
      "priority": "P0",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "比例、与沙发组合距离、中心对齐",
      "weaknesses": [
        {
          "id": "retrieval_hit_as_capability",
          "label": "检索命中被当能力",
          "note": "检索到素材只算参考输入，不算系统能力。"
        }
      ],
      "nextTrainingTarget": "补标准尺寸和组合关系检查",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补标准尺寸和组合关系检查。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“比例、与沙发组合距离、中心对齐”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补标准尺寸和组合关系检查。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“比例、与沙发组合距离、中心对齐”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-dining-table",
      "capabilityId": "dining-table",
      "name": "餐桌",
      "title": "餐桌 · 训练餐桌+餐椅组合",
      "priority": "P0",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "桌面尺寸、椅子围合、通行净距",
      "weaknesses": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "训练餐桌+餐椅组合",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：训练餐桌+餐椅组合。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“桌面尺寸、椅子围合、通行净距”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：训练餐桌+餐椅组合。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“桌面尺寸、椅子围合、通行净距”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-dining-chair",
      "capabilityId": "dining-chair",
      "name": "餐椅",
      "title": "餐椅 · 补椅背和入座方向规则",
      "priority": "P0",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "朝向、椅背表达、与桌边关系",
      "weaknesses": [
        {
          "id": "missing_furniture_parts",
          "label": "家具部件缺失",
          "note": "对象必须拆清关键部件，不应只画外轮廓。"
        }
      ],
      "nextTrainingTarget": "补椅背和入座方向规则",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补椅背和入座方向规则。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“朝向、椅背表达、与桌边关系”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补椅背和入座方向规则。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“朝向、椅背表达、与桌边关系”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-bed",
      "capabilityId": "bed",
      "name": "床铺",
      "title": "床铺 · 开卧室组合训练",
      "priority": "P0",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_visual_intent",
          "name": "视觉语义智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "床头方向、床垫/枕头/床头柜组合",
      "weaknesses": [
        {
          "id": "plan_view_role_direction_errors",
          "label": "平面角色方向错误",
          "note": "平面图方向、入座方向和开门方向需要显式说明。"
        }
      ],
      "nextTrainingTarget": "开卧室组合训练",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：开卧室组合训练。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“床头方向、床垫/枕头/床头柜组合”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：开卧室组合训练。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“床头方向、床垫/枕头/床头柜组合”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-nightstand",
      "capabilityId": "nightstand",
      "name": "床头柜",
      "title": "床头柜 · 补床侧组合默认值",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "成对摆放、床侧净距、比例",
      "weaknesses": [
        {
          "id": "size_only_repair_loop",
          "label": "只靠尺寸修复",
          "note": "视觉语义错时，只调尺寸会进入无效回环。"
        }
      ],
      "nextTrainingTarget": "补床侧组合默认值",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补床侧组合默认值。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“成对摆放、床侧净距、比例”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补床侧组合默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“成对摆放、床侧净距、比例”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-wardrobe",
      "capabilityId": "wardrobe",
      "name": "衣柜",
      "title": "衣柜 · 训练衣柜开门净空 audit",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "focus": "开门净空、贴墙、与床通道",
      "weaknesses": [
        {
          "id": "machine_green_delivery",
          "label": "机器绿但视觉未验",
          "note": "机器审计绿灯不能直接替代用户可见验收。"
        }
      ],
      "nextTrainingTarget": "训练衣柜开门净空 audit",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：训练衣柜开门净空 audit。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“开门净空、贴墙、与床通道”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：训练衣柜开门净空 audit。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“开门净空、贴墙、与床通道”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-tv-cabinet",
      "capabilityId": "tv-cabinet",
      "name": "电视柜",
      "title": "电视柜 · 补客厅视线方向规则",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "朝向、墙面关系、电视/柜比例",
      "weaknesses": [
        {
          "id": "clone_reference_fragments",
          "label": "误克隆参考碎片",
          "note": "参考图不能被碎片化克隆为系统资产。"
        }
      ],
      "nextTrainingTarget": "补客厅视线方向规则",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补客厅视线方向规则。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“朝向、墙面关系、电视/柜比例”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补客厅视线方向规则。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“朝向、墙面关系、电视/柜比例”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-desk",
      "capabilityId": "desk",
      "name": "书桌",
      "title": "书桌 · 补书桌+椅组合训练",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "基础家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "座椅空间、靠窗/靠墙偏好",
      "weaknesses": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "补书桌+椅组合训练",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补书桌+椅组合训练。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“座椅空间、靠窗/靠墙偏好”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补书桌+椅组合训练。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“座椅空间、靠窗/靠墙偏好”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-low-cabinet",
      "capabilityId": "low-cabinet",
      "name": "矮柜",
      "title": "矮柜 · 先补对象默认值",
      "priority": "P2",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "基础家具",
      "matrixGroup": "储位家具",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "focus": "低柜高度语义、墙边摆放",
      "weaknesses": [
        {
          "id": "retrieval_hit_as_capability",
          "label": "检索命中被当能力",
          "note": "检索到素材只算参考输入，不算系统能力。"
        }
      ],
      "nextTrainingTarget": "先补对象默认值",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“低柜高度语义、墙边摆放”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“低柜高度语义、墙边摆放”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-basin",
      "capabilityId": "basin",
      "name": "洗手台",
      "title": "洗手台 · 训练卫浴对象部件表达",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "台盆、柜体、水龙头语义和卫浴墙面关系",
      "weaknesses": [
        {
          "id": "missing_furniture_parts",
          "label": "家具部件缺失",
          "note": "对象必须拆清关键部件，不应只画外轮廓。"
        }
      ],
      "nextTrainingTarget": "训练卫浴对象部件表达",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：训练卫浴对象部件表达。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“台盆、柜体、水龙头语义和卫浴墙面关系”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：训练卫浴对象部件表达。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“台盆、柜体、水龙头语义和卫浴墙面关系”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-toilet",
      "capabilityId": "toilet",
      "name": "马桶",
      "title": "马桶 · 补洁具默认净距",
      "priority": "P1",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "朝向、离墙尺寸、检修空间",
      "weaknesses": [
        {
          "id": "machine_size_drift_only",
          "label": "仅尺寸漂移",
          "note": "只盯尺寸漂移会漏掉语义或视觉错误。"
        }
      ],
      "nextTrainingTarget": "补洁具默认净距",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补洁具默认净距。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“朝向、离墙尺寸、检修空间”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补洁具默认净距。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“朝向、离墙尺寸、检修空间”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-stove",
      "capabilityId": "stove",
      "name": "灶台",
      "title": "灶台 · 先补厨房对象 catalog",
      "priority": "P2",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "focus": "台面、火口、厨房操作三角",
      "weaknesses": [
        {
          "id": "unsupported_or_risky",
          "label": "暂不支持或风险高",
          "note": "高风险或未支持对象应先阻塞并补常识。"
        }
      ],
      "nextTrainingTarget": "先补厨房对象 catalog",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“台面、火口、厨房操作三角”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“台面、火口、厨房操作三角”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-fridge",
      "capabilityId": "fridge",
      "name": "冰箱",
      "title": "冰箱 · 补冰箱门向和净距",
      "priority": "P2",
      "kind": "object",
      "kindLabel": "对象训练",
      "group": "厨卫对象",
      "matrixGroup": "厨卫对象",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "focus": "门开启方向、散热间距、厨房动线",
      "weaknesses": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "补冰箱门向和净距",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“门开启方向、散热间距、厨房动线”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“门开启方向、散热间距、厨房动线”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-wall",
      "capabilityId": "wall",
      "name": "墙体绘制",
      "title": "墙体绘制 · 强化墙线重复与开口检查",
      "priority": "P0",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "闭合轮廓、墙厚、图层归类",
      "weaknesses": [
        {
          "id": "duplicate_shared_edges",
          "label": "共享边重复",
          "note": "相邻部件允许贴合，但同一 CAD 段不能重复生成。"
        }
      ],
      "nextTrainingTarget": "强化墙线重复与开口检查",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：强化墙线重复与开口检查。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“闭合轮廓、墙厚、图层归类”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：强化墙线重复与开口检查。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“闭合轮廓、墙厚、图层归类”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-door",
      "capabilityId": "door",
      "name": "门绘制",
      "title": "门绘制 · 补门向语义训练",
      "priority": "P0",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "门洞、开启弧、门扇方向",
      "weaknesses": [
        {
          "id": "plan_view_role_direction_errors",
          "label": "平面角色方向错误",
          "note": "平面图方向、入座方向和开门方向需要显式说明。"
        }
      ],
      "nextTrainingTarget": "补门向语义训练",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补门向语义训练。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“门洞、开启弧、门扇方向”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补门向语义训练。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“门洞、开启弧、门扇方向”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-window",
      "capabilityId": "window",
      "name": "窗户绘制",
      "title": "窗户绘制 · 补窗洞与墙体关系 audit",
      "priority": "P0",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "窗洞、窗线层级、墙体嵌入",
      "weaknesses": [
        {
          "id": "machine_green_delivery",
          "label": "机器绿但视觉未验",
          "note": "机器审计绿灯不能直接替代用户可见验收。"
        }
      ],
      "nextTrainingTarget": "补窗洞与墙体关系 audit",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补窗洞与墙体关系 audit。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“窗洞、窗线层级、墙体嵌入”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补窗洞与墙体关系 audit。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“窗洞、窗线层级、墙体嵌入”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-door-opening",
      "capabilityId": "door-opening",
      "name": "门洞绘制",
      "title": "门洞绘制 · 训练洞口扣减检查",
      "priority": "P1",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "洞口扣减、门套语义、墙段连续",
      "weaknesses": [
        {
          "id": "duplicate_shared_edges",
          "label": "共享边重复",
          "note": "相邻部件允许贴合，但同一 CAD 段不能重复生成。"
        }
      ],
      "nextTrainingTarget": "训练洞口扣减检查",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：训练洞口扣减检查。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“洞口扣减、门套语义、墙段连续”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：训练洞口扣减检查。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“洞口扣减、门套语义、墙段连续”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-window-opening",
      "capabilityId": "window-opening",
      "name": "窗洞绘制",
      "title": "窗洞绘制 · 补窗洞标准语义",
      "priority": "P1",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "窗洞宽度、离地语义、墙内关系",
      "weaknesses": [
        {
          "id": "machine_size_drift_only",
          "label": "仅尺寸漂移",
          "note": "只盯尺寸漂移会漏掉语义或视觉错误。"
        }
      ],
      "nextTrainingTarget": "补窗洞标准语义",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补窗洞标准语义。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“窗洞宽度、离地语义、墙内关系”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补窗洞标准语义。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“窗洞宽度、离地语义、墙内关系”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-room-outline",
      "capabilityId": "room-outline",
      "name": "房间轮廓绘制",
      "title": "房间轮廓绘制 · 强化房间轮廓 validate",
      "priority": "P1",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_intent",
      "ownerAgentName": "需求拆解智能体",
      "responsibleAgentIds": [
        "pipeline_intent",
        "pipeline_context_curator",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_context_curator",
          "name": "上下文整理智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_context_curator",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "focus": "房间闭合、基点、尺寸约束",
      "weaknesses": [
        {
          "id": "silent_bbox_fallback",
          "label": "弱资产时画空 bbox",
          "note": "资产或常识不足时不能悄悄退化为空外框。"
        }
      ],
      "nextTrainingTarget": "强化房间轮廓 validate",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：强化房间轮廓 validate。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“房间闭合、基点、尺寸约束”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：强化房间轮廓 validate。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“房间闭合、基点、尺寸约束”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-column",
      "capabilityId": "column",
      "name": "柱子绘制",
      "title": "柱子绘制 · 补柱子对象规范",
      "priority": "P2",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "pipeline_execute",
      "ownerAgentName": "落图执行智能体",
      "responsibleAgentIds": [
        "pipeline_execute",
        "pipeline_intent"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute"
      ],
      "focus": "结构柱尺寸、图层、与墙体关系",
      "weaknesses": [
        {
          "id": "retrieval_hit_as_capability",
          "label": "检索命中被当能力",
          "note": "检索到素材只算参考输入，不算系统能力。"
        }
      ],
      "nextTrainingTarget": "补柱子对象规范",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“结构柱尺寸、图层、与墙体关系”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“结构柱尺寸、图层、与墙体关系”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-furniture-layout",
      "capabilityId": "furniture-layout",
      "name": "基础家具摆放",
      "title": "基础家具摆放 · 开客厅/卧室组合训练",
      "priority": "P2",
      "kind": "draw",
      "kindLabel": "绘图训练",
      "group": "基础绘图",
      "matrixGroup": "基础绘图",
      "ownerAgentId": "residential",
      "ownerAgentName": "家装场景智能体",
      "responsibleAgentIds": [
        "residential",
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_learning_promoter"
      ],
      "responsibleAgents": [
        {
          "id": "residential",
          "name": "家装场景智能体"
        },
        {
          "id": "pipeline_asset_retriever",
          "name": "资产检索智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        },
        {
          "id": "pipeline_learning_promoter",
          "name": "训练沉淀智能体"
        }
      ],
      "pipeline": [
        "pipeline_asset_retriever",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_learning_promoter"
      ],
      "focus": "组合关系、通道、朝向和避让",
      "weaknesses": [
        {
          "id": "visual_fail_size_only_repair",
          "label": "视觉失败却只调尺寸",
          "note": "视觉失败时应回到视觉语义智能体。"
        }
      ],
      "nextTrainingTarget": "开客厅/卧室组合训练",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮需要检索标准图库、对象默认值或参考资料；命中只算上游证据，不算 CAD 通过。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“组合关系、通道、朝向和避让”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "planned",
          "label": "计划中",
          "note": "只有经过 promotion gate、证据边界和回归检查后，才允许进入自产资产或通用规则。"
        }
      },
      "trainingObjective": "围绕“组合关系、通道、朝向和避让”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-dimension",
      "capabilityId": "dimension",
      "name": "简单尺寸标注",
      "title": "简单尺寸标注 · 补尺寸标注检查器",
      "priority": "P1",
      "kind": "annotation",
      "kindLabel": "标注训练",
      "group": "标注表达",
      "matrixGroup": "标注表达",
      "ownerAgentId": "pipeline_delivery",
      "ownerAgentName": "交付汇报智能体",
      "responsibleAgentIds": [
        "pipeline_delivery",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_delivery",
          "name": "交付汇报智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_delivery"
      ],
      "focus": "标注对象、尺寸线位置、比例和避让",
      "weaknesses": [
        {
          "id": "missing_annotation",
          "label": "标注缺失",
          "note": "标注训练要明确对象、位置、比例和避让。"
        }
      ],
      "nextTrainingTarget": "补尺寸标注检查器",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：补尺寸标注检查器。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“标注对象、尺寸线位置、比例和避让”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：补尺寸标注检查器。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“标注对象、尺寸线位置、比例和避让”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-text",
      "capabilityId": "text",
      "name": "简单文字标注",
      "title": "简单文字标注 · 训练对象名称标注",
      "priority": "P1",
      "kind": "annotation",
      "kindLabel": "标注训练",
      "group": "标注表达",
      "matrixGroup": "标注表达",
      "ownerAgentId": "pipeline_delivery",
      "ownerAgentName": "交付汇报智能体",
      "responsibleAgentIds": [
        "pipeline_delivery",
        "pipeline_intent",
        "pipeline_execute"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_delivery",
          "name": "交付汇报智能体"
        },
        {
          "id": "pipeline_intent",
          "name": "需求拆解智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        }
      ],
      "pipeline": [
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_delivery"
      ],
      "focus": "文字内容、图层、与对象关联",
      "weaknesses": [
        {
          "id": "missing_annotation",
          "label": "标注缺失",
          "note": "标注训练要明确对象、位置、比例和避让。"
        }
      ],
      "nextTrainingTarget": "训练对象名称标注",
      "stageState": {
        "id": "prompt_defined",
        "label": "目标已声明",
        "rank": 1,
        "note": "已在训练表单中声明下一轮目标：训练对象名称标注。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“文字内容、图层、与对象关联”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "planned",
          "label": "计划中",
          "note": "下一轮训练目标：训练对象名称标注。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“文字内容、图层、与对象关联”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    },
    {
      "id": "program-layers",
      "capabilityId": "layers",
      "name": "基础图层归类",
      "title": "基础图层归类 · 补图层归类审计",
      "priority": "P2",
      "kind": "annotation",
      "kindLabel": "标注训练",
      "group": "标注表达",
      "matrixGroup": "标注表达",
      "ownerAgentId": "pipeline_audit",
      "ownerAgentName": "机器审计智能体",
      "responsibleAgentIds": [
        "pipeline_audit",
        "pipeline_execute",
        "pipeline_delivery"
      ],
      "responsibleAgents": [
        {
          "id": "pipeline_audit",
          "name": "机器审计智能体"
        },
        {
          "id": "pipeline_execute",
          "name": "落图执行智能体"
        },
        {
          "id": "pipeline_delivery",
          "name": "交付汇报智能体"
        }
      ],
      "pipeline": [
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_delivery"
      ],
      "focus": "CODEX_PREVIEW、正式图层保护、对象分层",
      "weaknesses": [
        {
          "id": "formal_layer_write_risk",
          "label": "正式图层写入风险",
          "note": "训练默认只写 CODEX_PREVIEW，不碰正式图层。"
        }
      ],
      "nextTrainingTarget": "补图层归类审计",
      "stageState": {
        "id": "not_started",
        "label": "未开训",
        "rank": 0,
        "note": "已列入候选训练项，尚未进入当前主训案例。"
      },
      "assetStates": {
        "raw": {
          "state": "empty",
          "label": "未纳入",
          "note": "此项当前不以标准图库接收为主。"
        },
        "knowledge": {
          "state": "planned",
          "label": "计划中",
          "note": "围绕“CODEX_PREVIEW、正式图层保护、对象分层”整理中文常识、默认值和场景规则。"
        },
        "trained": {
          "state": "empty",
          "label": "未纳入",
          "note": "尚未进入案例训练，先补 Prompt 或对象默认值。"
        },
        "system": {
          "state": "empty",
          "label": "未纳入",
          "note": "当前没有自产资产沉淀计划。"
        }
      },
      "trainingObjective": "围绕“CODEX_PREVIEW、正式图层保护、对象分层”开一轮可验收训练，不把页面状态当作真实 CAD 几何证明。",
      "successCriteria": [
        "能用中文说明对象或绘图动作的方向、部件、尺寸和边界。",
        "责任智能体能说清输入、输出、硬门槛和禁止事项。",
        "如进入真实落图，必须保留 validate、dry-run、CODEX_PREVIEW、回读或审计证据。"
      ],
      "notPassConditions": [
        "只有计划、标签或检索命中，不能算训练通过。",
        "机器审计通过但用户可见效果或 Agent 自检未过，不能算训练通过。",
        "未写清失败根因和沉淀位置，不能算已沉淀。"
      ],
      "evidenceRequired": [
        "本轮 intent / visual_parts / CAD_PLAN 或明确的 deferred 说明。",
        "机器审计、Agent 自检和用户反馈中的至少一种可追溯证据。",
        "训练失败时的根因、修复目标和下一轮 Prompt 调整点。"
      ]
    }
  ],
  "failureModes": [
    {
      "id": "sofa_direction_semantics_inverted",
      "label": "方向语义反了",
      "weight": 92,
      "agents": [
        "residential",
        "pipeline_visual_intent",
        "pipeline_intent"
      ],
      "note": "沙发硬背、软靠垫、坐垫的前后语义容易被倒置。"
    },
    {
      "id": "duplicate_shared_edges",
      "label": "共享边重复",
      "weight": 78,
      "agents": [
        "pipeline_execute",
        "pipeline_repair",
        "pipeline_audit"
      ],
      "note": "相邻部件允许贴合，但同一 CAD 段不能重复生成。"
    },
    {
      "id": "silent_bbox_fallback",
      "label": "弱资产时画空 bbox",
      "weight": 70,
      "agents": [
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "note": "资产或常识不足时不能悄悄退化为空外框。"
    },
    {
      "id": "retrieval_hit_as_capability",
      "label": "检索命中被当能力",
      "weight": 45,
      "agents": [
        "pipeline_asset_retriever",
        "pipeline_learning_promoter"
      ],
      "note": "检索到素材只算参考输入，不算系统能力。"
    },
    {
      "id": "machine_green_delivery",
      "label": "机器绿但视觉未验",
      "weight": 50,
      "agents": [
        "pipeline_audit",
        "pipeline_delivery"
      ],
      "note": "机器审计绿灯不能直接替代用户可见验收。"
    },
    {
      "id": "clone_reference_fragments",
      "label": "误克隆参考碎片",
      "weight": 58,
      "agents": [
        "pipeline_asset_retriever",
        "pipeline_visual_intent"
      ],
      "note": "参考图不能被碎片化克隆为系统资产。"
    },
    {
      "id": "size_only_repair_loop",
      "label": "只靠尺寸修复",
      "weight": 64,
      "agents": [
        "pipeline_repair",
        "pipeline_audit"
      ],
      "note": "视觉语义错时，只调尺寸会进入无效回环。"
    },
    {
      "id": "missing_furniture_parts",
      "label": "家具部件缺失",
      "weight": 72,
      "agents": [
        "pipeline_visual_intent",
        "pipeline_execute",
        "pipeline_audit"
      ],
      "note": "对象必须拆清关键部件，不应只画外轮廓。"
    },
    {
      "id": "plan_view_role_direction_errors",
      "label": "平面角色方向错误",
      "weight": 66,
      "agents": [
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_audit"
      ],
      "note": "平面图方向、入座方向和开门方向需要显式说明。"
    },
    {
      "id": "machine_size_drift_only",
      "label": "仅尺寸漂移",
      "weight": 40,
      "agents": [
        "pipeline_audit",
        "pipeline_repair"
      ],
      "note": "只盯尺寸漂移会漏掉语义或视觉错误。"
    },
    {
      "id": "unsupported_or_risky",
      "label": "暂不支持或风险高",
      "weight": 36,
      "agents": [
        "pipeline_asset_retriever",
        "pipeline_intent"
      ],
      "note": "高风险或未支持对象应先阻塞并补常识。"
    },
    {
      "id": "visual_fail_size_only_repair",
      "label": "视觉失败却只调尺寸",
      "weight": 62,
      "agents": [
        "pipeline_repair",
        "pipeline_audit"
      ],
      "note": "视觉失败时应回到视觉语义智能体。"
    },
    {
      "id": "missing_annotation",
      "label": "标注缺失",
      "weight": 52,
      "agents": [
        "pipeline_delivery",
        "pipeline_audit"
      ],
      "note": "标注训练要明确对象、位置、比例和避让。"
    },
    {
      "id": "formal_layer_write_risk",
      "label": "正式图层写入风险",
      "weight": 34,
      "agents": [
        "pipeline_execute",
        "pipeline_audit"
      ],
      "note": "训练默认只写 CODEX_PREVIEW，不碰正式图层。"
    }
  ],
  "learningRoutes": [
    {
      "from": "单案例失败",
      "to": "projects/<case>/feedback.md",
      "desc": "先留在案例反馈，不立即污染通用规则。"
    },
    {
      "from": "重复失败",
      "to": "docs/training/training-errors.md",
      "desc": "记录模式、根因和下一轮训练约束。"
    },
    {
      "from": "场景常识",
      "to": "agents/<scene>/rules.md",
      "desc": "比如家装家具方向、组合关系、默认净距。"
    },
    {
      "from": "链路硬门槛",
      "to": "agents/pipeline/*/agent.json",
      "desc": "比如禁止 bbox fallback、必须声明证据边界。"
    },
    {
      "from": "可机器检查",
      "to": "core/verification 或 tests",
      "desc": "重复问题应晋升为检查器或回归测试。"
    },
    {
      "from": "可复用图块",
      "to": "libraries/system_library",
      "desc": "只有经过 promotion gate 的资产才进入自有图库。"
    }
  ],
  "sources": [
    {
      "title": "场景 Agent",
      "path": "agents/<scene>/agent.json + rules.md",
      "desc": "领域词汇、偏好、场景边界和训练状态。"
    },
    {
      "title": "Pipeline Agent",
      "path": "agents/pipeline/*/agent.json",
      "desc": "上下文、资产、视觉意图、执行、审计、修复、沉淀等链路职责。"
    },
    {
      "title": "能力覆盖快照",
      "path": "output/validation_runs/capability-lab/cad_capability_coverage.json",
      "desc": "表 C 机器指标来源，不和本页阶段混用。"
    },
    {
      "title": "标准图库 raw",
      "path": "standard_cad_library_raw/",
      "desc": "外来参考素材入口，默认 reference_only，不直接算系统能力。"
    },
    {
      "title": "训练反馈",
      "path": "projects/<case>/feedback.md + docs/training/training-errors.md",
      "desc": "点对点训练和失败复盘的沉淀位置。"
    }
  ],
  "pipelineFlow": [
    {
      "id": "context",
      "title": "上下文整理",
      "desc": "先恢复上下文，过滤旧状态和历史噪声。"
    },
    {
      "id": "asset",
      "title": "资产检索",
      "desc": "查标准图库、常识、历史失败和证据边界。"
    },
    {
      "id": "visual",
      "title": "视觉语义",
      "desc": "把参考图和白话拆成部件级视觉契约。"
    },
    {
      "id": "intent",
      "title": "意图与计划",
      "desc": "白话转结构化意图，再进入 CAD_PLAN。"
    },
    {
      "id": "execute",
      "title": "执行审计修复",
      "desc": "落 CODEX_PREVIEW，审计，失败则修复并沉淀。"
    }
  ]
};
