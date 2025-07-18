import json
import sys
from pathlib import Path

# --- Local Imports ---
from ncc_risk_detector.contract_parser import parse_contract_pdf
from ncc_risk_detector.matcher import find_similarities
from ncc_risk_detector.matcher_llama import reason_with_llama
from ncc_risk_detector.ncc_processor import load_ncc_data
# CORRECTED IMPORT PATH
from ncc_risk_detector.report_generator import generate_llama_summary_report

# --- CONFIGURATION ---
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
CONTRACT_FILE = DATA_DIR / "contract.pdf"
NCC_FILE = DATA_DIR / "nccs.xlsx"
RESULTS_JSON_FILE = OUTPUT_DIR / "results_llama.json"
SUMMARY_TXT_FILE = OUTPUT_DIR / "summary_llama.txt" # Added config for summary file
SIMILARITY_THRESHOLD = 0.55

def main():
    """
    Main function to run the risk analysis pipeline using Llama for reasoning.
    """
    # --- 1. Load Data ---
    print("➡️ Loading input files...")
    try:
        nccs = load_ncc_data(NCC_FILE)
        contract_segments = parse_contract_pdf(CONTRACT_FILE)
    except FileNotFoundError as e:
        print(f"❌ ERROR: Input file not found - {e}", file=sys.stderr)
        sys.exit(1)

    # --- 2. Analyze Risks ---
    print("➡️ Finding initial similarities... (This may take a moment)")
    similarity_results = find_similarities(nccs, contract_segments, threshold=SIMILARITY_THRESHOLD)
    print(f"Found {len(similarity_results)} potential matches. Now reasoning with Llama...")

    final_output = []
    for item in similarity_results:
        contract_text = item['contract_segment']
        ncc = next((n for n in nccs if n["ID"] == item["matches"][0]["ncc_id"]), None)
        if not ncc:
            continue
        
        print(f"   - Analyzing risk for NCC ID: {ncc['ID']}...")
        judgment = reason_with_llama(contract_text, ncc['Description'])

        final_output.append({
            "contract_segment": contract_text,
            "ncc_id": ncc['ID'],
            "ncc_title": ncc['Title'],
            "initial_similarity": item['matches'][0]['similarity'],
            "risk_judgment": judgment.get("risk_judgment", "Error"),
            "reasoning": judgment.get("reasoning", "No reasoning provided.")
        })
    
    print("✅ Llama analysis complete.")

    # --- 3. Save Results ---
    print("➡️ Saving Llama-powered results...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    with RESULTS_JSON_FILE.open("w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)

    # --- 4. Generate Human-Readable Report ---
    # MOVED THIS SECTION INSIDE THE MAIN FUNCTION
    print("➡️ Generating human-readable Llama summary...")
    generate_llama_summary_report(final_output, SUMMARY_TXT_FILE)

    # Use a single, comprehensive success message
    print(f"\n🎉 Success! Llama-verified results in '{RESULTS_JSON_FILE}' and a summary in '{SUMMARY_TXT_FILE}'")

if __name__ == "__main__":
    main()