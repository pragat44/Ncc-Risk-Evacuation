# In src/report_generator.py
from pathlib import Path

# ... (keep your existing generate_summary_report function) ...

def generate_llama_summary_report(results: list[dict], output_path: Path):
    """
    Generates a human-readable summary from the Llama model's analysis.
    """
    # Filter results into categories based on the judgment
    risks_identified = [r for r in results if r.get('risk_judgment') == 'Risk Identified']
    risks_uncertain = [r for r in results if r.get('risk_judgment') == 'Uncertain']
    risks_mitigated = [r for r in results if r.get('risk_judgment') == 'Risk Mitigated']

    report_lines = []
    report_lines.append("LLAMA-POWERED RISK ANALYSIS SUMMARY")
    report_lines.append("==================================\n")

    if not risks_identified and not risks_uncertain:
        report_lines.append("✅ Llama analysis found no significant risks or uncertainties.\n")
    else:
        if risks_identified:
            report_lines.append("--- 🚨 High-Risk Items Identified ---")
            for item in risks_identified:
                report_lines.append(f"  - NCC Title: {item.get('ncc_title', 'N/A')}")
                report_lines.append(f"    Contract Clause: \"{item.get('contract_segment', '').strip()}\"")
                report_lines.append(f"    Llama's Reasoning: {item.get('reasoning', 'N/A')}\n")

        if risks_uncertain:
            report_lines.append("--- ⚠️ Uncertain / Needs Manual Review ---")
            for item in risks_uncertain:
                report_lines.append(f"  - NCC Title: {item.get('ncc_title', 'N/A')}")
                report_lines.append(f"    Contract Clause: \"{item.get('contract_segment', '').strip()}\"")
                report_lines.append(f"    Llama's Reasoning: {item.get('reasoning', 'N/A')}\n")

    if risks_mitigated:
        report_lines.append("--- ✅ Mitigated Risks ---")
        report_lines.append("The following potential issues were analyzed and appear to be mitigated by the contract:\n")
        for item in risks_mitigated:
            report_lines.append(f"  - NCC Title: {item.get('ncc_title', 'N/A')}")
            report_lines.append(f"    Llama's Reasoning: {item.get('reasoning', 'N/A')}\n")

    # Write the report to the specified file
    try:
        with output_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
    except IOError as e:
        print(f"Error writing summary file: {e}")