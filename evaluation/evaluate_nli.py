"""Run a small, manually labelled CPU pilot for the cached NLI model."""

import json
import time
from collections import Counter
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


MODEL_ID = "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli"
MODEL_REVISION = "0a71e92a985b6e1ad1828cf67ce9c459639c1dca"
ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = Path(__file__).with_name("nli_pilot_results.json")


def load_records(relative_path: str) -> dict[str, dict[str, str]]:
    path = ROOT / relative_path
    return {
        row["id"]: row
        for row in (
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
        )
    }


def make_case(
    records: dict[str, dict[str, str]],
    category: str,
    record_id: str,
    evidence: str,
    claim: str,
    expected: str,
) -> dict[str, str]:
    source = records[record_id]["text"]
    if evidence not in source:
        prefix = evidence.rstrip(".")
        start = source.find(prefix)
        if start < 0:
            raise ValueError(
                f"Evidence is not an exact substring of {record_id}: {evidence!r}"
            )
        end = source.find(".", start + len(prefix))
        if end < 0:
            raise ValueError(f"Evidence has no sentence boundary in {record_id}")
        evidence = source[start : end + 1]
    return {
        "category": category,
        "record_id": record_id,
        "evidence": evidence,
        "claim": claim,
        "expected": expected,
    }


def build_cases() -> list[dict[str, str]]:
    english = load_records("data/processed/xlsum_pilot/english.jsonl")
    hindi = load_records("data/processed/xlsum_pilot/hindi.jsonl")
    mixed = load_records("data/processed/mutant_pilot/code_mixed.jsonl")
    cases: list[dict[str, str]] = []

    def add(category, records, record_id, evidence, claim, expected):
        cases.append(make_case(records, category, record_id, evidence, claim, expected))

    add("english", english, "uk-wales-56321577",
        "The Met Office has issued a yellow weather warning for wind covering Wales and England.",
        "A yellow wind warning covers Wales and England.", "entailment")
    add("english", english, "uk-wales-56321577",
        "Travel and power are both likely to be disrupted.",
        "Travel and power will definitely be unaffected.", "contradiction")
    add("english", english, "uk-wales-56321577",
        "Gusts of 55mph (88kmh) are likely.",
        "The warning was issued in Scotland.", "neutral")
    add("english", english, "uk-scotland-highlands-islands-11069985",
        "The device stands 22.5m (73ft) tall, weighs 1,300 tonnes and has two sets of blades on a single unit.",
        "The device is 22.5m tall and weighs 1,300 tonnes.", "entailment")
    add("english", english, "uk-scotland-highlands-islands-11069985",
        "It could generate enough power for 1,000 homes.",
        "It could generate enough power for 10,000 homes.", "contradiction")
    add("english", english, "uk-scotland-highlands-islands-11069985",
        "Trials on the device will now be run at the European Marine Energy Centre test site off Eday.",
        "The trials will be run in London.", "contradiction")
    add("english", english, "uk-england-leeds-45776523",
        "The man was taken to hospital for treatment but his condition is not known.",
        "The man was taken to hospital, but his condition is unknown.", "entailment")
    add("english", english, "uk-england-leeds-45776523",
        "The force has appealed for information.",
        "The force did not ask the public for information.", "contradiction")
    add("english", english, "uk-england-leeds-45776523",
        "the area has been cordoned off and officers remain at the scene.",
        "The incident happened at an airport.", "neutral")
    add("english", english, "uk-scotland-highlands-islands-11069985",
        "The device stands 22.5m (73ft) tall.",
        "The device is 73 feet tall.", "entailment")
    add("english", english, "uk-wales-56321577",
        "the warning to remain in place until 15:00 on Thursday.",
        "The warning is for rain rather than wind.", "neutral")
    add("english", english, "uk-england-leeds-45776523",
        "Police were called to the scene outside the Coral shop on Compton Road in Harehills just before 14:00 BST.",
        "The shop was closed for renovations the next day.", "neutral")

    add("hindi", hindi, "international-50010000",
        "नेपाल में इस दौरे की भरपूर तैयारियां चल रही हैं.",
        "नेपाल में इस दौरे की तैयारियां चल रही हैं।", "entailment")
    add("hindi", hindi, "international-50010000",
        "23 साल बाद कोई चीनी राष्ट्रपति नेपाल पहुंच रहा है.",
        "23 साल बाद कोई भारतीय राष्ट्रपति नेपाल पहुंच रहा है।", "contradiction")
    add("hindi", hindi, "international-50010000",
        "नेपाल में इस दौरे की भरपूर तैयारियां चल रही हैं.",
        "नेपाल की राजधानी काठमांडू में बारिश हो रही है।", "neutral")
    add("hindi", hindi, "vert-fut-45498890",
        "राजी केवट ने साल 2014 में ये ऑपरेशन कराया था.",
        "राजी केवट ने 2014 में यह ऑपरेशन कराया था।", "entailment")
    add("hindi", hindi, "vert-fut-45498890",
        "उनकी नसबंदी भारत के सरकारी नसबंदी शिविर में हुआ था.",
        "उनकी नसबंदी किसी निजी अस्पताल में हुई थी।", "contradiction")
    add("hindi", hindi, "vert-fut-45498890",
        "इसके बाद राजी ने अपनी बहन शिव कुमारी केवट को भी नसबंदी कराने की सलाह दी.",
        "शिव कुमारी केवट ने 2015 में यह सलाह दी थी।", "neutral")
    add("hindi", hindi, "india-49258186",
        "संसद के दोनों सदनों ने पास कर दिया.",
        "संसद के दोनों सदनों ने इसे पारित कर दिया।", "entailment")
    add("hindi", hindi, "india-49258186",
        "जम्मू-कश्मीर अब दो केंद्र शासित प्रदेश में विभाजित हो गया है.",
        "जम्मू-कश्मीर एक ही केंद्र शासित प्रदेश बना रहा।", "contradiction")
    add("hindi", hindi, "india-49258186",
        "केंद्र सरकार ने जम्मू-कश्मीर राज्य पुर्नगठन बिल का भी प्रस्ताव रखा.",
        "इस विधेयक पर संयुक्त राष्ट्र में मतदान हुआ।", "neutral")
    add("hindi", hindi, "050225_iraq_violence",
        "अमरीकी सेना के एक प्रवक्ता ने कहा कि सैनिक बग़दाद के उत्तरी शहर तरमीया में पैदल गश्त लगा रहे थे",
        "अमरीकी सैनिक तरमीया में पैदल गश्त लगा रहे थे।", "entailment")
    add("hindi", hindi, "050225_iraq_violence",
        "उन पर बमों से हमला किया गया.",
        "उन पर किसी हथियार से हमला नहीं हुआ।", "contradiction")
    add("hindi", hindi, "050225_iraq_violence",
        "मौक़े पर मौजूद लोगों का कहना है कि बमों को संभवतः सड़क के किनारे पेड़ों में छुपाया गया था.",
        "हमले के बाद बग़दाद में कर्फ्यू लगाया गया।", "neutral")

    add("code_mixed", mixed, "mutant:bhaskar/Part1/business_1000.txt",
        "सरकार ने ऑटोमोबाइल इंडस्ट्री के लिए तय की गई 25,938 करोड़ रुपए की प्रोडक्शन लिंक्ड इन्सेंटिव (PLI) स्कीम के लिए 20 कंपनियों को शॉर्टलिस्ट कर लिया है।",
        "PLI स्कीम के लिए 20 कंपनियां शॉर्टलिस्ट की गई हैं।", "entailment")
    add("code_mixed", mixed, "mutant:bhaskar/Part1/business_1000.txt",
        "इसके लिए 115 कंपनियों ने ऐप्लीकेशन दिया था।",
        "इस स्कीम के लिए केवल 15 कंपनियों ने ऐप्लीकेशन दिया था।", "contradiction")
    add("code_mixed", mixed, "mutant:bhaskar/Part1/business_1000.txt",
        "चैंपियन OEM सेल्स प्राइस से जुड़ा प्लान है।",
        "यह योजना केवल software companies के लिए है।", "neutral")
    add("code_mixed", mixed, "mutant:bhaskar/Part1/business_1001.txt",
        "दिल्ली से मुंबई तक कई शहरों में बंद रहा ट्विटर",
        "Twitter कई शहरों में बंद रहा।", "entailment")
    add("code_mixed", mixed, "mutant:bhaskar/Part1/business_1001.txt",
        "ट्विटर ऐप और वेबसाइट पूरी तरह बंद हो गई थीं।",
        "Twitter app और website पूरी तरह चालू थीं।", "contradiction")
    add("code_mixed", mixed, "mutant:bhaskar/Part1/business_1001.txt",
        "TweetDeck जैसी सर्विसेज कुछ यूजर्स के लिए काम कर रहीं थीं।",
        "Twitter outage के कारण सभी users ने अपना password बदल दिया।", "neutral")
    add("code_mixed", mixed, "mutant:pm-speech/100.txt",
        "Energy, food processing, logistics, infrastructure, machinery, software आदि अनेक क्षेत्रों में डेनिश कंपनियां लंबे समय से भारत में काम कर रही हैं।",
        "Danish companies have worked in India in several sectors for a long time.", "entailment")
    add("code_mixed", mixed, "mutant:pm-speech/100.txt",
        "भारत की प्रगति के लिए जो हमारा vision हैं",
        "भारत की प्रगति के लिए कोई vision नहीं है।", "contradiction")
    add("code_mixed", mixed, "mutant:pm-speech/100.txt",
        "हमने आज एक निर्णय यह भी लिया, कि हम अपने सहयोग के दायरे का सतत रूप से विस्तार करते रहेंगे",
        "The meeting took place in Mumbai.", "neutral")
    add("code_mixed", mixed, "mutant:pib/10007.txt",
        "मुम्बई बंदरगाह पर वाटरफ्रंट विकास के तहत दो तैरते रेस्त्रां का उद्घाटन करेंगे।",
        "Mumbai port will have two floating restaurants inaugurated.", "entailment")
    add("code_mixed", mixed, "mutant:pib/10007.txt",
        "इन रेस्त्रां में 500 जीवन रक्षक जैकेट और रबर की 24 छोटी नौकाएं उपलब्ध रहेंगी।",
        "इन रेस्त्रां में कोई life jacket उपलब्ध नहीं होगी।", "contradiction")
    add("code_mixed", mixed, "mutant:pib/10007.txt",
        "मुम्बई-ऐलिफेंटा रोपवे समुद्र पर बनी दुनिया की सबसे अधिक लगभग 8 किलोमीटर लम्बी होगी।",
        "The ropeway will connect Delhi and Agra.", "neutral")
    return cases


