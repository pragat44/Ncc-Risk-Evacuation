from .matcher import find_similarities
from transformers import pipeline

nli_pipeline = pipeline("text-classification", model="roberta-large-mnli")

def reason_about_risks(similarity_results, nccs, contract_segments):
    enhanced_results = []

    for result in similarity_results:
        clause = result["contract_segment"]
        enhanced_matches = []

        for match in result["matches"]:
            ncc = next((n for n in nccs if n["ID"] == match["ncc_id"]), None)
            if not ncc:
                continue

            hypothesis = f"The contract clause explicitly addresses and mitigates the risk of: {ncc['Title']}."
            output = nli_pipeline(f"{clause} </s> {hypothesis}", truncation=True)[0]
            label = output["label"]
            score = output["score"]

            # --- THIS IS THE CORRECTED LOGIC ---
            if label == "ENTAILMENT":
                judgment = "Risk Mitigated"
            elif label == "CONTRADICTION":
                judgment = "Risk Present"
            else: # NEUTRAL
                judgment = "Uncertain / Needs Manual Review"
            # ------------------------------------

            match["nli_label"] = label
            match["nli_score"] = score
            match["risk_judgment"] = judgment
            enhanced_matches.append(match)

        if enhanced_matches:
            enhanced_results.append({
                "contract_segment": clause,
                "matches": enhanced_matches
            })

    return enhanced_results