import json, csv, os

with open("data/demo_messages.json", "r", encoding="utf-8") as f:
    data = json.load(f)

os.makedirs("output", exist_ok=True)
out_path = "output/demo_output.csv"
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["channel_id", "author", "timestamp", "content"])
    for m in data:
        w.writerow([m["channel_id"], m["author"], m["timestamp"], m["content"]])

print(f"Demo finished. Output written to {out_path}")
