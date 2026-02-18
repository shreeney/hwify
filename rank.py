import glob
import re

def get_rows():
    data_list = []

    for filepath in glob.glob("**/*.txt", recursive=True):
        try:
            with open(filepath, 'r') as f:
                content = f.read()

                # Updated: Captures the entire string after "Hardware: "
                hw_match = re.search(r"Hardware:\s*(.*)", content)
                score_match = re.search(r"Ranking:\s*(\d+)/", content)

                if hw_match and score_match:
                    data_list.append({
                        "name": hw_match.group(1).strip(),
                        "score": int(score_match.group(1))
                    })
        except Exception:
            continue

    data_list.sort(key=lambda x: x['score'], reverse=True)

    for item in data_list:
        row = f"<tr><td>{item['name']}</td><td>{item['score']}</td></tr>"
        print(row)

if __name__ == "__main__":
    get_rows()