def metrics(results: list[dict[str, object]]) -> dict[str, object]:
    labels = ["entailment", "contradiction", "neutral"]
    expected = [str(row["expected"]) for row in results]
    predicted = [str(row["predicted"]) for row in results]
    matrix = {actual: {label: 0 for label in labels} for actual in labels}
    for actual, prediction in zip(expected, predicted):
        matrix[actual][prediction] += 1
    per_class = {}
    for label in labels:
        tp = matrix[label][label]
        fp = sum(matrix[actual][label] for actual in labels if actual != label)
        fn = sum(matrix[label][other] for other in labels if other != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1}
    return {
        "accuracy": sum(a == p for a, p in zip(expected, predicted)) / len(results),
        "macro_f1": sum(item["f1"] for item in per_class.values()) / len(labels),
        "per_class": per_class,
        "confusion_matrix": matrix,
    }


def main() -> None:
    cases = build_cases()
    assert len(cases) == 36
    assert Counter(case["category"] for case in cases) == {
        "english": 12,
        "hindi": 12,
        "code_mixed": 12,
    }
    assert Counter(
        (case["category"], case["expected"]) for case in cases
    ) == Counter({(category, label): 4 for category in ("english", "hindi", "code_mixed") for label in ("entailment", "contradiction", "neutral")})

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, local_files_only=True
    ).to("cpu")
    model.eval()
    id2label = {int(key): value for key, value in model.config.id2label.items()}
    assert id2label == {0: "entailment", 1: "neutral", 2: "contradiction"}

    results = []
    with torch.inference_mode():
        for case in cases:
            encoded = tokenizer(
                case["evidence"],
                case["claim"],
                truncation=True,
                return_tensors="pt",
            )
            token_count = int(encoded["input_ids"].shape[1])
            started = time.perf_counter()
            logits = model(**encoded).logits[0]
            elapsed_ms = (time.perf_counter() - started) * 1000
            probabilities = torch.softmax(logits, dim=-1)
            best_index = int(torch.argmax(probabilities))
            results.append({
                **case,
                "predicted": id2label[best_index],
                "scores": {
                    id2label[index]: float(probabilities[index])
                    for index in range(len(probabilities))
                },
                "token_count": token_count,
                "truncated": token_count >= tokenizer.model_max_length,
                "latency_ms": elapsed_ms,
            })

    report = {
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "device": "cpu",
        "id2label": id2label,
        "example_count": len(results),
        "metrics": metrics(results),
        "by_category": {
            category: metrics([row for row in results if row["category"] == category])
            for category in ("english", "hindi", "code_mixed")
        },
        "latency_ms": {
            "mean": sum(row["latency_ms"] for row in results) / len(results),
            "median": sorted(row["latency_ms"] for row in results)[len(results) // 2],
        },
        "truncated_count": sum(row["truncated"] for row in results),
        "results": results,
    }
    RESULTS_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "device": "cpu",
        "id2label": id2label,
        "example_count": len(results),
        "metrics": report["metrics"],
        "by_category": report["by_category"],
        "latency_ms": report["latency_ms"],
        "truncated_count": report["truncated_count"],
        "results_path": str(RESULTS_PATH),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
