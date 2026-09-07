
import glob
import hashlib
import json
import re
import frontmatter

SOURCE_GLOB = "data/knowledge_base/*.md"
OUTPUT_PATH = "data/knowledge_base.json"

PROCESS_CONTROL = "predictive-maintenance"

# One question template per section title. Falls back to a generic
# "Tell me about {section}" phrasing if a section title isn't listed here.
QUESTION_TEMPLATES = {
    "Symptoms": "What are the symptoms of {name}?",
    "Root Cause": "What is the root cause of {name}?",
    "Sensor Signature": "What is the sensor signature of {name}?",
    "Recommended Action": "What is the recommended action for {name}?",
    "Escalation & Safety": "What are the escalation and safety considerations for {name}?",
    "Trigger Confirmation & Severity Classification": "How do I confirm the trigger and classify severity for a maintenance incident?",
    "Halt Criteria": "What are the halt criteria for a production line incident?",
    "Report Contents & Escalation Contacts": "What should an incident report contain and who should it be escalated to?",
    "Raw Sensor Fields": "What raw sensor fields does the AI4I dataset include?",
    "Derived Features & Quick Lookup": "What derived features are needed for failure diagnosis, and which fields does each failure mode require?",
}


def split_sections(markdown_body: str):
    """Split a doc body on ## headers into (section_title, section_text) pairs."""
    parts = re.split(r"\n##\s+", markdown_body.strip())
    sections = []
    for part in parts[1:]:  # parts[0] is the '# Title' preamble, skip it
        lines = part.strip().split("\n", 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        sections.append((title, body))
    return sections


def make_id(process_control: str, question: str) -> str:
    return hashlib.md5(f"{process_control}-{question}".encode()).hexdigest()[:10]


def build():
    records = []
    for filepath in sorted(glob.glob(SOURCE_GLOB)):
        post = frontmatter.load(filepath)
        name = post.get("name")
        failure_mode = post.get("failure_mode")

        for section_title, section_body in split_sections(post.content):
            question = QUESTION_TEMPLATES.get(
                section_title, f"Tell me about {section_title} for {name}."
            ).format(name=name)

            records.append({
                "id": make_id(PROCESS_CONTROL, question),
                "process_control": PROCESS_CONTROL,
                "failure_mode": failure_mode,
                "section": name,
                "question": question,
                "answer": section_body,
            })

    with open(OUTPUT_PATH, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Parsed {len(glob.glob(SOURCE_GLOB))} source docs -> {len(records)} Q&A records")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
