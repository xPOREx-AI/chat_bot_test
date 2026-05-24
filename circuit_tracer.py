import networkx as nx
import json

def build_circuit_graph():
    # สร้างกราฟแบบมีทิศทาง (Directed Graph: จากแหล่งจ่ายไฟไหลไปหาโหลด)
    G = nx.DiGraph()

    # 1. เพิ่ม Nodes (อุปกรณ์) พร้อมใส่ข้อมูล Metadata ลงไป
    G.add_node("-QAB1", type="Circuit Breaker 1250A", page=6)
    G.add_node("-QCE1", type="Earthing Switch", page=6)
    G.add_node("-PFV1", type="Voltage Indicator", page=6)
    G.add_node("-FA1", type="Protection Relay", page=6)
    G.add_node("BUSBAR_MAIN", type="Main Power Source", page=None)
    G.add_node("MOTOR_PUMP", type="3-Phase Motor", page=10) # สมมติโหลดปลายทาง

    # 2. เพิ่ม Edges (การโยงสายไฟ / การเชื่อมต่อวงจร)
    G.add_edges_from([
        ("BUSBAR_MAIN", "-QAB1", {"wire_type": "Main Power Line"}),
        ("-QAB1", "-QCE1", {"wire_type": "Grounding Connection"}),
        ("-QAB1", "-FA1", {"wire_type": "Control Signal"}),
        ("-QAB1", "-PFV1", {"wire_type": "Measurement Line"}),
        ("-QAB1", "MOTOR_PUMP", {"wire_type": "Power Output"})
    ])
    
    return G

def analyze_fault_impact(G, faulty_component):
    print(f"🔍 วิเคราะห์ผลกระทบเมื่ออุปกรณ์ [{faulty_component}] เสียหาย/ทริป:\n" + "-"*50)
    
    if not G.has_node(faulty_component):
        print("ไม่พบอุปกรณ์นี้ในระบบฐานข้อมูลวงจร")
        return

    # หาว่าอุปกรณ์นี้รับไฟ/สัญญาณมาจากไหน (Upstream)
    upstream = list(G.predecessors(faulty_component))
    if upstream:
        print(f"⚡ รับไฟมาจาก: {', '.join(upstream)}")
        
    # [แก้ไขตรงนี้] หาว่าอุปกรณ์นี้ส่งไฟ/สัญญาณไปที่ไหนบ้าง (Downstream - จุดที่ได้รับผลกระทบ)
    downstream = list(nx.descendants(G, faulty_component))
    if downstream:
        print(f"⚠️ อุปกรณ์ที่ได้รับผลกระทบ (วงจรปลายทาง):")
        for node in downstream:
            node_data = G.nodes[node]
            print(f"   - {node} ({node_data.get('type')}) [ดูแบบไฟฟ้าหน้า {node_data.get('page')}]")

if __name__ == "__main__":
    circuit_graph = build_circuit_graph()
    
    # สมมติสถานการณ์: ช่างแจ้งว่าเบรกเกอร์ -QAB1 ทริป
    analyze_fault_impact(circuit_graph, "-QAB1")